from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class TimestampMixin(models.Model):
    """Abstract base model for created_at and updated_at timestamps."""
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# =============================================================================
# District and Constituency
# =============================================================================

class District(models.Model):
    """
    District model with bilingual support.
    Karnataka has 31 districts as of 2024.
    """
    district_name_en = models.CharField(
        max_length=100,
        verbose_name=_('District Name (English)'),
        db_index=True
    )
    district_name_kn = models.CharField(
        max_length=100,
        verbose_name=_('District Name (Kannada)')
    )
    district_code = models.CharField(
        max_length=10,
        unique=True,
        verbose_name=_('District Code')
    )
    region = models.CharField(
        max_length=50,
        choices=[
            ('north', _('North Karnataka')),
            ('south', _('South Karnataka')),
            ('central', _('Central Karnataka')),
            ('bangalore', _('Bangalore Region')),
        ],
        db_index=True,
        verbose_name=_('Region')
    )
    area_sq_km = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Area (Sq Km)')
    )
    population_2011 = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Population (2011 Census)')
    )

    class Meta:
        verbose_name = _('District')
        verbose_name_plural = _('Districts')
        ordering = ['district_name_en']
        indexes = [
            # district_name_en already has db_index=True — only add kn and composites
            models.Index(fields=['district_name_kn']),
            models.Index(fields=['district_code']),
        ]

    def __str__(self):
        return self.district_name_en


class Constituency(models.Model):
    """
    Legislative Assembly Constituency with bilingual support.
    Karnataka has 224 assembly constituencies.
    """
    constituency_name_en = models.CharField(
        max_length=150,
        verbose_name=_('Constituency Name (English)'),
        db_index=True
    )
    constituency_name_kn = models.CharField(
        max_length=150,
        verbose_name=_('Constituency Name (Kannada)')
    )
    constituency_number = models.PositiveSmallIntegerField(
        verbose_name=_('Constituency Number')
    )
    district = models.ForeignKey(
        District,
        on_delete=models.PROTECT,
        related_name='constituencies',
        verbose_name=_('District')
    )
    constituency_type = models.CharField(
        max_length=20,
        choices=[
            ('general', _('General')),
            ('sc', _('Scheduled Caste')),
            ('st', _('Scheduled Tribe')),
        ],
        db_index=True,
        verbose_name=_('Constituency Type')
    )
    population_2011 = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Population (2011 Census)')
    )
    male_population = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Male Population')
    )
    female_population = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Female Population')
    )
    sex_ratio = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Sex Ratio (per 1000 males)')
    )
    literacy_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Literacy Rate (%)')
    )
    
    # Official Census 2011 Religion & Community Demographics (%)
    pop_hindu_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Hindu Population (%)')
    )
    pop_muslim_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Muslim Population (%)')
    )
    pop_christian_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Christian Population (%)')
    )
    pop_jain_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Jain Population (%)')
    )
    pop_buddhist_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Buddhist Population (%)')
    )
    pop_sikh_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Sikh Population (%)')
    )
    pop_sc_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Scheduled Caste Population (%)')
    )
    pop_st_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Scheduled Tribe Population (%)')
    )

    class Meta:
        verbose_name = _('Constituency')
        verbose_name_plural = _('Constituencies')
        ordering = ['constituency_number']
        indexes = [
            # constituency_name_en already has db_index=True — only add kn and composites
            models.Index(fields=['constituency_name_kn']),
            # Composite index for common filter: district + type
            models.Index(fields=['district', 'constituency_type']),
        ]

    def __str__(self):
        return self.constituency_name_en


# =============================================================================
# Politician
# =============================================================================

