from django.core.management.base import BaseCommand
from politicians_tracker.apps.core.models import Politician, FinancialDeclaration, LegalRecord
from politicians_tracker.apps.core.scrapers.myneta_scraper import MyNetaScraper
from politicians_tracker.apps.core.scrapers.base_scraper import polite_request
from bs4 import BeautifulSoup
import logging
import time

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Scrape only criminal cases for politicians who have financial declarations'

    def handle(self, *args, **options):
        self.stdout.write("Starting criminal cases scraping...")
        declarations = FinancialDeclaration.objects.filter(declaration_url__isnull=False).exclude(declaration_url="")
        self.stdout.write(f"Found {declarations.count()} politicians with profile URLs to parse")
        
        scraper = MyNetaScraper(election_year='2023', state='Karnataka', save_to_db=False)
        
        updated_count = 0
        for decl in declarations:
            pol = decl.politician
            
            # Defensive check for empty or invalid url
            url = decl.declaration_url.strip() if decl.declaration_url else ""
            if not url or not url.startswith('http'):
                continue
                
            # Check if we already have legal records for this politician to avoid double-scraping
            if LegalRecord.objects.filter(politician=pol).exists():
                continue
                
            self.stdout.write(f"Scraping cases for {pol.full_name_en}...")
            
            resp, error = polite_request(url)
            if error or not resp:
                self.stdout.write(self.style.ERROR(f"Failed to fetch {url}: {error}"))
                continue
                
            soup = BeautifulSoup(resp.text, 'html.parser')
            cases = scraper._extract_criminal_cases(soup)
            
            if cases:
                LegalRecord.objects.filter(politician=pol).delete()
                for case in cases:
                    fir_no = case.get('fir_no', '')
                    police_station = ''
                    if ',' in fir_no:
                        parts = fir_no.split(',')
                        fir_no = parts[0].strip()
                        if len(parts) > 1:
                            police_station = parts[1].strip()
                    
                    LegalRecord.objects.create(
                        politician=pol,
                        case_status='charges_filed',
                        case_number=case.get('case_no') or fir_no or 'Pending',
                        police_station=police_station,
                        ipc_sections=case.get('ipc_sections', []),
                        other_sections=case.get('other_sections', []),
                        description_en=case.get('description', ''),
                        court_name=case.get('court_name', ''),
                        case_url=decl.declaration_url
                    )
                self.stdout.write(self.style.SUCCESS(f"  Added {len(cases)} cases for {pol.full_name_en}"))
                updated_count += 1
            else:
                self.stdout.write(f"  No cases found for {pol.full_name_en}")
                
            time.sleep(2)
            
        self.stdout.write(self.style.SUCCESS(f"Finished. Updated cases for {updated_count} politicians."))
