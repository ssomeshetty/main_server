from django.core.management.base import BaseCommand
from django.db import transaction
import re

from politicians_tracker.apps.core.models import Politician, Party, Constituency, District, RawScrapedData

class Command(BaseCommand):
    help = 'Process raw MyNeta scraped data into core Politician models'

    def handle(self, *args, **options):
        raw_records = RawScrapedData.objects.filter(source_type='ec_portal', content_json__isnull=False)
        self.stdout.write(f"Found {raw_records.count()} records to process")
        
        with transaction.atomic():
            for record in raw_records:
                data = record.content_json
                if not data:
                    continue
                    
                # 1. District
                district_name = data.get('district', '').strip()
                if not district_name:
                    district_name = 'Unknown'
                district, _ = District.objects.get_or_create(
                    district_name_en=district_name,
                    defaults={'region': 'Unknown'}
                )
                
                # 2. Constituency
                const_name = data.get('constituency', '').strip()
                if not const_name:
                    continue
                # Extract number if present (e.g., "Mysuru (15)")
                match = re.search(r'\((\d+)\)', const_name)
                const_num = int(match.group(1)) if match else 0
                const_name = re.sub(r'\(\d+\)', '', const_name).strip()
                
                constituency, _ = Constituency.objects.get_or_create(
                    constituency_name_en=const_name,
                    defaults={
                        'district': district,
                        'constituency_number': const_num,
                        'constituency_type': 'assembly'
                    }
                )
                
                # 3. Party
                party_name = data.get('party', '').strip()
                if not party_name:
                    party_name = 'Independent'
                party, _ = Party.objects.get_or_create(
                    party_name_en=party_name,
                    defaults={'party_short_name_en': party_name[:10]}
                )
                
                # 4. Politician
                name = data.get('name', '').strip()
                if not name:
                    continue
                    
                politician, created = Politician.objects.update_or_create(
                    full_name_en=name,
                    defaults={
                        'age': data.get('age'),
                        'gender': data.get('gender', '').lower() if data.get('gender') else 'unknown',
                        'current_party': party,
                        'current_constituency': constituency,
                        'is_active': True,
                        'is_verified': True
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created: {name} ({const_name})"))
                else:
                    self.stdout.write(f"Updated: {name} ({const_name})")
                    
        self.stdout.write(self.style.SUCCESS("Finished processing MyNeta data!"))