class Politician(models.Model):
    """
    Politician profile with bilingual support.
    Optimized for read-heavy workloads with denormalized term counts.
    """
    first_name_en = models.CharField(
        max_length=100,
        verbose_name=_('First Name (English)'),
        db_index=True
    )
    first_name_kn = models.CharField(
        max_length=100,
        verbose_name=_('First Name (Kannada)')
    )
    last_name_en = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Last Name (English)')
    )
    last_name_kn = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Last Name (Kannada)')
    )
    full_name_en = models.CharField(
        max_length=255,
        verbose_name=_('Full Name (English)'),
        db_index=True
    )
    full_name_kn = models.CharField(
        max_length=255,
        verbose_name=_('Full Name (Kannada)')
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name=_('Slug')
    )
    
    # Basic Info
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Date of Birth')
    )
    age = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Age')
    )
    gender = models.CharField(
        max_length=10,
        choices=[
            ('male', _('Male')),
            ('female', _('Female')),
            ('other', _('Other')),
        ],
        null=True,
        blank=True,
        verbose_name=_('Gender')
    )
    photo_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name=_('Photo URL')
    )
    
    # Contact Info
    email = models.EmailField(
        blank=True,
        verbose_name=_('Email')
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Phone')
    )
    residence_address = models.TextField(
        blank=True,
        verbose_name=_('Residence Address')
    )
    
    # Political Info
    current_party = models.ForeignKey(
        'Party',
        on_delete=models.PROTECT,
        related_name='current_politicians',
        null=True,
        blank=True,
        verbose_name=_('Current Party')
    )
    current_constituency = models.ForeignKey(
        Constituency,
        on_delete=models.PROTECT,
        related_name='current_politicians',
        null=True,
        blank=True,
        verbose_name=_('Current Constituency')
    )
    constituency_history = models.JSONField(
        blank=True,
        default=list,
        verbose_name=_('Constituency History (JSON)')
    )
    
    # Denormalized counts for performance
    total_terms_contested = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_('Total Terms Contested')
    )
    total_terms_won = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_('Total Terms Won')
    )
    terms_as_mla = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_('Terms as MLA')
    )
    terms_as_mlna = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_('Terms as MLNA')
    )
    terms_as_mp = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_('Terms as MP')
    )
    terms_as_minister = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_('Terms as Minister')
    )
    
    # Cabinet & Executive Position
    is_minister = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_('Is Minister')
    )
    MINISTER_TYPE_CHOICES = (
        ('cm', _('Chief Minister')),
        ('deputy_cm', _('Deputy Chief Minister')),
        ('cabinet_minister', _('Cabinet Minister')),
        ('minister_of_state', _('Minister of State')),
    )
    minister_type = models.CharField(
        max_length=30,
        choices=MINISTER_TYPE_CHOICES,
        blank=True,
        verbose_name=_('Minister Type')
    )
    minister_title_en = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Minister Title (English)')
    )
    minister_title_kn = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Minister Title (Kannada)')
    )
    portfolio_en = models.TextField(
        blank=True,
        verbose_name=_('Portfolio Description (English)')
    )
    portfolio_kn = models.TextField(
        blank=True,
        verbose_name=_('Portfolio Description (Kannada)')
    )
    
    # Parliamentary & Representative Type Info
    REPRESENTATIVE_TYPE_CHOICES = (
        ('mla', _('Member of Legislative Assembly (MLA)')),
        ('mp_ls', _('Member of Parliament - Lok Sabha (MP)')),
        ('mp_rs', _('Member of Parliament - Rajya Sabha (MP)')),
    )
    representative_type = models.CharField(
        max_length=20,
        choices=REPRESENTATIVE_TYPE_CHOICES,
        default='mla',
        db_index=True,
        verbose_name=_('Representative Type')
    )
    parliamentary_constituency_en = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Parliamentary Constituency (English)')
    )
    parliamentary_constituency_kn = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Parliamentary Constituency (Kannada)')
    )
    
    # Union Cabinet (Central Government) Position
    is_union_minister = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_('Is Union Minister')
    )
    union_title_en = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Union Minister Title (English)')
    )
    union_title_kn = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Union Minister Title (Kannada)')
    )
    union_portfolio_en = models.TextField(
        blank=True,
        verbose_name=_('Union Portfolio (English)')
    )
    union_portfolio_kn = models.TextField(
        blank=True,
        verbose_name=_('Union Portfolio (Kannada)')
    )
    
    # Biographies
    biography_en = models.TextField(
        blank=True,
        verbose_name=_('Biography (English)')
    )
    biography_kn = models.TextField(
        blank=True,
        verbose_name=_('Biography (Kannada)')
    )
    
    # Social Media Links
    facebook_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name=_('Facebook URL')
    )
    twitter_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name=_('Twitter/X URL')
    )
    instagram_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name=_('Instagram URL')
    )
    youtube_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name=_('YouTube URL')
    )
    linkedin_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name=_('LinkedIn URL')
    )
    website_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name=_('Personal Website')
    )
    
    # Election Commission ID
    ec_candidate_id = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name=_('Election Commission Candidate ID')
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_('Is Active')
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_('Is Verified')
    )

    class Meta:
        verbose_name = _('Politician')
        verbose_name_plural = _('Politicians')
        ordering = ['full_name_en']
        indexes = [
            # full_name_en and first_name_en already have db_index=True
            models.Index(fields=['full_name_kn']),
            # Composite indexes for common queries
            models.Index(fields=['current_party', 'is_active']),
            models.Index(fields=['current_constituency', 'is_active']),
            models.Index(fields=['first_name_en', 'last_name_en']),
        ]

    def __str__(self):
        return self.full_name_en

    def save(self, *args, **kwargs):
        """Generate full name from first and last name if not provided."""
        if not self.full_name_en and self.first_name_en:
            self.full_name_en = f"{self.first_name_en} {self.last_name_en or ''}".strip()
        if not self.full_name_kn and self.first_name_kn:
            self.full_name_kn = f"{self.first_name_kn} {self.last_name_kn or ''}".strip()
        super().save(*args, **kwargs)


