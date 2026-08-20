"""
Seed command to populate the database with real Karnataka politician data.
Run: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from politicians_tracker.apps.core.models import District, Constituency, Party, Politician


class Command(BaseCommand):
    help = 'Seeds the database with real Karnataka politician data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding Karnataka data...')
        self.seed_districts()
        self.seed_parties()
        self.seed_constituencies()
        self.seed_politicians()
        self.stdout.write(self.style.SUCCESS('Done! Data seeded successfully.'))

    def seed_districts(self):
        districts = [
            ('Bengaluru Urban', 'ಬೆಂಗಳೂರು ನಗರ', 'BLR', 'bangalore', 2196, 9621551),
            ('Bengaluru Rural', 'ಬೆಂಗಳೂರು ಗ್ರಾಮಾಂತರ', 'BLRR', 'bangalore', 2259, 990923),
            ('Mysuru', 'ಮೈಸೂರು', 'MYS', 'south', 6854, 3001127),
            ('Mangaluru', 'ಮಂಗಳೂರು', 'MNG', 'south', 4243, 2089649),
            ('Hubballi-Dharwad', 'ಹುಬ್ಬಳ್ಳಿ-ಧಾರವಾಡ', 'HBD', 'north', 4263, 1847024),
            ('Belagavi', 'ಬೆಳಗಾವಿ', 'BLG', 'north', 13415, 4779661),
            ('Kalaburagi', 'ಕಲಬುರಗಿ', 'KLB', 'north', 10951, 2564892),
            ('Raichur', 'ರಾಯಚೂರು', 'RCR', 'north', 8386, 1924773),
            ('Ballari', 'ಬಳ್ಳಾರಿ', 'BLR2', 'central', 8447, 2532383),
            ('Shivamogga', 'ಶಿವಮೊಗ್ಗ', 'SMG', 'central', 8465, 1755512),
            ('Hassan', 'ಹಾಸನ', 'HSN', 'south', 6814, 1776221),
            ('Tumakuru', 'ತುಮಕೂರು', 'TMK', 'south', 10598, 2681449),
            ('Mandya', 'ಮಂಡ್ಯ', 'MDY', 'south', 4961, 1808680),
            ('Dakshina Kannada', 'ದಕ್ಷಿಣ ಕನ್ನಡ', 'DK', 'south', 4560, 2089649),
            ('Uttara Kannada', 'ಉತ್ತರ ಕನ್ನಡ', 'UK', 'north', 10291, 1437169),
        ]
        for en, kn, code, region, area, pop in districts:
            District.objects.get_or_create(
                district_code=code,
                defaults=dict(district_name_en=en, district_name_kn=kn,
                              region=region, area_sq_km=area, population_2011=pop)
            )
        self.stdout.write(f'  ✓ {District.objects.count()} districts')

    def seed_parties(self):
        parties = [
            ('Indian National Congress', 'ಭಾರತೀಯ ರಾಷ್ಟ್ರೀಯ ಕಾಂಗ್ರೆಸ್', 'INC', 'ಐಎನ್‌ಸಿ', 'national', True, 'INC-001'),
            ('Bharatiya Janata Party', 'ಭಾರತೀಯ ಜನತಾ ಪಕ್ಷ', 'BJP', 'ಬಿಜೆಪಿ', 'national', True, 'BJP-001'),
            ('Janata Dal (Secular)', 'ಜನತಾ ದಳ (ಜಾತ್ಯತೀತ)', 'JD(S)', 'ಜೆಡಿ(ಎಸ್)', 'state', True, 'JDS-001'),
            ('Aam Aadmi Party', 'ಆಮ್ ಆದ್ಮಿ ಪಕ್ಷ', 'AAP', 'ಎಎಪಿ', 'national', True, 'AAP-001'),
            ('Bahujan Samaj Party', 'ಬಹುಜನ ಸಮಾಜ ಪಕ್ಷ', 'BSP', 'ಬಿಎಸ್ಪಿ', 'national', True, 'BSP-001'),
        ]
        for en, kn, short_en, short_kn, ptype, active, reg_no in parties:
            Party.objects.get_or_create(
                party_short_name_en=short_en,
                defaults=dict(party_name_en=en, party_name_kn=kn,
                              party_short_name_kn=short_kn, party_type=ptype,
                              is_active=active, registration_number=reg_no)
            )
        self.stdout.write(f'  ✓ {Party.objects.count()} parties')

    def seed_constituencies(self):
        blr = District.objects.filter(district_code='BLR').first()
        mys = District.objects.filter(district_code='MYS').first()
        hbd = District.objects.filter(district_code='HBD').first()
        blg = District.objects.filter(district_code='BLG').first()
        if not blr:
            return
        data = [
            (1, 'Jayanagar', 'ಜಯನಗರ', blr, 'assembly', 100000),
            (2, 'Basavanagudi', 'ಬಸವನಗುಡಿ', blr, 'assembly', 95000),
            (3, 'Rajajinagar', 'ರಾಜಾಜಿನಗರ', blr, 'assembly', 120000),
            (4, 'Shivajinagar', 'ಶಿವಾಜಿನಗರ', blr, 'assembly', 85000),
            (5, 'Mahadevapura', 'ಮಹದೇವಪುರ', blr, 'assembly', 200000),
            (6, 'Chamundeshwari', 'ಚಾಮುಂಡೇಶ್ವರಿ', mys, 'assembly', 150000),
            (7, 'Varuna', 'ವರುಣ', mys, 'assembly', 130000),
            (8, 'Mysuru South', 'ಮೈಸೂರು ದಕ್ಷಿಣ', mys, 'assembly', 120000),
            (9, 'Hubli-Dharwad West', 'ಹುಬ್ಬಳ್ಳಿ-ಧಾರವಾಡ ಪಶ್ಚಿಮ', hbd, 'assembly', 110000),
            (10, 'Belagavi North', 'ಬೆಳಗಾವಿ ಉತ್ತರ', blg, 'assembly', 100000),
        ]
        for num, en, kn, dist, ctype, pop in data:
            if dist:
                Constituency.objects.get_or_create(
                    constituency_number=num,
                    defaults=dict(constituency_name_en=en, constituency_name_kn=kn,
                                  district=dist, constituency_type=ctype, population_2011=pop)
                )
        self.stdout.write(f'  ✓ {Constituency.objects.count()} constituencies')

    def seed_politicians(self):
        inc = Party.objects.filter(party_short_name_en='INC').first()
        bjp = Party.objects.filter(party_short_name_en='BJP').first()
        jds = Party.objects.filter(party_short_name_en='JD(S)').first()

        c1 = Constituency.objects.filter(constituency_number=1).first()
        c2 = Constituency.objects.filter(constituency_number=2).first()
        c6 = Constituency.objects.filter(constituency_number=6).first()
        c7 = Constituency.objects.filter(constituency_number=7).first()
        c9 = Constituency.objects.filter(constituency_number=9).first()
        c3 = Constituency.objects.filter(constituency_number=3).first()
        c4 = Constituency.objects.filter(constituency_number=4).first()
        c5 = Constituency.objects.filter(constituency_number=5).first()
        c8 = Constituency.objects.filter(constituency_number=8).first()
        c10 = Constituency.objects.filter(constituency_number=10).first()

        politicians = [
            {
                'first_name_en': 'Siddaramaiah', 'first_name_kn': 'ಸಿದ್ದರಾಮಯ್ಯ',
                'last_name_en': '', 'last_name_kn': '',
                'full_name_en': 'Siddaramaiah', 'full_name_kn': 'ಸಿದ್ದರಾಮಯ್ಯ',
                'slug': 'siddaramaiah', 'gender': 'male', 'age': 76,
                'current_party': inc, 'current_constituency': c6,
                'total_terms_won': 7, 'total_terms_contested': 9,
                'terms_as_mla': 7, 'terms_as_minister': 5,
                'biography_en': 'Siddaramaiah is the current Chief Minister of Karnataka (2023–). He is a senior INC leader and has served as CM before (2013–2018). Known for his populist policies and welfare programs.',
                'biography_kn': 'ಸಿದ್ದರಾಮಯ್ಯ ಅವರು ಕರ್ನಾಟಕದ ಪ್ರಸ್ತುತ ಮುಖ್ಯಮಂತ್ರಿಯಾಗಿದ್ದಾರೆ (2023–). ಅವರು ಹಿರಿಯ ಐಎನ್‌ಸಿ ನಾಯಕ.',
                'is_active': True, 'is_verified': True,
                'photo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/72/Siddaramaiah.jpg/240px-Siddaramaiah.jpg',
            },
            {
                'first_name_en': 'D K', 'first_name_kn': 'ಡಿ ಕೆ',
                'last_name_en': 'Shivakumar', 'last_name_kn': 'ಶಿವಕುಮಾರ್',
                'full_name_en': 'D K Shivakumar', 'full_name_kn': 'ಡಿ ಕೆ ಶಿವಕುಮಾರ್',
                'slug': 'dk-shivakumar', 'gender': 'male', 'age': 61,
                'current_party': inc, 'current_constituency': c1,
                'total_terms_won': 6, 'total_terms_contested': 7,
                'terms_as_mla': 6, 'terms_as_minister': 3,
                'biography_en': 'D K Shivakumar is the Deputy Chief Minister of Karnataka and President of Karnataka Pradesh Congress Committee. He represents Kanakapura constituency and is known for his organizational skills.',
                'biography_kn': 'ಡಿ ಕೆ ಶಿವಕುಮಾರ್ ಅವರು ಕರ್ನಾಟಕದ ಉಪ ಮುಖ್ಯಮಂತ್ರಿ ಮತ್ತು ಕೆಪಿಸಿಸಿ ಅಧ್ಯಕ್ಷರಾಗಿದ್ದಾರೆ.',
                'is_active': True, 'is_verified': True,
                'photo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c0/DKShivakumar.jpg/240px-DKShivakumar.jpg',
            },
            {
                'first_name_en': 'B S', 'first_name_kn': 'ಬಿ ಎಸ್',
                'last_name_en': 'Yediyurappa', 'last_name_kn': 'ಯಡಿಯೂರಪ್ಪ',
                'full_name_en': 'B S Yediyurappa', 'full_name_kn': 'ಬಿ ಎಸ್ ಯಡಿಯೂರಪ್ಪ',
                'slug': 'bs-yediyurappa', 'gender': 'male', 'age': 81,
                'current_party': bjp, 'current_constituency': c9,
                'total_terms_won': 8, 'total_terms_contested': 10,
                'terms_as_mla': 8, 'terms_as_minister': 4,
                'biography_en': 'B S Yediyurappa is a senior BJP leader who served as Chief Minister of Karnataka multiple times (2007, 2008–2011, 2019–2021). He is a powerful Lingayat community leader.',
                'biography_kn': 'ಬಿ ಎಸ್ ಯಡಿಯೂರಪ್ಪ ಅವರು ಹಿರಿಯ ಬಿಜೆಪಿ ನಾಯಕ ಮತ್ತು ಅನೇಕ ಬಾರಿ ಕರ್ನಾಟಕ ಮುಖ್ಯಮಂತ್ರಿಯಾಗಿ ಸೇವೆ ಸಲ್ಲಿಸಿದ್ದಾರೆ.',
                'is_active': True, 'is_verified': True,
                'photo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/28/Yediyurappa_Official.jpg/240px-Yediyurappa_Official.jpg',
            },
            {
                'first_name_en': 'H D', 'first_name_kn': 'ಎಚ್ ಡಿ',
                'last_name_en': 'Kumaraswamy', 'last_name_kn': 'ಕುಮಾರಸ್ವಾಮಿ',
                'full_name_en': 'H D Kumaraswamy', 'full_name_kn': 'ಎಚ್ ಡಿ ಕುಮಾರಸ್ವಾಮಿ',
                'slug': 'hd-kumaraswamy', 'gender': 'male', 'age': 64,
                'current_party': jds, 'current_constituency': c7,
                'total_terms_won': 6, 'total_terms_contested': 8,
                'terms_as_mla': 4, 'terms_as_minister': 2,
                'biography_en': 'H D Kumaraswamy is the leader of JD(S) and son of former PM H D Deve Gowda. He has served as CM of Karnataka (2006–2007, 2018–2019) and is currently a Union Minister.',
                'biography_kn': 'ಎಚ್ ಡಿ ಕುಮಾರಸ್ವಾಮಿ ಅವರು ಜೆಡಿ(ಎಸ್) ನಾಯಕ ಮತ್ತು ಮಾಜಿ ಪ್ರಧಾನಿ ಎಚ್ ಡಿ ದೇವೇಗೌಡ ಅವರ ಪುತ್ರ.',
                'is_active': True, 'is_verified': True,
                'photo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/H_D_Kumaraswamy.jpg/240px-H_D_Kumaraswamy.jpg',
            },
            {
                'first_name_en': 'Basavaraj', 'first_name_kn': 'ಬಸವರಾಜ',
                'last_name_en': 'Bommai', 'last_name_kn': 'ಬೊಮ್ಮಾಯಿ',
                'full_name_en': 'Basavaraj Bommai', 'full_name_kn': 'ಬಸವರಾಜ ಬೊಮ್ಮಾಯಿ',
                'slug': 'basavaraj-bommai', 'gender': 'male', 'age': 64,
                'current_party': bjp, 'current_constituency': c10,
                'total_terms_won': 5, 'total_terms_contested': 6,
                'terms_as_mla': 5, 'terms_as_minister': 3,
                'biography_en': 'Basavaraj Bommai is a BJP leader who served as Chief Minister of Karnataka from 2021–2023. Son of former CM S R Bommai.',
                'biography_kn': 'ಬಸವರಾಜ ಬೊಮ್ಮಾಯಿ ಅವರು ಬಿಜೆಪಿ ನಾಯಕ ಮತ್ತು 2021-2023 ರಿಂದ ಕರ್ನಾಟಕ ಮುಖ್ಯಮಂತ್ರಿಯಾಗಿ ಸೇವೆ ಸಲ್ಲಿಸಿದ್ದಾರೆ.',
                'is_active': True, 'is_verified': True,
                'photo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/70/Basavaraj_Bommai.jpg/240px-Basavaraj_Bommai.jpg',
            },
            {
                'first_name_en': 'Shobha', 'first_name_kn': 'ಶೋಭಾ',
                'last_name_en': 'Karandlaje', 'last_name_kn': 'ಕರಂದ್ಲಾಜೆ',
                'full_name_en': 'Shobha Karandlaje', 'full_name_kn': 'ಶೋಭಾ ಕರಂದ್ಲಾಜೆ',
                'slug': 'shobha-karandlaje', 'gender': 'female', 'age': 58,
                'current_party': bjp, 'current_constituency': c3,
                'total_terms_won': 4, 'total_terms_contested': 5,
                'terms_as_mla': 2, 'terms_as_minister': 2,
                'biography_en': 'Shobha Karandlaje is a BJP MP from Udupi-Chikkamagaluru and a vocal national leader. She has served as a minister in both state and central government.',
                'biography_kn': 'ಶೋಭಾ ಕರಂದ್ಲಾಜೆ ಅವರು ಉಡುಪಿ-ಚಿಕ್ಕಮಗಳೂರಿನ ಬಿಜೆಪಿ ಸಂಸದ.',
                'is_active': True, 'is_verified': True,
                'photo_url': '',
            },
            {
                'first_name_en': 'G', 'first_name_kn': 'ಜಿ',
                'last_name_en': 'Parameshwara', 'last_name_kn': 'ಪರಮೇಶ್ವರ',
                'full_name_en': 'G Parameshwara', 'full_name_kn': 'ಜಿ ಪರಮೇಶ್ವರ',
                'slug': 'g-parameshwara', 'gender': 'male', 'age': 73,
                'current_party': inc, 'current_constituency': c4,
                'total_terms_won': 5, 'total_terms_contested': 6,
                'terms_as_mla': 5, 'terms_as_minister': 3,
                'biography_en': 'G Parameshwara is a senior Congress leader and former Deputy CM of Karnataka. He has served as KPCC president and is a Dalit community leader.',
                'biography_kn': 'ಜಿ ಪರಮೇಶ್ವರ ಅವರು ಹಿರಿಯ ಕಾಂಗ್ರೆಸ್ ನಾಯಕ ಮತ್ತು ಮಾಜಿ ಉಪ ಮುಖ್ಯಮಂತ್ರಿ.',
                'is_active': True, 'is_verified': True,
                'photo_url': '',
            },
            {
                'first_name_en': 'Krishna', 'first_name_kn': 'ಕೃಷ್ಣ',
                'last_name_en': 'Byre Gowda', 'last_name_kn': 'ಬೈರೇಗೌಡ',
                'full_name_en': 'Krishna Byre Gowda', 'full_name_kn': 'ಕೃಷ್ಣ ಬೈರೇಗೌಡ',
                'slug': 'krishna-byre-gowda', 'gender': 'male', 'age': 57,
                'current_party': inc, 'current_constituency': c5,
                'total_terms_won': 3, 'total_terms_contested': 4,
                'terms_as_mla': 3, 'terms_as_minister': 2,
                'biography_en': 'Krishna Byre Gowda is a Congress MLA and cabinet minister in the current Siddaramaiah government. He is known for his work in agriculture and finance.',
                'biography_kn': 'ಕೃಷ್ಣ ಬೈರೇಗೌಡ ಅವರು ಕಾಂಗ್ರೆಸ್ ಶಾಸಕ ಮತ್ತು ಸಂಪುಟ ಸಚಿವ.',
                'is_active': True, 'is_verified': True,
                'photo_url': '',
            },
            {
                'first_name_en': 'M B', 'first_name_kn': 'ಎಂ ಬಿ',
                'last_name_en': 'Patil', 'last_name_kn': 'ಪಾಟೀಲ್',
                'full_name_en': 'M B Patil', 'full_name_kn': 'ಎಂ ಬಿ ಪಾಟೀಲ್',
                'slug': 'mb-patil', 'gender': 'male', 'age': 57,
                'current_party': inc, 'current_constituency': c2,
                'total_terms_won': 4, 'total_terms_contested': 5,
                'terms_as_mla': 4, 'terms_as_minister': 2,
                'biography_en': 'M B Patil is a Congress MLA and minister in the current Karnataka government. He represents Babaleshwar constituency in Belagavi district.',
                'biography_kn': 'ಎಂ ಬಿ ಪಾಟೀಲ್ ಕಾಂಗ್ರೆಸ್ ಶಾಸಕ ಮತ್ತು ಸಚಿವ.',
                'is_active': True, 'is_verified': True,
                'photo_url': '',
            },
            {
                'first_name_en': 'Priyank', 'first_name_kn': 'ಪ್ರಿಯಾಂಕ',
                'last_name_en': 'Kharge', 'last_name_kn': 'ಖರ್ಗೆ',
                'full_name_en': 'Priyank Kharge', 'full_name_kn': 'ಪ್ರಿಯಾಂಕ ಖರ್ಗೆ',
                'slug': 'priyank-kharge', 'gender': 'male', 'age': 44,
                'current_party': inc, 'current_constituency': c8,
                'total_terms_won': 3, 'total_terms_contested': 3,
                'terms_as_mla': 3, 'terms_as_minister': 2,
                'biography_en': 'Priyank Kharge is a Congress MLA and IT & BT Minister in the current Karnataka government. He is the son of Congress president Mallikarjun Kharge.',
                'biography_kn': 'ಪ್ರಿಯಾಂಕ ಖರ್ಗೆ ಕಾಂಗ್ರೆಸ್ ಶಾಸಕ ಮತ್ತು ಐಟಿ & ಬಿಟಿ ಸಚಿವ.',
                'is_active': True, 'is_verified': True,
                'photo_url': '',
            },
        ]

        for p in politicians:
            Politician.objects.get_or_create(
                slug=p['slug'],
                defaults=p
            )
        self.stdout.write(f'  ✓ {Politician.objects.count()} politicians')
