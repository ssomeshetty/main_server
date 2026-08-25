from django.test import TestCase
from politicians_tracker.apps.core.models import Politician, FinancialDeclaration, ElectionResult, LegalRecord
from politicians_tracker.apps.core.intelligence_engine import PoliticalAnalyticsEngine

class PoliticalAnalyticsEngineTests(TestCase):
    def setUp(self):
        self.politician = Politician.objects.create(
            first_name_en="Test",
            last_name_en="MP",
            full_name_en="Test MP",
            representative_type="mp_ls",
            slug="test-mp",
            total_terms_won=2,
            terms_as_mla=1,
            terms_as_mp=1
        )

    def test_financial_trajectory_no_data(self):
        """Test financial analysis when no declarations exist."""
        engine = PoliticalAnalyticsEngine(self.politician)
        financial = engine.analyze_financial_trajectory()
        self.assertEqual(financial['state'], 'NO_DATA')
        self.assertIsNone(financial['cagr_pct'])
        self.assertIsNone(financial['asset_growth_factor'])
        self.assertFalse(financial['has_multi_year_history'])

    def test_financial_trajectory_single_declaration(self):
        """Test financial analysis when only one declaration exists."""
        FinancialDeclaration.objects.create(
            politician=self.politician,
            declaration_year=2023,
            total_assets=100000000,
            total_liabilities=10000000
        )
        engine = PoliticalAnalyticsEngine(self.politician)
        financial = engine.analyze_financial_trajectory()
        self.assertEqual(financial['state'], 'SINGLE_DECLARATION')
        self.assertIsNone(financial['cagr_pct'])
        self.assertIsNone(financial['asset_growth_factor'])
        self.assertFalse(financial['has_multi_year_history'])

    def test_financial_trajectory_multi_year_data(self):
        """Test financial analysis when multiple declarations exist."""
        FinancialDeclaration.objects.create(
            politician=self.politician,
            declaration_year=2018,
            total_assets=50000000,
            total_liabilities=5000000
        )
        FinancialDeclaration.objects.create(
            politician=self.politician,
            declaration_year=2023,
            total_assets=100000000,
            total_liabilities=10000000
        )
        engine = PoliticalAnalyticsEngine(self.politician)
        financial = engine.analyze_financial_trajectory()
        self.assertEqual(financial['state'], 'MULTI_YEAR_DATA')
        self.assertEqual(financial['cagr_pct'], 14.9)  # (100/50)^(1/5) - 1 = 14.869% -> 14.9%
        self.assertEqual(financial['asset_growth_factor'], '2.0x')
        self.assertTrue(financial['has_multi_year_history'])

    def test_electoral_competitiveness_no_data(self):
        """Test HECI when no election results exist."""
        engine = PoliticalAnalyticsEngine(self.politician)
        heci = engine.analyze_electoral_competitiveness()
        self.assertIsNone(heci)

    def test_electoral_competitiveness_data(self):
        """Test HECI with valid election results."""
        ElectionResult.objects.create(
            politician=self.politician,
            election_year=2023,
            total_votes_polled=200000,
            votes_secured=100000,
            runner_up_votes=80000,
            vote_percentage=50.0,
            runner_up_vote_pct=40.0,
            margin_votes=20000,
            is_winner=True
        )
        
        # margin = 20000 / 200000 = 10%
        engine = PoliticalAnalyticsEngine(self.politician)
        heci = engine.analyze_electoral_competitiveness()
        
        self.assertEqual(heci['competitiveness_score'], 60) # 10% * 4 = 40 penalty -> 60 score
        self.assertEqual(heci['margin_pct'], 10.00)
        self.assertEqual(heci['competitiveness_category'], 'COMPETITIVE')

    def test_electoral_competitiveness_loss(self):
        # Politician lost the election, we do not have the winner's votes in this row
        ElectionResult.objects.create(
            politician=self.politician,
            election_year=2018,
            votes_secured=4000,
            runner_up_votes=4000, # even if this is populated, it doesn't represent the winner
            total_votes_polled=10000,
            is_winner=False
        )
        
        engine = PoliticalAnalyticsEngine(self.politician)
        heci = engine.analyze_electoral_competitiveness()
        self.assertIsNone(heci) # Should return None if required data to calculate actual margin is missing

    def test_provenance_block(self):
        # 11. no fabricated URLs, 12. no fabricated dates
        # 13. no fabricated retrieval timestamps
        from politicians_tracker.apps.core.models import FinancialDeclaration, ElectionResult
        
        # Setup data for provenance test
        FinancialDeclaration.objects.create(
            politician=self.politician,
            declaration_year=2023,
            total_assets=500,
            is_verified=False
        )
        ElectionResult.objects.create(
            politician=self.politician,
            election_year=2023,
            is_verified=False
        )
        
        engine = PoliticalAnalyticsEngine(self.politician)
        report = engine.get_full_report()
        
        prov = report['provenance']
        self.assertIn('financial_trajectory', prov)
        self.assertIn('historical_electoral_competitiveness', prov)
        
        fin_prov = prov['financial_trajectory']
        self.assertEqual(fin_prov['earliest_declaration_year'], 2023)
        self.assertEqual(fin_prov['latest_declaration_year'], 2023)
        self.assertEqual(fin_prov['verification_status'], 'UNVERIFIED') # the setup didn't set is_verified=True
        self.assertIsNone(fin_prov['retrieved_at'])
        self.assertIsNone(fin_prov['last_verified'])
        
        heci_prov = prov['historical_electoral_competitiveness']
        self.assertEqual(heci_prov['based_on_election'], 2023)
        self.assertIsNone(heci_prov['source_url'])
        self.assertEqual(heci_prov['verification_status'], 'UNVERIFIED')

    def test_institutional_seniority(self):
        """Test ISI bounds and values."""
        engine = PoliticalAnalyticsEngine(self.politician)
        isi = engine.analyze_institutional_seniority()
        self.assertEqual(isi['total_terms'], 2)
        # mp_ls -> executive_weight 65. seniority_score = min(100, 2 * 20) = 40.
        # score = 0.60 * 65 + 0.40 * 40 = 39 + 16 = 55
        self.assertEqual(isi['seniority_score'], 55)

    def test_legal_records_summary(self):
        # Test legal summary
        LegalRecord.objects.create(
            politician=self.politician,
            case_number='FIR 123',
            case_status='Pending Investigation'
        )
        LegalRecord.objects.create(
            politician=self.politician,
            case_number='CC 456',
            case_status='Acquitted by High Court'
        )
        LegalRecord.objects.create(
            politician=self.politician,
            case_number='SC 789',
            case_status='Convicted'
        )
        
        engine = PoliticalAnalyticsEngine(self.politician)
        report = engine.get_full_report()
        legal = report['legal_summary']
        
        self.assertEqual(legal['total_cases'], 3)
        self.assertEqual(legal['pending_cases'], 1)
        self.assertEqual(legal['acquittals'], 1)
        self.assertEqual(legal['convictions'], 1)
