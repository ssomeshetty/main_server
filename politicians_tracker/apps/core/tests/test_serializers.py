"""
Serializer tests for the Karnataka Politicians Tracker.

Tests verify:
- Correct field serialization
- Bilingual field handling
- Computed fields
- Language parameter handling
"""
from django.test import TestCase

from ..models import (
    District, Constituency, Party, Politician,
    FinancialDeclaration, LegalRecord, PublicRecord, ConstituencyFund
)
from ..serializers import (
    DistrictSerializer, ConstituencySerializer, PartySerializer,
    PoliticianListSerializer, PoliticianDetailSerializer, FinancialDeclarationSerializer,
    LegalRecordSerializer, PublicRecordSerializer, ConstituencyFundSerializer
)


class DistrictSerializerTests(TestCase):
    """Tests for DistrictSerializer."""
    
    def setUp(self):
        self.district_data = {
            'id': 1,
            'district_name_en': 'Bangalore Urban',
            'district_name_kn': 'ಬೆಂಗಳೂರು ನಗರ',
            'district_code': 'BLR001',
            'region': 'bangalore',
            'area_sq_km': 219.36,
            'population_2011': 9308131,
        }
        self.district = District.objects.create(**self.district_data)
    
    def test_serialization(self):
        """Test that district serializes correctly."""
        serializer = DistrictSerializer(self.district)
        data = serializer.data
        
        self.assertEqual(data['id'], self.district.id)
        self.assertEqual(data['name'], self.district.district_name_en)
        self.assertEqual(data['district_code'], self.district.district_code)
        self.assertEqual(data['region'], self.district.region)
        self.assertEqual(float(data['area_sq_km']), float(self.district.area_sq_km))
        self.assertEqual(data['population_2011'], self.district.population_2011)
    
    def test_language_support(self):
        """Test that language parameter changes name field."""
        context = {'lang': 'kn'}
        serializer = DistrictSerializer(self.district, context=context)
        data = serializer.data
        
        self.assertEqual(data['name'], self.district.district_name_kn)