class Party(models.Model):
    """
    Political Party model with bilingual support.
    """
    party_name_en = models.CharField(
        max_length=150,
        unique=True,
        verbose_name=_('Party Name (English)')
    )
    party_name_kn = models.CharField(
        max_length=150,
        verbose_name=_('Party Name (Kannada)')
    )
    party_short_name_en = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('Short Name (English)')
    )
    party_short_name_kn = models.CharField(
        max_length=50,
        verbose_name=_('Short Name (Kannada)')
    )
    party_symbol = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Party Symbol')
    )
    party_symbol_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name=_('Party Symbol URL')
    )
    party_type = models.CharField(
        max_length=20,
        choices=[
            ('national', _('National Party')),
            ('state', _('State Party')),
            ('registered', _('Registered Party')),
        ],
        default='registered',
        verbose_name=_('Party Type')
    )
    registration_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('Registration Number')
    )
    date_of_registration = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Date of Registration')
    )
    president_name_en = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('President Name (English)')
    )
    president_name_kn = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('President Name (Kannada)')
    )
    headquarters_address = models.TextField(
        blank=True,
        verbose_name=_('Headquarters Address')
    )
    official_website = models.URLField(
        max_length=500,
        blank=True,
        verbose_name=_('Official Website')
    )
    facebook_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name=_('Facebook Page URL')
    )
    twitter_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name=_('Twitter Page URL')
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_('Is Active')
    )

    class Meta:
        verbose_name = _('Party')
        verbose_name_plural = _('Parties')
        ordering = ['party_name_en']
        indexes = [
            models.Index(fields=['party_name_en']),
            models.Index(fields=['party_name_kn']),
            models.Index(fields=['party_short_name_en']),
            models.Index(fields=['party_short_name_kn']),
            models.Index(fields=['party_type']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.party_name_en


# =============================================================================
# Financial Declaration
# =============================================================================

class FinancialDeclaration(models.Model):
    """
    Financial declarations (assets and liabilities) by politicians.
    Optimized for filtering by politician and year.
    """
    politician = models.ForeignKey(
        Politician,
        on_delete=models.CASCADE,
        related_name='financial_declarations',
        verbose_name=_('Politician')
    )
    declaration_year = models.PositiveSmallIntegerField(
        verbose_name=_('Declaration Year'),
        db_index=True
    )
    declaration_type = models.CharField(
        max_length=20,
        choices=[
            ('election', _('Election Declaration')),
            ('annual', _('Annual Declaration')),
            ('appointment', _('Appointment Declaration')),
            ('other', _('Other')),
        ],
        db_index=True,
        verbose_name=_('Declaration Type')
    )
    
    # Assets - Current Value (in Rupees)
    total_assets = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        verbose_name=_('Total Assets')
    )
    
    # Real Estate
    residential_property_count = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_('Residential Property Count')
    )
    residential_property_value = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        verbose_name=_('Residential Property Value')
    )
    commercial_property_count = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_('Commercial Property Count')
    )
    commercial_property_value = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        verbose_name=_('Commercial Property Value')
    )
    agricultural_land_acres = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('Agricultural Land (Acres)')
    )
    agricultural_land_value = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        verbose_name=_('Agricultural Land Value')
    )
    
    # Financial Assets
    bank_deposits = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        verbose_name=_('Bank Deposits')
    )
    shares_and_securities = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        verbose_name=_('Shares and Securities')
    )
    insurance_policies = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        verbose_name=_('Insurance Policies')
    )
    loans_received = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        verbose_name=_('Loans Received')
    )
    
    # Personal Property
    vehicles_count = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_('Vehicle Count')
    )
    vehicles_value = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        verbose_name=_('Vehicle Value')
    )
    jewelry_value = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        verbose_name=_('Jewelry Value')
    )
    other_assets = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        verbose_name=_('Other Assets')
    )
    
    # Liabilities
    total_liabilities = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        verbose_name=_('Total Liabilities')
    )
    
    # Personal Liabilities
    personal_loans = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        verbose_name=_('Personal Loans')
    )
    business_loans = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        verbose_name=_('Business Loans')
    )
    mortgage = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        verbose_name=_('Mortgage')
    )
    other_liabilities = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        verbose_name=_('Other Liabilities')
    )
    
    # Declaration Details
    declaration_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Declaration Date')
    )
    declaration_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name=_('Declaration URL')
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notes')
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_('Is Verified')
    )

    class Meta:
        verbose_name = _('Financial Declaration')
        verbose_name_plural = _('Financial Declarations')
        ordering = ['-declaration_year', 'politician']
        indexes = [
            models.Index(fields=['politician', 'declaration_year']),
            models.Index(fields=['declaration_year']),
            models.Index(fields=['declaration_type']),
            models.Index(fields=['politician', 'declaration_type']),
            models.Index(fields=['is_verified']),
        ]
        unique_together = ['politician', 'declaration_year', 'declaration_type']

    def __str__(self):
        return f"{self.politician.full_name_en} - {self.declaration_year}"

    def calculate_net_worth(self):
        """Calculate net worth: Total Assets - Total Liabilities"""
        return self.total_assets - self.total_liabilities

    @property
    def net_worth(self):
        """Property to expose net worth to Django REST Framework serializers"""
        return self.calculate_net_worth()


