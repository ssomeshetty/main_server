"""
Factory classes for generating test data using factory_boy.
"""
import factory
from factory.django import DjangoModelFactory
import random
from faker import Faker

fake = Faker()

from ..models import (
    District, Constituency, Party, Politician,
    FinancialDeclaration, LegalRecord, PublicRecord, ConstituencyFund
)


class DistrictFactory(DjangoModelFactory):
    """Factory for District model."""
    
    class Meta:
        model = District
    
    district_name_en = factory.Faker('city')
    district_name_kn = factory.LazyAttribute(lambda o: f'{o.district_name_en} ಜಿಲ್ಲೆ')
    district_code = factory.Sequence(lambda n: f'DST{n:03d}')
    region = factory.Iterator(['north', 'south', 'central', 'bangalore'])
    area_sq_km = factory.Faker('random_number', digits=5)
    population_2011 = factory.Faker('random_number', digits=6)


class ConstituencyFactory(DjangoModelFactory):
    """Factory for Constituency model."""
    
    class Meta:
        model = Constituency
    
    constituency_name_en = factory.Faker('city')
    constituency_name_kn = factory.LazyAttribute(lambda o: f'{o.constituency_name_en} ವಿಧಾನ ಮಂಡಲ')
    constituency_number = factory.Sequence(lambda n: n + 1)
    district = factory.SubFactory(DistrictFactory)
    constituency_type = factory.Iterator(['general', 'sc', 'st'])
    population_2011 = factory.Faker('random_number', digits=5)
    male_population = factory.LazyAttribute(lambda o: int(o.population_2011 * 0.52))
    female_population = factory.LazyAttribute(lambda o: int(o.population_2011 * 0.48))
    sex_ratio = factory.LazyAttribute(lambda o: round(o.female_population / o.male_population * 1000, 2))
    literacy_rate = factory.Faker('pyfloat', min_value=60, max_value=95)


class PartyFactory(DjangoModelFactory):
    """Factory for Party model."""
    
    class Meta:
        model = Party
    
    party_name_en = factory.Sequence(lambda n: f"{fake.company()} {n}")
    party_name_kn = factory.LazyAttribute(lambda o: f'{o.party_name_en} ಪಕ್ಷ')
    party_short_name_en = factory.Sequence(lambda n: f'P{n:04d}')
    party_short_name_kn = factory.LazyAttribute(lambda o: f'{o.party_short_name_en}ಕ')
    party_symbol = factory.Faker('word')
    party_type = factory.Iterator(['national', 'state', 'registered'])
    registration_number = factory.Sequence(lambda n: f'NCA{1000 + n}')
    is_active = factory.Faker('boolean')


class PoliticianFactory(DjangoModelFactory):
    """Factory for Politician model."""
    
    class Meta:
        model = Politician
    
    first_name_en = factory.Faker('first_name')
    first_name_kn = factory.LazyAttribute(lambda o: f'{o.first_name_en} ಕನ್ನಡ')
    last_name_en = factory.Faker('last_name')
    last_name_kn = factory.LazyAttribute(lambda o: f'{o.last_name_en} ಕನ್ನಡ')
    full_name_en = factory.LazyAttribute(lambda o: f'{o.first_name_en} {o.last_name_en}')
    full_name_kn = factory.LazyAttribute(lambda o: f'{o.first_name_kn} {o.last_name_kn}')
    slug = factory.LazyAttributeSequence(lambda o, n: f'{o.first_name_en.lower()}-{o.last_name_en.lower()}-{n}')
    date_of_birth = factory.Faker('date_of_birth', minimum_age=30, maximum_age=80)
    age = factory.Faker('random_int', min=30, max=80)
    gender = factory.Iterator(['male', 'female', 'other'])
    photo_url = factory.Faker('image_url', width=400, height=400)
    email = factory.Faker('email')
    phone = factory.Faker('phone_number')
    residence_address = factory.Faker('address')
    current_party = factory.SubFactory(PartyFactory)
    current_constituency = factory.SubFactory(ConstituencyFactory)
    constituency_history = factory.LazyAttribute(lambda o: [
        {'year': 2018, 'constituency': 'Old Constituency 1'},
        {'year': 2023, 'constituency': o.current_constituency.constituency_name_en}
    ])
    total_terms_contested = factory.Faker('random_int', min=1, max=5)
    total_terms_won = factory.LazyAttribute(lambda o: random.randint(0, o.total_terms_contested))
    terms_as_mla = factory.LazyAttribute(lambda o: random.randint(0, o.total_terms_won))
    terms_as_mlna = factory.LazyAttribute(lambda o: random.randint(0, o.total_terms_won))
    terms_as_mp = factory.Faker('random_int', min=0, max=2)
    terms_as_minister = factory.Faker('random_int', min=0, max=3)
    biography_en = factory.Faker('text', max_nb_chars=500)
    biography_kn = factory.LazyAttribute(lambda o: f'{o.biography_en} - ಕನ್ನಡ')
    facebook_url = factory.Faker('url')
    twitter_url = factory.Faker('url')
    instagram_url = factory.Faker('url')
    youtube_url = factory.Faker('url')
    linkedin_url = factory.Faker('url')
    website_url = factory.Faker('url')
    ec_candidate_id = factory.Sequence(lambda n: f'ECI{n:08d}')
    is_active = factory.Faker('boolean', chance_of_getting_true=80)
    is_verified = factory.Faker('boolean', chance_of_getting_true=30)


