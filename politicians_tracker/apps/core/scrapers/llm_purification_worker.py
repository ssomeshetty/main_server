"""
LLM Purification Worker
=======================
Background worker that processes RawScrapedData through LLM for content purification.
Uses Google GenAI SDK or OpenAI SDK for structured JSON outputs.
"""

import os
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from django.conf import settings

# Import models
from ..models import RawScrapedData, PublicRecord, Politician

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# LLM Configuration
# =============================================================================

LLM_PROVIDER = getattr(settings, 'LLM_PROVIDER', 'google')  # 'google' or 'openai'
LLM_MODEL = getattr(settings, 'LLM_MODEL', 'gemini-2.0-flash-exp')

# Google GenAI Configuration
GOOGLE_API_KEY = getattr(settings, 'GOOGLE_API_KEY', os.environ.get('GOOGLE_API_KEY', ''))

# OpenAI Configuration
OPENAI_API_KEY = getattr(settings, 'OPENAI_API_KEY', os.environ.get('OPENAI_API_KEY', ''))
OPENAI_MODEL = getattr(settings, 'OPENAI_MODEL', 'gpt-4o')

# Processing Configuration
BATCH_SIZE = int(getattr(settings, 'LLM_WORKER_BATCH_SIZE', 10))
MAX_RETRIES = int(getattr(settings, 'LLM_WORKER_MAX_RETRIES', 3))
WORKER_CONCURRENCY = int(getattr(settings, 'LLM_WORKER_CONCURRENCY', 4))


# =============================================================================
# System Prompt - Strict Guidelines
# =============================================================================

SYSTEM_PROMPT = """You are a politically neutral, completely objective, non-partisan editor specializing in processing political data.

## CRITICAL RULES

1. **NEUTRALITY**: Remain completely neutral. Do not express opinions, take sides, or use emotionally charged language. Politicians from ALL parties must be treated equally.

2. **OBJECTIVE LANGUAGE**: 
   - Use passive legal phrases for allegations
   - Examples: "An FIR was filed alleging..." instead of "The politician stole..."
   - Examples: "Assets were declared totaling..." instead of "The politician is corrupt..."
   - Never use words like "corrupt", "criminal", "scam", "fraud", "dirty", "stolen"

3. **FACT-BASED ONLY**:
   - Extract only from the provided raw text
   - Never add facts outside the source
   - If information is not in the text, say "Not mentioned in source"

4. **BILINGUAL OUTPUT**:
   - Generate English summary (formal, factual news tone)
   - Generate Kannada translation (maintain formal, objective news-style tone)
    - Use proper Kannada script. Write raw Kannada characters directly (e.g., "ಅಖಂಡ"). Do NOT output unicode escape sequences like \\uXXXX.

5. **STRUCTURED OUTPUT**:
   - Output ONLY valid JSON matching the specified schema
   - Include all required fields
   - Use null for missing information

6. **IMPACT-FREE SUMMARY**:
   - Summarize the raw text's content without editorializing
   - Focus on: WHO, WHAT, WHEN, WHERE
   - For speeches: Key points raised, topics discussed
   - For allegations: Nature of allegations, current status
   - For financial: Total amounts declared, categories
"""


# =============================================================================
# LLM Response Schema
# =============================================================================

@dataclass
class PurifiedContent:
    """Structured output from LLM purification."""
    # Identification
    politician_name: Optional[str] = None
    politician_name_kn: Optional[str] = None
    constituency: Optional[str] = None
    district: Optional[str] = None
    party: Optional[str] = None

    # Content Classification
    record_type: str = 'statement'  # speech, statement, controversy, allegation, etc.
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    # English Content
    title_en: Optional[str] = None
    summary_en: Optional[str] = None
    content_en: Optional[str] = None

    # Kannada Content
    title_kn: Optional[str] = None
    summary_kn: Optional[str] = None
    content_kn: Optional[str] = None

    # Verification
    verification_status: str = 'unverified'
    confidence_score: Optional[float] = None

    # Metadata
    event_date: Optional[str] = None
    source_organization: Optional[str] = None
    language_detected: str = 'en'

    # Error handling
    error: Optional[str] = None

    @property
    def is_valid(self) -> bool:
        """Check if response has meaningful content."""
        return bool(self.summary_en or self.summary_kn) and self.error is None


