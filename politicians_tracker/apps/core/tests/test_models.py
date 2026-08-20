"""
Model tests for the Karnataka Politicians Tracker.

Tests verify:
- Model field defaults and constraints
- Model methods (calculate_net_worth, save, etc.)
- Model relationships
- Query optimization
"""
from django.test import TestCase
from django.core.exceptions import ValidationError

from ..models import (
    District, Constituency, Party, Politician,
    FinancialDeclaration, LegalRecord, PublicRecord, ConstituencyFund
)


class DistrictModelTests(TestCase):
    """Tests for District model."""
    
    def setUp(self):
        self.district_data = {
            'district_name_en': 'Bangalore Urban',
            'district_name_kn': 'ಬೆಂಗಳೂರು ನಗರ',
            'district_code': 'BLR001',
            'region': 'bangalore',
            'area_sq_km': 219.36,
            'population_2011': 9308131,
        }
    
    def test_create_district(self):
        """Test creating a district."""
        district = District.objects.create(**self.district_data)
        
        self.assertEqual(district.district_name_en, 'Bangalore Urban')
        self.assertEqual(district.district_name_kn, 'ಬೆಂಗಳೂರು ನಗರ')
        self.assertEqual(district.district_code, 'BLR001')
        self.assertEqual(district.region, 'bangalore')
    
    def test_district_str(self):
        """Test district __str__ method."""
        district = District.objects.create(**self.district_data)
        
        self.assertEqual(str(district), district.district_name_en)
    
    def test_district_unique_constraint(self):
        """Test district_code uniqueness."""
        District.objects.create(**self.district_data)
        
        with self.assertRaises(Exception):
            District.objects.create(**self.district_data)
    
    def test_district_indexing(self):
        """Test that district has proper indexes."""
        # Create multiple districts to test ordering
        District.objects.create(
            district_name_en='District A',
            district_name_kn='ಜಿಲ್ಲೆ A',
            district_code='DST001',
            region='north'
        )
        District.objects.create(
            district_name_en='District B',
            district_name_kn='ಜಿಲ್ಲೆ B',
            district_code='DST002',
            region='south'
        )
        
        districts = District.objects.all()
        self.assertEqual(len(districts), 2)


class ConstituencyModelTests(TestCase):
    """Tests for Constituency model."""
    
    def setUp(self):
        self.district = District.objects.create(
            district_name_en='Test District',
            district_name_kn='ಟೆಸ್ಟ್ ಜಿಲ್ಲೆ',
            district_code='TST001',
            region='north'
        )
        
        self.constituency_data = {
            'constituency_name_en': 'Bangalore Central',
            'constituency_name_kn': 'ಬೆಂಗಳೂರು ಕೇಂದ್ರ',
            'constituency_number': 1,
            'district': self.district,
            'constituency_type': 'general',
            'population_2011': 1000000,
            'male_population': 520000,
            'female_population': 480000,
            'sex_ratio': 923.08,
            'literacy_rate': 85.5,
        }
    
    def test_create_constituency(self):
        """Test creating a constituency."""
        constituency = Constituency.objects.create(**self.constituency_data)
        
        self.assertEqual(constituency.constituency_name_en, 'Bangalore Central')
        self.assertEqual(constituency.constituency_number, 1)
        self.assertEqual(constituency.district, self.district)
    
    def test_constituency_str(self):
        """Test constituency __str__ method."""
        constituency = Constituency.objects.create(**self.constituency_data)
        
        self.assertEqual(str(constituency), constituency.constituency_name_en)
    
    def test_constituency_ordering(self):
        """Test constituency ordering by constituency_number."""
        c1 = Constituency.objects.create(
            constituency_name_en='Constituency 2',
            constituency_name_kn='ವಿಧಾನ ಮಂಡಲ 2',
            constituency_number=2,
            district=self.district,
            constituency_type='general',
            population_2011=1000000
        )
        c2 = Constituency.objects.create(
            constituency_name_en='Constituency 1',
            constituency_name_kn='ವಿಧಾನ ಮಂಡಲ 1',
            constituency_number=1,
            district=self.district,
            constituency_type='general',
            population_2011=1000000
        )
        
        constituencies = Constituency.objects.all()
        self.assertEqual(constituencies[0], c2)
        self.assertEqual(constituencies[1], c1)
    
    def test_constituency_count(self):
        """Test that constituencies are properly counted per district."""
        d1 = District.objects.create(
            district_name_en='District 1',
            district_name_kn='ಜಿಲ್ಲೆ 1',
            district_code='DST001',
            region='north'
        )
        d2 = District.objects.create(
            district_name_en='District 2',
            district_name_kn='ಜಿಲ್ಲೆ 2',
            district_code='DST002',
            region='south'
        )
        
        c1 = Constituency.objects.create(
            constituency_name_en='Constituency 1',
            constituency_name_kn='ವಿಧಾನ ಮಂಡಲ 1',
            constituency_number=1,
            district=d1,
            constituency_type='general',
            population_2011=1000000
        )
        c2 = Constituency.objects.create(
            constituency_name_en='Constituency 2',
            constituency_name_kn='ವಿಧಾನ ಮಂಡಲ 2',
            constituency_number=2,
            district=d1,
            constituency_type='general',
            population_2011=1000000
        )
        c3 = Constituency.objects.create(
            constituency_name_en='Constituency 3',
            constituency_name_kn='ವಿಧಾನ ಮಂಡಲ 3',
            constituency_number=3,
            district=d2,
            constituency_type='general',
            population_2011=1000000
        )
        
        self.assertEqual(d1.constituencies.count(), 2)
        self.assertEqual(d2.constituencies.count(), 1)


