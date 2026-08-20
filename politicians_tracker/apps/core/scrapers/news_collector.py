import logging
import re
import urllib.parse
from typing import List
import xml.etree.ElementTree as ET

from .base_scraper import polite_request
from .generic_fetcher import GenericDocumentFetcher
from ..models import RawScrapedData

logger = logging.getLogger(__name__)

class NewsCollector:
    """
    Collects news articles for politicians using Google News RSS 
    and the GenericDocumentFetcher.
    """
    
    def __init__(self, max_articles: int = 10, **kwargs):
        self.max_articles = max_articles
        self.fetcher = GenericDocumentFetcher(default_source_type='news_article', **kwargs)
        
    def get_news_links_for_query(self, query: str) -> List[dict]:
        """Fetch news links from Google News RSS."""
        encoded_query = urllib.parse.quote(query)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"
        
        logger.info(f"Fetching RSS: {rss_url}")
        response, error = polite_request(rss_url)
        
        if error or not response:
            logger.error(f"Failed to fetch RSS: {error}")
            return []
            
        try:
            root = ET.fromstring(response.text)
            items = []
            
            for item in root.findall('.//item')[:self.max_articles]:
                link = item.find('link').text
                title = item.find('title').text
                pub_date = item.find('pubDate').text
                source = item.find('source').text if item.find('source') is not None else 'Unknown'
                
                # Google News links sometimes need to be resolved, but we'll try fetching them directly
                items.append({
                    'url': link,
                    'title': title,
                    'pub_date': pub_date,
                    'source': source
                })
                
            return items
        except Exception as e:
            logger.error(f"Failed to parse RSS XML: {e}")
            return []
            
    def resolve_google_news_url(self, google_rss_url: str) -> str:
        """Resolve Google News redirect URL to the final article URL using the batchexecute API."""
        import requests
        import json
        from bs4 import BeautifulSoup
        try:
            response_obj, error = polite_request(google_rss_url)
            if error or not response_obj or not response_obj.text:
                return google_rss_url
            soup = BeautifulSoup(response_obj.text, 'html.parser')
            element = soup.select_one('c-wiz[data-p]')
            if not element:
                return google_rss_url
            data = element.get('data-p')
            obj = json.loads(data.replace('%.@.', '["garturlreq",'))
            payload = {
                'f.req': json.dumps([[
                    ['Fbv4je', json.dumps(obj[:-6] + obj[-2:]), 'null', 'generic']
                ]])
            }
            url = 'https://news.google.com/_/DotsSplashUi/data/batchexecute'
            headers = {'content-type': 'application/x-www-form-urlencoded;charset=UTF-8'}
            response = requests.post(url, headers=headers, data=payload, timeout=10)
            text_cleaned = response.text.replace(")]}'\n", "")
            array_string = json.loads(text_cleaned)[0][2]
            article_url = json.loads(array_string)[1]
            return article_url
        except Exception as e:
            logger.warning(f"Failed to resolve Google News URL {google_rss_url}: {e}")
            return google_rss_url

    def collect_news_for_politician(self, politician_name: str, state: str = "Karnataka") -> List[RawScrapedData]:
        """Collect news articles for a specific politician."""
        # Query without strict quotes to maximize relevant articles (Entity Resolution filters out false positives later)
        query = f'{politician_name} {state}'
        
        news_items = self.get_news_links_for_query(query)
        logger.info(f"Found {len(news_items)} news articles for {politician_name}")
        
        results = []
        for item in news_items:
            resolved_url = self.resolve_google_news_url(item['url'])
            logger.info(f"Resolved {item['url']} -> {resolved_url}")
            # Check if we already have it
            if self.fetcher.scrape(resolved_url):
                # The fetcher saves to RawScrapedData and returns it
                # We can also attach the politician name to metadata
                record = RawScrapedData.objects.filter(source_url=resolved_url).first()
                if record:
                    metadata = record.scrape_metadata or {}
                    metadata['related_politician'] = politician_name
                    metadata['rss_title'] = item['title']
                    metadata['rss_pubDate'] = item['pub_date']
                    metadata['google_news_original_url'] = item['url']
                    record.scrape_metadata = metadata
                    # Make sure source organization is set from RSS if possible
                    if item['source'] != 'Unknown':
                        record.source_organization = item['source']
                    record.save()
                    results.append(record)
                    
        return results