# =============================================================================
# Legal Record
# =============================================================================

class LegalRecord(models.Model):
    """
    Criminal cases and legal records against politicians.
    Optimized for filtering by politician, case status, and IPC sections.
    """
    POLICE_STATION_CHOICES = [
        # Karnataka police stations will be populated from data
    ]
    
    CASE_STATUS_CHOICES = [
        ('charges_filed', _('Charges Filed')),
        ('trial_in_progress', _('Trial in Progress')),
        ('admitted', _('Admitted')),
        ('discharged', _('Discharged')),
        ('acquitted', _('Acquitted')),
        ('convicted', _('Convicted')),
        ('pending', _('Pending')),
        ('withdrawn', _('Withdrawn')),
    ]
    
    politician = models.ForeignKey(
        Politician,
        on_delete=models.CASCADE,
        related_name='legal_records',
        verbose_name=_('Politician')
    )
    case_number = models.CharField(
        max_length=100,
        verbose_name=_('FIR/Case Number')
    )
    police_station = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Police Station')
    )
    district = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('District')
    )
    
    # Case Details
    fir_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('FIR Date')
    )
    registration_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Registration Date')
    )
    case_status = models.CharField(
        max_length=30,
        choices=CASE_STATUS_CHOICES,
        default='pending',
        db_index=True,
        verbose_name=_('Case Status')
    )
    
    # IPC Sections (JSON array for flexibility)
    ipc_sections = models.JSONField(
        default=list,
        verbose_name=_('IPC Sections')
    )
    other_sections = models.JSONField(
        default=list,
        verbose_name=_('Other Sections (CrPC, SAJS, etc.)')
    )
    
    # Description
    description_en = models.TextField(
        blank=True,
        verbose_name=_('Description (English)')
    )
    description_kn = models.TextField(
        blank=True,
        verbose_name=_('Description (Kannada)')
    )
    
    # Court Information
    court_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Court Name')
    )
    case_type = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Case Type')
    )
    case_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name=_('Case URL')
    )
    next_hearing_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Next Hearing Date')
    )
    
    # Outcome
    conviction_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Conviction Date')
    )
    sentence_details = models.TextField(
        blank=True,
        verbose_name=_('Sentence Details')
    )
    fine_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Fine Amount')
    )
    imprisonment_years = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_('Imprisonment (Years)')
    )
    imprisonment_months = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_('Imprisonment (Months)')
    )
    
    # Source Information
    source_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name=_('Source URL')
    )
    source_organization = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Source Organization')
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_('Is Verified')
    )
    verification_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Verification Date')
    )

    class Meta:
        verbose_name = _('Legal Record')
        verbose_name_plural = _('Legal Records')
        ordering = ['-fir_date', 'politician']
        indexes = [
            models.Index(fields=['politician']),
            models.Index(fields=['case_status']),
            models.Index(fields=['district']),
            models.Index(fields=['police_station']),
            models.Index(fields=['ipc_sections'], name='legal_record_ipc_sections_idx'),
            models.Index(fields=['next_hearing_date']),
            models.Index(fields=['is_verified']),
            # Composite index for common queries
            models.Index(fields=['politician', 'case_status']),
            models.Index(fields=['case_status', 'district']),
        ]

    def __str__(self):
        return f"{self.case_number} - {self.politician.full_name_en}"


# =============================================================================
# Public Record
# =============================================================================

