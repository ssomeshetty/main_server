"""
Comprehensive MyNeta Enrichment Command
========================================
Scrapes myneta.info for all 224 Karnataka 2023 MLAs and populates:
- Age, Photo URL
- Total Assets (movable + immovable), Total Liabilities
- Education, Profession
- Criminal Cases → LegalRecord entries
"""
import logging
import re
import time
from decimal import Decimal
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand
from django.db import transaction

from politicians_tracker.apps.core.models import (
    Politician, Constituency, FinancialDeclaration, LegalRecord,
)
from politicians_tracker.apps.core.scrapers.base_scraper import polite_request

logger = logging.getLogger(__name__)

MYNETA_BASE = "https://myneta.info/karnataka2023/"


def parse_rs_value(val_str):
    """Parse 'Rs 33,14,49,445~33 Crore+' → Decimal."""
    if not val_str:
        return Decimal('0')
    val_str = val_str.strip()
    if 'Nil' in val_str or val_str == '':
        return Decimal('0')
    match = re.search(r'Rs\s*([\d,]+)', val_str)
    if match:
        num_str = match.group(1).replace(',', '')
        try:
            return Decimal(num_str)
        except Exception:
            return Decimal('0')
    # Try plain number
    match2 = re.search(r'([\d,]+)', val_str)
    if match2:
        num_str = match2.group(1).replace(',', '')
        try:
            return Decimal(num_str)
        except Exception:
            return Decimal('0')
    return Decimal('0')


def normalize_const_name(name):
    """Normalize constituency name for fuzzy matching."""
    name = name.upper()
    name = re.sub(r'\(SC\)|\(ST\)', '', name)
    name = re.sub(r'[^A-Z0-9]', '', name)
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


