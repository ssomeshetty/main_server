from django.test import TestCase
from politicians_tracker.apps.core.models import Politician, Party, Constituency, OfficeTenure, PartyMembership
from django.utils import timezone


class TemporalModelsTests(TestCase):
    def setUp(self):
        self.party = Party.objects.create(party_name_en="Test Party", party_short_name_en="TP", registration_number="REG01")
        self.party2 = Party.objects.create(party_name_en="Another Party", party_short_name_en="AP", registration_number="REG02")
        
        self.pol = Politician.objects.create(
            first_name_en="Jane",
            last_name_en="Doe",
            full_name_en="Jane Doe",
            slug="jane-doe",
            representative_type="mla",
            is_minister=True,
            minister_type="cabinet_minister",
            current_party=self.party
        )

    def test_office_tenure_creation_and_overlapping(self):
        # 1. OfficeTenure creation & 5. Overlapping MLA + Minister
        mla_tenure = OfficeTenure.objects.create(
            politician=self.pol,
            office_type="mla",
            office_title="Member of Legislative Assembly",
            is_current=True,
            is_verified=False
        )
        minister_tenure = OfficeTenure.objects.create(
            politician=self.pol,
            office_type="cabinet_minister",
            office_title="Minister of Magic",
            is_current=True,
            is_verified=False
        )
        
        # Ensure they both exist concurrently
        self.assertEqual(OfficeTenure.objects.filter(politician=self.pol, is_current=True).count(), 2)
        
        # 3. Nullable dates
        self.assertIsNone(mla_tenure.start_date)
        self.assertIsNone(mla_tenure.end_date)
        
        # 8. Missing source_url remains NULL
        self.assertIsNone(mla_tenure.source_url)
        
        # 9. unverified snapshot remains is_verified=False
        self.assertFalse(mla_tenure.is_verified)

    def test_party_membership_transitions(self):
        # 2. PartyMembership creation & 6. multiple party memberships
        past_membership = PartyMembership.objects.create(
            politician=self.pol,
            party=self.party2,
            is_current=False,
            is_verified=True,
            source_url="http://example.com/past-party",
            start_date=timezone.now().date(),
            end_date=timezone.now().date()
        )
        
        current_membership = PartyMembership.objects.create(
            politician=self.pol,
            party=self.party,
            is_current=True,
            is_verified=False
        )
        
        self.assertEqual(PartyMembership.objects.filter(politician=self.pol).count(), 2)
        self.assertTrue(current_membership.is_current)
        self.assertFalse(past_membership.is_current)

    def test_existing_politician_data_unchanged(self):
        # 10. existing Politician data remains unchanged
        pol = Politician.objects.get(id=self.pol.id)
        self.assertEqual(pol.representative_type, "mla")
        self.assertTrue(pol.is_minister)
        self.assertEqual(pol.current_party, self.party)