class PublicRecord(TimestampMixin, models.Model):
    """
    LLM-purified summaries of speeches, controversies, and allegations.
    Optimized for full-text search and categorization.
    """
    RECORD_TYPE_CHOICES = [
        ('speech', _('Speech')),
        ('statement', _('Statement')),
        ('controversy', _('Controversy')),
        ('allegation', _('Allegation')),
        ('promise', _('Promise/Pledge')),
        ('bill_proposed', _('Bill Proposed')),
        ('initiative', _('Initiative')),
        ('other', _('Other')),
    ]
    
    VERIFICATION_STATUS_CHOICES = [
        ('unverified', _('Unverified')),
        ('partially_verified', _('Partially Verified')),
        ('verified', _('Verified')),
        ('false', _('False/Unfounded')),
    ]
    
    politician = models.ForeignKey(
        Politician,
        on_delete=models.CASCADE,
        related_name='public_records',
        verbose_name=_('Politician')
    )
    record_type = models.CharField(
        max_length=30,
        choices=RECORD_TYPE_CHOICES,
        db_index=True,
        verbose_name=_('Record Type')
    )
    
    # Title and Content (Bilingual)
    title_en = models.CharField(
        max_length=500,
        verbose_name=_('Title (English)')
    )
    title_kn = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_('Title (Kannada)')
    )
    content_en = models.TextField(
        verbose_name=_('Content (English)')
    )
    content_kn = models.TextField(
        blank=True,
        verbose_name=_('Content (Kannada)')
    )
    
    # Summary (LLM-purified)
    summary_en = models.TextField(
        blank=True,
        verbose_name=_('Summary (English)')
    )
    summary_kn = models.TextField(
        blank=True,
        verbose_name=_('Summary (Kannada)')
    )
    
    # Categories and Tags
    categories = models.JSONField(
        default=list,
        verbose_name=_('Categories')
    )
    tags = models.JSONField(
        default=list,
        verbose_name=_('Tags')
    )
    
    # Context
    event_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Event Name')
    )
    event_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Event Date')
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Location')
    )
    
    # Verification
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default='unverified',
        db_index=True,
        verbose_name=_('Verification Status')
    )
    verification_details = models.TextField(
        blank=True,
        verbose_name=_('Verification Details')
    )
    
    # Source Information
    source_url = models.URLField(
        max_length=500,
        verbose_name=_('Source URL')
    )
    source_organization = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Source Organization')
    )
    is_verified = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_('Is Verified')
    )
    verified_by = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Verified By')
    )
    verification_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Verification Date')
    )
    
    # Metadata
    sentiment_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Sentiment Score (-1 to 1)')
    )
    word_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Word Count')
    )
    language = models.CharField(
        max_length=10,
        choices=[
            ('en', _('English')),
            ('kn', _('Kannada')),
            ('mixed', _('Mixed')),
        ],
        default='en',
        verbose_name=_('Language')
    )

    class Meta:
        verbose_name = _('Public Record')
        verbose_name_plural = _('Public Records')
        ordering = ['-event_date', 'politician']
        indexes = [
            models.Index(fields=['politician']),
            models.Index(fields=['record_type']),
            models.Index(fields=['verification_status']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['event_date']),
            models.Index(fields=['categories']),
            models.Index(fields=['tags']),
            # Full-text search indexes (for MySQL)
            # Note: Use MySQL full-text index on content_en, content_kn
        ]

    def __str__(self):
        return f"{self.record_type}: {self.title_en}"

    def save(self, *args, **kwargs):
        """Calculate word count on save."""
        if self.content_en:
            self.word_count = len(self.content_en.split())
        super().save(*args, **kwargs)


# =============================================================================
# Constituency Fund
# =============================================================================

class ConstituencyFund(models.Model):
    """
    Fund allocation and utilization for each constituency.
    Tracks MLA/MLNA fund usage.
    """
    FUND_TYPE_CHOICES = [
        ('mla', _('MLA Fund')),
        ('mllp', _('MLLP Fund')),
        ('central', _('Central Scheme Fund')),
        ('other', _('Other')),
    ]
    
    FINANCIAL_YEAR_CHOICES = [
        ('2024-25', '2024-25'),
        ('2023-24', '2023-24'),
        ('2022-23', '2022-23'),
        ('2021-22', '2021-22'),
        ('2020-21', '2020-21'),
        # Add more as needed
    ]
    
    constituency = models.ForeignKey(
        Constituency,
        on_delete=models.PROTECT,
        related_name='funds',
        verbose_name=_('Constituency')
    )
    fund_type = models.CharField(
        max_length=20,
        choices=FUND_TYPE_CHOICES,
        db_index=True,
        verbose_name=_('Fund Type')
    )
    financial_year = models.CharField(
        max_length=7,
        choices=FINANCIAL_YEAR_CHOICES,
        db_index=True,
        verbose_name=_('Financial Year')
    )
    
    # Allocation
    allocated_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name=_('Allocated Amount')
    )
    allocated_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Allocated Date')
    )
    
    # Utilization
    utilized_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name=_('Utilized Amount')
    )
    utilization_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Last Utilization Date')
    )
    utilization_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name=_('Utilization Percentage')
    )
    
    # Project Details
    project_name_en = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_('Project Name (English)')
    )
    project_name_kn = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_('Project Name (Kannada)')
    )
    project_description_en = models.TextField(
        blank=True,
        verbose_name=_('Project Description (English)')
    )
    project_description_kn = models.TextField(
        blank=True,
        verbose_name=_('Project Description (Kannada)')
    )
    
    # Implementation
    implementing_agency = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Implementing Agency')
    )
    contractor_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Contractor Name')
    )
    
    # Status
    project_status = models.CharField(
        max_length=30,
        choices=[
            ('planned', _('Planned')),
            ('in_progress', _('In Progress')),
            ('completed', _('Completed')),
            ('halted', _('Halted')),
            ('cancelled', _('Cancelled')),
        ],
        default='planned',
        verbose_name=_('Project Status')
    )
    completion_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name=_('Completion Percentage')
    )
    
    # Source
    fund_source_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name=_('Fund Source URL')
    )
    utilization_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name=_('Utilization URL')
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notes')
    )

    class Meta:
        verbose_name = _('Constituency Fund')
        verbose_name_plural = _('Constituency Funds')
        ordering = ['-financial_year', 'constituency']
        indexes = [
            models.Index(fields=['constituency']),
            models.Index(fields=['financial_year']),
            models.Index(fields=['fund_type']),
            models.Index(fields=['project_status']),
            models.Index(fields=['utilization_percentage']),
            # Composite indexes for common queries
            models.Index(fields=['financial_year', 'fund_type']),
            models.Index(fields=['constituency', 'financial_year']),
            models.Index(fields=['constituency', 'fund_type']),
        ]
        unique_together = ['constituency', 'financial_year', 'fund_type']

    @property
    def remaining_amount(self):
        """Calculate remaining amount of allocated funds."""
        return self.allocated_amount - self.utilized_amount

    def __str__(self):
        return f"{self.constituency.constituency_name_en} - {self.financial_year} - {self.fund_type}"

    def save(self, *args, **kwargs):
        """Calculate utilization percentage on save."""
        if self.allocated_amount > 0:
            self.utilization_percentage = (
                self.utilized_amount / self.allocated_amount
            ) * 100
        super().save(*args, **kwargs)


