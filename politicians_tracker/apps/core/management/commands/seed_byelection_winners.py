"""
Seed the 3 Karnataka by-election winners from November 2024.
Constituencies: Channapatna (#185), Shiggaon (#83), Sandur (#95).

Data sourced from:
- Election Commission of India (ECI) official results
- MyNeta / ADR election affidavits
- Wikipedia verified profiles
"""
import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from decimal import Decimal

from politicians_tracker.apps.core.models import (
    Politician, Party, Constituency, FinancialDeclaration
)

logger = logging.getLogger(__name__)


# By-election winners data — sourced from ECI results + MyNeta affidavits
BYELECTION_WINNERS = [
    {
        'full_name_en': 'C.P. Yogeshwara',
        'full_name_kn': 'ಸಿ.ಪಿ. ಯೋಗೇಶ್ವರ',
        'first_name_en': 'C.P.',
        'first_name_kn': 'ಸಿ.ಪಿ.',
        'last_name_en': 'Yogeshwara',
        'last_name_kn': 'ಯೋಗೇಶ್ವರ',
        'constituency_number': 185,  # Channapatna
        'party_short': 'INC',
        'gender': 'male',
        'age': 62,  # Born Aug 29, 1963 — Wikipedia
        'date_of_birth': '1963-08-29',
        'representative_type': 'mla',
        'terms_as_mla': 4,  # Multiple terms as Channapatna MLA (2004, 2008, 2013 as IND/BJP, 2024 as INC)
        'total_terms_won': 4,
        'total_terms_contested': 5,
        'biography_en': (
            'Chakkere Puttamade Gowda Yogeshwara, popularly known as C.P. Yogeshwara, '
            'is a politician and former film actor who represents the Channapatna constituency '
            'in the Karnataka Legislative Assembly. Born on August 29, 1963, he has been a '
            'prominent political figure in the Ramanagara district. He has served as MLA for '
            'Channapatna multiple times, having first won in 2004. He was previously associated '
            'with the BJP before joining the Indian National Congress ahead of the 2024 by-election, '
            'which he won decisively, defeating JD(S) candidate Nikhil Kumaraswamy by a margin of '
            '25,413 votes. He holds a B.Sc. degree from V.V. Puram College, Bangalore.'
        ),
        'biography_kn': (
            'ಚಕ್ಕೆರೆ ಪುಟ್ಟಮಾದೇ ಗೌಡ ಯೋಗೇಶ್ವರ, ಸಿ.ಪಿ. ಯೋಗೇಶ್ವರ ಎಂದೇ ಪ್ರಸಿದ್ಧರಾಗಿರುವ ಅವರು '
            'ಕರ್ನಾಟಕ ವಿಧಾನಸಭೆಯಲ್ಲಿ ಚನ್ನಪಟ್ಟಣ ಕ್ಷೇತ್ರವನ್ನು ಪ್ರತಿನಿಧಿಸುವ ರಾಜಕಾರಣಿ ಮತ್ತು ಮಾಜಿ ಚಿತ್ರನಟ. '
            '2024ರ ಉಪಚುನಾವಣೆಯಲ್ಲಿ ಭಾರತೀಯ ರಾಷ್ಟ್ರೀಯ ಕಾಂಗ್ರೆಸ್ ಅಭ್ಯರ್ಥಿಯಾಗಿ ಗೆಲುವು ಸಾಧಿಸಿದರು.'
        ),
        # Financial data from MyNeta / The Hindu — 2024 by-election affidavit
        'financial': {
            'declaration_year': 2024,
            'declaration_type': 'election',
            'total_assets': Decimal('670000000'),    # ~₹67 Cr
            'total_liabilities': Decimal('290000000'),  # ~₹29 Cr
        },
    },
    {
        'full_name_en': 'Yasir Ahmed Khan Pathan',
        'full_name_kn': 'ಯಾಸಿರ್ ಅಹ್ಮದ್ ಖಾನ್ ಪಠಾಣ',
        'first_name_en': 'Yasir Ahmed Khan',
        'first_name_kn': 'ಯಾಸಿರ್ ಅಹ್ಮದ್ ಖಾನ್',
        'last_name_en': 'Pathan',
        'last_name_kn': 'ಪಠಾಣ',
        'constituency_number': 83,  # Shiggaon
        'party_short': 'INC',
        'gender': 'male',
        'age': 44,  # 43 at time of 2024 by-election, turning 44 in 2025
        'date_of_birth': None,  # Exact DOB not publicly confirmed
        'representative_type': 'mla',
        'terms_as_mla': 1,  # First time MLA
        'total_terms_won': 1,
        'total_terms_contested': 1,
        'biography_en': (
            'Yasir Ahmed Khan Pathan is an Indian National Congress politician who represents '
            'the Shiggaon constituency in the Karnataka Legislative Assembly. He won the 2024 '
            'Shiggaon by-election, defeating BJP candidate Bharath Bommai (son of former CM '
            'Basavaraj Bommai) by a margin of 13,448 votes. The by-election was necessitated '
            'after Basavaraj Bommai vacated the seat upon being elected as a Lok Sabha MP in '
            'the 2024 general elections. Pathan is a first-time MLA from Haveri district.'
        ),
        'biography_kn': (
            'ಯಾಸಿರ್ ಅಹ್ಮದ್ ಖಾನ್ ಪಠಾಣ ಅವರು ಕರ್ನಾಟಕ ವಿಧಾನಸಭೆಯಲ್ಲಿ ಶಿಗ್ಗಾಂವಿ ಕ್ಷೇತ್ರವನ್ನು ಪ್ರತಿನಿಧಿಸುವ '
            'ಭಾರತೀಯ ರಾಷ್ಟ್ರೀಯ ಕಾಂಗ್ರೆಸ್ ರಾಜಕಾರಣಿ. 2024ರ ಉಪಚುನಾವಣೆಯಲ್ಲಿ ಬಿಜೆಪಿ ಅಭ್ಯರ್ಥಿ ಭರತ್ ಬೊಮ್ಮಾಯಿ '
            'ಅವರನ್ನು 13,448 ಮತಗಳ ಅಂತರದಿಂದ ಸೋಲಿಸಿ ಪ್ರಥಮ ಬಾರಿಗೆ ಶಾಸಕರಾದರು.'
        ),
        # Financial data not found in public search — set to 0, to be enriched later
        'financial': None,
    },
    {
        'full_name_en': 'E. Annapoorna',
        'full_name_kn': 'ಇ. ಅನ್ನಪೂರ್ಣ',
        'first_name_en': 'E.',
        'first_name_kn': 'ಇ.',
        'last_name_en': 'Annapoorna',
        'last_name_kn': 'ಅನ್ನಪೂರ್ಣ',
        'constituency_number': 95,  # Sandur (ST)
        'party_short': 'INC',
        'gender': 'female',
        'age': 51,  # 50 at time of 2024 by-election
        'date_of_birth': None,
        'representative_type': 'mla',
        'terms_as_mla': 1,  # First time MLA
        'total_terms_won': 1,
        'total_terms_contested': 1,
        'biography_en': (
            'E. Annapoorna (also known as E. Annapoorna Tukaram) is an Indian National Congress '
            'politician who represents the Sandur (ST) constituency in the Karnataka Legislative '
            'Assembly. She is the wife of E. Tukaram, the current Lok Sabha MP from Bellary. '
            'She won the 2024 Sandur by-election by defeating the BJP candidate Bangaru Hanumanthu '
            'with a margin of 9,649 votes. The by-election was necessitated after her husband '
            'E. Tukaram vacated the assembly seat upon being elected to the Lok Sabha in the '
            '2024 general elections. She is a first-time MLA from Ballari district.'
        ),
        'biography_kn': (
            'ಇ. ಅನ್ನಪೂರ್ಣ (ಇ. ಅನ್ನಪೂರ್ಣ ತುಕಾರಾಮ್ ಎಂದೂ ಕರೆಯಲಾಗುತ್ತದೆ) ಅವರು ಕರ್ನಾಟಕ ವಿಧಾನಸಭೆಯಲ್ಲಿ '
            'ಸಂಡೂರು (ಪ.ಪಂ) ಕ್ಷೇತ್ರವನ್ನು ಪ್ರತಿನಿಧಿಸುವ ಭಾರತೀಯ ರಾಷ್ಟ್ರೀಯ ಕಾಂಗ್ರೆಸ್ ರಾಜಕಾರಣಿ. '
            '2024ರ ಉಪಚುನಾವಣೆಯಲ್ಲಿ 9,649 ಮತಗಳ ಅಂತರದಿಂದ ಗೆಲುವು ಸಾಧಿಸಿ ಪ್ರಥಮ ಬಾರಿಗೆ ಶಾಸಕರಾದರು.'
        ),
        # Financial data from MyNeta/ADR — 2024 by-election affidavit
        'financial': {
            'declaration_year': 2024,
            'declaration_type': 'election',
            'total_assets': Decimal('33671404'),     # ₹3.36 Cr (₹3,36,71,404)
            'total_liabilities': Decimal('14725000'),  # ₹1.47 Cr (₹1,47,25,000)
        },
    },
]