class FinancialDeclarationFactory(DjangoModelFactory):
    """Factory for FinancialDeclaration model."""
    
    class Meta:
        model = FinancialDeclaration
    
    politician = factory.SubFactory(PoliticianFactory)
    declaration_year = factory.Faker('random_int', min=2018, max=2024)
    declaration_type = factory.Iterator(['election', 'annual', 'appointment', 'other'])
    total_assets = factory.Faker('random_number', digits=10)
    total_liabilities = factory.LazyAttribute(lambda o: int(o.total_assets * 0.1))
    
    residential_property_count = factory.Faker('random_int', min=0, max=3)
    residential_property_value = factory.Faker('random_number', digits=8)
    commercial_property_count = factory.Faker('random_int', min=0, max=2)
    commercial_property_value = factory.Faker('random_number', digits=8)
    agricultural_land_acres = factory.Faker('pydecimal', left_digits=4, right_digits=2, positive=True)
    agricultural_land_value = factory.Faker('random_number', digits=8)
    
    bank_deposits = factory.Faker('random_number', digits=8)
    shares_and_securities = factory.Faker('random_number', digits=7)
    insurance_policies = factory.Faker('random_number', digits=7)
    loans_received = factory.Faker('random_number', digits=7)
    
    vehicles_count = factory.Faker('random_int', min=0, max=3)
    vehicles_value = factory.Faker('random_number', digits=6)
    jewelry_value = factory.Faker('random_number', digits=6)
    other_assets = factory.Faker('random_number', digits=6)
    
    personal_loans = factory.Faker('random_number', digits=7)
    business_loans = factory.Faker('random_number', digits=7)
    mortgage = factory.Faker('random_number', digits=7)
    other_liabilities = factory.Faker('random_number', digits=6)
    
    declaration_date = factory.Faker('date_between', start_date='-1y', end_date='today')
    declaration_url = factory.Faker('url')
    notes = factory.Faker('text', max_nb_chars=200)
    is_verified = factory.Faker('boolean', chance_of_getting_true=50)


class LegalRecordFactory(DjangoModelFactory):
    """Factory for LegalRecord model."""
    
    class Meta:
        model = LegalRecord
    
    politician = factory.SubFactory(PoliticianFactory)
    case_number = factory.Sequence(lambda n: f'FIR/{n:04d}/2024')
    police_station = factory.Faker('city')
    district = factory.LazyAttribute(lambda o: o.politician.current_constituency.district.district_name_en)
    fir_date = factory.Faker('date_between', start_date='-5y', end_date='today')
    registration_date = factory.LazyAttribute(lambda o: o.fir_date)
    case_status = factory.Iterator([
        'charges_filed', 'trial_in_progress', 'admitted', 'discharged',
        'acquitted', 'convicted', 'pending', 'withdrawn'
    ])
    ipc_sections = factory.LazyAttribute(lambda o: [
        random.randint(100, 400) for _ in range(random.randint(1, 3))
    ])
    other_sections = factory.LazyAttribute(lambda o: [
        random.randint(100, 500) for _ in range(random.randint(0, 2))
    ])
    description_en = factory.Faker('text', max_nb_chars=300)
    description_kn = factory.LazyAttribute(lambda o: f'{o.description_en} - ಕನ್ನಡ')
    court_name = factory.Faker('company')
    case_type = factory.LazyAttribute(lambda o: f'Criminal Case {random.randint(1, 100)}')
    case_url = factory.Faker('url')
    next_hearing_date = factory.Faker('date_between', start_date='today', end_date='+6m')
    is_verified = factory.Faker('boolean', chance_of_getting_true=40)


