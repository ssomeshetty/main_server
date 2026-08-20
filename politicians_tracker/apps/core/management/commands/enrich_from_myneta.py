import logging
import re
import time
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand
from django.db import transaction

from politicians_tracker.apps.core.models import Politician, Constituency, FinancialDeclaration, LegalRecord
from politicians_tracker.apps.core.scrapers.myneta_scraper import MyNetaScraper
from politicians_tracker.apps.core.scrapers.base_scraper import polite_request

logger = logging.getLogger(__name__)

def parse_currency_to_decimal(val_str):
    """Parse a string like 'Rs 1,00,00,000 ~ 1 Crore+' to a Decimal value."""
    if not val_str or 'Nil' in val_str:
        return 0
    # Extract the numeric part (e.g. 1,00,00,000)
    match = re.search(r'Rs\s*([\d,]+)', val_str)
    if match:
        num_str = match.group(1).replace(',', '')
        try:
            return int(num_str)
        except ValueError:
            return 0
    return 0

class Command(BaseCommand):
    help = 'Enrich existing politicians with MyNeta data (assets, liabilities, criminal cases)'

    def handle(self, *args, **options):
        self.stdout.write('Starting MyNeta enrichment for Karnataka 2023...')
        
        scraper = MyNetaScraper(election_year='2023', state='Karnataka', save_to_db=False)
        base_url = "https://myneta.info/karnataka2023/"
        
        # Fetch constituency index
        self.stdout.write('Fetching constituency index...')
        response, error = polite_request(base_url)
        if error or not response:
            self.stdout.write(self.style.ERROR(f'Failed to fetch MyNeta index: {error}'))
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all constituency links
        constituency_links = []
        for link in soup.find_all('a', href=re.compile('action=show_candidates')):
            href = link.get('href')
            name = link.get_text(strip=True)
            if href and name:
                constituency_links.append((name, urljoin(base_url, href)))
                
        self.stdout.write(f'Found {len(constituency_links)} constituencies on MyNeta')
        
        db_constituencies = list(Constituency.objects.all())
        
        def normalize_const_name(name):
            name = name.upper()
            name = re.sub(r'\(SC\)|\(ST\)', '', name)
            name = re.sub(r'[^A-Z0-9]', '', name)
            
            # Common variations
            replacements = {
                'CHAMRAJAPET': 'CHAMARAJAPET',
                'CVRAMANNNAGAR': 'CVRAMANNAGAR',
                'KRPURA': 'KRISHNARAJAPURAM',
                'PULAKESHINAGAR': 'PULIKESHINAGAR',
                'YASHWANTHAPURA': 'YESHWANTHPUR',
                'YESHWANTHPUR': 'YESHWANTHPUR',
                'GOVINDARAJANAGAR': 'GOVINDRAJNAGAR',
                'PADMANABANAGAR': 'PADMANABHANAGAR',
                'HOSAKOTE': 'HOSKOTE',
                'BAILAHONGAL': 'BAILHONGAL',
                'RAYBAG': 'RAIBAG',
                'YEMKANAMARDI': 'YEMKANMARDI',
                'SIRAGUPPA': 'SIRUGUPPA',
                'DEVARAHIPPARGI': 'DEVARHIPPARGI',
                'NAGTHAN': 'NAGATHAN',
                'SINDGI': 'SINDAGI',
                'GAURIBIDANUR': 'GOWRIBIDANUR',
                'CHICKAMAGALUR': 'CHIKMAGALUR',
                'CHIKKAMAGALURU': 'CHIKMAGALUR',
                'BANTWAL': 'BANTVAL',
                'GANGAVATHI': 'GANGAWATI',
                'PIRIYAPATNA': 'PERIYAPATNA',
                'BHADRAVATHI': 'BHADRAVATI',
                'BAINDUR': 'BYNDOOR',
                'RAMANAGARAM': 'RAMANAGARAM',
                'CHIKKNAYAKANHALLI': 'CHIKNAYAKANHALLI',
                'ARAKALGUD': 'ARKALGUD',
                'SAKALESHPUR': 'SAKLESHPUR',
                'KALAGHATGI': 'KALGHATGI',
                'KRISHNARAJPET': 'KRISHNARAJAPET',
                'VIJAYANAGAR': 'VIJAYNAGAR',
            }
            if name in replacements:
                name = replacements[name]
            return name
            
        def find_matching_constituency(mn_name):
            norm_mn = normalize_const_name(mn_name)
            
            # 1. Exact match on normalized
            for db_c in db_constituencies:
                norm_db = normalize_const_name(db_c.constituency_name_en)
                if norm_mn == norm_db:
                    return db_c
                    
            # 2. Contains match
            for db_c in db_constituencies:
                norm_db = normalize_const_name(db_c.constituency_name_en)
                if norm_mn in norm_db or norm_db in norm_mn:
                    return db_c
                    
            # 3. Try fallback using first 6 chars contains
            for db_c in db_constituencies:
                if db_c.constituency_name_en.lower()[:6] == mn_name.lower()[:6]:
                    return db_c
            return None

        updated_count = 0
        for const_name, const_url in constituency_links:
            db_constituency = find_matching_constituency(const_name)
            if not db_constituency:
                self.stdout.write(self.style.WARNING(f'  Could not match constituency {const_name}'))
                continue
                
            # Find the active politician for this constituency
            politician = Politician.objects.filter(current_constituency=db_constituency, is_active=True).first()
            if not politician:
                continue
                
            # Skip if already enriched
            if FinancialDeclaration.objects.filter(politician=politician).exists():
                continue
                
            self.stdout.write(f'Processing {const_name} -> found {politician.full_name_en}')
            
            # Fetch candidates in this constituency
            resp, err = polite_request(const_url)
            if err or not resp:
                continue
                
            c_soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Find candidate table
            tables = c_soup.find_all('table')
            candidate_url = None
            for table in tables:
                headers = [th.get_text(strip=True).lower() for th in table.find_all('th')]
                if not headers and table.find('tr'):
                    # Sometimes th is td
                    headers = [td.get_text(strip=True).lower() for td in table.find('tr').find_all('td')]
                    
                if 'candidate' in headers or any('candidate' in h for h in headers):
                    # Find winner or match by name
                    for row in table.find_all('tr')[1:]:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) > 1:
                            cand_name = cells[1].get_text(strip=True)
                            
                            # Myneta puts 'Winner' in the name cell for the winner
                            if 'Winner' in cand_name or politician.first_name_en.lower() in cand_name.lower():
                                link_tag = cells[1].find('a')
                                if link_tag:
                                    candidate_url = urljoin(base_url, link_tag.get('href'))
                                    break
                    if candidate_url:
                        break
                        
            if not candidate_url:
                self.stdout.write(self.style.WARNING(f'  Could not find MyNeta profile for {politician.full_name_en}'))
                continue
                
            # Now we have the URL, parse profile
            self.stdout.write(f'  Fetching profile: {candidate_url}')
            data = scraper.parse_candidate_profile(candidate_url)
            if not data:
                continue
                
            # Update database
            with transaction.atomic():
                # 1. Update Politician demographics
                if data.age:
                    # Not standard field, but good to have. We don't have age field in Politician, so we skip age
                    pass
                if data.education:
                    # We can put this in biography if we want
                    politician.biography_en += f"\\nEducation: {data.education}"
                    politician.save()
                    
                # 2. Add FinancialDeclaration
                assets = parse_currency_to_decimal(data.assets_total)
                liabilities = parse_currency_to_decimal(data.liabilities_total)
                
                # Check if declaration exists
                decl, created = FinancialDeclaration.objects.update_or_create(
                    politician=politician,
                    declaration_year=2023,
                    declaration_type='election',
                    defaults={
                        'total_assets': assets,
                        'total_liabilities': liabilities,
                        'declaration_url': candidate_url,
                        'is_verified': True
                    }
                )
                
                # 3. Add LegalRecords (Criminal Cases)
                if data.criminal_cases:
                    # Delete old records to avoid duplicates if re-running
                    LegalRecord.objects.filter(politician=politician).delete()
                    for case in data.criminal_cases:
                        try:
                            fir_no = case.get('fir_no', '')
                            police_station = ''
                            if ',' in fir_no:
                                parts = fir_no.split(',')
                                fir_no = parts[0].strip()
                                if len(parts) > 1:
                                    police_station = parts[1].strip()
                                    
                            LegalRecord.objects.create(
                                politician=politician,
                                case_status='charges_filed',
                                case_number=case.get('case_no') or fir_no or 'Pending',
                                police_station=police_station,
                                ipc_sections=case.get('ipc_sections', []),
                                other_sections=case.get('other_sections', []),
                                description_en=case.get('description', ''),
                                court_name=case.get('court_name', ''),
                                case_url=candidate_url
                            )
                        except Exception as e:
                            logger.error(f"Error creating LegalRecord for {politician.full_name_en}: {e}")
                        
            updated_count += 1
            self.stdout.write(self.style.SUCCESS(f'  Successfully enriched {politician.full_name_en}'))
            
            # Polite delay
            time.sleep(2)
            
        self.stdout.write(self.style.SUCCESS(f'\\nEnrichment complete! Updated {updated_count} politicians.'))