class Command(BaseCommand):
    help = 'Seed 3 Karnataka by-election winners from November 2024 (Channapatna, Shiggaon, Sandur)'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Show what would be created without modifying DB')

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN — no changes will be made'))

        inc_party = Party.objects.filter(party_short_name_en='INC').first()
        if not inc_party:
            self.stdout.write(self.style.ERROR('INC party not found in database. Aborting.'))
            return

        created_count = 0

        with transaction.atomic():
            for entry in BYELECTION_WINNERS:
                const_num = entry['constituency_number']
                constituency = Constituency.objects.filter(constituency_number=const_num).first()
                if not constituency:
                    self.stdout.write(self.style.ERROR(
                        f'  Constituency #{const_num} not found! Skipping {entry["full_name_en"]}'
                    ))
                    continue

                slug = slugify(entry['full_name_en'])
                # Handle slug collision
                if Politician.objects.filter(slug=slug).exclude(full_name_en=entry['full_name_en']).exists():
                    slug = f'{slug}-{const_num}'

                if dry_run:
                    self.stdout.write(self.style.SUCCESS(
                        f'  [DRY] Would create: {entry["full_name_en"]} → {constituency} (INC)'
                    ))
                    continue

                pol, created = Politician.objects.update_or_create(
                    full_name_en=entry['full_name_en'],
                    defaults={
                        'slug': slug,
                        'full_name_kn': entry['full_name_kn'],
                        'first_name_en': entry['first_name_en'],
                        'first_name_kn': entry['first_name_kn'],
                        'last_name_en': entry['last_name_en'],
                        'last_name_kn': entry['last_name_kn'],
                        'current_party': inc_party,
                        'current_constituency': constituency,
                        'representative_type': entry['representative_type'],
                        'gender': entry['gender'],
                        'age': entry['age'],
                        'date_of_birth': entry.get('date_of_birth'),
                        'terms_as_mla': entry['terms_as_mla'],
                        'total_terms_won': entry['total_terms_won'],
                        'total_terms_contested': entry['total_terms_contested'],
                        'biography_en': entry['biography_en'],
                        'biography_kn': entry['biography_kn'],
                        'is_active': True,
                        'is_verified': True,
                    }
                )

                action = 'Created' if created else 'Updated'
                self.stdout.write(self.style.SUCCESS(
                    f'  {action}: {entry["full_name_en"]} ({slug}) → '
                    f'{constituency.constituency_name_en} #{const_num} (INC)'
                ))

                # Create financial declaration if data is available
                if entry.get('financial'):
                    fin = entry['financial']
                    fd, fd_created = FinancialDeclaration.objects.update_or_create(
                        politician=pol,
                        declaration_year=fin['declaration_year'],
                        declaration_type=fin['declaration_type'],
                        defaults={
                            'total_assets': fin['total_assets'],
                            'total_liabilities': fin['total_liabilities'],
                            'declaration_url': f'https://myneta.info/KarnatakaByelection2024/',
                            'is_verified': True,
                        }
                    )
                    fd_action = 'Created' if fd_created else 'Updated'
                    self.stdout.write(
                        f'    {fd_action} financial declaration: '
                        f'Assets ₹{float(fin["total_assets"])/10000000:.2f} Cr, '
                        f'Liabilities ₹{float(fin["total_liabilities"])/10000000:.2f} Cr'
                    )

                if created:
                    created_count += 1

        total_mlas = Politician.objects.filter(is_active=True, representative_type='mla').count()
        total_all = Politician.objects.filter(is_active=True).count()
        self.stdout.write(self.style.SUCCESS(
            f'\nDone! Created {created_count} new by-election winners.'
            f'\nTotal active MLAs: {total_mlas} | Total active representatives: {total_all}'
        ))
