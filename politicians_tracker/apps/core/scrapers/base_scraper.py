"""
Base Scraper Framework
======================
Common utilities and base class for all scrapers.
Implements polite scraping practices: user-agent rotation, delays, and retry logic.
"""

import random
import time
import hashlib
import logging
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urlparse, urljoin
from contextlib import contextmanager

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from django.utils import timezone

from ..models import RawScrapedData

logger = logging.getLogger(__name__)


# =============================================================================
# User-Agent Pool for Rotation
# =============================================================================

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.2151.72",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.43 Mobile Safari/537.36",
]


# =============================================================================
# Utility Functions
# =============================================================================

def rotate_user_agent() -> str:
    """Return a random user-agent from the pool."""
    return random.choice(USER_AGENTS)


def polite_request(
    url: str,
    timeout: int = 30,
    max_retries: int = 3,
    base_delay: float = 2.0,
    headers: Optional[Dict[str, str]] = None,
) -> Tuple[Optional[requests.Response], Optional[str]]:
    """
    Make a polite HTTP request with retry logic and delay.

    Args:
        url: Target URL
        timeout: Request timeout in seconds
        max_retries: Maximum retry attempts
        base_delay: Base delay between retries (seconds)
        headers: Optional custom headers

    Returns:
        Tuple of (Response object or None, Error message or None)
    """
    # Default headers with rotation
    default_headers = {
        "User-Agent": rotate_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    if headers:
        default_headers.update(headers)

    # Setup session with retry strategy
    session = requests.Session()
    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    for attempt in range(max_retries):
        try:
            # Polite delay before request
            time.sleep(random.uniform(base_delay, base_delay * 1.5))

            response = session.get(
                url,
                headers=default_headers,
                timeout=timeout,
                allow_redirects=True,
            )

            # Check for rate limiting
            if response.status_code == 429:
                logger.warning(f"Rate limited on attempt {attempt + 1}: {url}")
                time.sleep(base_delay * (attempt + 1) * 2)
                continue

            # Success
            if response.status_code == 200:
                logger.info(f"Successfully fetched: {url}")
                return response, None

            # Server errors - retry
            if 500 <= response.status_code < 600:
                logger.warning(
                    f"Server error {response.status_code} on attempt {attempt + 1}: {url}"
                )
                time.sleep(base_delay * (attempt + 1))
                continue

            # Client errors - don't retry (4xx)
            logger.error(f"Client error {response.status_code}: {url}")
            return None, f"HTTP {response.status_code}"

        except requests.exceptions.Timeout:
            logger.warning(f"Timeout on attempt {attempt + 1}: {url}")
            time.sleep(base_delay * (attempt + 1))

        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Connection error on attempt {attempt + 1}: {url} - {e}")
            time.sleep(base_delay * (attempt + 1))

        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception: {url} - {e}")
            return None, str(e)

    # All retries exhausted
    logger.error(f"Max retries exceeded for: {url}")
    return None, "Max retries exceeded"


def sanitize_html(raw_html: str) -> str:
    """
    Remove scripts, styles, and navigation from HTML.

    Args:
        raw_html: Raw HTML string

    Returns:
        Sanitized HTML suitable for text extraction
    """
    soup = BeautifulSoup(raw_html, 'html.parser')

    # Remove unwanted elements
    for tag in soup(["script", "style", "nav", "header", "footer", "aside",
                     "iframe", "noscript", "form", "advertisement"]):
        tag.decompose()

    # Remove comments
    for comment in soup.find_all(string=lambda text: isinstance(text, type(soup.string.__class__)) and text.startswith('<!--')):
        comment.extract()

    return str(soup)


def extract_text_from_html(html_content: str) -> str:
    """
    Extract clean text from HTML content.

    Args:
        html_content: HTML string

    Returns:
        Cleaned text content
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Get text and clean up
    text = soup.get_text(separator='\n')
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text.strip()


def calculate_content_hash(content: str) -> str:
    """Calculate SHA-256 hash of content for deduplication."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def get_domain_from_url(url: str) -> str:
    """Extract domain from URL."""
    parsed = urlparse(url)
    return parsed.netloc.lower()


def is_url_already_scraped(source_url: str, content_hash: Optional[str] = None) -> bool:
    """
    Check if URL has already been scraped.

    Args:
        source_url: Source URL to check
        content_hash: Optional content hash for duplicate detection

    Returns:
        True if already exists
    """
    query = RawScrapedData.objects.filter(source_url=source_url)
    if content_hash:
        query = query.filter(content_hash=content_hash)
    return query.exists()


def detect_language(text: str) -> str:
    """
    Simple language detection based on character sets.

    Args:
        text: Text to analyze

    Returns:
        'en', 'kn', 'mixed', or 'unknown'
    """
    if not text:
        return 'unknown'

    kannada_chars = sum(1 for c in text if '\u0C80' <= c <= '\u0CFF')
    english_chars = sum(1 for c in text if c.isalpha() and c.isascii())

    total_chars = kannada_chars + english_chars
    if total_chars == 0:
        return 'unknown'

    kannada_ratio = kannada_chars / total_chars
    english_ratio = english_chars / total_chars

    if kannada_ratio > 0.3 and english_ratio > 0.3:
        return 'mixed'
    elif kannada_ratio > 0.3:
        return 'kn'
    else:
        return 'en'


@dataclass
class ScrapeResult:
    """Data class for scrape operation results."""
    success: bool
    content_html: Optional[str] = None
    content_text: Optional[str] = None
    error_message: Optional[str] = None
    status_code: Optional[int] = None
    redirected_url: Optional[str] = None


# =============================================================================
# Base Scraper Class
# =============================================================================

class BaseScraper:
    """
    Abstract base class for all scrapers.
    Provides common functionality and interface.
    """

    SOURCE_TYPE = 'other'
    SOURCE_DOMAIN = ''
    SCRAPER_NAME = 'base_scraper'

    def __init__(
        self,
        base_delay: float = 3.0,
        timeout: int = 30,
        max_retries: int = 3,
        save_to_db: bool = True,
    ):
        """
        Initialize scraper with configuration.

        Args:
            base_delay: Minimum delay between requests (seconds)
            timeout: Request timeout (seconds)
            max_retries: Maximum retry attempts
            save_to_db: Whether to save results to RawScrapedData
        """
        self.base_delay = base_delay
        self.timeout = timeout
        self.max_retries = max_retries
        self.save_to_db = save_to_db
        self.session = requests.Session()

    def scrape(self, url: str, **kwargs) -> Optional[RawScrapedData]:
        """
        Scrape a URL and optionally save to database.

        Args:
            url: URL to scrape
            **kwargs: Additional metadata

        Returns:
            RawScrapedData instance or None
        """
        # Check for existing record first
        response, error = polite_request(
            url,
            timeout=self.timeout,
            max_retries=self.max_retries,
            base_delay=self.base_delay,
        )

        if error or not response:
            logger.error(f"Failed to scrape {url}: {error}")
            if self.save_to_db:
                return self._save_failed(url, error, **kwargs)
            return None

        # Deduplication check
        content_hash = calculate_content_hash(response.text)
        if is_url_already_scraped(url, content_hash):
            logger.info(f"Duplicate detected, skipping: {url}")
            return None

        # Process content
        result = self._process_response(response, url, **kwargs)

        if result and self.save_to_db:
            return self._save_to_database(url, response, result, content_hash, **kwargs)

        return result

    def _process_response(
        self,
        response: requests.Response,
        url: str,
        **kwargs
    ) -> Optional[ScrapeResult]:
        """
        Process HTTP response. Override in subclasses.

        Args:
            response: HTTP response object
            url: Original URL
            **kwargs: Additional metadata

        Returns:
            ScrapeResult instance
        """
        return ScrapeResult(
            success=True,
            content_html=response.text,
            content_text=extract_text_from_html(response.text),
        )

    def _save_to_database(
        self,
        url: str,
        response: requests.Response,
        result: ScrapeResult,
        content_hash: str,
        **kwargs
    ) -> RawScrapedData:
        """
        Save scrape result to RawScrapedData table.

        Args:
            url: Source URL
            response: HTTP response
            result: Processed result
            content_hash: Content hash for deduplication
            **kwargs: Additional metadata

        Returns:
            RawScrapedData instance
        """
        source_domain = get_domain_from_url(url)

        # Detect language
        text_content = result.content_text or ''
        language = detect_language(text_content)

        # Create record
        record = RawScrapedData(
            content_raw_html=result.content_html or response.text[:100000],
            content_raw_text=text_content[:50000],
            source_type=self.SOURCE_TYPE,
            source_url=url,
            source_domain=source_domain,
            source_organization=self.SOURCE_DOMAIN,
            scraper_name=self.SCRAPER_NAME,
            processing_status='pending',
            language_detected=language,
            word_count=len(text_content.split()),
            content_hash=content_hash,
            published_date=kwargs.get('published_date'),
        )

        record.full_clean()
        record.save()

        logger.info(f"Saved to RawScrapedData: {record.id} - {url}")
        return record

    def _save_failed(
        self,
        url: str,
        error: str,
        **kwargs
    ) -> RawScrapedData:
        """
        Save failed scrape attempt to database.

        Args:
            url: Source URL
            error: Error message
            **kwargs: Additional metadata

        Returns:
            RawScrapedData instance
        """
        record = RawScrapedData(
            source_type=self.SOURCE_TYPE,
            source_url=url,
            source_domain=get_domain_from_url(url),
            source_organization=self.SOURCE_DOMAIN,
            scraper_name=self.SCRAPER_NAME,
            processing_status='failed',
            processing_error=error,
            content_hash='',
            language_detected='unknown',
        )

        record.full_clean()
        record.save()

        return record

    def scrape_batch(
        self,
        urls: list[str],
        delay_between_urls: Optional[float] = None,
        **kwargs
    ) -> list[RawScrapedData]:
        """
        Scrape multiple URLs sequentially.

        Args:
            urls: List of URLs to scrape
            delay_between_urls: Additional delay between URLs (uses base_delay if None)
            **kwargs: Additional metadata for all URLs

        Returns:
            List of RawScrapedData instances
        """
        results = []
        delay = delay_between_urls or self.base_delay

        for i, url in enumerate(urls):
            logger.info(f"Scraping {i + 1}/{len(urls)}: {url}")
            try:
                result = self.scrape(url, **kwargs)
                if result:
                    results.append(result)
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                if self.save_to_db:
                    results.append(self._save_failed(url, str(e), **kwargs))

            # Delay between URLs
            if i < len(urls) - 1:
                time.sleep(delay)

        return results


# =============================================================================
# Scraper Runner
# =============================================================================

def run_scraper(
    scraper_class,
    urls: list[str],
    scraper_kwargs: Optional[Dict[str, Any]] = None,
    **kwargs
) -> list[RawScrapedData]:
    """
    Run a scraper with proper initialization.

    Args:
        scraper_class: Scraper class to instantiate
        urls: List of URLs to scrape
        scraper_kwargs: Optional scraper configuration
        **kwargs: Additional metadata for scrape

    Returns:
        List of RawScrapedData instances
    """
    scraper = scraper_class(**(scraper_kwargs or {}))
    return scraper.scrape_batch(urls, **kwargs)