# =============================================================================
def safe_extract_json(text: str) -> dict:
    """Robustly extract and parse JSON from LLM response text, handling surrounding markdown and text."""
    import re
    import json
    
    text = text.strip()
    
    # 1. Try matching ```json ... ``` block
    match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass
            
    # 2. Try matching ``` ... ``` block
    match = re.search(r'```\s*(.*?)\s*```', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass
            
    # 3. Try matching between first '{' and last '}'
    match = re.search(r'(\{.*\})', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass
            
    # 4. Standard fallback
    return json.loads(text)


def get_full_prompt(prompt: str, system_prompt: str) -> str:
    return f"""{system_prompt}

## INPUT TEXT TO PROCESS:
{prompt}

## REQUIRED OUTPUT FORMAT (JSON):
{{
    "politician_name": "Name in English or null",
    "politician_name_kn": "Name in Kannada or null", 
    "constituency": "Constituency name or null",
    "district": "District name or null",
    "party": "Party name or null",
    "record_type": "speech|statement|controversy|allegation|promise|initiative|other",
    "categories": ["category1", "category2"],
    "tags": ["tag1", "tag2"],
    "title_en": "English title or null",
    "summary_en": "English summary - factual, neutral, news-style",
    "content_en": "Full English content or null",
    "title_kn": "Kannada title or null",
    "summary_kn": "Kannada summary - formal, objective translation",
    "content_kn": "Full Kannada content or null",
    "verification_status": "unverified|partially_verified|verified",
    "confidence_score": 0.0-1.0 or null,
    "event_date": "YYYY-MM-DD or null",
    "source_organization": "Source name or null",
    "language_detected": "en|kn|mixed"
}}

## OUTPUT:
Provide ONLY valid JSON. No markdown formatting, no code blocks, no explanations.
"""


class BaseLLMProvider:
    """Abstract base class for LLM providers."""

    def complete(self, prompt: str, system_prompt: str) -> PurifiedContent:
        """Generate purified content from raw text."""
        raise NotImplementedError


class GoogleGenAIProvider(BaseLLMProvider):
    """Google GenAI SDK provider (Gemini)."""

    def __init__(self, model: str = LLM_MODEL):
        self.model = model
        self._client = None
        self._init_client()

    def _init_client(self):
        """Initialize Google GenAI client."""
        try:
            from google import genai
            self._client = genai.Client(api_key=GOOGLE_API_KEY)
        except ImportError:
            logger.error("Google GenAI SDK not installed. Run: pip install google-genai")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Google GenAI client: {e}")
            raise

    def complete(self, prompt: str, system_prompt: str = SYSTEM_PROMPT) -> PurifiedContent:
        """Call Gemini API with structured output."""
        import time

        for attempt in range(MAX_RETRIES):
            try:
                # Construct the full prompt
                full_prompt = get_full_prompt(prompt, system_prompt)

                # Call API with response mime type for JSON
                response = self._client.models.generate_content(
                    model=self.model,
                    contents=full_prompt,
                    config={
                        'response_mime_type': 'application/json',
                    }
                )

                # Parse response
                if hasattr(response, 'text'):
                    text = response.text
                else:
                    text = str(response)

                data = safe_extract_json(text)
                return self._parse_response(data)

            except json.JSONDecodeError as e:
                logger.warning(f"JSON parse error (attempt {attempt + 1}): {e}")
                time.sleep(2 ** attempt)

            except Exception as e:
                logger.warning(f"API error (attempt {attempt + 1}): {e}")
                time.sleep(2 ** attempt)

        return PurifiedContent(error=f"Max retries exceeded after {MAX_RETRIES} attempts")

    def _parse_response(self, data: Dict[str, Any]) -> PurifiedContent:
        """Parse API response into PurifiedContent."""
        return PurifiedContent(
            politician_name=data.get('politician_name'),
            politician_name_kn=data.get('politician_name_kn'),
            constituency=data.get('constituency'),
            district=data.get('district'),
            party=data.get('party'),
            record_type=data.get('record_type', 'statement'),
            categories=data.get('categories', []),
            tags=data.get('tags', []),
            title_en=data.get('title_en'),
            summary_en=data.get('summary_en'),
            content_en=data.get('content_en'),
            title_kn=data.get('title_kn'),
            summary_kn=data.get('summary_kn'),
            content_kn=data.get('content_kn'),
            verification_status=data.get('verification_status', 'unverified'),
            confidence_score=data.get('confidence_score'),
            event_date=data.get('event_date'),
            source_organization=data.get('source_organization'),
            language_detected=data.get('language_detected', 'en'),
        )


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider (GPT-4)."""

    def __init__(self, model: str = OPENAI_MODEL):
        self.model = model
        self._client = None
        self._init_client()

    def _init_client(self):
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI
            kwargs = {'api_key': OPENAI_API_KEY, 'max_retries': 0}
            if OPENAI_API_KEY and OPENAI_API_KEY.startswith('nvapi-'):
                kwargs['base_url'] = 'https://integrate.api.nvidia.com/v1'
                if self.model == 'gpt-4o' or '70b' in self.model:
                    self.model = 'meta/llama-3.1-8b-instruct'
            self._client = OpenAI(**kwargs)
        except ImportError:
            logger.error("OpenAI SDK not installed. Run: pip install openai")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise

    def complete(self, prompt: str, system_prompt: str = SYSTEM_PROMPT) -> PurifiedContent:
        """Call OpenAI API with JSON mode."""
        import time

        for attempt in range(MAX_RETRIES):
            try:
                response = self._client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that outputs only valid JSON conforming to the requested schema."},
                        {"role": "user", "content": get_full_prompt(prompt, system_prompt)}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.3,  # Adjusted to avoid repetition loops on llama models
                    max_tokens=2048,
                    timeout=30,
                )

                text = response.choices[0].message.content
                data = safe_extract_json(text)
                return self._parse_response(data)

            except json.JSONDecodeError as e:
                logger.warning(f"JSON parse error (attempt {attempt + 1}): {e}")
                print(f"Raw Text: {response.choices[0].message.content}")
                time.sleep(2 ** attempt)

            except Exception as e:
                logger.warning(f"API error (attempt {attempt + 1}): {e}")
                print(f"API Error Details: {e}")
                time.sleep(2 ** attempt)

        return PurifiedContent(error=f"Max retries exceeded after {MAX_RETRIES} attempts")

    def _parse_response(self, data: Dict[str, Any]) -> PurifiedContent:
        """Parse API response into PurifiedContent."""
        return PurifiedContent(
            politician_name=data.get('politician_name'),
            politician_name_kn=data.get('politician_name_kn'),
            constituency=data.get('constituency'),
            district=data.get('district'),
            party=data.get('party'),
            record_type=data.get('record_type', 'statement'),
            categories=data.get('categories', []),
            tags=data.get('tags', []),
            title_en=data.get('title_en'),
            summary_en=data.get('summary_en'),
            content_en=data.get('content_en'),
            title_kn=data.get('title_kn'),
            summary_kn=data.get('summary_kn'),
            content_kn=data.get('content_kn'),
            verification_status=data.get('verification_status', 'unverified'),
            confidence_score=data.get('confidence_score'),
            event_date=data.get('event_date'),
            source_organization=data.get('source_organization'),
            language_detected=data.get('language_detected', 'en'),
        )


def get_llm_provider() -> BaseLLMProvider:
    """Get configured LLM provider."""
    if LLM_PROVIDER == 'google':
        return GoogleGenAIProvider()
    elif LLM_PROVIDER == 'openai':
        return OpenAIProvider()
    else:
        raise ValueError(f"Unknown LLM provider: {LLM_PROVIDER}")


# =============================================================================
# Purification Worker
# =============================================================================

class PurificationWorker:
    """
    Background worker that processes RawScrapedData through LLM.
    """

    def __init__(
        self,
        provider: Optional[BaseLLMProvider] = None,
        batch_size: int = BATCH_SIZE,
        max_workers: int = WORKER_CONCURRENCY,
    ):
        """
        Initialize worker.

        Args:
            provider: LLM provider instance (auto-created if None)
            batch_size: Number of records to process per batch
            max_workers: Thread pool concurrency
        """
        self.provider = provider or get_llm_provider()
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.stats = {
            'processed': 0,
            'failed': 0,
            'skipped': 0,
        }

    def run(self, limit: Optional[int] = None):
        """
        Run the worker to process pending records.

        Args:
            limit: Optional limit on records to process
        """
        logger.info("Starting LLM purification worker")

        while True:
            # Fetch pending records
            records = RawScrapedData.objects.filter(
                processing_status='pending'
            ).order_by('priority', 'published_date', 'scraped_at')[:self.batch_size]

            if not records:
                logger.info("No pending records. Worker idle.")
                break

            if limit and self.stats['processed'] >= limit:
                logger.info(f"Reached processing limit: {limit}")
                break

            # Process in parallel
            self._process_batch(records)

            logger.info(
                f"Progress: {self.stats['processed']} processed, "
                f"{self.stats['failed']} failed, "
                f"{self.stats['skipped']} skipped"
            )

        logger.info("Worker finished")
        return self.stats

    def _process_batch(self, records: List[RawScrapedData]):
        """Process a batch of records."""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._process_record, record): record
                for record in records
            }

            for future in as_completed(futures):
                record = futures[future]
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Record {record.id} raised exception: {e}")
                    self.stats['failed'] += 1

    def _process_record(self, record: RawScrapedData) -> Optional[PublicRecord]:
        """
        Process a single RawScrapedData record.

        Args:
            record: RawScrapedData instance

        Returns:
            PublicRecord instance or None
        """
        logger.info(f"Processing record {record.id}: {record.source_url[:50]}...")

        # Prepare raw text for LLM
        raw_text = self._prepare_raw_text(record)

        # Call LLM
        purified = self.provider.complete(raw_text)

        if purified.error:
            logger.error(f"Record {record.id} LLM error: {purified.error}")
            record.processing_status = 'failed'
            record.processing_error = purified.error
            record.processing_attempts += 1
            record.save(update_fields=['processing_status', 'processing_error', 'processing_attempts'])
            self.stats['failed'] += 1
            return None

        # Save to PublicRecord in transaction
        try:
            public_record = self._save_public_record(record, purified)
            self.stats['processed'] += 1
            return public_record
        except Exception as e:
            logger.error(f"Record {record.id} database error: {e}")
            self.stats['failed'] += 1
            raise

    def _prepare_raw_text(self, record: RawScrapedData) -> str:
        """Prepare raw text for LLM processing."""
        parts = []

        # Source info
        if record.source_organization:
            parts.append(f"Source: {record.source_organization}")

        if record.published_date:
            parts.append(f"Date: {record.published_date}")

        if record.source_url:
            parts.append(f"URL: {record.source_url}")

        # Content
        if record.content_raw_text:
            parts.append(f"\nContent:\n{record.content_raw_text[:15000]}")

        if record.content_pdf_text:
            parts.append(f"\nPDF Content:\n{record.content_pdf_text[:15000]}")

        # Metadata from scrape_metadata
        if record.scrape_metadata:
            metadata_str = json.dumps(record.scrape_metadata, ensure_ascii=False)
            parts.append(f"\nMetadata: {metadata_str}")

        return '\n'.join(parts)

    @transaction.atomic
    def _save_public_record(
        self,
        raw_record: RawScrapedData,
        purified: PurifiedContent
    ) -> PublicRecord:
        """
        Save purified content to PublicRecord and update RawScrapedData.

        Args:
            raw_record: Source RawScrapedData instance
            purified: LLM purified content

        Returns:
            Created PublicRecord instance
        """
        # Create PublicRecord
        public_record = PublicRecord(
            politician=self._find_or_create_politician(purified),
            record_type=purified.record_type,
            title_en=purified.title_en or '',
            title_kn=purified.title_kn or '',
            content_en=purified.content_en or '',
            content_kn=purified.content_kn or '',
            summary_en=purified.summary_en or '',
            summary_kn=purified.summary_kn or '',
            categories=purified.categories,
            tags=purified.tags,
            event_date=self._parse_date(purified.event_date),
            source_url=raw_record.source_url,
            source_organization=purified.source_organization or raw_record.source_organization,
            verification_status=purified.verification_status,
            sentiment_score=Decimal(str(purified.confidence_score)) if purified.confidence_score else None,
            language=purified.language_detected,
            word_count=len((purified.summary_en or '').split()) + len((purified.summary_kn or '').split()),
        )

        public_record.full_clean()
        public_record.save()

        # Update RawScrapedData status
        raw_record.processing_status = 'processed'
        raw_record.processing_completed_at = timezone.now()
        raw_record.processed_by = f"{LLM_PROVIDER}-{LLM_MODEL}"
        raw_record.processing_metadata = {
            'model': LLM_MODEL,
            'confidence_score': purified.confidence_score,
            'record_type': purified.record_type,
        }
        raw_record.linked_public_record = public_record
        raw_record.save(update_fields=[
            'processing_status', 'processing_completed_at', 'processed_by',
            'processing_metadata', 'linked_public_record'
        ])

        logger.info(f"Created PublicRecord {public_record.id} from RawScrapedData {raw_record.id}")
        return public_record

    def _find_or_create_politician(self, purified: PurifiedContent) -> Optional[Politician]:
        """
        Find or create Politician from purified data.

        Args:
            purified: Purified content with politician info

        Returns:
            Politician instance or None
        """
        if not purified.politician_name:
            return None

        # Try to find by name
        try:
            politician = Politician.objects.filter(
                full_name_en__icontains=purified.politician_name.split()[-1]
            ).first()

            if politician:
                return politician
        except Exception as e:
            logger.warning(f"Politician lookup failed: {e}")

        return None

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime."""
        if not date_str:
            return None

        formats = [
            '%Y-%m-%d',
            '%d-%m-%Y',
            '%Y/%m/%d',
            '%d/%m/%Y',
            '%B %d, %Y',
            '%d %B %Y',
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return None


# =============================================================================
# CLI Entry Point
# =============================================================================

def run_worker(limit: Optional[int] = None, provider: Optional[str] = None):
    """
    Run the purification worker.

    Args:
        limit: Optional limit on records to process
        provider: Override LLM provider ('google' or 'openai')
    """
    if provider:
        global LLM_PROVIDER
        LLM_PROVIDER = provider

    worker = PurificationWorker()
    stats = worker.run(limit=limit)

    print(f"\n{'='*50}")
    print("Worker Statistics:")
    print(f"  Processed: {stats['processed']}")
    print(f"  Failed:    {stats['failed']}")
    print(f"  Skipped:   {stats['skipped']}")
    print(f"{'='*50}\n")

    return stats


def process_single_record(record_id: int) -> Optional[PublicRecord]:
    """
    Process a single record by ID.

    Args:
        record_id: RawScrapedData ID

    Returns:
        PublicRecord instance or None
    """
    try:
        record = RawScrapedData.objects.get(id=record_id)
    except RawScrapedData.DoesNotExist:
        logger.error(f"Record {record_id} not found")
        return None

    worker = PurificationWorker()
    return worker._process_record(record)


def reprocess_failed_records(limit: int = 100):
    """
    Reprocess failed records.

    Args:
        limit: Maximum records to reprocess
    """
    # Update status back to pending
    updated = RawScrapedData.objects.filter(
        processing_status='failed',
        processing_attempts__lt=MAX_RETRIES
    )[:limit].update(processing_status='pending')

    logger.info(f"Requeued {updated} failed records for reprocessing")

    # Run worker
    worker = PurificationWorker()
    return worker.run(limit=limit)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='LLM Purification Worker')
    parser.add_argument('--limit', type=int, default=None, help='Limit records to process')
    parser.add_argument('--provider', choices=['google', 'openai'], default=None, help='LLM provider')
    parser.add_argument('--single', type=int, default=None, help='Process single record by ID')
    parser.add_argument('--reprocess', action='store_true', help='Reprocess failed records')
    parser.add_argument('--batch', type=int, default=None, help='Batch size')

    args = parser.parse_args()

    if args.single:
        process_single_record(args.single)
    elif args.reprocess:
        reprocess_failed_records(args.limit or 100)
    else:
        run_worker(limit=args.limit, provider=args.provider)