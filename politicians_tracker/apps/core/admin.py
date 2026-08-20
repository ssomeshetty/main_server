from django.contrib import admin
from django.utils.html import format_html
from .models import (
    District, Constituency, Politician, Party,
    FinancialDeclaration, LegalRecord, PublicRecord, ConstituencyFund
)


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'district_code', 'region', 'population_2011', 'area_sq_km']
    list_filter = ['region']
    search_fields = ['district_name_en', 'district_name_kn', 'district_code']
    ordering = ['district_name_en']
    
    def name_en(self, obj):
        return obj.district_name_en
    name_en.short_description = 'Name (English)'
    name_en.admin_order_field = 'district_name_en'


@admin.register(Constituency)
class ConstituencyAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'constituency_number', 'district', 'constituency_type', 'population_2011']
    list_filter = ['district', 'constituency_type']
    search_fields = ['constituency_name_en', 'constituency_name_kn']
    ordering = ['constituency_number']
    
    def name_en(self, obj):
        return obj.constituency_name_en
    name_en.short_description = 'Name (English)'
    name_en.admin_order_field = 'constituency_name_en'


@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'short_name_en', 'party_type', 'is_active', 'date_of_registration']
    list_filter = ['party_type', 'is_active']
    search_fields = ['party_name_en', 'party_name_kn', 'party_short_name_en', 'party_short_name_kn']
    ordering = ['party_name_en']
    
    def name_en(self, obj):
        return obj.party_name_en
    name_en.short_description = 'Name (English)'
    name_en.admin_order_field = 'party_name_en'
    
    def short_name_en(self, obj):
        return obj.party_short_name_en
    short_name_en.short_description = 'Short Name (English)'
    short_name_en.admin_order_field = 'party_short_name_en'


@admin.register(Politician)
class PoliticianAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'current_party', 'current_constituency', 'is_active', 'is_verified', 'total_terms_won']
    list_filter = ['current_party', 'current_constituency__district', 'is_active', 'is_verified']
    search_fields = ['full_name_en', 'full_name_kn', 'first_name_en', 'first_name_kn']
    ordering = ['full_name_en']
    readonly_fields = ['slug']
    autocomplete_fields = ['current_party', 'current_constituency']
    
    def name_en(self, obj):
        return obj.full_name_en
    name_en.short_description = 'Name (English)'
    name_en.admin_order_field = 'full_name_en'


@admin.register(FinancialDeclaration)
class FinancialDeclarationAdmin(admin.ModelAdmin):
    list_display = ['politician_name', 'declaration_year', 'declaration_type', 'total_assets', 'net_worth', 'is_verified']
    list_filter = ['declaration_type', 'declaration_year', 'is_verified']
    search_fields = ['politician__full_name_en', 'politician__full_name_kn']
    ordering = ['-declaration_year', 'politician']
    readonly_fields = ['politician']
    
    def politician_name(self, obj):
        return obj.politician.full_name_en
    politician_name.short_description = 'Politician'
    politician_name.admin_order_field = 'politician__full_name_en'
    
    def net_worth(self, obj):
        return obj.calculate_net_worth()
    net_worth.short_description = 'Net Worth'
    net_worth.admin_order_field = 'net_worth'


@admin.register(LegalRecord)
class LegalRecordAdmin(admin.ModelAdmin):
    list_display = ['case_number', 'politician_name', 'case_status', 'district', 'is_verified']
    list_filter = ['case_status', 'district', 'is_verified']
    search_fields = ['case_number', 'politician__full_name_en', 'politician__full_name_kn']
    ordering = ['-fir_date', 'case_number']
    
    def politician_name(self, obj):
        return obj.politician.full_name_en
    politician_name.short_description = 'Politician'
    politician_name.admin_order_field = 'politician__full_name_en'


@admin.register(PublicRecord)
class PublicRecordAdmin(admin.ModelAdmin):
    list_display = ['title_en', 'politician_name', 'record_type', 'verification_status', 'is_verified', 'event_date']
    list_filter = ['record_type', 'verification_status', 'is_verified', 'event_date']
    search_fields = ['title_en', 'title_kn', 'content_en', 'content_kn']
    ordering = ['-event_date', 'title_en']
    
    def politician_name(self, obj):
        return obj.politician.full_name_en
    politician_name.short_description = 'Politician'
    politician_name.admin_order_field = 'politician__full_name_en'
    
    def title_en(self, obj):
        return obj.title_en
    title_en.short_description = 'Title (English)'
    title_en.admin_order_field = 'title_en'


@admin.register(ConstituencyFund)
class ConstituencyFundAdmin(admin.ModelAdmin):
    list_display = ['project_name_en', 'constituency', 'fund_type', 'financial_year', 'allocated_amount', 'utilized_amount', 'project_status']
    list_filter = ['fund_type', 'financial_year', 'project_status']
    search_fields = ['project_name_en', 'project_name_kn', 'constituency__constituency_name_en']
    ordering = ['-financial_year', 'constituency']
    
    def project_name_en(self, obj):
        return obj.project_name_en
    project_name_en.short_description = 'Project Name (English)'
    project_name_en.admin_order_field = 'project_name_en'
