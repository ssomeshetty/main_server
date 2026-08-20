"""
API endpoint tests for the Karnataka Politicians Tracker.

These tests verify the correct behavior of all API endpoints with a focus on:
- Read-only operations (POST, PUT, PATCH, DELETE should return 405)
- Bilingual support (language parameter)
- Cursor pagination
- Query optimization (no N+1 queries)
"""
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .factories import (
    DistrictFactory, ConstituencyFactory, PartyFactory,
    PoliticianFactory, FinancialDeclarationFactory,
    LegalRecordFactory, PublicRecordFactory, ConstituencyFundFactory
)


class APIReadonlyTests(APITestCase):
    """Test that all write operations return 405 Method Not Allowed."""
    
    def test_politician_create_returns_405(self):
        """POST to politician list should return 405."""
        url = reverse('politician-list')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_politician_update_returns_405(self):
        """PUT to politician detail should return 405."""
        politician = PoliticianFactory()
        url = reverse('politician-detail', kwargs={'slug': politician.slug})
        response = self.client.put(url, {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_politician_patch_returns_405(self):
        """PATCH to politician detail should return 405."""
        politician = PoliticianFactory()
        url = reverse('politician-detail', kwargs={'slug': politician.slug})
        response = self.client.patch(url, {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_politician_delete_returns_405(self):
        """DELETE to politician detail should return 405."""
        politician = PoliticianFactory()
        url = reverse('politician-detail', kwargs={'slug': politician.slug})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_district_create_returns_405(self):
        """POST to district list should return 405."""
        url = reverse('district-list')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_constituency_create_returns_405(self):
        """POST to constituency list should return 405."""
        url = reverse('constituency-list')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class APILanguageSupportTests(APITestCase):
    """Test bilingual support via language parameter."""
    
    def setUp(self):
        self.party = PartyFactory(
            party_name_en="Democratic Party",
            party_name_kn="ಪ್ರಜಾಪ್ರಭುತ್ವ ಪಕ್ಷ",
            party_short_name_en="DP",
            party_short_name_kn="ಪ್ರಪ",
            is_active=True
        )
        self.district = DistrictFactory(
            district_name_en="Bangalore Urban",
            district_name_kn="ಬೆಂಗಳೂರು ನಗರ",
        )
        self.constituency = ConstituencyFactory(
            constituency_name_en="Bangalore Central",
            constituency_name_kn="ಬೆಂಗಳೂರು ಕೇಂದ್ರ",
            district=self.district
        )
        self.politician = PoliticianFactory(
            full_name_en="John Doe",
            full_name_kn="ಜಾನ್ ಡೊ",
            first_name_en="John",
            first_name_kn="ಜಾನ್",
            last_name_en="Doe",
            last_name_kn="ಡೊ",
            is_active=True,
            current_party=self.party,
            current_constituency=self.constituency
        )
    
    def test_politician_name_in_english(self):
        """Test politician name returns in English by default."""
        url = reverse('politician-detail', kwargs={'slug': self.politician.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "John Doe")
    
    def test_politician_name_in_kannada(self):
        """Test politician name returns in Kannada with lang=kn."""
        url = reverse('politician-detail', kwargs={'slug': self.politician.slug})
        response = self.client.get(url, {'lang': 'kn'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "ಜಾನ್ ಡೊ")
    
    def test_party_name_in_kannada(self):
        """Test party name returns in Kannada with lang=kn."""
        url = reverse('politician-detail', kwargs={'slug': self.politician.slug})
        response = self.client.get(url, {'lang': 'kn'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['party']['name'], "ಪ್ರಜಾಪ್ರಭುತ್ವ ಪಕ್ಷ")
    
    def test_constituency_name_in_kannada(self):
        """Test constituency name returns in Kannada with lang=kn."""
        url = reverse('politician-detail', kwargs={'slug': self.politician.slug})
        response = self.client.get(url, {'lang': 'kn'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['constituency']['name'], "ಬೆಂಗಳೂರು ಕೇಂದ್ರ")


class APICursorPaginationTests(APITestCase):
    """Test cursor-based pagination."""
    
    def setUp(self):
        # Create 50 politicians
        self.politicians = [PoliticianFactory() for _ in range(50)]
        
        # Create 50 constituencies
        self.constituencies = [ConstituencyFactory() for _ in range(50)]
    
    def test_default_page_size(self):
        """Test default page size is 20."""
        url = reverse('politician-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 20)
        self.assertIn('next', response.data)
    
    def test_custom_page_size(self):
        """Test custom page size parameter."""
        url = reverse('politician-list')
        response = self.client.get(url, {'page_size': 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)
    
    def test_max_page_size_enforced(self):
        """Test that max page size is enforced."""
        url = reverse('politician-list')
        response = self.client.get(url, {'page_size': 200})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data['results']), 100)
    
    def test_next_cursor_present(self):
        """Test that next cursor is present when more results exist."""
        url = reverse('politician-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data['next'])
    
    def test_prev_cursor_absent_on_first_page(self):
        """Test that previous cursor is absent on first page."""
        url = reverse('politician-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data['previous'])
    
    def test_pagination_no_count(self):
        """Test that cursor pagination doesn't return count."""
        url = reverse('politician-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('count', response.data)


class APIQueryOptimizationTests(APITestCase):
    """Test query optimization with select_related and prefetch_related."""
    
    def setUp(self):
        # Create related objects
        self.district = DistrictFactory()
        self.constituency = ConstituencyFactory(district=self.district)
        self.party = PartyFactory()
        
        # Create politician with related data
        self.politician = PoliticianFactory(
            current_party=self.party,
            current_constituency=self.constituency,
            is_active=True
        )
        
        # Create financial declarations
        self.financial_declarations = [
            FinancialDeclarationFactory(politician=self.politician, declaration_year=2018+i)
            for i in range(5)
        ]
        
        # Create legal records
        self.legal_records = [
            LegalRecordFactory(politician=self.politician)
            for _ in range(3)
        ]
        
        # Create public records
        self.public_records = [
            PublicRecordFactory(politician=self.politician)
            for _ in range(4)
        ]
    
    def test_politician_detail_no_nplus1(self):
        """Test that politician detail doesn't cause N+1 queries."""
        url = reverse('politician-detail', kwargs={'slug': self.politician.slug})
        
        from django.test.utils import CaptureQueriesContext
        from django.db import connection
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(len(queries), 10)
    
    def test_politician_list_no_nplus1(self):
        """Test that politician list doesn't cause N+1 queries."""
        url = reverse('politician-list')
        
        from django.test.utils import CaptureQueriesContext
        from django.db import connection
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(len(queries), 10)


class APIFilterTests(APITestCase):
    """Test filtering functionality."""
    
    def setUp(self):
        self.district1 = DistrictFactory()
        self.district2 = DistrictFactory()
        
        self.constituency1 = ConstituencyFactory(district=self.district1)
        self.constituency2 = ConstituencyFactory(district=self.district2)
        
        self.party1 = PartyFactory()
        self.party2 = PartyFactory()
        
        self.politician1 = PoliticianFactory(
            current_party=self.party1,
            current_constituency=self.constituency1,
            is_active=True,
            is_verified=True
        )
        
        self.politician2 = PoliticianFactory(
            current_party=self.party2,
            current_constituency=self.constituency2,
            is_active=False,
            is_verified=False
        )
    
    def test_filter_by_district(self):
        """Test filtering politicians by district."""
        url = reverse('politician-list')
        response = self.client.get(url, {'district': self.district1.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.politician1.pk)
    
    def test_filter_by_constituency(self):
        """Test filtering politicians by constituency."""
        url = reverse('politician-list')
        response = self.client.get(url, {'constituency': self.constituency1.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.politician1.pk)
    
    def test_filter_by_party(self):
        """Test filtering politicians by party."""
        url = reverse('politician-list')
        response = self.client.get(url, {'party': self.party1.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.politician1.pk)
    
    def test_filter_by_is_active(self):
        """Test filtering politicians by active status."""
        url = reverse('politician-list')
        response = self.client.get(url, {'is_active': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_search_politicians(self):
        """Test searching politicians by name."""
        url = reverse('politician-list')
        response = self.client.get(url, {'search': self.politician1.first_name_en[:3]})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)


class APIOrderingTests(APITestCase):
    """Test ordering functionality."""
    
    def setUp(self):
        self.politician1 = PoliticianFactory(total_terms_won=3, is_active=True)
        self.politician2 = PoliticianFactory(total_terms_won=5, is_active=True)
        self.politician3 = PoliticianFactory(total_terms_won=1, is_active=True)
    
    def test_order_by_name(self):
        """Test ordering by name."""
        url = reverse('politician-list')
        response = self.client.get(url, {'ordering': 'full_name_en'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [p['name'] for p in response.data['results']]
        self.assertEqual(names, sorted(names))
    
    def test_order_by_terms_won_descending(self):
        """Test ordering by terms_won descending."""
        url = reverse('politician-list')
        response = self.client.get(url, {'ordering': '-total_terms_won'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        terms = [p['total_terms_won'] for p in response.data['results']]
        self.assertEqual(terms, sorted(terms, reverse=True))

