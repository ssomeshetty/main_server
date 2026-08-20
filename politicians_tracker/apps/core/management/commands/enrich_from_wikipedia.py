import logging
import time
import requests
import difflib

from django.core.management.base import BaseCommand
from django.db import transaction

from politicians_tracker.apps.core.models import Politician

logger = logging.getLogger(__name__)

def get_clean_words(name):
    # Remove initials like 'B. K.', 'H. D.', 'S. T.'
    parts = name.split()
    clean_parts = [p for p in parts if len(p.replace('.', '')) > 1]
    return clean_parts

def get_search_queries(name):
    clean_parts = get_clean_words(name)
    queries = []
    
    # Query 1: Full name
    queries.append(name)
    
    # Query 2: Clean parts joined
    if len(clean_parts) > 0 and ' '.join(clean_parts) != name:
        queries.append(' '.join(clean_parts))
        
    # Query 3: Last two words of the clean parts
    if len(clean_parts) >= 2:
        queries.append(' '.join(clean_parts[-2:]))
        
    # Query 4: First and last word of the clean parts
    if len(clean_parts) >= 3:
        queries.append(f"{clean_parts[0]} {clean_parts[-1]}")
        
    return list(dict.fromkeys(queries)) # unique queries

def is_valid_person_title(title, name):
    title_lower = title.lower()
    name_lower = name.lower()
    
    # Blacklisted terms for biographical articles
    blacklist = ['election', 'constituency', 'list of', 'district', 'government', 'taluk', 'county', 'assembly']
    if any(b in title_lower for b in blacklist):
        return False
        
    # Title should share some significant word overlap with the politician name
    name_words = set(get_clean_words(name_lower))
    title_words = set(get_clean_words(title_lower))
    
    # If there is no overlap in clean words, it's probably not the right page
    if not name_words.intersection(title_words):
        # Check fuzzy matching score of the entire name
        ratio = difflib.SequenceMatcher(None, name_lower, title_lower).ratio()
        if ratio < 0.6:
            return False
            
    return True

class Command(BaseCommand):
    help = 'Enrich existing politicians with Wikipedia biographies using search fallback and redirects'

    def handle(self, *args, **options):
        self.stdout.write('Starting Wikipedia enrichment...')
        
        politicians = Politician.objects.filter(is_active=True)
        self.stdout.write(f'Found {politicians.count()} active politicians')
        
        updated_count = 0
        
        url = 'https://en.wikipedia.org/w/api.php'
        headers = {'User-Agent': 'KarnatakaPoliticiansTracker/1.0 (research@example.com)'}
        
        for politician in politicians:
            # Skip if we already have a solid biography
            if politician.biography_en and len(politician.biography_en) > 500 and not politician.biography_en.startswith('Profession:'):
                continue
                
            name = politician.full_name_en
            self.stdout.write(f'Fetching Wikipedia for {name}...')
            
            # Try exact name, then with (politician), then with (Indian politician)
            candidates = [name, f"{name} (politician)", f"{name} (Indian politician)"]
            extract = None
            matched_title = None
            
            for candidate_title in candidates:
                params = {
                    'action': 'query',
                    'prop': 'extracts',
                    'exintro': True,
                    'explaintext': True,
                    'format': 'json',
                    'titles': candidate_title,
                    'redirects': 1
                }
                
                try:
                    r = requests.get(url, params=params, headers=headers, timeout=15)
                    data = r.json()
                    pages = data.get('query', {}).get('pages', {})
                    for page_id, page_info in pages.items():
                        if page_id != '-1':
                            ext = page_info.get('extract')
                            if ext and len(ext) > 100:
                                # Confirm it is the right person (Karnataka-related)
                                lower_ext = ext.lower()
                                if any(kw in lower_ext for kw in ['karnataka', 'bengaluru', 'bangalore']):
                                    extract = ext
                                    matched_title = page_info.get('title')
                                    break
                    if extract:
                        break
                except Exception as e:
                    logger.error(f'Error fetching exact match {candidate_title}: {e}')
            
            # Search-based fallback if exact matches failed
            if not extract:
                queries = get_search_queries(name)
                for q in queries:
                    search_params = {
                        'action': 'query',
                        'list': 'search',
                        'srsearch': q,
                        'format': 'json',
                        'srlimit': 5
                    }
                    try:
                        r = requests.get(url, params=search_params, headers=headers, timeout=15)
                        search_data = r.json()
                        search_results = search_data.get('query', {}).get('search', [])
                        
                        for res in search_results:
                            title = res['title']
                            if is_valid_person_title(title, name):
                                # Fetch the extract for the search result title
                                extract_params = {
                                    'action': 'query',
                                    'prop': 'extracts',
                                    'exintro': True,
                                    'explaintext': True,
                                    'format': 'json',
                                    'titles': title,
                                    'redirects': 1
                                }
                                r_ext = requests.get(url, params=extract_params, headers=headers, timeout=15)
                                ext_data = r_ext.json()
                                pages = ext_data.get('query', {}).get('pages', {})
                                for page_id, page_info in pages.items():
                                    if page_id != '-1':
                                        ext = page_info.get('extract')
                                        if ext and len(ext) > 100:
                                            lower_ext = ext.lower()
                                            if any(kw in lower_ext for kw in ['karnataka', 'bengaluru', 'bangalore']):
                                                extract = ext
                                                matched_title = page_info.get('title')
                                                break
                                if extract:
                                    self.stdout.write(f'  Found search fallback match: "{matched_title}"')
                                    break
                        if extract:
                            break
                    except Exception as e:
                        logger.error(f'Error searching for {name} with query "{q}": {e}')
            
            if extract:
                with transaction.atomic():
                    existing_bio = politician.biography_en
                    if existing_bio:
                        if existing_bio.startswith('Profession:'):
                            politician.biography_en = extract
                        else:
                            # Prepend Wikipedia extract, separate with two newlines
                            politician.biography_en = f"{extract}\n\n{existing_bio}"
                    else:
                        politician.biography_en = extract
                    politician.save()
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f'  Updated biography for {name} to Wikipedia page "{matched_title}"'))
            else:
                self.stdout.write(self.style.WARNING(f'  Could not find Wikipedia extract for {name}'))
                
            time.sleep(1) # Polite delay
            
        self.stdout.write(self.style.SUCCESS(f'\nEnrichment complete! Updated {updated_count} politicians from Wikipedia.'))
