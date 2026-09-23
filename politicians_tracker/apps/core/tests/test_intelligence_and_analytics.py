from decimal import Decimal

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from ..intelligence_engine import PalantirIntelligenceEngine
from ..models import FinancialDeclaration
from .factories import PoliticianFactory


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'core-tests',
        },
        'sessions': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'core-session-tests',
        },
    },
    REST_FRAMEWORK={
        'DEFAULT_THROTTLE_CLASSES': [],
    },
)
class FinancialIntelligenceTests(TestCase):
    def test_missing_declarations_are_not_fabricated(self):
        politician = PoliticianFactory(is_active=True)

        report = PalantirIntelligenceEngine(politician).analyze_financial_trajectory()

        self.assertFalse(report['has_data'])
        self.assertIsNone(report['current_net_worth'])
        self.assertIsNone(report['cagr_pct'])
        self.assertEqual(report['data_status'], 'NO_RECORD_FOUND')

    def test_declining_assets_do_not_get_positive_fallback_growth(self):
        politician = PoliticianFactory(is_active=True)
        FinancialDeclaration.objects.create(
            politician=politician,
            declaration_year=2023,
            declaration_type='election',
            total_assets=Decimal('1000000'),
            total_liabilities=Decimal('100000'),
        )
        FinancialDeclaration.objects.create(
            politician=politician,
            declaration_year=2024,
            declaration_type='election',
            total_assets=Decimal('500000'),
            total_liabilities=Decimal('50000'),
        )

        report = PalantirIntelligenceEngine(politician).analyze_financial_trajectory()

        self.assertEqual(report['cagr_pct'], -50.0)
        self.assertEqual(report['asset_growth_factor'], '0.5x')
        self.assertEqual(report['current_net_worth'], 450000.0)


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'analytics-tests',
        },
        'sessions': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'analytics-session-tests',
        },
    },
    REST_FRAMEWORK={
        'DEFAULT_THROTTLE_CLASSES': [],
    },
)
class AnalyticsAggregationTests(TestCase):
    def test_summary_and_rankings_use_latest_declaration_once(self):
        politician = PoliticianFactory(is_active=True)
        FinancialDeclaration.objects.create(
            politician=politician,
            declaration_year=2023,
            declaration_type='election',
            total_assets=Decimal('10000000'),
            total_liabilities=Decimal('1000000'),
        )
        FinancialDeclaration.objects.create(
            politician=politician,
            declaration_year=2024,
            declaration_type='election',
            total_assets=Decimal('20000000'),
            total_liabilities=Decimal('2000000'),
        )

        response = APIClient().get('/api/v1/analytics/?lang=en')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['summary']['total_assembly_assets_cr'], 2.0)
        self.assertEqual(response.data['summary']['total_assembly_liabilities_cr'], 0.2)
        self.assertEqual(
            [item['id'] for item in response.data['top_richest']].count(politician.id),
            1,
        )