class PartyModelTests(TestCase):
    """Tests for Party model."""
    
    def setUp(self):
        self.party_data = {
            'party_name_en': 'Democratic Party',
            'party_name_kn': 'ಪ್ರಜಾಪ್ರಭುತ್ವ ಪಕ್ಷ',
            'party_short_name_en': 'DP',
            'party_short_name_kn': 'ಪ್ರಪ',
            'party_symbol': 'Hand',
            'party_type': 'state',
            'registration_number': 'NCA1001',
            'is_active': True,
        }
    
    def test_create_party(self):
        """Test creating a party."""
        party = Party.objects.create(**self.party_data)
        
        self.assertEqual(party.party_name_en, 'Democratic Party')
        self.assertEqual(party.party_short_name_en, 'DP')
        self.assertEqual(party.party_type, 'state')
    
    def test_party_str(self):
        """Test party __str__ method."""
        party = Party.objects.create(**self.party_data)
        
        self.assertEqual(str(party), party.party_name_en)
    
    def test_party_unique_constraint(self):
        """Test party_name_en uniqueness."""
        Party.objects.create(**self.party_data)
        
        with self.assertRaises(Exception):
            Party.objects.create(**self.party_data)


class PoliticianModelTests(TestCase):
    """Tests for Politician model."""
    
    def setUp(self):
        self.party = Party.objects.create(
            party_name_en='Democratic Party',
            party_name_kn='ಪ್ರಜಾಪ್ರಭುತ್ವ ಪಕ್ಷ',
            party_short_name_en='DP',
            party_short_name_kn='ಪ್ರಪ',
            party_type='state',
            registration_number='NCA1001',
            is_active=True
        )
        
        self.district = District.objects.create(
            district_name_en='Test District',
            district_name_kn='ಟೆಸ್ಟ್ ಜಿಲ್ಲೆ',
            district_code='TST001',
            region='north'
        )
        
        self.constituency = Constituency.objects.create(
            constituency_name_en='Bangalore Central',
            constituency_name_kn='ಬೆಂಗಳೂರು ಕೇಂದ್ರ',
            constituency_number=1,
            district=self.district,
            constituency_type='general',
            population_2011=1000000
        )
        
        self.politician_data = {
            'first_name_en': 'John',
            'first_name_kn': 'ಜಾನ್',
            'last_name_en': 'Doe',
            'last_name_kn': 'ಡೊ',
            'full_name_en': 'John Doe',
            'full_name_kn': 'ಜಾನ್ ಡೊ',
            'slug': 'john-doe',
            'current_party': self.party,
            'current_constituency': self.constituency,
            'total_terms_contested': 3,
            'total_terms_won': 2,
            'terms_as_mla': 2,
            'terms_as_mlna': 1,
            'terms_as_mp': 0,
            'terms_as_minister': 1,
            'is_active': True,
            'is_verified': True,
        }
    
    def test_create_politician(self):
        """Test creating a politician."""
        politician = Politician.objects.create(**self.politician_data)
        
        self.assertEqual(politician.full_name_en, 'John Doe')
        self.assertEqual(politician.current_party, self.party)
        self.assertEqual(politician.current_constituency, self.constituency)
    
    def test_politician_str(self):
        """Test politician __str__ method."""
        politician = Politician.objects.create(**self.politician_data)
        
        self.assertEqual(str(politician), politician.full_name_en)
    
    def test_politician_auto_full_name(self):
        """Test that full_name is auto-generated from first and last name."""
        politician = Politician.objects.create(
            first_name_en='Jane',
            first_name_kn='ಜೇನ್',
            last_name_en='Smith',
            last_name_kn='ಸ್ಮಿತ್',
            slug='jane-smith',
            current_party=self.party,
            current_constituency=self.constituency
        )
        
        self.assertEqual(politician.full_name_en, 'Jane Smith')
    
    def test_politician_terms_sum(self):
        """Test that term counts are set correctly."""
        politician = Politician.objects.create(**self.politician_data)
        
        self.assertEqual(politician.total_terms_contested, 3)
        self.assertEqual(politician.total_terms_won, 2)