# =============================================================================
# Raw Scraped Data (Staging Table)
# =============================================================================

class RawScrapedData(models.Model):
    """
    Staging table for raw, unpurified data from various scraping sources.
    Used for ETL pipeline: Raw -> LLM Processing -> Purified PublicRecord.
    Optimized for high-volume batch inserts and efficient processing queries.
    """
    PROCESSING_STATUS_CHOICES = [
        ('pending', _('Pending Processing')),
        ('processing', _('Currently Processing')),
        ('processed', _('Successfully Processed')),
        ('failed', _('Processing Failed')),
        ('duplicate', _('Duplicate Detected')),
        ('skipped', _('Skipped')),
    ]

    SOURCE_TYPE_CHOICES = [
        ('news_article', _('News Article')),
        ('press_release', _('Press Release')),
        ('social_media', _('Social Media Post')),
        ('assembly_speech', _('Assembly Speech Transcript')),
        ('court_order', _('Court Order/Judgment')),
        ('affidavit', _('Affidavit PDF')),
        ('gazette', _('Government Gazette')),
        ('ec_portal', _('ECI Portal Data')),
        ('assembly_directory', _('Assembly Directory')),
        ('fund_portal', _('Government Fund Portal')),
        ('other', _('Other')),
    ]

    # Content Storage
    content_raw_html = models.TextField(
        blank=True,
        verbose_name=_('Raw HTML Content')
    )
    content_raw_text = models.TextField(
        blank=True,
        verbose_name=_('Raw Text Content')
    )
    content_pdf_text = models.TextField(
        blank=True,
        verbose_name=_('Extracted PDF Text')
    )
    content_json = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_('JSON Content')
    )
    content_binary = models.BinaryField(
        blank=True,
        null=True,
        verbose_name=_('Binary Content (PDF/Images)')
    )

    # Metadata
    source_type = models.CharField(
        max_length=30,
        choices=SOURCE_TYPE_CHOICES,
        db_index=True,
        verbose_name=_('Source Type')
    )
    source_url = models.URLField(
        max_length=2000,
        db_index=True,
        verbose_name=_('Source URL')
    )
    source_domain = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name=_('Source Domain')
    )
    source_organization = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Source Organization')
    )

    # Politician Identification (for reference)
    identified_politician = models.ForeignKey(
        Politician,
        on_delete=models.PROTECT,
        related_name='raw_scraped_data',
        null=True,
        blank=True,
        verbose_name=_('Identified Politician')
    )
    identified_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Identified Name from Source')
    )
    identified_constituency = models.ForeignKey(
        Constituency,
        on_delete=models.PROTECT,
        related_name='raw_scraped_data',
        null=True,
        blank=True,
        verbose_name=_('Identified Constituency')
    )

    # Processing Status
    processing_status = models.CharField(
        max_length=20,
        choices=PROCESSING_STATUS_CHOICES,
        default='pending',
        db_index=True,
        verbose_name=_('Processing Status')
    )
    processing_attempts = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_('Processing Attempts')
    )
    processing_error = models.TextField(
        blank=True,
        verbose_name=_('Processing Error Details')
    )
    processing_started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Processing Start Time')
    )
    processing_completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Processing Completion Time')
    )
    processed_by = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Processed By (LLM/Worker)')
    )
    processing_metadata = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_('Processing Metadata')
    )

    # Content Quality
    language_detected = models.CharField(
        max_length=10,
        choices=[
            ('en', _('English')),
            ('kn', _('Kannada')),
            ('mixed', _('Mixed')),
            ('unknown', _('Unknown')),
        ],
        default='unknown',
        verbose_name=_('Detected Language')
    )
    word_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Word Count')
    )
    content_hash = models.CharField(
        max_length=64,
        unique=True,
        verbose_name=_('Content Hash (SHA-256)')
    )

    # Scraping Metadata
    scraper_name = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name=_('Scraper Name/Identifier')
    )
    scraped_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name=_('Scraped At')
    )
    last_scraped_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Last Scraped At')
    )
    scrape_metadata = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_('Scraping Metadata')
    )

    # Date Information from Source
    published_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_('Published Date')
    )
    crawled_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Crawled Date')
    )

    # Priority (for processing queue)
    priority = models.PositiveSmallIntegerField(
        default=5,
        db_index=True,
        verbose_name=_('Processing Priority (1=High, 10=Low)')
    )

    # Output Reference (after processing)
    linked_public_record = models.ForeignKey(
        PublicRecord,
        on_delete=models.PROTECT,
        related_name='source_raw_data',
        null=True,
        blank=True,
        verbose_name=_('Linked Public Record')
    )

    class Meta:
        verbose_name = _('Raw Scraped Data')
        verbose_name_plural = _('Raw Scraped Data Records')
        ordering = ['-priority', '-published_date', '-scraped_at']
        indexes = [
            models.Index(fields=['processing_status']),
            models.Index(fields=['processing_status', 'priority']),
            models.Index(fields=['source_type']),
            models.Index(fields=['source_domain']),
            models.Index(fields=['scraper_name']),
            models.Index(fields=['scraped_at']),
            models.Index(fields=['published_date']),
            models.Index(fields=['content_hash']),
            models.Index(fields=['identified_politician']),
            models.Index(fields=['identified_politician', 'processing_status']),
            models.Index(fields=['processing_status', 'scraper_name']),
            # Composite index for processing queue
            models.Index(fields=['processing_status', 'priority', 'published_date']),
            # Index for duplicate detection
            models.Index(fields=['source_url', 'content_hash']),
        ]
        # Partial indexes for common query patterns
        constraints = [
            models.CheckConstraint(
                check=models.Q(processing_attempts__gte=0),
                name='non_negative_processing_attempts'
            ),
        ]

    def __str__(self):
        return f"{self.source_type}: {self.source_domain} - {self.processing_status}"

    def save(self, *args, **kwargs):
        """Calculate word count and update timestamps on save."""
        from django.utils import timezone

        # Calculate word count from raw text
        if self.content_raw_text:
            self.word_count = len(self.content_raw_text.split())
        elif self.content_pdf_text:
            self.word_count = len(self.content_pdf_text.split())

        # Update last_scraped_at on update
        if self.pk:
            self.last_scraped_at = timezone.now()

        super().save(*args, **kwargs)

    def mark_processing(self):
        """Mark record as being processed."""
        from django.utils import timezone
        self.processing_status = 'processing'
        self.processing_started_at = timezone.now()
        self.processing_attempts += 1
        self.save(update_fields=[
            'processing_status', 'processing_started_at', 'processing_attempts'
        ])

    def mark_processed(self, worker_name=None, metadata=None):
        """Mark record as successfully processed."""
        from django.utils import timezone
        self.processing_status = 'processed'
        self.processing_completed_at = timezone.now()
        self.processed_by = worker_name or 'worker'
        self.processing_metadata = metadata
        self.save(update_fields=[
            'processing_status', 'processing_completed_at', 'processed_by',
            'processing_metadata'
        ])

    def mark_failed(self, error_message):
        """Mark record as failed with error details."""
        self.processing_status = 'failed'
        self.processing_error = error_message
        self.save(update_fields=['processing_status', 'processing_error'])


