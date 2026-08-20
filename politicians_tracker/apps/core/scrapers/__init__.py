"""
Data Collection Scrapers Package
================================
Modular scraping framework for Karnataka Politicians data collection.
"""

from .myneta_scraper import MyNetaScraper
from .karnataka_assembly_scraper import KarnatakaAssemblyScraper
from .generic_fetcher import GenericDocumentFetcher
from .base_scraper import BaseScraper, polite_request, rotate_user_agent
from .llm_purification_worker import (
    PurificationWorker,
    run_worker,
    process_single_record,
    reprocess_failed_records,
    get_llm_provider,
    SYSTEM_PROMPT,
)

__all__ = [
    'MyNetaScraper',
    'KarnatakaAssemblyScraper',
    'GenericDocumentFetcher',
    'BaseScraper',
    'polite_request',
    'rotate_user_agent',
    'PurificationWorker',
    'run_worker',
    'process_single_record',
    'reprocess_failed_records',
    'get_llm_provider',
    'SYSTEM_PROMPT',
]