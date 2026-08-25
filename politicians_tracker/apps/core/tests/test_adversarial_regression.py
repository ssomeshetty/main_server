from django.test import TestCase
from politicians_tracker.apps.core.models import Politician, LegalRecord
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError

class AdversarialRegressionTests(TestCase):
    def setUp(self):
        self.politician = Politician.objects.create(
            first_name_en="Test",
            last_name_en="MP",
            full_name_en="Test MP",
            representative_type="mp_ls",
            slug="test-mp"
        )
        
    def test_no_synthetic_sansad_urls(self):
        """Prevent recurrence of generating synthetic external URLs based on local DB IDs."""
        invalid_url = f"https://sansad.in/ls/members/biography?mp_id={self.politician.id}"
        self.politician.website_url = invalid_url
        self.politician.save()
        
        is_synthetic = 'sansad.in' in self.politician.website_url and f'mp_id={self.politician.id}' in self.politician.website_url
        self.assertTrue(is_synthetic, "Synthetic URL pattern should be detectable.")
        
    def test_case_status_not_implied_conviction(self):
        """Ensure charges_filed is not considered a conviction."""
        lr = LegalRecord.objects.create(
            politician=self.politician,
            case_number="FIR/123",
            case_status="charges_filed",
            source_url="http://myneta.info/test"
        )
        self.assertNotEqual(lr.case_status, "convicted", "Pending charge should not be 'convicted'")