# =============================================================================
# Election Results & Candidate Electoral Performance (Official ECI Data)
# =============================================================================

class ElectionResult(TimestampMixin):
    """
    Official ECI Election Result Record for candidates in an election.
    """
    politician = models.ForeignKey(
        Politician,
        on_delete=models.CASCADE,
        related_name='electoral_results',
        verbose_name=_('Politician')
    )
    election_year = models.PositiveSmallIntegerField(
        db_index=True,
        verbose_name=_('Election Year')
    )
    election_type = models.CharField(
        max_length=20,
        choices=[
            ('assembly', _('Karnataka Legislative Assembly')),
            ('lok_sabha', _('Lok Sabha')),
        ],
        default='assembly',
        verbose_name=_('Election Type')
    )
    constituency_name = models.CharField(
        max_length=150,
        verbose_name=_('Constituency Name')
    )
    party_name = models.CharField(
        max_length=100,
        verbose_name=_('Party Name')
    )
    total_electors = models.BigIntegerField(
        default=0,
        verbose_name=_('Total Electors')
    )
    total_votes_polled = models.BigIntegerField(
        default=0,
        verbose_name=_('Total Votes Polled')
    )
    votes_secured = models.BigIntegerField(
        default=0,
        verbose_name=_('Votes Secured')
    )
    vote_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name=_('Vote Percentage')
    )
    margin_votes = models.BigIntegerField(
        default=0,
        verbose_name=_('Margin of Victory / Loss')
    )
    is_winner = models.BooleanField(
        default=True,
        verbose_name=_('Is Winner')
    )
    evm_votes = models.BigIntegerField(
        default=0,
        verbose_name=_('EVM Votes')
    )
    postal_votes = models.BigIntegerField(
        default=0,
        verbose_name=_('Postal Votes')
    )
    runner_up_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name=_('Runner-up Candidate')
    )
    runner_up_party = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Runner-up Party')
    )
    runner_up_votes = models.BigIntegerField(
        default=0,
        verbose_name=_('Runner-up Votes')
    )
    runner_up_vote_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name=_('Runner-up Vote Percentage')
    )

    # Provenance
    source_url = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name=_('Source URL')
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_('Is Verified')
    )

    class Meta:
        verbose_name = _('Election Result')
        verbose_name_plural = _('Election Results')
        ordering = ['-election_year']
        indexes = [
            models.Index(fields=['politician', '-election_year']),
            models.Index(fields=['election_year', 'election_type']),
            models.Index(fields=['politician', 'election_type']),
        ]

    def __str__(self):
        return f"{self.politician.full_name_en} - {self.constituency_name} ({self.election_year})"