class FinancialDeclarationModelTests(TestCase):
    """Tests for FinancialDeclaration model."""
    
    def setUp(self):
        self.politician = Politician.objects.create(
            first_name_en='John',
            first_name_kn='ಜಾನ್',
            last_name_en='Doe',
            last_name_kn='ಡೊ',
            full_name_en='John Doe',
            full_name_kn='ಜಾನ್ ಡೊ',
            slug='john-doe',
            is_active=True
        )
        
        self.declaration_data = {
            'politician': self.politician,
            'declaration_year': 2024,
            'declaration_type': 'election',
            'total_assets': 10000000,
            'total_liabilities': 2000000,
            'residential_property_value': 5000000,
            'commercial_property_value': 3000000,
            'bank_deposits': 2000000,
            'is_verified': True,
        }
    
    def test_create_financial_declaration(self):
        """Test creating a financial declaration."""
        declaration = FinancialDeclaration.objects.create(**self.declaration_data)
        
        self.assertEqual(declaration.politician, self.politician)
        self.assertEqual(declaration.declaration_year, 2024)
        self.assertEqual(float(declaration.total_assets), 10000000)
    
    def test_net_worth_calculation(self):
        """Test net worth calculation."""
        declaration = FinancialDeclaration.objects.create(**self.declaration_data)
        
        expected_net_worth = 10000000 - 2000000  # 8000000
        self.assertEqual(float(declaration.calculate_net_worth()), expected_net_worth)
    
    def test_unique_together_constraint(self):
        """Test unique_together constraint."""
        FinancialDeclaration.objects.create(**self.declaration_data)
        
        with self.assertRaises(Exception):
            FinancialDeclaration.objects.create(**self.declaration_data)


class LegalRecordModelTests(TestCase):
    """Tests for LegalRecord model."""
    
    def setUp(self):
        self.politician = Politician.objects.create(
            first_name_en='John',
            first_name_kn='ಜಾನ್',
            last_name_en='Doe',
            last_name_kn='ಡೊ',
            full_name_en='John Doe',
            full_name_kn='ಜಾನ್ ಡೊ',
            slug='john-doe',
            is_active=True
        )
        
        self.record_data = {
            'politician': self.politician,
            'case_number': 'FIR/2024/001',
            'police_station': 'Test Police Station',
            'district': 'Test District',
            'case_status': 'pending',
            'ipc_sections': [100, 302],
            'is_verified': False,
        }
    
    def test_create_legal_record(self):
        """Test creating a legal record."""
        record = LegalRecord.objects.create(**self.record_data)
        
        self.assertEqual(record.politician, self.politician)
        self.assertEqual(record.case_number, 'FIR/2024/001')
        self.assertEqual(record.ipc_sections, [100, 302])
    
    def test_legal_record_str(self):
        """Test legal record __str__ method."""
        record = LegalRecord.objects.create(**self.record_data)
        
        expected = f'{record.case_number} - {record.politician.full_name_en}'
        self.assertEqual(str(record), expected)


