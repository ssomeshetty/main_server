"""
Karnataka Assembly Directory Scraper
====================================
Crawls official Karnataka Legislative Assembly website (kla.kar.nic.in)
for current MLA profiles, terms served, and contact details.
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
class AssemblyMemberData:
    """Structured data from assembly member profile."""
    name_en: str
    name_kn: Optional[str]
    constituency_name: str
    constituency_number: Optional[int]
    district: str
    party: str
    terms_served: List[Dict[str, Any]]
    contact_details: Dict[str, str]
    committees: List[str]
    committees_history: List[str]
    profile_image_url: Optional[str]
    education: Optional[str]
    profession: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    date_of_birth: Optional[str]
    place_of_birth: Optional[str]
    marital_status: Optional[str]
    source_url: str
    raw_html: str


class KarnatakaAssemblyScraper(BaseScraper):
    """
    Scraper for Karnataka Legislative Assembly website.
    Extracts current and historical MLA information.
    """

    SOURCE_TYPE = 'assembly_directory'
    SOURCE_DOMAIN = 'kla.kar.nic.in'
    SCRAPER_NAME = 'karnataka_assembly_scraper'

    def __init__(
        self,
        base_url: str = "https://kla.kar.nic.in",
        **kwargs
    ):
        """
        Initialize Karnataka Assembly scraper.

        Args:
            base_url: Base URL for assembly website
        """
        super().__init__(**kwargs)
        self.base_url = base_url
        self.members_url = f"{base_url}/english/legislativeassembly.aspx"
        self.current_mla_url = f"{base_url}/english/currentmember.aspx"

    def get_current_mla_links(self) -> List[str]:
        """
        Fetch current MLA list page and extract profile links.

        Returns:
            List of MLA profile URLs
        """
        logger.info(f"Fetching current MLA list: {self.current_mla_url}")

        response, error = polite_request(
            self.current_mla_url,
            timeout=self.timeout,
            max_retries=self.max_retries,
            base_delay=self.base_delay,
        )

        if error or not response:
            logger.error(f"Failed to fetch MLA list: {error}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        mla_links = []

        # Find MLA profile links
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True)

            # Match member profile patterns
            if 'memberprofile' in href.lower() or 'member' in href.lower():
                if 'javascript' not in href.lower():
                    full_url = urljoin(self.base_url, href)
                    if full_url not in mla_links:
                        mla_links.append(full_url)

        # Alternative: Parse table of MLAs
        table = soup.find('table', class_=re.compile('member|table', re.I))
        if table:
            for row in table.find_all('tr'):
                link = row.find('a', href=True)
                if link:
                    href = link['href']
                    if 'member' in href.lower():
                        full_url = urljoin(self.base_url, href)
                        if full_url not in mla_links:
                            mla_links.append(full_url)

        logger.info(f"Found {len(mla_links)} current MLA links")
        return mla_links

    def get_all_member_links(self) -> List[str]:
        """
        Fetch all historical and current members.

        Returns:
            List of all member profile URLs
        """
        logger.info(f"Fetching all members: {self.members_url}")

        response, error = polite_request(
            self.members_url,
            timeout=self.timeout,
            max_retries=self.max_retries,
            base_delay=self.base_delay,
        )

        if error or not response:
            logger.error(f"Failed to fetch members list: {error}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        member_links = []

        # Parse dropdown/select options
        select = soup.find('select', id=re.compile('member|ddl', re.I))
        if select:
            for option in select.find_all('option'):
                value = option.get('value')
                if value and 'memberprofile' in value.lower():
                    full_url = urljoin(self.base_url, value)
                    member_links.append(full_url)

        # Alternative: Parse table
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'memberprofile' in href.lower() or 'mlaprofile' in href.lower():
                full_url = urljoin(self.base_url, href)
                if full_url not in member_links:
                    member_links.append(full_url)

        logger.info(f"Found {len(member_links)} member links")
        return member_links

    def parse_member_profile(self, url: str) -> Optional[AssemblyMemberData]:
        """
        Parse a member profile page and extract all relevant data.

        Args:
            url: Member profile URL

        Returns:
            AssemblyMemberData instance or None
        """
        logger.info(f"Parsing member: {url}")

        response, error = polite_request(
            url,
            timeout=self.timeout,
            max_retries=self.max_retries,
            base_delay=self.base_delay,
        )

        if error or not response:
            logger.error(f"Failed to fetch member: {error}")
            return None

        # Check for duplicates
        content_hash = calculate_content_hash(response.text)
        if is_url_already_scraped(url, content_hash):
            logger.info(f"Duplicate detected, skipping: {url}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract data
        data = AssemblyMemberData(
            name_en=self._extract_name(soup),
            name_kn=self._extract_name_kn(soup),
            constituency_name=self._extract_constituency(soup),
            constituency_number=self._extract_constituency_number(soup),
            district=self._extract_district(soup),
            party=self._extract_party(soup),
            terms_served=self._extract_terms_served(soup),
            contact_details=self._extract_contact_details(soup),
            committees=self._extract_committees(soup),
            committees_history=self._extract_committees_history(soup),
            profile_image_url=self._extract_image_url(soup),
            education=self._extract_education(soup),
            profession=self._extract_profession(soup),
            email=self._extract_email(soup),
            phone=self._extract_phone(soup),
            address=self._extract_address(soup),
            date_of_birth=self._extract_dob(soup),
            place_of_birth=self._extract_place_of_birth(soup),
            marital_status=self._extract_marital_status(soup),
            source_url=url,
            raw_html=response.text[:100000],
        )

        return data

    def _extract_name(self, soup: BeautifulSoup) -> str:
        """Extract member name (English)."""
        # Look for name in common patterns
        for pattern in [
            ('h1', {'class': re.compile('name|title', re.I)}),
            ('h2', {'class': re.compile('name', re.I)}),
            ('span', {'id': re.compile('name', re.I)}),
        ]:
            elem = soup.find(pattern[0], pattern[1])
            if elem:
                return elem.get_text(strip=True)

        # Fallback: look for table cells with "Name"
        name_elem = soup.find(string=re.compile(r'\bName\b'))
        if name_elem:
            parent = name_elem.find_parent(['td', 'th'])
            if parent:
                next_elem = parent.find_next_sibling()
                if next_elem:
                    return next_elem.get_text(strip=True)

        # Look for first major heading
        for tag in ['h1', 'h2', 'h3']:
            elem = soup.find(tag)
            if elem:
                text = elem.get_text(strip=True)
                if text and len(text) > 3 and len(text) < 200:
                    return text

        return ''

    def _extract_name_kn(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract member name in Kannada."""
        # Kannada text is typically in a separate element
        kn_elem = soup.find(string=re.compile('[\u0C80-\u0CFF]'))
        if kn_elem:
            # Check if it's a name
            parent = kn_elem.find_parent()
            if parent:
                text = parent.get_text(strip=True)
                if len(text) > 3 and len(text) < 200:
                    return text
        return None

    def _extract_constituency(self, soup: BeautifulSoup) -> str:
        """Extract constituency name."""
        for label in ['Constituency', 'Assembly Constituency', 'Constituency No']:
            elem = soup.find(string=re.compile(f'^{label}'))
            if elem:
                parent = elem.find_parent(['td', 'th', 'tr', 'div'])
                if parent:
                    next_elem = parent.find_next_sibling()
                    if next_elem:
                        return next_elem.get_text(strip=True)
        return ''

    def _extract_constituency_number(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract constituency number."""
        for label in ['Constituency No', 'Constituency Number']:
            elem = soup.find(string=re.compile(f'^{label}'))
            if elem:
                parent = elem.find_parent(['td', 'th', 'tr', 'div'])
                if parent:
                    next_elem = parent.find_next_sibling()
                    if next_elem:
                        text = next_elem.get_text(strip=True)
                        match = re.search(r'(\d+)', text)
                        if match:
                            return int(match.group(1))
        return None

    def _extract_district(self, soup: BeautifulSoup) -> str:
        """Extract district name."""
        dist_elem = soup.find(string=re.compile('District', re.I))
        if dist_elem:
            parent = dist_elem.find_parent(['td', 'th', 'tr', 'div'])
            if parent:
                next_elem = parent.find_next_sibling()
                if next_elem:
                    return next_elem.get_text(strip=True)
        return ''

    def _extract_party(self, soup: BeautifulSoup) -> str:
        """Extract party name."""
        party_elem = soup.find(string=re.compile('Party|B Political', re.I))
        if party_elem:
            parent = party_elem.find_parent(['td', 'th', 'tr', 'div'])
            if parent:
                next_elem = parent.find_next_sibling()
                if next_elem:
                    return next_elem.get_text(strip=True)
        return ''

    def _extract_terms_served(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract terms served in assembly."""
        terms = []

        # Find terms/elections table
        for table in soup.find_all('table'):
            header = table.find('tr')
            if header:
                header_text = header.get_text().lower()
                if 'term' in header_text or 'election' in header_text or 'year' in header_text:
                    for row in table.find_all('tr')[1:]:  # Skip header
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 3:
                            term = {
                                'from_year': cells[0].get_text(strip=True),
                                'to_year': cells[1].get_text(strip=True),
                                'constituency': cells[2].get_text(strip=True),
                            }
                            terms.append(term)
                    break

        return terms

    def _extract_contact_details(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract contact information."""
        contact = {}

        # Email
        email_elem = soup.find(string=re.compile(r'[\w.-]+@[\w.-]+\.\w+'))
        if email_elem:
            contact['email'] = email_elem.strip()

        # Phone
        phone_elem = soup.find(string=re.compile(r'\d{3,4}[-\s]?\d{6,8}'))
        if phone_elem:
            contact['phone'] = phone_elem.strip()

        return contact

    def _extract_committees(self, soup: BeautifulSoup) -> List[str]:
        """Extract current committee memberships."""
        committees = []

        # Find committee section
        for heading in soup.find_all(['h2', 'h3', 'h4']):
            if 'committee' in heading.get_text().lower():
                parent = heading.find_parent()
                if parent:
                    for item in parent.find_all(['li', 'tr', 'p']):
                        text = item.get_text(strip=True)
                        if text and len(text) > 3:
                            committees.append(text)
                break

        return committees

    def _extract_committees_history(self, soup: BeautifulSoup) -> List[str]:
        """Extract committee history."""
        committees = []

        # Find past committees
        for heading in soup.find_all(['h2', 'h3', 'h4']):
            if 'past' in heading.get_text().lower() and 'committee' in heading.get_text().lower():
                parent = heading.find_parent()
                if parent:
                    for item in parent.find_all(['li', 'tr', 'p']):
                        text = item.get_text(strip=True)
                        if text and len(text) > 3:
                            committees.append(text)
                break

        return committees

    def _extract_image_url(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract profile image URL."""
        img = soup.find('img', class_=re.compile('photo|image|profile', re.I))
        if img and img.get('src'):
            src = img['src']
            if src.startswith('/'):
                return urljoin(self.base_url, src)
            return src
        return None

    def _extract_education(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract education qualification."""
        edu_elem = soup.find(string=re.compile('Education|Qualification', re.I))
        if edu_elem:
            parent = edu_elem.find_parent(['td', 'th', 'tr', 'div'])
            if parent:
                next_elem = parent.find_next_sibling()
                if next_elem:
                    return next_elem.get_text(strip=True)
        return None

    def _extract_profession(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract profession/occupation."""
        prof_elem = soup.find(string=re.compile('Profession|Occupation', re.I))
        if prof_elem:
            parent = prof_elem.find_parent(['td', 'th', 'tr', 'div'])
            if parent:
                next_elem = parent.find_next_sibling()
                if next_elem:
                    return next_elem.get_text(strip=True)
        return None

    def _extract_email(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract email address."""
        email_elem = soup.find('a', href=re.compile('mailto:', re.I))
        if email_elem:
            href = email_elem.get('href', '')
            return href.replace('mailto:', '').strip()
        return None

    def _extract_phone(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract phone number."""
        phone_elem = soup.find(string=re.compile(r'Phone|Telephone|Mobile', re.I))
        if phone_elem:
            parent = phone_elem.find_parent(['td', 'th', 'tr', 'div'])
            if parent:
                next_elem = parent.find_next_sibling()
                if next_elem:
                    return next_elem.get_text(strip=True)
        return None

    def _extract_address(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract address."""
        addr_elem = soup.find(string=re.compile('Address|Residence', re.I))
        if addr_elem:
            parent = addr_elem.find_parent(['td', 'th', 'tr', 'div'])
            if parent:
                next_elem = parent.find_next_sibling()
                if next_elem:
                    return next_elem.get_text(strip=True)
        return None

    def _extract_dob(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract date of birth."""
        dob_elem = soup.find(string=re.compile('Date of Birth|DOB|Birth', re.I))
        if dob_elem:
            parent = dob_elem.find_parent(['td', 'th', 'tr', 'div'])
            if parent:
                next_elem = parent.find_next_sibling()
                if next_elem:
                    return next_elem.get_text(strip=True)
        return None

    def _extract_place_of_birth(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract place of birth."""
        pob_elem = soup.find(string=re.compile('Place of Birth|Birth Place', re.I))
        if pob_elem:
            parent = pob_elem.find_parent(['td', 'th', 'tr', 'div'])
            if parent:
                next_elem = parent.find_next_sibling()
                if next_elem:
                    return next_elem.get_text(strip=True)
        return None

    def _extract_marital_status(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract marital status."""
        mar_elem = soup.find(string=re.compile('Marital Status|Married', re.I))
        if mar_elem:
            parent = mar_elem.find_parent(['td', 'th', 'tr', 'div'])
            if parent:
                next_elem = parent.find_next_sibling()
                if next_elem:
                    return next_elem.get_text(strip=True)
        return None

    def _process_response(
        self,
        response: requests.Response,
        url: str,
        **kwargs
    ) -> Optional[ScrapeResult]:
        """Process member profile response."""
        content_html = response.text
        content_text = extract_text_from_html(sanitize_html(content_html))

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
        """Save assembly member data to RawScrapedData."""
        # Parse member data
        soup = BeautifulSoup(response.text, 'html.parser')
        member_data = self.parse_member_profile(url)

        source_domain = get_domain_from_url(url)
        language = detect_language(result.content_text or '')

        # Create JSON metadata
        metadata = {
            'scraper': self.SCRAPER_NAME,
            'source': 'karnataka_assembly',
            'member_data': {
                'name_en': member_data.name_en if member_data else '',
                'name_kn': member_data.name_kn,
                'constituency': member_data.constituency_name if member_data else '',
                'constituency_number': member_data.constituency_number,
                'district': member_data.district if member_data else '',
                'party': member_data.party if member_data else '',
                'terms_served': member_data.terms_served if member_data else [],
                'committees': member_data.committees if member_data else [],
                'committees_history': member_data.committees_history if member_data else [],
                'email': member_data.email,
                'phone': member_data.phone,
                'education': member_data.education,
                'profession': member_data.profession,
                'date_of_birth': member_data.date_of_birth,
                'marital_status': member_data.marital_status,
            } if member_data else {},
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
            content_json=member_data.__dict__ if member_data else None,
        )

        record.full_clean()
        record.save()
        logger.info(f"Saved Assembly member: {record.id} - {url}")

        return record

    def crawl_current_mlas(self) -> List[RawScrapedData]:
        """
        Full pipeline: Crawl current MLA profiles and save to database.

        Returns:
            List of saved RawScrapedData records
        """
        logger.info("Starting Karnataka Assembly current MLA crawl")

        # Get MLA links
        mla_links = self.get_current_mla_links()

        all_records = []
        for url in mla_links:
            try:
                record = self.scrape(url)
                if record:
                    all_records.append(record)
                time.sleep(self.base_delay)
            except Exception as e:
                logger.error(f"Error processing {url}: {e}")

        logger.info(f"Crawl complete. Processed {len(all_records)} MLAs")
        return all_records

    def crawl_all_members(self) -> List[RawScrapedData]:
        """
        Full pipeline: Crawl all historical and current members.

        Returns:
            List of saved RawScrapedData records
        """
        logger.info("Starting Karnataka Assembly full member crawl")

        # Get all member links
        member_links = self.get_all_member_links()

        all_records = []
        for url in member_links:
            try:
                record = self.scrape(url)
                if record:
                    all_records.append(record)
                time.sleep(self.base_delay)
            except Exception as e:
                logger.error(f"Error processing {url}: {e}")

        logger.info(f"Crawl complete. Processed {len(all_records)} members")
        return all_records

    def scrape_specific_members(
        self,
        member_urls: List[str]
    ) -> List[RawScrapedData]:
        """
        Scrape specific member URLs without crawling.

        Args:
            member_urls: List of member profile URLs

        Returns:
            List of saved RawScrapedData records
        """
        return self.scrape_batch(member_urls)