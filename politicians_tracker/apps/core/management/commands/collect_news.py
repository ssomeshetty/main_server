import logging
import time

from django.core.management.base import BaseCommand
from django.db.models import Count

from politicians_tracker.apps.core.models import Politician
from politicians_tracker.apps.core.scrapers.news_collector import NewsCollector

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Collect news articles for politicians using Google News RSS'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=10, help='Max articles per politician')
        parser.add_argument('--politician-id', type=int, help='Process specific politician ID')
        parser.add_argument('--all', action='store_true', help='Process all politicians (takes a long time)')

    def handle(self, *args, **options):
        max_articles = options['limit']
        process_all = options['all']
        p_id = options['politician_id']
        
        collector = NewsCollector(max_articles=max_articles)
        
        if p_id:
            politicians = Politician.objects.filter(id=p_id)
        elif process_all:
            politicians = Politician.objects.filter(is_active=True)
        else:
            # Prioritize politicians who have fewer or zero news articles scraped
            from django.db.models import Count, Q
            politicians = Politician.objects.filter(is_active=True).annotate(
                news_count=Count(
                    'raw_scraped_data',
                    filter=Q(raw_scraped_data__scraper_name='generic_fetcher')
                )
            ).order_by('news_count')[:20]
            
        self.stdout.write(f'Starting news collection for {politicians.count()} politicians (Max {max_articles} articles each)...')
        
        collected = 0
        for i, p in enumerate(politicians, 1):
            try:
                self.stdout.write(f'[{i}/{politicians.count()}] Collecting news for {p.full_name_en}...')
                records = collector.collect_news_for_politician(p.full_name_en)
                collected += len(records)
                self.stdout.write(self.style.SUCCESS(f'  Saved {len(records)} new articles for {p.full_name_en}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  Error collecting for {p.full_name_en}: {e}'))
            time.sleep(2) # polite delay between politicians
            
        self.stdout.write(self.style.SUCCESS(f'\\nNews collection complete! Total new articles: {collected}'))
