"""
Generic Link/News Document Fetcher
==================================
Robust document fetcher for news articles and public PDFs.
Handles raw text extraction, HTML sanitization, and database storage.
"""

import re
import logging
import hashlib
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urljoin, urlparse
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from django.utils import timezone

from ..models import RawScrapedData
from .base_scraper import (
    BaseScraper,
    polite_request,
    rotate_user_agent,
    extract_text_from_html,
    sanitize_html,
    calculate_content_hash,
    get_domain_from_url,
    is_url_already_scraped,
    detect_language,
    ScrapeResult,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Supported Content Types
# =============================================================================

PDF_MIME_TYPES = [
    'application/pdf',
    'application/x-pdf',
    'pdf',
]

HTML_MIME_TYPES = [
    'text/html',
    'application/xhtml+xml',
]

TEXT_MIME_TYPES = [
    'text/plain',
    'application/json',
    'application/xml',
]


@dataclass
class DocumentMetadata:
    """Metadata extracted from document."""
    title: Optional[str]
    author: Optional[str]
    publish_date: Optional[datetime]
    description: Optional[str]
    keywords: List[str]
    language: str
    mime_type: str
    content_length: int
    source_url: str
    redirected_url: Optional[str]


class GenericDocumentFetcher(BaseScraper):
    """
    Universal document fetcher for news, PDFs, and web content.
    Handles content extraction, sanitization, and database storage.
    """

    SOURCE_TYPE = 'news_article'
    SCRAPER_NAME = 'generic_fetcher'

    # Domain-specific processing configurations
    DOMAIN_CONFIG = {
        'deccanherald.com': {
            'article_selector': 'article',
            'title_selector': 'h1',
            'content_selector': '.article-body, .content-body, article',
            'author_selector': '.author-name, .byline',
            'date_selector': 'time[datetime], .publish-date',
            'remove_selectors': ['script', 'style', 'nav', 'footer', '.ad', '.advertisement'],
        },
        'prajavani.net': {
            'article_selector': 'article',
            'title_selector': 'h1.entry-title, h1.post-title',
            'content_selector': '.entry-content, .post-content, article',
            'author_selector': '.author, .byline',
            'date_selector': 'time, .published-date',
            'remove_selectors': ['script', 'style', 'nav', 'footer', '.ad', '.social-share'],
        },
        'thehindu.com': {
            'article_selector': 'article',
            'title_selector': 'h1.title',
            'content_selector': '.article-text, .article-body, article',
            'author_selector': '.author-name, .byline',
            'date_selector': 'time[datetime]',
            'remove_selectors': ['script', 'style', '.ad', '.promo'],
        },
        'indianexpress.com': {
            'article_selector': 'article',
            'title_selector': 'h1.headline',
            'content_selector': '.article-body, .article-content',
            'author_selector': '.author-name',
            'date_selector': 'time[datetime]',
            'remove_selectors': ['script', 'style', '.ad', '.social-share'],
        },
    }

    def __init__(
        self,
        pdf_processor: Optional['PDFProcessor'] = None,
        default_source_type: str = 'news_article',
        **kwargs
    ):
        """
        Initialize generic document fetcher.

        Args:
            pdf_processor: Optional custom PDF processor
            default_source_type: Default source type for URLs
            **kwargs: Base scraper kwargs
        """
        super().__init__(**kwargs)
        self.pdf_processor = pdf_processor
        self.default_source_type = default_source_type

        # Detect content type from URL extension
        self.url_extension_map = {
            '.pdf': 'affidavit',
            '.doc': 'document',
            '.docx': 'document',
            '.xlsx': 'document',
            '.csv': 'document',
            '.json': 'data_file',
            '.xml': 'data_file',
        }

    def fetch_url(
        self,
        url: str,
        source_type: Optional[str] = None,
        source_organization: Optional[str] = None,
        **kwargs
    ) -> Optional[RawScrapedData]:
        """
        Fetch a URL and save to database.

        Args:
            url: URL to fetch
            source_type: Optional source type override
            source_organization: Optional source organization override
            **kwargs: Additional metadata

        Returns:
            RawScrapedData instance or None
        """
        # Detect URL extension for content type
        parsed = urlparse(url)
        path = parsed.path.lower()

        detected_type = source_type
        if not detected_type:
            for ext, content_type in self.url_extension_map.items():
                if path.endswith(ext):
                    detected_type = content_type
                    break

        if not detected_type:
            detected_type = self.default_source_type

        # Check for PDF
        if path.endswith('.pdf') or 'content-type' in str(kwargs):
            return self._fetch_pdf(url, source_type, source_organization, **kwargs)

        # Fetch HTML/text content
        return self._fetch_html(url, detected_type, source_organization, **kwargs)

    def _fetch_pdf(
        self,
        url: str,
        source_type: str,
        source_organization: Optional[str],
        **kwargs
    ) -> Optional[RawScrapedData]:
        """
        Fetch and process PDF document.

        Args:
            url: PDF URL
            source_type: Source type
            source_organization: Source organization
            **kwargs: Additional metadata

        Returns:
            RawScrapedData instance or None
        """
        logger.info(f"Fetching PDF: {url}")

        response, error = polite_request(
            url,
            timeout=self.timeout + 30,  # PDFs take longer
            max_retries=self.max_retries,
            base_delay=self.base_delay,
        )

        if error or not response:
            logger.error(f"Failed to fetch PDF: {error}")
            if self.save_to_db:
                return self._save_failed(url, error, source_type, source_organization, **kwargs)
            return None

        # Check for duplicates
        content_hash = calculate_content_hash(response.text if response.text else str(response.content))
        if is_url_already_scraped(url, content_hash):
            logger.info(f"Duplicate detected, skipping: {url}")
            return None

        # Process PDF
        pdf_content = response.content

        # Extract text using processor
        extracted_text = ''
        if self.pdf_processor:
            try:
                extracted_text = self.pdf_processor.extract_text(pdf_content)
            except Exception as e:
                logger.warning(f"PDF extraction failed: {e}")
                extracted_text = "PDF content - extraction failed"

        # Create metadata
        metadata = {
            'scraper': self.SCRAPER_NAME,
            'document_type': 'pdf',
            'content_size': len(pdf_content),
            'content_type': response.headers.get('content-type', 'application/pdf'),
        }

        source_domain = get_domain_from_url(url)
        language = detect_language(extracted_text)

        if self.save_to_db:
            record = RawScrapedData(
                content_raw_html='',
                content_raw_text=extracted_text[:50000],
                content_pdf_text=extracted_text,
                content_binary=pdf_content[:1000000],  # Limit binary storage
                source_type=source_type or 'affidavit',
                source_url=url,
                source_domain=source_domain,
                source_organization=source_organization or source_domain,
                scraper_name=self.SCRAPER_NAME,
                processing_status='pending',
                language_detected=language,
                word_count=len(extracted_text.split()),
                content_hash=content_hash,
                scrape_metadata=metadata,
            )

            record.full_clean()
            record.save()
            logger.info(f"Saved PDF: {record.id} - {url}")
            return record

        return None

    def _fetch_html(
        self,
        url: str,
        source_type: str,
        source_organization: Optional[str],
        **kwargs
    ) -> Optional[RawScrapedData]:
        """
        Fetch and process HTML document.

        Args:
            url: HTML URL
            source_type: Source type
            source_organization: Source organization
            **kwargs: Additional metadata

        Returns:
            RawScrapedData instance or None
        """
        logger.info(f"Fetching HTML: {url}")

        response, error = polite_request(
            url,
            timeout=self.timeout,
            max_retries=self.max_retries,
            base_delay=self.base_delay,
        )

        if error or not response:
            logger.error(f"Failed to fetch URL: {error}")
            if self.save_to_db:
                return self._save_failed(url, error, source_type, source_organization, **kwargs)
            return None

        # Check for duplicates
        content_hash = calculate_content_hash(response.text)
        if is_url_already_scraped(url, content_hash):
            logger.info(f"Duplicate detected, skipping: {url}")
            return None

        # Extract metadata and content
        metadata = self._extract_metadata(response, url)
        content = self._extract_content(response, url)

        source_domain = get_domain_from_url(url)
        language = detect_language(content.extracted_text)

        # Update metadata with extracted info
        metadata.update({
            'title': content.title,
            'author': content.author,
            'publish_date': content.publish_date.isoformat() if content.publish_date else None,
            'description': content.description,
        })

        if self.save_to_db:
            record = RawScrapedData(
                content_raw_html=response.text[:100000],
                content_raw_text=content.extracted_text[:50000],
                source_type=source_type,
                source_url=url,
                source_domain=source_domain,
                source_organization=source_organization or source_domain,
                scraper_name=self.SCRAPER_NAME,
                processing_status='pending',
                language_detected=language,
                word_count=len(content.extracted_text.split()),
                content_hash=content_hash,
                scrape_metadata=metadata,
                published_date=content.publish_date,
            )

            record.full_clean()
            record.save()
            logger.info(f"Saved document: {record.id} - {url}")
            return record

        return None

    def _extract_metadata(
        self,
        response: requests.Response,
        url: str
    ) -> Dict[str, Any]:
        """
        Extract metadata from HTML response.

        Args:
            response: HTTP response
            url: Source URL

        Returns:
            Dictionary of metadata
        """
        soup = BeautifulSoup(response.text, 'html.parser')
        source_domain = get_domain_from_url(url)

        metadata = {
            'scraper': self.SCRAPER_NAME,
            'document_type': 'html',
            'http_status': response.status_code,
            'final_url': response.url,
            'content_length': len(response.text),
            'content_type': response.headers.get('content-type', ''),
            'source_domain': source_domain,
        }

        # Extract Open Graph and Twitter Card metadata
        og_tags = {}
        for tag in soup.find_all('meta', property=re.compile(r'^og:')):
            prop = tag.get('property', '').replace('og:', '')
            og_tags[prop] = tag.get('content', '')

        if og_tags:
            metadata['og_tags'] = og_tags

        # Extract canonical URL
        canonical = soup.find('link', rel='canonical')
        if canonical:
            metadata['canonical_url'] = canonical.get('href', '')

        return metadata

    def _extract_content(
        self,
        response: requests.Response,
        url: str
    ) -> 'ExtractedContent':
        """
        Extract clean content from HTML.

        Args:
            response: HTTP response
            url: Source URL

        Returns:
            ExtractedContent instance
        """
        soup = BeautifulSoup(response.text, 'html.parser')
        source_domain = get_domain_from_url(url)

        # Get domain-specific config
        config = self.DOMAIN_CONFIG.get(source_domain, {})

        # Extract title
        title = self._extract_title(soup, config)

        # Extract author
        author = self._extract_author(soup, config)

        # Extract publish date
        publish_date = self._extract_publish_date(soup, config)

        # Extract description
        description = self._extract_description(soup)

        # Extract keywords
        keywords = self._extract_keywords(soup)

        # Extract main content
        extracted_text = self._extract_main_content(soup, url, config)

        return ExtractedContent(
            title=title,
            author=author,
            publish_date=publish_date,
            description=description,
            keywords=keywords,
            extracted_text=extracted_text,
            source_url=url,
        )

    def _extract_title(self, soup: BeautifulSoup, config: Dict) -> Optional[str]:
        """Extract article title."""
        title_selectors = config.get('title_selector', ['h1'])

        for selector in title_selectors:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text(strip=True)

        # Fallback: meta title
        meta_title = soup.find('meta', property='og:title')
        if meta_title:
            return meta_title.get('content', '').strip()

        meta_title = soup.find('title')
        if meta_title:
            return meta_title.get_text(strip=True)

        return None

    def _extract_author(self, soup: BeautifulSoup, config: Dict) -> Optional[str]:
        """Extract article author."""
        author_selectors = config.get('author_selector', ['.author', '.byline'])

        for selector in author_selectors:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text(strip=True)

        # Fallback: meta author
        meta_author = soup.find('meta', attrs={'name': 'author'})
        if meta_author:
            return meta_author.get('content', '').strip()

        return None

    def _extract_publish_date(
        self,
        soup: BeautifulSoup,
        config: Dict
    ) -> Optional[datetime]:
        """Extract publish date."""
        date_selectors = config.get('date_selector', ['time'])

        for selector in date_selectors:
            elem = soup.select_one(selector)
            if elem:
                # Try datetime attribute first
                datetime_val = elem.get('datetime')
                if datetime_val:
                    try:
                        return datetime.fromisoformat(datetime_val.replace('Z', '+00:00'))
                    except ValueError:
                        pass

                # Try text content
                text = elem.get_text(strip=True)
                if text:
                    return self._parse_date(text)

        # Fallback: meta article:published_time
        meta_date = soup.find('meta', property='article:published_time')
        if meta_date:
            try:
                return datetime.fromisoformat(meta_date.get('content', '').replace('Z', '+00:00'))
            except ValueError:
                pass

        return None

    def _parse_date(self, date_string: str) -> Optional[datetime]:
        """Parse date string to datetime."""
        # Try common formats
        formats = [
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%d %B %Y',
            '%d %b %Y',
            '%B %d, %Y',
            '%d-%m-%Y',
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue

        return None

    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article description."""
        # OG description
        meta_desc = soup.find('meta', property='og:description')
        if meta_desc:
            return meta_desc.get('content', '').strip()

        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            return meta_desc.get('content', '').strip()

        return None

    def _extract_keywords(self, soup: BeautifulSoup) -> List[str]:
        """Extract keywords."""
        # Meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            keywords = meta_keywords.get('content', '')
            return [k.strip() for k in keywords.split(',') if k.strip()]

        return []

    def _extract_main_content(
        self,
        soup: BeautifulSoup,
        url: str,
        config: Dict
    ) -> str:
        """Extract main article content."""
        source_domain = get_domain_from_url(url)

        # Remove unwanted elements
        remove_selectors = config.get(
            'remove_selectors',
            ['script', 'style', 'nav', 'footer', 'aside', '.ad', '.advertisement',
             '.social-share', '.comments', '.related', '.sidebar']
        )

        for selector in remove_selectors:
            for elem in soup.select(selector):
                elem.decompose()

        # Find article content
        article_selector = config.get('article_selector', 'article')
        content_selector = config.get('content_selector', '.article-body, .content')

        article = soup.select_one(article_selector)
        if article:
            content_elem = article
        else:
            content_elem = soup.select_one(content_selector)

        if content_elem:
            # Extract text from content area
            text = extract_text_from_html(str(content_elem))
        else:
            # Fallback: extract from body
            body = soup.find('body')
            if body:
                text = extract_text_from_html(str(body))
            else:
                text = extract_text_from_html(soup.get_text())

        # Clean up extra whitespace
        lines = (line.strip() for line in text.splitlines())
        text = '\n'.join(line for line in lines if line)

        return text

    def _save_failed(
        self,
        url: str,
        error: str,
        source_type: Optional[str] = None,
        source_organization: Optional[str] = None,
        **kwargs
    ) -> RawScrapedData:
        """Save failed fetch attempt."""
        if source_type is None:
            source_type = self.default_source_type
        source_domain = get_domain_from_url(url)
        if source_organization is None:
            source_organization = source_domain

        record = RawScrapedData(
            source_type=source_type,
            source_url=url,
            source_domain=source_domain,
            source_organization=source_organization,
            scraper_name=self.SCRAPER_NAME,
            processing_status='failed',
            processing_error=error,
            content_hash='',
            language_detected='unknown',
        )

        record.full_clean()
        record.save()
        return record

    def fetch_batch(
        self,
        urls: List[str],
        source_type: Optional[str] = None,
        source_organization: Optional[str] = None,
        delay_between_urls: Optional[float] = None,
    ) -> List[RawScrapedData]:
        """
        Fetch multiple URLs sequentially.

        Args:
            urls: List of URLs to fetch
            source_type: Optional source type for all URLs
            source_organization: Optional source organization
            delay_between_urls: Additional delay between URLs

        Returns:
            List of saved RawScrapedData records
        """
        results = []
        delay = delay_between_urls or self.base_delay

        for i, url in enumerate(urls):
            logger.info(f"Fetching {i + 1}/{len(urls)}: {url}")
            try:
                result = self.fetch_url(
                    url,
                    source_type=source_type,
                    source_organization=source_organization,
                )
                if result:
                    results.append(result)
            except Exception as e:
                logger.error(f"Error fetching {url}: {e}")
                results.append(self._save_failed(url, str(e), source_type or 'other', source_organization))

            # Delay between URLs
            if i < len(urls) - 1:
                time.sleep(delay)

        return results


@dataclass
class ExtractedContent:
    """Content extracted from document."""
    title: Optional[str]
    author: Optional[str]
    publish_date: Optional[datetime]
    description: Optional[str]
    keywords: List[str]
    extracted_text: str
    source_url: str


class PDFProcessor:
    """
    PDF text extraction processor.
    Uses pdfplumber or PyPDF2 for text extraction.
    """

    def __init__(self, use_ocr: bool = False):
        """
        Initialize PDF processor.

        Args:
            use_ocr: Whether to use OCR for scanned PDFs
        """
        self.use_ocr = use_ocr
        self.logger = logging.getLogger(__name__)

    def extract_text(self, pdf_bytes: bytes) -> str:
        """
        Extract text from PDF bytes.

        Args:
            pdf_bytes: Raw PDF bytes

        Returns:
            Extracted text
        """
        text = ''

        # Try pdfplumber first (better text extraction)
        try:
            import pdfplumber
            with pdfplumber.open(pdf_bytes) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + '\n\n'
            self.logger.info("Extracted text using pdfplumber")
            return text
        except ImportError:
            self.logger.warning("pdfplumber not installed, trying PyPDF2")
        except Exception as e:
            self.logger.warning(f"pdfplumber extraction failed: {e}")

        # Fallback to PyPDF2
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(pdf_bytes)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + '\n\n'
            self.logger.info("Extracted text using PyPDF2")
            return text
        except ImportError:
            self.logger.warning("PyPDF2 not installed")
        except Exception as e:
            self.logger.warning(f"PyPDF2 extraction failed: {e}")

        # OCR fallback for scanned PDFs
        if self.use_ocr:
            try:
                from PIL import Image
                import pytesseract
                images = self._pdf_to_images(pdf_bytes)
                for image in images:
                    text += pytesseract.image_to_string(image) + '\n'
                self.logger.info("Extracted text using OCR")
                return text
            except Exception as e:
                self.logger.warning(f"OCR extraction failed: {e}")

        return text

    def _pdf_to_images(self, pdf_bytes: bytes) -> List:
        """
        Convert PDF pages to images for OCR.

        Args:
            pdf_bytes: Raw PDF bytes

        Returns:
            List of PIL Images
        """
        # Implementation would use pdf2image library
        return []