class PublicRecordFactory(DjangoModelFactory):
    """Factory for PublicRecord model."""
    
    class Meta:
        model = PublicRecord
    
    politician = factory.SubFactory(PoliticianFactory)
    record_type = factory.Iterator(['speech', 'statement', 'controversy', 'allegation', 'promise', 'bill_proposed', 'initiative'])
    title_en = factory.Faker('sentence', nb_words=6)
    title_kn = factory.LazyAttribute(lambda o: f'{o.title_en} - ಕನ್ನಡ')
    content_en = factory.Faker('text', max_nb_chars=1000)
    content_kn = factory.LazyAttribute(lambda o: f'{o.content_en} - ಕನ್ನಡ')
    summary_en = factory.Faker('text', max_nb_chars=200)
    summary_kn = factory.LazyAttribute(lambda o: f'{o.summary_en} - ಕನ್ನಡ')
    categories = factory.LazyAttribute(lambda o: [fake.word() for _ in range(3)])
    tags = factory.LazyAttribute(lambda o: [fake.word() for _ in range(5)])
    event_name = factory.Faker('sentence', nb_words=4)
    event_date = factory.Faker('date_between', start_date='-2y', end_date='today')
    location = factory.Faker('city')
    verification_status = factory.Iterator(['unverified', 'partially_verified', 'verified', 'false'])
    verification_details = factory.Faker('text', max_nb_chars=200)
    source_url = factory.Faker('url')
    source_organization = factory.Faker('company')
    is_verified = factory.LazyAttribute(lambda o: o.verification_status in ['verified', 'partially_verified'])
    verified_by = factory.LazyAttribute(lambda o: fake.name() if o.is_verified else '')
    verification_date = factory.LazyAttribute(lambda o: fake.date_between(start_date='-1y', end_date='today') if o.is_verified else None)
    sentiment_score = factory.Faker('pyfloat', min_value=-1, max_value=1)
    word_count = factory.LazyAttribute(lambda o: len(o.content_en.split()))
    language = factory.Iterator(['en', 'kn', 'mixed'])


class ConstituencyFundFactory(DjangoModelFactory):
    """Factory for ConstituencyFund model."""
    
    class Meta:
        model = ConstituencyFund
    
    constituency = factory.SubFactory(ConstituencyFactory)
    fund_type = factory.Iterator(['mla', 'mllp', 'central', 'other'])
    financial_year = factory.Iterator(['2024-25', '2023-24', '2022-23', '2021-22', '2020-21'])
    allocated_amount = factory.Faker('random_number', digits=8)
    allocated_date = factory.Faker('date_between', start_date='-1y', end_date='today')
    utilized_amount = factory.LazyAttribute(lambda o: int(o.allocated_amount * random.uniform(0.3, 0.9)))
    utilization_date = factory.Faker('date_between', start_date='-1y', end_date='today')
    utilization_percentage = factory.LazyAttribute(lambda o: round((o.utilized_amount / o.allocated_amount) * 100, 2))
    project_name_en = factory.Faker('sentence', nb_words=5)
    project_name_kn = factory.LazyAttribute(lambda o: f'{o.project_name_en} - ಕನ್ನಡ')
    project_description_en = factory.Faker('text', max_nb_chars=500)
    project_description_kn = factory.LazyAttribute(lambda o: f'{o.project_description_en} - ಕನ್ನಡ')
    implementing_agency = factory.Faker('company')
    contractor_name = factory.Faker('name')
    project_status = factory.Iterator(['planned', 'in_progress', 'completed', 'halted', 'cancelled'])
    completion_percentage = factory.LazyAttribute(lambda o: 100 if o.project_status == 'completed' else random.randint(10, 90))
    fund_source_url = factory.Faker('url')
    utilization_url = factory.Faker('url')
    notes = factory.Faker('text', max_nb_chars=200)