class ConstituencySerializerTests(TestCase):
    """Tests for ConstituencySerializer."""
    
    def setUp(self):
        self.district = District.objects.create(
            district_name_en='Test District',
            district_name_kn='ಟೆಸ್ಟ್ ಜಿಲ್ಲೆ',
            district_code='TST001',
            region='north'
        )
        
        self.constituency_data = {
            'id': 1,
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
        self.constituency = Constituency.objects.create(**self.constituency_data)
    
    def test_serialization(self):
        """Test that constituency serializes correctly."""
        serializer = ConstituencySerializer(self.constituency)
        data = serializer.data
        
        self.assertEqual(data['id'], self.constituency.id)
        self.assertEqual(data['name'], self.constituency.constituency_name_en)
        self.assertEqual(data['district'], self.constituency.district.id)
        self.assertEqual(data['constituency_type'], self.constituency.constituency_type)
    
    def test_nested_district(self):
        """Test that district is nested correctly."""
        serializer = ConstituencySerializer(self.constituency)
        data = serializer.data
        
        self.assertEqual(data['district_name'], self.district.district_name_en)
    
    def test_language_support(self):
        """Test that language parameter changes name fields."""
        context = {'lang': 'kn'}
        serializer = ConstituencySerializer(self.constituency, context=context)
        data = serializer.data
        
        self.assertEqual(data['name'], self.constituency.constituency_name_kn)
        self.assertEqual(data['district_name'], self.district.district_name_kn)


class PartySerializerTests(TestCase):
    """Tests for PartySerializer."""
    
    def setUp(self):
        self.party_data = {
            'party_name_en': 'Democratic Party',
            'party_name_kn': 'ಪ್ರಜಾಪ್ರಭುತ್ವ ಪಕ್ಷ',
            'party_short_name_en': 'DP',
            'party_short_name_kn': 'ಪ್ರಪ',
            'party_symbol': 'Hand',
            'party_type': 'state',
            'is_active': True,
        }
        self.party = Party.objects.create(**self.party_data)
    
    def test_serialization(self):
        """Test that party serializes correctly."""
        serializer = PartySerializer(self.party)
        data = serializer.data
        
        self.assertEqual(data['id'], self.party.id)
        self.assertEqual(data['name'], self.party.party_name_en)
        self.assertEqual(data['short_name'], self.party.party_short_name_en)
        self.assertEqual(data['party_type'], self.party.party_type)
        self.assertEqual(data['is_active'], self.party.is_active)
    
    def test_language_support(self):
        """Test that language parameter changes name fields."""
        context = {'lang': 'kn'}
        serializer = PartySerializer(self.party, context=context)
        data = serializer.data
        
        self.assertEqual(data['name'], self.party.party_name_kn)
        self.assertEqual(data['short_name'], self.party.party_short_name_kn)


class PoliticianSerializerTests(TestCase):
    """Tests for PoliticianSerializer."""
    
    def setUp(self):
        self.party = Party.objects.create(
            party_name_en='Democratic Party',
            party_name_kn='ಪ್ರಜಾಪ್ರಭುತ್ವ ಪಕ್ಷ',
            party_short_name_en='DP',
            party_short_name_kn='ಪ್ರಪ',
            party_type='state',
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
        self.politician = Politician.objects.create(**self.politician_data)
    
    def test_list_serialization(self):
        """Test that politician list serializer works."""
        serializer = PoliticianListSerializer(self.politician)
        data = serializer.data
        
        self.assertEqual(data['id'], self.politician.id)
        self.assertEqual(data['name'], self.politician.full_name_en)
        self.assertEqual(data['party_name'], self.party.party_name_en)
        self.assertEqual(data['constituency_name'], self.constituency.constituency_name_en)
    
    def test_detail_serialization(self):
        """Test that politician detail serializer works."""
        serializer = PoliticianDetailSerializer(self.politician)
        data = serializer.data
        
        self.assertEqual(data['id'], self.politician.id)
        self.assertEqual(data['name'], self.politician.full_name_en)
        self.assertEqual(data['full_name_en'], self.politician.full_name_en)
        self.assertEqual(data['total_terms_contested'], self.politician.total_terms_contested)
    
    def test_language_support(self):
        """Test that language parameter changes name fields."""
        context = {'lang': 'kn'}
        serializer = PoliticianDetailSerializer(self.politician, context=context)
        data = serializer.data
        
        self.assertEqual(data['name'], self.politician.full_name_kn)
        self.assertEqual(data['full_name_kn'], self.politician.full_name_kn)


class FinancialDeclarationSerializerTests(TestCase):
    """Tests for FinancialDeclarationSerializer."""
    
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
        self.declaration = FinancialDeclaration.objects.create(**self.declaration_data)
    
    def test_serialization(self):
        """Test that financial declaration serializes correctly."""
        serializer = FinancialDeclarationSerializer(self.declaration)
        data = serializer.data
        
        self.assertEqual(data['id'], self.declaration.id)
        self.assertEqual(data['politician'], self.politician.id)
        self.assertEqual(data['declaration_year'], self.declaration.declaration_year)
        self.assertEqual(float(data['total_assets']), float(self.declaration.total_assets))
        self.assertEqual(float(data['total_liabilities']), float(self.declaration.total_liabilities))
    
    def test_net_worth_calculation(self):
        """Test that net worth is calculated correctly."""
        serializer = FinancialDeclarationSerializer(self.declaration)
        data = serializer.data
        
        expected_net_worth = 10000000 - 2000000  # 8000000
        self.assertEqual(float(data['net_worth']), expected_net_worth)


class LegalRecordSerializerTests(TestCase):
    """Tests for LegalRecordSerializer."""
    
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
        self.record = LegalRecord.objects.create(**self.record_data)
    
    def test_serialization(self):
        """Test that legal record serializes correctly."""
        serializer = LegalRecordSerializer(self.record)
        data = serializer.data
        
        self.assertEqual(data['id'], self.record.id)
        self.assertEqual(data['politician'], self.politician.id)
        self.assertEqual(data['case_number'], self.record.case_number)
        self.assertEqual(data['case_status'], self.record.case_status)
        self.assertEqual(data['ipc_sections'], self.record.ipc_sections)


class PublicRecordSerializerTests(TestCase):
    """Tests for PublicRecordSerializer."""
    
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
            'content_en': 'This is test content.',
            'content_kn': 'ಇದು ಪಠ್ಯದ ಪಠ್ಯವಾಗಿದೆ.',
            'summary_en': 'Test summary',
            'summary_kn': 'ಟೆಸ್ಟ್ ಸಾರಾಂಶ',
            'source_url': 'https://example.com/speech',
            'verification_status': 'verified',
            'is_verified': True,
            'word_count': 10,
        }
        self.record = PublicRecord.objects.create(**self.record_data)
    
    def test_serialization(self):
        """Test that public record serializes correctly."""
        serializer = PublicRecordSerializer(self.record)
        data = serializer.data
        
        self.assertEqual(data['id'], self.record.id)
        self.assertEqual(data['politician'], self.politician.id)
        self.assertEqual(data['record_type'], self.record.record_type)
        self.assertEqual(data['title_en'], self.record.title_en)
        self.assertEqual(data['content_en'], self.record.content_en)
    
    def test_language_support(self):
        """Test that language parameter changes content fields."""
        context = {'lang': 'kn'}
        serializer = PublicRecordSerializer(self.record, context=context)
        data = serializer.data
        
        self.assertEqual(data['title_kn'], self.record.title_kn)
        self.assertEqual(data['content_kn'], self.record.content_kn)
        self.assertEqual(data['summary_kn'], self.record.summary_kn)


class ConstituencyFundSerializerTests(TestCase):
    """Tests for ConstituencyFundSerializer."""
    
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
        self.fund = ConstituencyFund.objects.create(**self.fund_data)
    
    def test_serialization(self):
        """Test that constituency fund serializes correctly."""
        serializer = ConstituencyFundSerializer(self.fund)
        data = serializer.data
        
        self.assertEqual(data['id'], self.fund.id)
        self.assertEqual(data['constituency'], self.constituency.id)
        self.assertEqual(data['fund_type'], self.fund.fund_type)
        self.assertEqual(float(data['allocated_amount']), float(self.fund.allocated_amount))
        self.assertEqual(float(data['utilized_amount']), float(self.fund.utilized_amount))
    
    def test_remaining_amount_calculation(self):
        """Test that remaining amount is calculated correctly."""
        serializer = ConstituencyFundSerializer(self.fund)
        data = serializer.data
        
        expected_remaining = 10000000 - 5000000  # 5000000
        self.assertEqual(float(data['remaining_amount']), expected_remaining)
    
    def test_utilization_percentage_calculation(self):
        """Test that utilization percentage is calculated correctly."""
        serializer = ConstituencyFundSerializer(self.fund)
        data = serializer.data
        
        self.assertEqual(float(data['utilization_percentage']), 50.0)