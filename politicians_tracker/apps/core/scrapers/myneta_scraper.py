"""
MyNeta/ADR Scraper Framework
============================
Crawls myneta.info for election candidate data.
Extracts candidate profiles, assets, and criminal records.
"""

import re
import logging
import time
import requests
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urljoin, parse_qs, urlparse

from bs4 import BeautifulSoup
from django.utils import timezone

from ..models import Politician, Constituency, District, RawScrapedData
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


@dataclass
class CandidateData:
    """Structured data extracted from candidate profile."""
    name: str
    constituency: str
    district: str
    party: str
    age: Optional[int]
    gender: Optional[str]
    education: Optional[str]
    profession: Optional[str]
    assets_total: Optional[str]
    liabilities_total: Optional[str]
    criminal_cases: List[Dict[str, Any]]
    source_url: str
    raw_html: str


class MyNetaScraper(BaseScraper):
    """
    Scraper for MyNeta.info election data.
    Targets Karnataka 2023 and other state elections.
    """

    SOURCE_TYPE = 'ec_portal'
    SOURCE_DOMAIN = 'myneta.info'
    SCRAPER_NAME = 'myneta_scraper'

    def __init__(
        self,
        election_year: str = '2023',
        state: str = 'Karnataka',
        **kwargs
    ):
        """
        Initialize MyNeta scraper.

        Args:
            election_year: Election year (e.g., '2023', '2018')
            state: State name for URL construction
        """
        super().__init__(**kwargs)
        self.election_year = election_year
        self.state = state
        self.state_code = state.lower().replace(' ', '%20')

        # Base URLs
        self.base_url = "https://myneta.info"
        self.candidates_url = (
            f"{self.base_url}/{self.state_code}{self.election_year}/"
        )

    def get_constituency_links(self) -> List[str]:
        """
        Fetch the main candidates index page and extract all constituency links.

        Returns:
            List of absolute URLs for each constituency
        """
        logger.info(f"Fetching constituency index: {self.candidates_url}")

        response, error = polite_request(
            self.candidates_url,
            timeout=self.timeout,
            max_retries=self.max_retries,
            base_delay=self.base_delay,
        )

        if error or not response:
            logger.error(f"Failed to fetch index: {error}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find constituency table/links
        # MyNeta typically has a table or list with constituency links
        constituency_links = []

        # Common patterns for constituency links
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Use candidates_url as the base since the page is /karnataka2023/
            full_url = urljoin(self.candidates_url, href)
            
            # Match constituency URLs (e.g., index.php?action=show_candidates&constituency_id=1)
            if 'constituency' in full_url.lower() or 'action=show_candidates' in full_url.lower():
                constituency_links.append(full_url)

        # Remove duplicates and sort
        constituency_links = list(set(constituency_links))
        logger.info(f"Found {len(constituency_links)} constituency links")

        return constituency_links

    def get_candidate_links(self, constituency_url: str) -> List[str]:
        """
        Fetch a constituency page and extract individual candidate profile links.

        Args:
            constituency_url: URL of constituency page

        Returns:
            List of candidate profile URLs
        """
        logger.info(f"Fetching constituency: {constituency_url}")

        response, error = polite_request(
            constituency_url,
            timeout=self.timeout,
            max_retries=self.max_retries,
            base_delay=self.base_delay,
        )

        if error or not response:
            logger.error(f"Failed to fetch constituency: {error}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        candidate_links = []

        # Find candidate profile links
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            full_url = urljoin(self.candidates_url, href)

            # Match candidate profile URLs
            if 'candidate.php' in full_url.lower() or 'candidate_id=' in full_url.lower():
                candidate_links.append(full_url)

        # Remove duplicates
        candidate_links = list(set(candidate_links))
        logger.info(f"Found {len(candidate_links)} candidate links")

        return candidate_links

    def parse_candidate_profile(self, url: str) -> Optional[CandidateData]:
        """
        Parse a candidate profile page and extract all relevant data.

        Args:
            url: Candidate profile URL

        Returns:
            CandidateData instance or None
        """
        logger.info(f"Parsing candidate: {url}")

        response, error = polite_request(
            url,
            timeout=self.timeout,
            max_retries=self.max_retries,
            base_delay=self.base_delay,
        )

        if error or not response:
            logger.error(f"Failed to fetch candidate: {error}")
            return None

        # Check for duplicates - disabled so we always parse fetched/cached HTML
        # content_hash = calculate_content_hash(response.text)
        # if is_url_already_scraped(url, content_hash):
        #     logger.info(f"Duplicate detected, skipping: {url}")
        #     return None

        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        raw_text = extract_text_from_html(sanitize_html(response.text))

        # Extract data using common MyNeta patterns
        data = CandidateData(
            name=self._extract_name(soup),
            constituency=self._extract_constituency(soup),
            district=self._extract_district(soup),
            party=self._extract_party(soup),
            age=self._extract_age(soup),
            gender=self._extract_gender(soup),
            education=self._extract_education(soup),
            profession=self._extract_profession(soup),
            assets_total=self._extract_total_assets(soup),
            liabilities_total=self._extract_total_liabilities(soup),
            criminal_cases=self._extract_criminal_cases(soup),
            source_url=url,
            raw_html=response.text[:100000],
        )

        return data

    def _extract_name(self, soup: BeautifulSoup) -> str:
        """Extract candidate name from page."""
        # Common patterns: h1, h2 with candidate name
        for tag in soup.find_all(['h1', 'h2', 'h3']):
            text = tag.get_text(strip=True)
            if text and len(text) > 3:
                # Filter out navigation text
                if 'Candidate' in text or 'MyNeta' in text:
                    continue
                return text

        # Fallback: look for specific class patterns
        name_elem = soup.find('td', string=re.compile('Name', re.I))
        if name_elem:
            next_td = name_elem.find_next_sibling('td')
            if next_td:
                return next_td.get_text(strip=True)

        return ''

    def _extract_constituency(self, soup: BeautifulSoup) -> str:
        """Extract constituency name."""
        const_elem = soup.find(string=re.compile('Constituency', re.I))
        if const_elem:
            parent = const_elem.find_parent(['td', 'th', 'div', 'span'])
            if parent:
                next_elem = parent.find_next_sibling()
                if next_elem:
                    return next_elem.get_text(strip=True)

        return ''

    def _extract_district(self, soup: BeautifulSoup) -> str:
        """Extract district name."""
        dist_elem = soup.find(string=re.compile('District', re.I))
        if dist_elem:
            parent = dist_elem.find_parent(['td', 'th', 'div', 'span'])
            if parent:
                next_elem = parent.find_next_sibling()
                if next_elem:
                    return next_elem.get_text(strip=True)

        return ''

    def _extract_party(self, soup: BeautifulSoup) -> str:
        """Extract party name."""
        party_elem = soup.find(string=re.compile('Party', re.I))
        if party_elem:
            parent = party_elem.find_parent(['td', 'th', 'div', 'span'])
            if parent:
                next_elem = parent.find_next_sibling()
                if next_elem:
                    return next_elem.get_text(strip=True)

        return ''

    def _extract_age(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract age."""
        age_elem = soup.find(string=re.compile(r'\bAge\b'))
        if age_elem:
            match = re.search(r'(\d+)', age_elem)
            if match:
                return int(match.group(1))
        return None

    def _extract_gender(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract gender."""
        gender_elem = soup.find(string=re.compile(r'\bGender\b'))
        if gender_elem:
            text = gender_elem.lower()
            if 'male' in text:
                return 'male'
            elif 'female' in text:
                return 'female'
        return None

    def _extract_education(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract education level."""
        edu_elem = soup.find(string=re.compile('Education', re.I))
        if edu_elem:
            parent = edu_elem.find_parent(['td', 'th', 'div', 'span'])
            if parent:
                next_elem = parent.find_next_sibling()
                if next_elem:
                    return next_elem.get_text(strip=True)
        return None

    def _extract_profession(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract profession."""
        prof_elem = soup.find(string=re.compile(r'Self\s*Occupation', re.I))
        if prof_elem:
            parent = prof_elem.find_parent(['td', 'th', 'div', 'span'])
            if parent:
                next_elem = parent.find_next_sibling()
                if next_elem:
                    return next_elem.get_text(strip=True)
        return None

    def _extract_total_assets(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract total assets value."""
        # Look for "Total Assets" or similar
        for pattern in [r'Total\s*Assets', r'Total\s*Movable', r'Total\s*Immovable']:
            assets_elem = soup.find(string=re.compile(pattern, re.I))
            if assets_elem:
                # Navigate to value (typically next element)
                row = assets_elem.find_parent('tr')
                if row:
                    values = row.find_all(['td', 'th'])
                    if len(values) >= 2:
                        return values[-1].get_text(strip=True)
        return None

    def _extract_total_liabilities(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract total liabilities value."""
        liab_elem = soup.find(string=re.compile(r'Total\s*Liabilities', re.I))
        if liab_elem:
            row = liab_elem.find_parent('tr')
            if row:
                values = row.find_all(['td', 'th'])
                if len(values) >= 2:
                    return values[-1].get_text(strip=True)
        return None

    def _extract_criminal_cases(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract criminal case details."""
        cases = []
        for table in soup.find_all('table'):
            header_row = table.find('tr')
            if not header_row:
                continue
            headers = [cell.get_text(strip=True).lower() for cell in header_row.find_all(['td', 'th'])]
            if any('ipc section' in h or 'ipc applicability' in h or 'ipc sections' in h for h in headers):
                # This is a case table!
                idx_fir = -1
                idx_case = -1
                idx_court = -1
                idx_ipc = -1
                idx_other = -1
                for idx, h in enumerate(headers):
                    if 'fir' in h:
                        idx_fir = idx
                    elif 'case no' in h:
                        idx_case = idx
                    elif 'court' in h:
                        idx_court = idx
                    elif 'ipc section' in h:
                        idx_ipc = idx
                    elif 'other details' in h or 'other acts' in h:
                        idx_other = idx
                
                rows = table.find_all('tr')[1:]
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) < len(headers):
                        continue
                    row_text = row.get_text(strip=True)
                    if 'no cases' in row_text.lower():
                        continue
                    
                    fir_text = cells[idx_fir].get_text(strip=True) if idx_fir != -1 else ''
                    case_no = cells[idx_case].get_text(strip=True) if idx_case != -1 else ''
                    court = cells[idx_court].get_text(strip=True) if idx_court != -1 else ''
                    ipc = cells[idx_ipc].get_text(strip=True) if idx_ipc != -1 else ''
                    other = cells[idx_other].get_text(strip=True) if idx_other != -1 else ''
                    
                    # Split ipc sections by comma/space
                    sections = [s.strip() for s in re.split(r'[,;\s]+', ipc) if s.strip()]
                    if other:
                        sections.append(other)
                        
                    cases.append({
                        'description': f"FIR: {fir_text}. Court: {court}.",
                        'ipc_sections': sections,
                        'other_sections': [other] if other else [],
                        'case_no': case_no,
                        'court_name': court,
                        'fir_no': fir_text
                    })
        return cases

    def _process_response(
        self,
        response: requests.Response,
        url: str,
        **kwargs
    ) -> Optional[ScrapeResult]:
        """Process candidate profile response."""
        content_html = response.text
        content_text = extract_text_from_html(sanitize_html(content_html))

        # Parse and extract candidate data
        soup = BeautifulSoup(content_html, 'html.parser')
        candidate_data = self.parse_candidate_profile(url)

        # Additional metadata for database
        metadata = {
            'candidate_name': candidate_data.name if candidate_data else '',
            'constituency': candidate_data.constituency if candidate_data else '',
            'party': candidate_data.party if candidate_data else '',
        }

        return ScrapeResult(
            success=True,
            content_html=content_html[:100000],
            content_text=content_text,
            status_code=response.status_code,
            redirected_url=response.url if response.url != url else None,
        )

    def _save_to_database(
        self,
        url: str,
        response: requests.Response,
        result: ScrapeResult,
        content_hash: str,
        **kwargs
    ) -> RawScrapedData:
        """Save candidate data to RawScrapedData."""
        # Parse candidate for additional metadata
        soup = BeautifulSoup(response.text, 'html.parser')
        candidate_data = self.parse_candidate_profile(url)

        source_domain = get_domain_from_url(url)
        language = detect_language(result.content_text or '')

        # Create JSON metadata
        metadata = {
            'scraper': self.SCRAPER_NAME,
            'election_year': self.election_year,
            'state': self.state,
            'candidate_data': {
                'name': candidate_data.name if candidate_data else '',
                'constituency': candidate_data.constituency if candidate_data else '',
                'district': candidate_data.district if candidate_data else '',
                'party': candidate_data.party if candidate_data else '',
                'age': candidate_data.age,
                'assets_total': candidate_data.assets_total,
                'liabilities_total': candidate_data.liabilities_total,
                'criminal_cases_count': len(candidate_data.criminal_cases) if candidate_data else 0,
            } if candidate_data else {},
        }

        record = RawScrapedData(
            content_raw_html=result.content_html or response.text[:100000],
            content_raw_text=result.content_text[:50000] if result.content_text else '',
            source_type=self.SOURCE_TYPE,
            source_url=url,
            source_domain=source_domain,
            source_organization=self.SOURCE_DOMAIN,
            scraper_name=self.SCRAPER_NAME,
            processing_status='pending',
            language_detected=language,
            word_count=len((result.content_text or '').split()),
            content_hash=content_hash,
            scrape_metadata=metadata,
            content_json=candidate_data.__dict__ if candidate_data else None,
        )

        record.full_clean()
        record.save()
        logger.info(f"Saved MyNeta candidate: {record.id} - {url}")

        return record

    def crawl_election(self, max_constituencies: Optional[int] = None) -> List[RawScrapedData]:
        """
        Full pipeline: Crawl election, extract candidates, save to database.

        Args:
            max_constituencies: Limit constituencies to crawl (for testing)

        Returns:
            List of saved RawScrapedData records
        """
        logger.info(f"Starting MyNeta crawl for {self.state} {self.election_year}")

        # Step 1: Get constituency links
        constituency_links = self.get_constituency_links()

        if max_constituencies:
            constituency_links = constituency_links[:max_constituencies]

        all_candidates = []
        processed_count = 0

        # Step 2: For each constituency, get candidate links
        for const_url in constituency_links:
            candidate_links = self.get_candidate_links(const_url)

            # Step 3: Scrape each candidate
            for candidate_url in candidate_links:
                try:
                    record = self.scrape(candidate_url)
                    if record:
                        all_candidates.append(record)
                        processed_count += 1
                except Exception as e:
                    logger.error(f"Error processing {candidate_url}: {e}")

                # Rate limiting
                time.sleep(self.base_delay)

        logger.info(f"Crawl complete. Processed {processed_count} candidates")
        return all_candidates

    def scrape_specific_candidates(
        self,
        candidate_urls: List[str]
    ) -> List[RawScrapedData]:
        """
        Scrape specific candidate URLs without crawling.

        Args:
            candidate_urls: List of candidate profile URLs

        Returns:
            List of saved RawScrapedData records
        """
        return self.scrape_batch(candidate_urls)