# =============================================================================
# Temporal Domain Models
# =============================================================================

class OfficeTenure(TimestampMixin):
    """
    Historical and current political office holding periods.
    """
    OFFICE_TYPE_CHOICES = (
        ('mla', _('Member of Legislative Assembly (MLA)')),
        ('mp_ls', _('Member of Parliament - Lok Sabha (MP)')),
        ('mp_rs', _('Member of Parliament - Rajya Sabha (MP)')),
        ('cm', _('Chief Minister')),
        ('deputy_cm', _('Deputy Chief Minister')),
        ('cabinet_minister', _('Cabinet Minister')),
        ('minister_of_state', _('Minister of State')),
        ('union_minister', _('Union Minister')),
        ('other', _('Other')),
    )
    politician = models.ForeignKey(
        Politician,
        on_delete=models.CASCADE,
        related_name='office_tenures',
        verbose_name=_('Politician')
    )
    office_type = models.CharField(
        max_length=50,
        choices=OFFICE_TYPE_CHOICES,
        db_index=True,
        verbose_name=_('Office Type')
    )
    office_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Office Title / Portfolio')
    )
    constituency = models.ForeignKey(
        Constituency,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='historical_representatives',
        verbose_name=_('Constituency')
    )
    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Start Date')
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('End Date')
    )
    is_current = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_('Is Current')
    )
    source_url = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name=_('Source URL')
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_('Is Verified')
    )

    class Meta:
        verbose_name = _('Office Tenure')
        verbose_name_plural = _('Office Tenures')
        ordering = ['-start_date', '-is_current']
        indexes = [
            models.Index(fields=['politician', 'is_current']),
            models.Index(fields=['politician', 'office_type']),
        ]

    def __str__(self):
        return f"{self.politician.full_name_en} - {self.get_office_type_display()} ({'Current' if self.is_current else 'Historical'})"


class PartyMembership(TimestampMixin):
    """
    Historical and current political party affiliations.
    """
    politician = models.ForeignKey(
        Politician,
        on_delete=models.CASCADE,
        related_name='party_memberships',
        verbose_name=_('Politician')
    )
    party = models.ForeignKey(
        Party,
        on_delete=models.CASCADE,
        related_name='historical_members',
        verbose_name=_('Party')
    )
    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Start Date')
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('End Date')
    )
    is_current = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_('Is Current')
    )
    source_url = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name=_('Source URL')
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_('Is Verified')
    )

    class Meta:
        verbose_name = _('Party Membership')
        verbose_name_plural = _('Party Memberships')
        ordering = ['-start_date', '-is_current']
        indexes = [
            models.Index(fields=['politician', 'is_current']),
            models.Index(fields=['party', 'is_current']),
        ]

    def __str__(self):
        return f"{self.politician.full_name_en} - {self.party.party_short_name_en} ({'Current' if self.is_current else 'Historical'})"
