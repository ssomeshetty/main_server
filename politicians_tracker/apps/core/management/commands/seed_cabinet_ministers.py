from django.core.management.base import BaseCommand
from politicians_tracker.apps.core.models import Politician, Party

# Official D. K. Shivakumar Cabinet Portfolio Mapping (2026 - Present)
CABINET_MINISTERS = [
    {
        'match_slug': 'dk-shivakumar',
        'minister_type': 'cm',
        'title_en': 'Chief Minister of Karnataka',
        'title_kn': 'ಕರ್ನಾಟಕದ ಮುಖ್ಯಮಂತ್ರಿ',
        'portfolio_en': 'Finance, Cabinet Affairs, Personnel and Administrative Reforms, Intelligence, and all unallocated portfolios',
        'portfolio_kn': 'ಹಣಕಾಸು, ಸಂಪುಟ ವ್ಯವಹಾರಗಳು, ಸಿಬ್ಬಂದಿ ಮತ್ತು ಆಡಳಿತ ಸುಧಾರಣೆ, ಗುಪ್ತಚರ ಮತ್ತು ಹಂಚಿಕೆ ಮಾಡದ ಇಲಾಖೆಗಳು'
    },
    {
        'match_slug': 'g-parameshwara',
        'minister_type': 'deputy_cm',
        'title_en': 'Deputy Chief Minister',
        'title_kn': 'ಉಪ ಮುಖ್ಯಮಂತ್ರಿ',
        'portfolio_en': 'Revenue, Sports',
        'portfolio_kn': 'ಕಂದಾಯ, ಕ್ರೀಡೆ'
    },
    {
        'match_slug': 'k-h-muniyappa',
        'minister_type': 'cabinet_minister',
        'title_en': 'Cabinet Minister',
        'title_kn': 'ಸಂಪುಟ ಸಚಿವರು',
        'portfolio_en': 'Food & Civil Supplies, Consumer Affairs',
        'portfolio_kn': 'ಆಹಾರ ಮತ್ತು ನಾಗರಿಕ ಸರಬರಾಜು, ಗ್ರಾಹಕ ವ್ಯವಹಾರಗಳು'
    },
    {
        'match_slug': 'k-j-george',
        'minister_type': 'cabinet_minister',
        'title_en': 'Cabinet Minister',
        'title_kn': 'ಸಂಪುಟ ಸಚಿವರು',
        'portfolio_en': 'Energy',
        'portfolio_kn': 'ಇಂಧನ'
    },
    {
        'match_slug': 'm-b-patil',
        'minister_type': 'cabinet_minister',
        'title_en': 'Cabinet Minister',
        'title_kn': 'ಸಂಪುಟ ಸಚಿವರು',
        'portfolio_en': 'Large & Medium Industries, Infrastructure Development',
        'portfolio_kn': 'ಬೃಹತ್ ಮತ್ತು ಮಧ್ಯಮ ಕೈಗಾರಿಕೆಗಳು, ಮೂಲಸೌಕರ್ಯ ಅಭಿವೃದ್ಧಿ'
    },
    {
        'match_slug': 'ramalinga-reddy',
        'minister_type': 'cabinet_minister',
        'title_en': 'Cabinet Minister',
        'title_kn': 'ಸಂಪುಟ ಸಚಿವರು',
        'portfolio_en': 'Major & Medium Irrigation',
        'portfolio_kn': 'ಬೃಹತ್ ಮತ್ತು ಮಧ್ಯಮ ನೀರಾವರಿ'
    },
    {
        'match_slug': 'satish-jarkiholi',
        'minister_type': 'cabinet_minister',
        'title_en': 'Cabinet Minister',
        'title_kn': 'ಸಂಪುಟ ಸಚಿವರು',
        'portfolio_en': 'Public Works',
        'portfolio_kn': 'ಲೋಕೋಪಯೋಗಿ'
    },
    {
        'match_slug': 'krishna-byre-gowda',
        'minister_type': 'cabinet_minister',
        'title_en': 'Cabinet Minister',
        'title_kn': 'ಸಂಪುಟ ಸಚಿವರು',
        'portfolio_en': 'Greater Bengaluru Development',
        'portfolio_kn': 'ಬೃಹತ್ ಬೆಂಗಳೂರು ಅಭಿವೃದ್ಧಿ'
    },
    {
        'match_slug': 'priyank-kharge',
        'minister_type': 'cabinet_minister',
        'title_en': 'Cabinet Minister',
        'title_kn': 'ಸಂಪುಟ ಸಚಿವರು',
        'portfolio_en': 'Home (excluding intelligence), IT & BT, e-Governance',
        'portfolio_kn': 'ಗೃಹ ವ್ಯವಹಾರಗಳು (ಗುಪ್ತಚರ ಹೊರತುಪಡಿಸಿ), ಐಟಿ ಮತ್ತು ಬಿಟಿ, ಇ-ಆಡಳಿತ'
    },
    {
        'match_slug': 'u-t-khader',
        'minister_type': 'cabinet_minister',
        'title_en': 'Cabinet Minister',
        'title_kn': 'ಸಂಪುಟ ಸಚಿವರು',
        'portfolio_en': 'Health & Family Welfare',
        'portfolio_kn': 'ಆರೋಗ್ಯ ಮತ್ತು ಕುಟುಂಬ ಕಲ್ಯಾಣ'
    },
    {
        'match_slug': 'eshwara-khandre',
        'minister_type': 'cabinet_minister',
        'title_en': 'Cabinet Minister',
        'title_kn': 'ಸಂಪುಟ ಸಚಿವರು',
        'portfolio_en': 'Rural Development and Panchayat Raj',
        'portfolio_kn': 'ಗ್ರಾಮೀಣಾಭಿವೃದ್ಧಿ ಮತ್ತು ಪಂಚಾಯತ್ ರಾಜ್'
    },
    {
        'match_slug': 'byrathi-suresh',
        'minister_type': 'cabinet_minister',
        'title_en': 'Cabinet Minister',
        'title_kn': 'ಸಂಪುಟ ಸಚಿವರು',
        'portfolio_en': 'Transport',
        'portfolio_kn': 'ಸಾರಿಗೆ'
    },
    {
        'match_slug': 'sharan-prakash-patil',
        'minister_type': 'cabinet_minister',
        'title_en': 'Cabinet Minister',
        'title_kn': 'ಸಂಪುಟ ಸಚಿವರು',
        'portfolio_en': 'Medical Education & Skill Development',
        'portfolio_kn': 'ವೈದ್ಯಕೀಯ ಶಿಕ್ಷಣ ಮತ್ತು ಕೌಶಲ್ಯಾಭಿವೃದ್ಧಿ'
    },
    {
        'match_slug': 'yathindra-siddaramaiah',
        'minister_type': 'cabinet_minister',
        'title_en': 'Cabinet Minister',
        'title_kn': 'ಸಂಪುಟ ಸಚಿವರು',
        'portfolio_en': 'Urban Development',
        'portfolio_kn': 'ನಗರಾಭಿವೃದ್ಧಿ'
    }
]