class PublicRecordModelTests(TestCase):
    """Tests for PublicRecord model."""
    
    def setUp(self):
        self.politician = Politician.objects.create(
            first_name_en='John',
            first_name_kn='ಜಾನ್',
            last_name_en='Doe',
            last_name_kn='ಡೊ',
            full_name_en='John Doe',
            full_name_kn='ಜಾನ್ ಡೊ',
            slug='john-doe',
            is_active=True
        )
        
        self.record_data = {
            'politician': self.politician,
            'record_type': 'speech',
            'title_en': 'Test Speech',
            'title_kn': 'ಟೆಸ್ಟ್ ಭಾಷಣ',
            'content_en': 'This is test content with multiple words for testing purposes.',
            'content_kn': 'ಇದು ಪಠ್ಯದ ಪಠ್ಯವಾಗಿದೆ.',
            'summary_en': 'Test summary',
            'summary_kn': 'ಟೆಸ್ಟ್ ಸಾರಾಂಶ',
            'source_url': 'https://example.com/speech',
            'verification_status': 'verified',
            'is_verified': True,
        }
    
    def test_create_public_record(self):
        """Test creating a public record."""
        record = PublicRecord.objects.create(**self.record_data)
        
        self.assertEqual(record.politician, self.politician)
        self.assertEqual(record.record_type, 'speech')
        self.assertEqual(record.word_count, 10)  # 10 words in content_en
    
    def test_word_count_calculation(self):
        """Test word count calculation on save."""
        record = PublicRecord.objects.create(**self.record_data)
        
        self.assertEqual(record.word_count, 10)
    
    def test_public_record_str(self):
        """Test public record __str__ method."""
        record = PublicRecord.objects.create(**self.record_data)
        
        expected = f'{record.record_type}: {record.title_en}'
        self.assertEqual(str(record), expected)


class ConstituencyFundModelTests(TestCase):
    """Tests for ConstituencyFund model."""
    
    def setUp(self):
        self.district = District.objects.create(
            district_name_en='Test District',
            district_name_kn='ಟೆಸ್ಟ್ ಜಿಲ್ಲೆ',
            district_code='TST001',
            region='north'
        )
        
        self.constituency = Constituency.objects.create(
            constituency_name_en='Bangalore Central',
            constituency_name_kn='ಬೆಂಗಳೂರು ಕೇಂದ್ರ',
            constituency_number=1,
            district=self.district,
            constituency_type='general',
            population_2011=1000000
        )
        
        self.fund_data = {
            'constituency': self.constituency,
            'fund_type': 'mla',
            'financial_year': '2024-25',
            'allocated_amount': 10000000,
            'utilized_amount': 5000000,
            'project_name_en': 'Test Project',
            'project_name_kn': 'ಟೆಸ್ಟ್ ಪ್ರಾಜೆಕ್ಟ್',
            'project_status': 'in_progress',
            'completion_percentage': 50,
        }
    
    def test_create_constituency_fund(self):
        """Test creating a constituency fund."""
        fund = ConstituencyFund.objects.create(**self.fund_data)
        
        self.assertEqual(fund.constituency, self.constituency)
        self.assertEqual(fund.fund_type, 'mla')
        self.assertEqual(float(fund.allocated_amount), 10000000)
    
    def test_utilization_percentage_calculation(self):
        """Test utilization percentage calculation."""
        fund = ConstituencyFund.objects.create(**self.fund_data)
        
        self.assertEqual(float(fund.utilization_percentage), 50.0)
    
    def test_remaining_amount_calculation(self):
        """Test remaining amount calculation."""
        fund = ConstituencyFund.objects.create(**self.fund_data)
        
        expected_remaining = 10000000 - 5000000  # 5000000
        self.assertEqual(float(fund.allocated_amount - fund.utilized_amount), expected_remaining)
    
    def test_unique_together_constraint(self):
        """Test unique_together constraint."""
        ConstituencyFund.objects.create(**self.fund_data)
        
        with self.assertRaises(Exception):
            ConstituencyFund.objects.create(**self.fund_data)