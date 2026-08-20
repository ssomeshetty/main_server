from django.core.management.base import BaseCommand
from politicians_tracker.apps.core.models import Politician
from politicians_tracker.apps.core.scrapers.myneta_scraper import MyNetaScraper

import re
from urllib.parse import urljoin
from politicians_tracker.apps.core.scrapers.base_scraper import polite_request
from bs4 import BeautifulSoup

def parse_currency_to_decimal(val_str):
    if not val_str or 'Nil' in val_str:
        return 0
    match = re.search(r'Rs\s*([\d,]+)', val_str)
    if match:
        num_str = match.group(1).replace(',', '')
        try:
            return int(num_str)
        except ValueError:
            return 0
    return 0

class Command(BaseCommand):
    def handle(self, *args, **options):
        pol = Politician.objects.get(slug='h-c-mahadevappa')
        self.stdout.write(f"Scraping {pol.full_name_en}...")
        
        # 2. MyNeta
        self.stdout.write("Fetching MyNeta...")
        base_url = "https://myneta.info/karnataka2023/"
        resp, _ = polite_request(base_url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        const_url = None
        for link in soup.find_all('a', href=re.compile('action=show_candidates')):
            if 'NARASIPUR' in link.get_text(strip=True).upper():
                const_url = urljoin(base_url, link.get('href'))
                break
                
        if not const_url:
            self.stdout.write("Could not find T. Narasipur on MyNeta")
            return
            
        self.stdout.write(f"Found Constituency: {const_url}")
        resp, _ = polite_request(const_url)
        soup = BeautifulSoup(resp.text, 'html.parser')

        
        cand_url = None
        tables = soup.find_all('table')
        for table in tables:
            for row in table.find_all('tr'):
                if 'Winner' in row.get_text():
                    link = row.find('a')
                    if link:
                        cand_url = urljoin(base_url, link.get('href'))
                        break
            if cand_url: break
                
        if cand_url:
            self.stdout.write(f"Found MyNeta profile: {cand_url}")
            scraper = MyNetaScraper(election_year='2023', state='Karnataka', save_to_db=False)
            data = scraper.parse_candidate_profile(cand_url)
            
            from politicians_tracker.apps.core.models import FinancialDeclaration, LegalRecord
            assets = parse_currency_to_decimal(data.assets_total)
            liabilities = parse_currency_to_decimal(data.liabilities_total)
            
            FinancialDeclaration.objects.update_or_create(
                politician=pol,
                declaration_year=2023,
                defaults={
                    'total_assets': assets,
                    'total_liabilities': liabilities,
                    'declaration_url': cand_url,
                    'declaration_type': 'election'
                }
            )
            self.stdout.write("Saved Financials")
            
            LegalRecord.objects.filter(politician=pol).delete()
            for case in (data.criminal_cases or []):
                LegalRecord.objects.create(
                    politician=pol,
                    case_status='charges_filed',
                    ipc_sections=[case.get('ipc_section', '')],
                    description_en=case.get('description', ''),
                    case_url=cand_url
                )
            self.stdout.write(f"Saved {len(data.criminal_cases or [])} Legal Records")
        
        self.stdout.write(self.style.SUCCESS('Done!'))