class Command(BaseCommand):
    help = 'Seeds cabinet minister portfolio details and rank titles for active MLAs'

    def handle(self, *args, **kwargs):
        # 1. Clear old minister designations
        cleared_count = Politician.objects.filter(is_minister=True).update(
            is_minister=False,
            minister_type='',
            minister_title_en='',
            minister_title_kn='',
            portfolio_en='',
            portfolio_kn=''
        )
        self.stdout.write(self.style.WARNING(f'Cleared {cleared_count} old Cabinet Minister designations.'))

        # 2. Ensure Yathindra Siddaramaiah exists in database
        yathindra_slug = 'yathindra-siddaramaiah'
        yathindra_exists = Politician.objects.filter(slug=yathindra_slug).exists()
        if not yathindra_exists:
            inc = Party.objects.filter(party_short_name_en='INC').first()
            Politician.objects.create(
                first_name_en="Yathindra",
                first_name_kn="ಯತೀಂದ್ರ",
                last_name_en="Siddaramaiah",
                last_name_kn="ಸಿದ್ದರಾಮಯ್ಯ",
                full_name_en="Dr. Yathindra Siddaramaiah",
                full_name_kn="ಡಾ. ಯತೀಂದ್ರ ಸಿದ್ದರಾಮಯ್ಯ",
                slug=yathindra_slug,
                gender="male",
                age=46,
                is_active=True,
                is_verified=True,
                current_party=inc,
                representative_type="mla",
                photo_url='https://upload.wikimedia.org/wikipedia/commons/e/ea/Jagadish_Shettar.jpg' # fallback / none
            )
            self.stdout.write(self.style.SUCCESS(f'Created Politician record for Yathindra Siddaramaiah.'))

        # 3. Seed new cabinet
        updated_count = 0
        for item in CABINET_MINISTERS:
            slug = item['match_slug']
            pol = Politician.objects.filter(slug=slug).first()
            if pol:
                pol.is_minister = True
                pol.minister_type = item['minister_type']
                pol.minister_title_en = item['title_en']
                pol.minister_title_kn = item['title_kn']
                pol.portfolio_en = item['portfolio_en']
                pol.portfolio_kn = item['portfolio_kn']
                pol.save()
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f'Updated Cabinet Minister: {pol.full_name_en} ({item["title_en"]})'))
            else:
                self.stdout.write(self.style.WARNING(f'Could not find politician matching slug: {slug}'))

        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully seeded {updated_count} Cabinet Ministers!'))
