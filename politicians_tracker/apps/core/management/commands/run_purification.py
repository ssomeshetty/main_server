import logging
import time

from django.core.management.base import BaseCommand
from django.db import transaction

from politicians_tracker.apps.core.models import RawScrapedData, PublicRecord, Politician
from politicians_tracker.apps.core.scrapers.llm_purification_worker import get_llm_provider, SYSTEM_PROMPT

logger = logging.getLogger(__name__)

def resolve_politician(pol_name: str, text_to_process: str, politician_hint: str = None):
    from django.db.models import Q
    
    # 1. Gather candidates
    candidates = []
    if pol_name:
        candidates = list(Politician.objects.filter(
            Q(full_name_en__icontains=pol_name) | Q(full_name_kn__icontains=pol_name),
            is_active=True
        ))
    
    # If no matches, try politician_hint
    if not candidates and politician_hint:
        candidates = list(Politician.objects.filter(
            Q(full_name_en__icontains=politician_hint) | Q(full_name_kn__icontains=politician_hint),
            is_active=True
        ))
        
    if not candidates:
        return None
        
    if len(candidates) == 1:
        return candidates[0]
        
    # Disambiguate using contextual clues in the raw text
    text_lower = text_to_process.lower()
    scored_candidates = []
    for p in candidates:
        score = 0
        
        # Check constituency
        if p.current_constituency:
            const_name = p.current_constituency.constituency_name_en.lower()
            if const_name in text_lower:
                score += 10
            
        # Check party
        if p.current_party:
            party_name = p.current_party.party_name_en.lower()
            party_abbr = p.current_party.party_short_name_en.lower() if p.current_party.party_short_name_en else ''
            if party_name in text_lower:
                score += 5
            if party_abbr and party_abbr in text_lower:
                score += 3
                
        # Check district
        if p.current_constituency and p.current_constituency.district:
            district_name = p.current_constituency.district.district_name_en.lower()
            if district_name in text_lower:
                score += 4
                
        # Check exact full name match in text
        if p.full_name_en.lower() in text_lower:
            score += 8
            
        # If politician_hint matches exactly
        if politician_hint and p.full_name_en.lower() == politician_hint.lower():
            score += 15
            
        scored_candidates.append((score, p))
        
    scored_candidates.sort(key=lambda x: x[0], reverse=True)
    return scored_candidates[0][1]


class Command(BaseCommand):
    help = 'Process raw scraped data through LLM for purification and categorization'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=10, help='Max records to process')
        parser.add_argument('--status', type=str, default='pending', help='Status to filter by (pending, failed)')

    def handle(self, *args, **options):
        limit = options['limit']
        status = options['status']
        
        self.stdout.write(f'Initializing LLM Provider (will use NVIDIA API if nvapi key set)...')
        
        try:
            llm_provider = get_llm_provider()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to initialize LLM provider: {e}'))
            return
            
        records = RawScrapedData.objects.filter(processing_status=status).order_by('scraper_name', '-id')[:limit]
        self.stdout.write(f'Found {records.count()} records to process.')
        
        processed_count = 0
        failed_count = 0
        
        for record in records:
            # Mark as processing
            record.processing_status = 'processing'
            record.save()
            
            # Prepare prompt
            text_to_process = record.content_raw_text or record.content_raw_html
            # Limit length for LLM context window
            text_to_process = text_to_process[:8000]
            
            # Include metadata in prompt to help LLM
            meta = record.scrape_metadata or {}
            politician_hint = meta.get('related_politician', '')
            if politician_hint:
                text_to_process = f"[HINT: This article is related to politician '{politician_hint}']\n\n" + text_to_process
                
            self.stdout.write(f'Processing Record {record.id}...')
            
            try:
                result = llm_provider.complete(text_to_process, SYSTEM_PROMPT)
                
                if result.error:
                    self.stdout.write(self.style.ERROR(f'  LLM Error: {result.error}'))
                    record.processing_status = 'failed'
                    record.processing_error = result.error
                    record.save()
                    failed_count += 1
                    continue
                    
                if not result.is_valid:
                    self.stdout.write(self.style.WARNING(f'  Invalid response format from LLM'))
                    record.processing_status = 'failed'
                    record.processing_error = 'Invalid or empty response format'
                    record.save()
                    failed_count += 1
                    continue
                    
                # Success! Map LLM result to PublicRecord
                with transaction.atomic():
                    # Attempt to link to politician
                    pol_name = result.politician_name or politician_hint
                    politician = resolve_politician(pol_name, text_to_process, politician_hint)
                    
                    if not politician:
                        self.stdout.write(self.style.WARNING(f'  Could not resolve politician "{pol_name}". Skipping record.'))
                        record.processing_status = 'skipped'
                        record.processing_error = f"Could not resolve politician '{pol_name}' to any target database MLA"
                        record.save()
                        continue
                        
                    # Prepare data
                    event_date = None
                    if result.event_date and result.event_date.strip().lower() not in ('null', 'none', ''):
                        try:
                            from datetime import datetime
                            # Parse and validate YYYY-MM-DD
                            event_date = datetime.strptime(result.event_date.strip()[:10], '%Y-%m-%d').date()
                        except ValueError:
                            pass
                            
                    PublicRecord.objects.create(
                        politician=politician,
                        record_type=result.record_type,
                        title_en=result.title_en or 'Untitled',
                        title_kn=result.title_kn or 'Untitled',
                        summary_en=result.summary_en or '',
                        summary_kn=result.summary_kn or '',
                        content_en=result.content_en or '',
                        content_kn=result.content_kn or '',
                        categories=result.categories,
                        tags=result.tags,
                        event_date=event_date,
                        source_url=record.source_url,
                        source_organization=result.source_organization or record.source_organization,
                        verification_status=result.verification_status,
                    )
                    
                    record.processing_status = 'processed'
                    if politician:
                        record.identified_politician = politician
                    record.save()
                    
                self.stdout.write(self.style.SUCCESS(f'  Successfully purified! Mapped to: {result.record_type}'))
                processed_count += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  Exception: {e}'))
                record.processing_status = 'failed'
                record.processing_error = str(e)
                record.save()
                failed_count += 1
                
        self.stdout.write(self.style.SUCCESS(f'\\nPurification complete! Processed: {processed_count}, Failed: {failed_count}'))
