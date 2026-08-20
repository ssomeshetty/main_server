#!/usr/bin/env python
"""
Scraper Runner Script
=====================
Demonstrates usage of the scraping framework.

Usage:
    python run_scrapers.py --scraper myneta --election-year 2023
    python run_scrapers.py --scraper assembly --type current
    python run_scrapers.py --fetcher --url "https://example.com/article"
    python run_scrapers.py --fetcher-batch --urls-file urls.txt
"""

import argparse
import logging
import sys
import os

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'politicians_tracker.settings')
import django
django.setup()

from politicians_tracker.apps.core.scrapers.myneta_scraper import MyNetaScraper
from politicians_tracker.apps.core.scrapers.karnataka_assembly_scraper import KarnatakaAssemblyScraper
from politicians_tracker.apps.core.scrapers.generic_fetcher import GenericDocumentFetcher
from politicians_tracker.apps.core.scrapers.base_scraper import run_scraper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_myneta_scraper(election_year: str, max_constituencies: int = None):
    """Run MyNeta scraper for Karnataka election."""
    logger.info(f"Starting MyNeta scraper for {election_year}")

    scraper = MyNetaScraper(
        election_year=election_year,
        state='Karnataka',
        base_delay=3.0,
        timeout=30,
        max_retries=3,
        save_to_db=True,
    )

    records = scraper.crawl_election(max_constituencies=max_constituencies)
    logger.info(f"Scraped {len(records)} candidate records")
    return records


def run_assembly_scraper(mla_type: str):
    """Run Karnataka Assembly scraper."""
    logger.info(f"Starting Karnataka Assembly scraper for {mla_type}")

    scraper = KarnatakaAssemblyScraper(
        base_url="https://kla.kar.nic.in",
        base_delay=3.0,
        timeout=30,
        max_retries=3,
        save_to_db=True,
    )

    if mla_type == 'current':
        records = scraper.crawl_current_mlas()
    else:
        records = scraper.crawl_all_members()

    logger.info(f"Scraped {len(records)} member records")
    return records


def run_generic_fetcher(url: str, source_type: str = None, organization: str = None):
    """Fetch a single URL."""
    logger.info(f"Fetching URL: {url}")

    fetcher = GenericDocumentFetcher(
        base_delay=2.0,
        timeout=30,
        max_retries=3,
        save_to_db=True,
    )

    record = fetcher.fetch_url(
        url,
        source_type=source_type,
        source_organization=organization,
    )

    if record:
        logger.info(f"Fetched and saved: {record.id}")
    return record


def run_batch_fetcher(urls_file: str, source_type: str = None, organization: str = None):
    """Fetch multiple URLs from file."""
    with open(urls_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]

    logger.info(f"Fetching {len(urls)} URLs from {urls_file}")

    fetcher = GenericDocumentFetcher(
        base_delay=3.0,
        timeout=30,
        max_retries=3,
        save_to_db=True,
    )

    records = fetcher.fetch_batch(
        urls,
        source_type=source_type,
        source_organization=organization,
    )

    logger.info(f"Fetched {len(records)} documents")
    return records


def main():
    parser = argparse.ArgumentParser(
        description='Karnataka Politicians Data Scraper Runner'
    )

    # Scraper selection
    parser.add_argument(
        '--scraper',
        choices=['myneta', 'assembly'],
        help='Select specific scraper'
    )
    parser.add_argument(
        '--fetcher',
        action='store_true',
        help='Use generic document fetcher for single URL'
    )
    parser.add_argument(
        '--fetcher-batch',
        action='store_true',
        help='Use generic document fetcher for multiple URLs'
    )

    # MyNeta options
    parser.add_argument(
        '--election-year',
        default='2023',
        help='Election year for MyNeta scraper (default: 2023)'
    )
    parser.add_argument(
        '--max-constituencies',
        type=int,
        default=None,
        help='Limit constituencies to scrape (for testing)'
    )

    # Assembly options
    parser.add_argument(
        '--type',
        choices=['current', 'all'],
        default='current',
        help='Assembly member type (default: current)'
    )

    # Generic fetcher options
    parser.add_argument(
        '--url',
        help='URL to fetch (for --fetcher)'
    )
    parser.add_argument(
        '--urls-file',
        help='File containing URLs (for --fetcher-batch)'
    )
    parser.add_argument(
        '--source-type',
        help='Source type for URLs'
    )
    parser.add_argument(
        '--organization',
        help='Source organization name'
    )

    # Logging
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        if args.fetcher and args.url:
            run_generic_fetcher(
                args.url,
                source_type=args.source_type,
                organization=args.organization,
            )

        elif args.fetcher_batch and args.urls_file:
            run_batch_fetcher(
                args.urls_file,
                source_type=args.source_type,
                organization=args.organization,
            )

        elif args.scraper == 'myneta':
            run_myneta_scraper(
                args.election_year,
                max_constituencies=args.max_constituencies,
            )

        elif args.scraper == 'assembly':
            run_assembly_scraper(args.type)

        else:
            parser.print_help()
            sys.exit(1)

    except Exception as e:
        logger.error(f"Scraper failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()