class Command(BaseCommand):
    help = 'Full MyNeta enrichment: age, photo, assets, liabilities, criminal cases for all MLAs'

    def add_arguments(self, parser):
        parser.add_argument('--politician-id', type=int, help='Process specific politician ID')
        parser.add_argument('--dry-run', action='store_true', help='Print what would be done without saving')
        parser.add_argument('--limit', type=int, default=0, help='Limit number of politicians to process')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        limit = options['limit']
        specific_id = options['politician_id']

        self.stdout.write(self.style.NOTICE('=== MyNeta Full Enrichment ==='))

        if specific_id:
            politicians = Politician.objects.filter(id=specific_id, is_active=True)
        else:
            politicians = Politician.objects.filter(is_active=True).order_by('id')

        if limit:
            politicians = politicians[:limit]

        total = politicians.count()
        success = 0
        skipped = 0
        failed = 0

        # Lazy-loaded winner map (only built if needed)
        winner_map = None

        for idx, pol in enumerate(politicians, 1):
            self.stdout.write(f'\n[{idx}/{total}] {pol.full_name_en}')

            # Strategy 1: Use existing declaration_url (instant)
            myneta_url = None
            fin = FinancialDeclaration.objects.filter(politician=pol).first()
            if fin and fin.declaration_url and 'myneta.info' in fin.declaration_url:
                myneta_url = fin.declaration_url

            # Strategy 2: Fall back to winner map (slow, built once)
            if not myneta_url:
                if winner_map is None:
                    self.stdout.write('Building winner map from MyNeta (one-time)...')
                    winner_map = self._build_winner_map()
                    self.stdout.write(f'  Found winner URLs for {len(winner_map)} constituencies')
                db_constituencies = list(Constituency.objects.all())
                myneta_url = self._find_myneta_url(pol, winner_map, db_constituencies)

            if not myneta_url:
                self.stdout.write(self.style.WARNING(f'  ✗ No MyNeta URL found'))
                skipped += 1
                continue

            self.stdout.write(f'  URL: {myneta_url}')

            # Step 3: Fetch and parse the profile
            data = self._parse_profile(myneta_url)
            if not data:
                self.stdout.write(self.style.WARNING(f'  ✗ Could not parse profile'))
                failed += 1
                continue

            # Print what we found
            self.stdout.write(f'  Age: {data["age"]}, Photo: {"✓" if data["photo_url"] else "✗"}')
            self.stdout.write(f'  Assets: ₹{data["assets"]}, Liabilities: ₹{data["liabilities"]}')
            self.stdout.write(f'  Education: {data["education"]}, Profession: {data["profession"]}')
            self.stdout.write(f'  Criminal Cases: {len(data["criminal_cases"])}')

            if dry_run:
                success += 1
                continue

            # Step 4: Save to database
            with transaction.atomic():
                self._save_politician_data(pol, data, myneta_url)

            success += 1
            self.stdout.write(self.style.SUCCESS(f'  ✓ Enriched successfully'))

            # Polite delay
            time.sleep(1.5)

        self.stdout.write(self.style.SUCCESS(
            f'\n=== Complete: {success} enriched, {skipped} skipped, {failed} failed ==='
        ))

    def _build_winner_map(self):
        """Build a map of normalized constituency name → MyNeta winner candidate URL."""
        result = {}

        response, error = polite_request(MYNETA_BASE)
        if error or not response:
            self.stdout.write(self.style.ERROR(f'Failed to fetch MyNeta index: {error}'))
            return result

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all constituency links
        constituency_links = []
        for link in soup.find_all('a', href=re.compile('action=show_candidates')):
            href = link.get('href')
            name = link.get_text(strip=True)
            if href and name:
                constituency_links.append((name, urljoin(MYNETA_BASE, href)))

        self.stdout.write(f'  Found {len(constituency_links)} constituencies on MyNeta')

        for const_name, const_url in constituency_links:
            norm = normalize_const_name(const_name)

            resp, err = polite_request(const_url)
            if err or not resp:
                continue

            c_soup = BeautifulSoup(resp.text, 'html.parser')

            # Find the winner in the candidates table
            for table in c_soup.find_all('table'):
                for row in table.find_all('tr'):
                    text = row.get_text()
                    if 'Winner' in text:
                        link_tag = row.find('a', href=re.compile('candidate.php'))
                        if link_tag:
                            candidate_url = urljoin(MYNETA_BASE, link_tag.get('href'))
                            result[norm] = candidate_url
                            break
                if norm in result:
                    break

            time.sleep(1)

        return result

    def _find_myneta_url(self, pol, winner_map, db_constituencies):
        """Find the MyNeta URL for a given politician."""
        if pol.current_constituency:
            norm = normalize_const_name(pol.current_constituency.constituency_name_en)
            if norm in winner_map:
                return winner_map[norm]

            # Try contains match
            for key, url in winner_map.items():
                if norm in key or key in norm:
                    return url
                # Try first 6 chars
                if len(norm) >= 6 and len(key) >= 6 and norm[:6] == key[:6]:
                    return url

        return None

    def _parse_profile(self, url):
        """Parse a MyNeta candidate profile page. Returns dict with all data."""
        response, error = polite_request(url)
        if error or not response:
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        full_text = soup.get_text()

        data = {
            'age': None,
            'photo_url': '',
            'assets': Decimal('0'),
            'liabilities': Decimal('0'),
            'education': '',
            'profession': '',
            'criminal_cases': [],
        }

        # === AGE ===
        age_match = re.search(r'Age:\s*(\d+)', full_text)
        if age_match:
            data['age'] = int(age_match.group(1))

        # === PHOTO ===
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if 'images_candidate' in src and 'nophoto' not in src.lower():
                if not src.startswith('http'):
                    src = urljoin(url, src)
                data['photo_url'] = src
                break

        # === ASSETS & LIABILITIES (from summary table) ===
        for table in soup.find_all('table'):
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    label = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    if 'Assets' in label and 'Rs' in value:
                        data['assets'] = parse_rs_value(value)
                    elif 'Liabilities' in label and 'Rs' in value:
                        data['liabilities'] = parse_rs_value(value)

        # === EDUCATION ===
        # Look for the education section after "Educational Details"
        edu_header = soup.find(string=re.compile('Educational Details'))
        if edu_header:
            parent = edu_header.find_parent()
            if parent:
                next_elem = parent.find_next_sibling()
                if next_elem:
                    edu_text = next_elem.get_text(strip=True)
                    if edu_text and len(edu_text) < 200:
                        data['education'] = edu_text

        # === PROFESSION ===
        prof_match = re.search(r'Self\s*Profession\s*:\s*(.+?)(?:\s*Spouse|$)', full_text)
        if prof_match:
            data['profession'] = prof_match.group(1).strip()

        # === CRIMINAL CASES ===
        for table in soup.find_all('table'):
            header_row = table.find('tr')
            if not header_row:
                continue
            headers = [c.get_text(strip=True).lower() for c in header_row.find_all(['td', 'th'])]

            if any('ipc section' in h or 'ipc applicability' in h or 'ipc sections' in h for h in headers):
                idx_map = {}
                for idx, h in enumerate(headers):
                    if 'fir' in h:
                        idx_map['fir'] = idx
                    elif 'case no' in h:
                        idx_map['case_no'] = idx
                    elif 'court' in h:
                        idx_map['court'] = idx
                    elif 'ipc section' in h:
                        idx_map['ipc'] = idx
                    elif 'other details' in h or 'other acts' in h:
                        idx_map['other'] = idx

                for row in table.find_all('tr')[1:]:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) < len(headers):
                        continue
                    row_text = row.get_text(strip=True)
                    if 'no cases' in row_text.lower():
                        continue

                    def get_cell(key):
                        idx = idx_map.get(key, -1)
                        return cells[idx].get_text(strip=True) if idx != -1 and idx < len(cells) else ''

                    fir = get_cell('fir')
                    case_no = get_cell('case_no')
                    court = get_cell('court')
                    ipc = get_cell('ipc')
                    other = get_cell('other')

                    sections = [s.strip() for s in re.split(r'[,;\s]+', ipc) if s.strip()]
                    if other:
                        sections.append(other)

                    data['criminal_cases'].append({
                        'fir_no': fir,
                        'case_no': case_no,
                        'court_name': court,
                        'ipc_sections': sections,
                        'other_sections': [other] if other else [],
                        'description': f"FIR: {fir}. Court: {court}.",
                    })

        return data

    def _save_politician_data(self, pol, data, myneta_url):
        """Save extracted data to the database."""
        # 1. Update Politician fields
        changed = False
        if data['age'] and not pol.age:
            pol.age = data['age']
            changed = True
        if data['photo_url'] and not pol.photo_url:
            pol.photo_url = data['photo_url']
            changed = True

        # Build enriched bio addendum
        bio_additions = []
        if data['education'] and data['education'] not in (pol.biography_en or ''):
            bio_additions.append(f"Education: {data['education']}")
        if data['profession'] and data['profession'] not in (pol.biography_en or ''):
            bio_additions.append(f"Profession: {data['profession']}")
        if bio_additions:
            existing_bio = pol.biography_en or ''
            pol.biography_en = (existing_bio + '\n' + '\n'.join(bio_additions)).strip()
            changed = True

        if changed:
            pol.save()

        # 2. Update/Create FinancialDeclaration
        FinancialDeclaration.objects.update_or_create(
            politician=pol,
            declaration_year=2023,
            declaration_type='election',
            defaults={
                'total_assets': data['assets'],
                'total_liabilities': data['liabilities'],
                'declaration_url': myneta_url,
                'is_verified': False,
                'verification_status': 'scraped',
                'source_organization': 'MyNeta / ADR',
            }
        )

        # 3. Upsert LegalRecords (Criminal Cases)
        if data['criminal_cases']:
            # Delete old records and recreate
            LegalRecord.objects.filter(politician=pol).delete()
            for case in data['criminal_cases']:
                try:
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
                        case_url=myneta_url,
                    )
                except Exception as e:
                    logger.error(f"Error creating LegalRecord for {pol.full_name_en}: {e}")
