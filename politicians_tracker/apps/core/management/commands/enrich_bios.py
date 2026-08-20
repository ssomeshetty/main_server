"""
Command to generate biographies for politicians missing them using LLM.
"""
import logging
import time

from django.core.management.base import BaseCommand
from politicians_tracker.apps.core.models import Politician
from politicians_tracker.apps.core.scrapers.llm_purification_worker import get_llm_provider

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Generate short factual biographies for politicians missing them using LLM'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=0, help='Max biographies to generate')

    def handle(self, *args, **options):
        limit = options['limit']
        
        self.stdout.write("Fetching politicians without biographies...")
        politicians = Politician.objects.filter(is_active=True).exclude(biography_en__regex=r'^.{20,}$')
        
        if limit:
            politicians = politicians[:limit]
            
        total = politicians.count()
        self.stdout.write(f"Found {total} politicians missing biographies.")
        
        if total == 0:
            return
            
        llm = get_llm_provider()
        
        system_prompt = "You are a helpful assistant. Output ONLY valid JSON containing a 'biography_en' key with a short, factual, neutral biography (3-4 sentences max)."
        
        for i, pol in enumerate(politicians, 1):
            self.stdout.write(f"[{i}/{total}] Generating biography for {pol.full_name_en}...")
            
            prompt = f"Name: {pol.full_name_en}\\nParty: {pol.current_party}\\nConstituency: {pol.current_constituency.constituency_name_en if pol.current_constituency else 'Unknown'}\\nState: Karnataka\\nAge: {pol.age or 'Unknown'}"
            
            try:
                # We can't use the structured PurifiedContent because it expects news format.
                # Instead we will just use the internal client directly to generate a simple JSON.
                if hasattr(llm, '_client'):
                    # OpenAI Provider
                    response = llm._client.chat.completions.create(
                        model=llm.model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        response_format={"type": "json_object"},
                        temperature=0.3,
                        max_tokens=256,
                    )
                    text = response.choices[0].message.content
                else:
                    self.stdout.write(self.style.ERROR("Only OpenAI/NVIDIA LLM provider supported for this script currently."))
                    continue
                    
                import json
                data = json.loads(text)
                bio = data.get('biography_en', '').strip()
                
                if bio:
                    pol.biography_en = bio
                    pol.save()
                    self.stdout.write(self.style.SUCCESS(f"  Generated: {bio[:60]}..."))
                else:
                    self.stdout.write(self.style.WARNING("  Failed to generate biography."))
                    
                time.sleep(2)
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  Error: {e}"))
                
        self.stdout.write(self.style.SUCCESS("Biography generation complete!"))
