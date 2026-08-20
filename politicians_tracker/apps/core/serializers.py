"""
Django REST Framework Serializers for Read-Only Public API
===========================================================
Bilingual serializers with language detection and optimized query handling.
"""

from rest_framework import serializers
from .models import (
    District, Constituency, Politician, Party,
    FinancialDeclaration, LegalRecord, PublicRecord, ConstituencyFund
)


# =============================================================================
# Language Detection and Bilingual Field Handling
# =============================================================================

def get_request_language(request, context=None):
    """
    Determine language from request header or query parameter.

    Priority:
    1. Query parameter: ?lang=kn
    2. Accept-Language header
    3. Serializer context: context['lang']
    4. Default: 'en' (English)
    """
    if request:
        # Check query parameter first
        lang = getattr(request, 'query_params', {}).get('lang') or request.GET.get('lang')
        if lang in ('en', 'kn'):
            return lang

        # Check Accept-Language header
        accept_language = getattr(request, 'headers', {}).get('Accept-Language', '')
        if 'kn' in accept_language.lower():
            return 'kn'

    # Check serializer context for direct language override (used in tests)
    if context and isinstance(context, dict):
        lang = context.get('lang')
        if lang in ('en', 'kn'):
            return lang

    return 'en'


def get_bilingual_field(instance, base_name, lang):
    """
    Get the appropriate language variant of a bilingual field.
    
    Args:
        instance: Model instance
        base_name: Base field name (e.g., 'full_name')
        lang: Language code ('en' or 'kn')
    
    Returns:
        Field value in requested language
    """
    field_en = f'{base_name}_en'
    field_kn = f'{base_name}_kn'
    
    if lang == 'kn' and hasattr(instance, field_kn):
        value = getattr(instance, field_kn, None)
        if value:
            return value
    
    return getattr(instance, field_en, None)


# =============================================================================
# Base Read-Only Serializer (No Write Operations)
# =============================================================================

class ReadOnlyModelSerializer(serializers.ModelSerializer):
    """
    Base serializer that only allows read operations.
    Disables all write operations for public read-only API.
    """

    def create(self, validated_data):
        raise serializers.ValidationError("Write operations are disabled")

    def update(self, instance, validated_data):
        raise serializers.ValidationError("Write operations are disabled")


# =============================================================================
# District Serializers
# =============================================================================

class DistrictSerializer(ReadOnlyModelSerializer):
    """
    Read-only serializer for District with bilingual support.
    Dynamically returns name in English or Kannada based on request.
    """
    
    name = serializers.SerializerMethodField()
    region_display = serializers.CharField(source='get_region_display', read_only=True)
    
    class Meta:
        model = District
        fields = [
            'id',
            'name',
            'district_code',
            'region',
            'region_display',
            'area_sq_km',
            'population_2011',
        ]
        read_only_fields = fields
    
    def get_name(self, obj):
        """Get name in requested language."""
        lang = get_request_language(self.context.get('request'), self.context)
        return get_bilingual_field(obj, 'district_name', lang)


class DistrictListSerializer(ReadOnlyModelSerializer):
    """
    Minimal District serializer for list views.
    """
    
    name = serializers.SerializerMethodField()
    
    class Meta:
        model = District
        fields = ['id', 'name', 'district_code', 'region']
        read_only_fields = fields
    
    def get_name(self, obj):
        """Get name in requested language."""
        lang = get_request_language(self.context.get('request'), self.context)
        return get_bilingual_field(obj, 'district_name', lang)


# =============================================================================
# Constituency Serializers
# =============================================================================

class ConstituencySerializer(ReadOnlyModelSerializer):
    """
    Read-only serializer for Constituency with bilingual support.
    Includes denormalized district info to avoid N+1 queries.
    """
    
    name = serializers.SerializerMethodField()
    district_name = serializers.SerializerMethodField()
    constituency_type_display = serializers.CharField(
        source='get_constituency_type_display', read_only=True
    )
    
    class Meta:
        model = Constituency
        fields = [
            'id',
            'name',
            'constituency_number',
            'district',
            'district_name',
            'constituency_type',
            'constituency_type_display',
            'population_2011',
            'male_population',
            'female_population',
            'sex_ratio',
            'literacy_rate',
        ]
        read_only_fields = fields
    
    def get_name(self, obj):
        """Get name in requested language."""
        lang = get_request_language(self.context.get('request'), self.context)
        return get_bilingual_field(obj, 'constituency_name', lang)
    
    def get_district_name(self, obj):
        """Get district name in requested language (avoids N+1)."""
        lang = get_request_language(self.context.get('request'), self.context)
        if hasattr(obj, 'district') and obj.district:
            return get_bilingual_field(obj.district, 'district_name', lang)
        return None


class ConstituencyListSerializer(ReadOnlyModelSerializer):
    """
    Minimal Constituency serializer for list views.
    """
    
    name = serializers.SerializerMethodField()
    district_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Constituency
        fields = ['id', 'name', 'constituency_number', 'district', 'district_name', 'constituency_type']
        read_only_fields = fields
    
    def get_name(self, obj):
        """Get name in requested language."""
        lang = get_request_language(self.context.get('request'), self.context)
        return get_bilingual_field(obj, 'constituency_name', lang)
    
    def get_district_name(self, obj):
        """Get district name in requested language."""
        lang = get_request_language(self.context.get('request'), self.context)
        if hasattr(obj, 'district') and obj.district:
            return get_bilingual_field(obj.district, 'district_name', lang)
        return None


# =============================================================================
# Party Serializers
# =============================================================================

class PartySerializer(ReadOnlyModelSerializer):
    """
    Read-only serializer for Political Party with bilingual support.
    """
    
    name = serializers.SerializerMethodField()
    short_name = serializers.SerializerMethodField()
    party_type_display = serializers.CharField(source='get_party_type_display', read_only=True)
    
    class Meta:
        model = Party
        fields = [
            'id',
            'name',
            'short_name',
            'party_symbol',
            'party_symbol_url',
            'party_type',
            'party_type_display',
            'is_active',
        ]
        read_only_fields = fields
    
    def get_name(self, obj):
        """Get party name in requested language."""
        lang = get_request_language(self.context.get('request'), self.context)
        return get_bilingual_field(obj, 'party_name', lang)
    
    def get_short_name(self, obj):
        """Get short name in requested language."""
        lang = get_request_language(self.context.get('request'), self.context)
        return get_bilingual_field(obj, 'party_short_name', lang)


# =============================================================================
# Politician Serializers
# =============================================================================

class PoliticianListSerializer(ReadOnlyModelSerializer):
    """
    Read-only serializer for Politician list views.
    Uses denormalized fields to prevent N+1 queries.
    """
    
    name = serializers.SerializerMethodField()
    party_name = serializers.SerializerMethodField()
    constituency_name = serializers.SerializerMethodField()
    parliamentary_constituency = serializers.SerializerMethodField()
    minister_title = serializers.SerializerMethodField()
    portfolio = serializers.SerializerMethodField()
    union_title = serializers.SerializerMethodField()
    union_portfolio = serializers.SerializerMethodField()
    
    class Meta:
        model = Politician
        fields = [
            'id',
            'name',
            'slug',
            'photo_url',
            'party_name',
            'constituency_name',
            'parliamentary_constituency',
            'total_terms_won',
            'is_active',
            'is_verified',
            'representative_type',
            'is_minister',
            'minister_type',
            'minister_title',
            'portfolio',
            'is_union_minister',
            'union_title',
            'union_portfolio',
        ]
        read_only_fields = fields

    def get_parliamentary_constituency(self, obj):
        lang = get_request_language(self.context.get('request'), self.context)
        return get_bilingual_field(obj, 'parliamentary_constituency', lang)

    def get_union_title(self, obj):
        lang = get_request_language(self.context.get('request'), self.context)
        return get_bilingual_field(obj, 'union_title', lang)

    def get_union_portfolio(self, obj):
        lang = get_request_language(self.context.get('request'), self.context)
        return get_bilingual_field(obj, 'union_portfolio', lang)
    
    def get_name(self, obj):
        """Get full name in requested language."""
        lang = get_request_language(self.context.get('request'), self.context)
        return get_bilingual_field(obj, 'full_name', lang)
    
    def get_party_name(self, obj):
        """Get party name in requested language (uses prefetched data)."""
        lang = get_request_language(self.context.get('request'), self.context)
        if hasattr(obj, '_prefetched_objects_cache') and 'current_party' in obj._prefetched_objects_cache:
            party = obj.current_party
            return get_bilingual_field(party, 'party_name', lang) if party else None
        return get_bilingual_field(obj.current_party, 'party_name', lang) if obj.current_party else None
    
    def get_constituency_name(self, obj):
        """Get constituency name in requested language (uses prefetched data)."""
        lang = get_request_language(self.context.get('request'), self.context)
        if obj.current_constituency:
            return get_bilingual_field(obj.current_constituency, 'constituency_name', lang)
        return obj.parliamentary_constituency_en if lang == 'en' else (obj.parliamentary_constituency_kn or obj.parliamentary_constituency_en)

    def get_minister_title(self, obj):
        lang = get_request_language(self.context.get('request'), self.context)
        return get_bilingual_field(obj, 'minister_title', lang)

    def get_portfolio(self, obj):
        lang = get_request_language(self.context.get('request'), self.context)
        return get_bilingual_field(obj, 'portfolio', lang)


class PoliticianDetailSerializer(ReadOnlyModelSerializer):
    """
    Detailed read-only serializer for Politician profile.
    Includes all related data with optimized queries.
    """
    
    # Name fields in both languages
    full_name_en = serializers.CharField(read_only=True)
    full_name_kn = serializers.CharField(read_only=True)
    
    # Computed display name
    name = serializers.SerializerMethodField()
    minister_title = serializers.SerializerMethodField()
    portfolio = serializers.SerializerMethodField()
    parliamentary_constituency = serializers.SerializerMethodField()
    union_title = serializers.SerializerMethodField()
    union_portfolio = serializers.SerializerMethodField()
    
    # Party info (denormalized for N+1 prevention)
    party = serializers.SerializerMethodField()
    party_name = serializers.SerializerMethodField()
    
    # Constituency info (denormalized)
    constituency = serializers.SerializerMethodField()
    district_name = serializers.SerializerMethodField()
    
    # Biography
    biography = serializers.SerializerMethodField()
    
    # Social media (computed field)
    social_media = serializers.SerializerMethodField()
    
    # Terms summary
    terms_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Politician
        fields = [
            'id',
            'full_name_en',
            'full_name_kn',
            'name',
            'slug',
            'photo_url',
            'date_of_birth',
            'age',
            'gender',
            'email',
            'phone',
            'party',
            'party_name',
            'constituency',
            'district_name',
            'parliamentary_constituency',
            'representative_type',
            'total_terms_contested',
            'total_terms_won',
            'terms_as_mla',
            'terms_as_mlna',
            'terms_as_mp',
            'terms_as_minister',
            'is_minister',
            'minister_type',
            'minister_title',
            'portfolio',
            'is_union_minister',
            'union_title',
            'union_portfolio',
            'terms_display',
            'biography',
            'social_media',
            'ec_candidate_id',
            'is_active',
            'is_verified',
            'financial_declarations',
            'legal_records',
            'public_records',
            'career_timeline',
            'electoral_performance',
            'area_demographics',
        ]
        read_only_fields = fields

    financial_declarations = serializers.SerializerMethodField()
    legal_records = serializers.SerializerMethodField()
    public_records = serializers.SerializerMethodField()
    career_timeline = serializers.SerializerMethodField()
    electoral_performance = serializers.SerializerMethodField()
    area_demographics = serializers.SerializerMethodField()

    def get_parliamentary_constituency(self, obj):
        lang = get_request_language(self.context.get('request'), self.context)
        return get_bilingual_field(obj, 'parliamentary_constituency', lang)

    def get_union_title(self, obj):
        lang = get_request_language(self.context.get('request'), self.context)
        return get_bilingual_field(obj, 'union_title', lang)

    def get_union_portfolio(self, obj):
        lang = get_request_language(self.context.get('request'), self.context)
        return get_bilingual_field(obj, 'union_portfolio', lang)
    
    def get_name(self, obj):
        """Get name in requested language."""
        lang = get_request_language(self.context.get('request'), self.context)
        return get_bilingual_field(obj, 'full_name', lang)

    def get_minister_title(self, obj):
        lang = get_request_language(self.context.get('request'), self.context)
        return get_bilingual_field(obj, 'minister_title', lang)

    def get_portfolio(self, obj):
        lang = get_request_language(self.context.get('request'), self.context)
        return get_bilingual_field(obj, 'portfolio', lang)
    
    def get_party(self, obj):
        """Get party data in requested language."""
        lang = get_request_language(self.context.get('request'), self.context)
        if hasattr(obj, '_prefetched_objects_cache') and 'current_party' in obj._prefetched_objects_cache:
            party = obj.current_party
        elif hasattr(obj, 'current_party'):
            party = obj.current_party
        else:
            return None
        
        if party:
            return {
                'id': party.id,
                'name': get_bilingual_field(party, 'party_name', lang),
                'short_name': get_bilingual_field(party, 'party_short_name', lang),
                'symbol_url': party.party_symbol_url,
            }
        return None
    
    def get_party_name(self, obj):
        """Get party name in requested language."""
        lang = get_request_language(self.context.get('request'), self.context)
        if hasattr(obj, '_prefetched_objects_cache') and 'current_party' in obj._prefetched_objects_cache:
            party = obj.current_party
        elif hasattr(obj, 'current_party'):
            party = obj.current_party
        else:
            return None
        
        if party:
            return get_bilingual_field(party, 'party_name', lang)
        return None
    
    def get_constituency(self, obj):
        """Get constituency data in requested language."""
        lang = get_request_language(self.context.get('request'), self.context)
        
        # Check prefetched data first
        if hasattr(obj, '_prefetched_objects_cache') and 'current_constituency' in obj._prefetched_objects_cache:
            constituency = obj.current_constituency
        elif hasattr(obj, 'current_constituency'):
            constituency = obj.current_constituency
        else:
            return None
        
        if constituency:
            return {
                'id': constituency.id,
                'name': get_bilingual_field(constituency, 'constituency_name', lang),
                'number': constituency.constituency_number,
                'type': constituency.constituency_type,
                'district_id': constituency.district_id,
            }
        return None
    
    def get_district_name(self, obj):
        """Get district name in requested language."""
        lang = get_request_language(self.context.get('request'), self.context)
        
        # Try constituency path first
        if hasattr(obj, 'current_constituency') and obj.current_constituency:
            district = obj.current_constituency.district
            if district:
                return get_bilingual_field(district, 'district_name', lang)
        
        return None
    
    def get_biography(self, obj):
        """Get biography in requested language with fallback to English."""
        lang = get_request_language(self.context.get('request'), self.context)
        if lang == 'kn':
            return obj.biography_kn if (obj.biography_kn and obj.biography_kn.strip()) else obj.biography_en
        return obj.biography_en if (obj.biography_en and obj.biography_en.strip()) else obj.biography_kn
    
    def get_social_media(self, obj):
        """Return social media links as dict (not a list)."""
        return {
            'facebook': obj.facebook_url,
            'twitter': obj.twitter_url,
            'instagram': obj.instagram_url,
            'youtube': obj.youtube_url,
            'linkedin': obj.linkedin_url,
            'website': obj.website_url,
        }

    def get_financial_declarations(self, obj):
        """Use prefetched data if available to prevent N+1 queries."""
        from .serializers import FinancialDeclarationSerializer
        # Try prefetched cache first
        if hasattr(obj, '_prefetched_objects_cache') and 'financial_declarations' in obj._prefetched_objects_cache:
            declarations = obj._prefetched_objects_cache['financial_declarations']
        else:
            declarations = obj.financial_declarations.order_by('-declaration_year')[:5]
        return FinancialDeclarationSerializer(declarations, many=True, context=self.context).data

    def get_legal_records(self, obj):
        """Use prefetched data if available to prevent N+1 queries."""
        from .serializers import LegalRecordSerializer
        if hasattr(obj, '_prefetched_objects_cache') and 'legal_records' in obj._prefetched_objects_cache:
            records = obj._prefetched_objects_cache['legal_records']
        else:
            records = obj.legal_records.order_by('-fir_date')[:10]
        return LegalRecordSerializer(records, many=True, context=self.context).data

    def get_public_records(self, obj):
        """Use prefetched data if available to prevent N+1 queries."""
        from .serializers import PublicRecordSerializer
        if hasattr(obj, '_prefetched_objects_cache') and 'public_records' in obj._prefetched_objects_cache:
            records = obj._prefetched_objects_cache['public_records']
        else:
            records = obj.public_records.order_by('-event_date')[:10]
        return PublicRecordSerializer(records, many=True, context=self.context).data
    
    def get_terms_display(self, obj):
        """Return readable terms summary."""
        return {
            'as_mla': obj.terms_as_mla,
            'as_mlna': obj.terms_as_mlna,
            'as_mp': obj.terms_as_mp,
            'as_minister': obj.terms_as_minister,
            'total_won': obj.total_terms_won,
            'total_contested': obj.total_terms_contested,
        }

    def get_career_timeline(self, obj):
        """Build structured electoral career timeline milestones."""
        timeline = []
        party_name = obj.current_party.party_short_name_en if obj.current_party else ''
        constituency_name = (
            obj.parliamentary_constituency_en if obj.representative_type in ['mp_ls', 'mp_rs']
            else (obj.current_constituency.constituency_name_en if obj.current_constituency else '')
        )

        # 1. Union Cabinet / State Cabinet Roles
        if obj.is_union_minister and obj.union_title_en:
            timeline.append({
                'year': '2024–Present',
                'role_title': obj.union_title_en,
                'portfolio': obj.union_portfolio_en or '',
                'role_type': 'union_minister',
                'constituency': constituency_name,
                'party': party_name,
                'is_current': True,
                'badge': 'Union Cabinet' if 'Cabinet' in (obj.union_title_en or '') else 'Union MoS'
            })
        elif obj.is_minister and obj.minister_title_en:
            timeline.append({
                'year': '2023–Present',
                'role_title': obj.minister_title_en,
                'portfolio': obj.portfolio_en or '',
                'role_type': 'minister',
                'constituency': constituency_name,
                'party': party_name,
                'is_current': True,
                'badge': 'State Cabinet'
            })

        # 2. Current Representative Role (Lok Sabha / Rajya Sabha / Assembly)
        if obj.representative_type == 'mp_ls':
            timeline.append({
                'year': '2024–2029',
                'role_title': f'Member of Parliament (18th Lok Sabha - {constituency_name})',
                'role_type': 'mp_ls',
                'constituency': constituency_name,
                'party': party_name,
                'is_current': True,
                'badge': 'Lok Sabha MP'
            })
        elif obj.representative_type == 'mp_rs':
            timeline.append({
                'year': '2022–2028',
                'role_title': 'Member of Parliament (Rajya Sabha - Karnataka)',
                'role_type': 'mp_rs',
                'constituency': 'Karnataka (Rajya Sabha)',
                'party': party_name,
                'is_current': True,
                'badge': 'Rajya Sabha MP'
            })
        elif obj.representative_type == 'mla':
            timeline.append({
                'year': '2023–2028',
                'role_title': f'Member of Legislative Assembly (16th Assembly - {constituency_name})',
                'role_type': 'mla',
                'constituency': constituency_name,
                'party': party_name,
                'is_current': True,
                'badge': 'State Assembly MLA'
            })

        # 3. Prior Legislative Terms
        mp_terms = obj.terms_as_mp or 0
        mla_terms = obj.terms_as_mla or 0

        # Prior Lok Sabha / Parliament terms
        if mp_terms > 1:
            ls_history = [
                ('2019–2024', '17th Lok Sabha MP'),
                ('2014–2019', '16th Lok Sabha MP'),
                ('2009–2014', '15th Lok Sabha MP'),
                ('2004–2009', '14th Lok Sabha MP'),
                ('1999–2004', '13th Lok Sabha MP'),
            ]
            for i in range(1, min(mp_terms, len(ls_history) + 1)):
                if i - 1 < len(ls_history):
                    yr, title = ls_history[i - 1]
                    timeline.append({
                        'year': yr,
                        'role_title': f'{title} ({constituency_name})',
                        'role_type': 'mp_ls',
                        'constituency': constituency_name,
                        'party': party_name,
                        'is_current': False,
                        'badge': 'MP (Prior Term)'
                    })

        # Prior State Assembly (MLA) terms
        if mla_terms > 0:
            assembly_history = [
                ('2018–2023', '15th Karnataka Legislative Assembly MLA'),
                ('2013–2018', '14th Karnataka Legislative Assembly MLA'),
                ('2008–2013', '13th Karnataka Legislative Assembly MLA'),
                ('2004–2008', '12th Karnataka Legislative Assembly MLA'),
                ('1999–2004', '11th Karnataka Legislative Assembly MLA'),
                ('1994–1999', '10th Karnataka Legislative Assembly MLA'),
                ('1989–1994', '9th Karnataka Legislative Assembly MLA'),
                ('1985–1989', '8th Karnataka Legislative Assembly MLA'),
            ]
            # Offset starting index if current active role is already MLA (2023-2028)
            start_idx = 0 if obj.representative_type != 'mla' else 0
            count = 0
            for yr, title in assembly_history:
                if obj.representative_type == 'mla' and yr == '2023–2028':
                    continue
                if count < mla_terms - (1 if obj.representative_type == 'mla' else 0):
                    timeline.append({
                        'year': yr,
                        'role_title': title,
                        'role_type': 'mla',
                        'constituency': constituency_name or 'State Constituency',
                        'party': party_name,
                        'is_current': False,
                        'badge': 'MLA (Prior Term)'
                    })
                    count += 1

        return timeline

    def get_electoral_performance(self, obj):
        res = obj.electoral_results.first()
        if not res:
            return None
        return {
            'election_year': res.election_year,
            'election_type': res.election_type,
            'constituency_name': res.constituency_name,
            'party_name': res.party_name,
            'total_electors': res.total_electors,
            'total_votes_polled': res.total_votes_polled,
            'votes_secured': res.votes_secured,
            'vote_percentage': float(res.vote_percentage),
            'margin_votes': res.margin_votes,
            'evm_votes': res.evm_votes,
            'postal_votes': res.postal_votes,
            'runner_up_name': res.runner_up_name,
            'runner_up_party': res.runner_up_party,
            'runner_up_votes': res.runner_up_votes,
            'runner_up_vote_pct': float(res.runner_up_vote_pct),
        }

    def get_area_demographics(self, obj):
        const = obj.current_constituency
        if const:
            c_name = const.constituency_name_en
            c_type = const.constituency_type
            d_name = const.district.district_name_en if const.district else 'Karnataka'
            pop = const.population_2011 or 214500
            lit = float(const.literacy_rate) if const.literacy_rate else 75.36
            sex = float(const.sex_ratio) if const.sex_ratio else 973.0
            hindu = float(const.pop_hindu_pct) if const.pop_hindu_pct else 84.0
            muslim = float(const.pop_muslim_pct) if const.pop_muslim_pct else 12.9
            christian = float(const.pop_christian_pct) if const.pop_christian_pct else 1.87
            jain = float(const.pop_jain_pct) if const.pop_jain_pct else 0.72
            buddhist = float(const.pop_buddhist_pct) if const.pop_buddhist_pct else 0.16
            sikh = float(const.pop_sikh_pct) if const.pop_sikh_pct else 0.05
            sc_val = float(const.pop_sc_pct) if const.pop_sc_pct else 17.15
            st_val = float(const.pop_st_pct) if const.pop_st_pct else 6.95
        else:
            c_name = obj.parliamentary_constituency_en or 'Parliamentary Constituency'
            c_type = 'general'
            d_name = 'Karnataka Region'
            pop = 1785400
            lit = 78.90
            sex = 968.0
            if 'Bangalore' in c_name or 'Bengaluru' in c_name:
                hindu, muslim, christian, jain, buddhist, sikh = 78.87, 13.90, 5.61, 0.97, 0.22, 0.14
                sc_val, st_val = 12.35, 1.74
            else:
                hindu, muslim, christian, jain, buddhist, sikh = 84.00, 12.90, 1.87, 0.72, 0.16, 0.05
                sc_val, st_val = 17.15, 6.95

        gen_val = max(0.0, round(100.0 - (sc_val + st_val), 2))
        return {
            'constituency_name': c_name,
            'constituency_type': c_type,
            'district_name': d_name,
            'population': pop,
            'literacy_rate': lit,
            'sex_ratio': sex,
            'religion_composition': {
                'hindu_pct': hindu,
                'muslim_pct': muslim,
                'christian_pct': christian,
                'jain_pct': jain,
                'buddhist_pct': buddhist,
                'sikh_pct': sikh,
            },
            'category_composition': {
                'sc_pct': sc_val,
                'st_pct': st_val,
                'general_pct': gen_val,
            }
        }


# =============================================================================
# Financial Declaration Serializers
# =============================================================================

class FinancialDeclarationSerializer(ReadOnlyModelSerializer):
    """
    Read-only serializer for Financial Declarations.
    Uses denormalized politician info to prevent N+1 queries.
    """
    
    politician_name = serializers.SerializerMethodField()
    party_name = serializers.SerializerMethodField()
    net_worth = serializers.DecimalField(
        max_digits=20, decimal_places=2, read_only=True
    )
    
    class Meta:
        model = FinancialDeclaration
        fields = [
            'id',
            'politician',
            'politician_name',
            'party_name',
            'declaration_year',
            'declaration_type',
            'declaration_date',
            'declaration_url',
            'total_assets',
            'total_liabilities',
            'net_worth',
            'is_verified',
        ]
        read_only_fields = fields
    
    def get_politician_name(self, obj):
        """Get politician name in requested language."""
        lang = get_request_language(self.context.get('request'), self.context)
        return get_bilingual_field(obj.politician, 'full_name', lang)
    
    def get_party_name(self, obj):
        """Get party name in requested language."""
        lang = get_request_language(self.context.get('request'), self.context)
        if obj.politician.current_party:
            return get_bilingual_field(obj.politician.current_party, 'party_name', lang)
        return None


class FinancialDeclarationDetailSerializer(ReadOnlyModelSerializer):
    """
    Detailed financial declaration with complete asset breakdown.
    """
    
    politician_name = serializers.SerializerMethodField()
    net_worth = serializers.DecimalField(
        max_digits=20, decimal_places=2, read_only=True
    )
    
    class Meta:
        model = FinancialDeclaration
        fields = [
            'id',
            'politician',
            'politician_name',
            'declaration_year',
            'declaration_type',
            'declaration_date',
            'declaration_url',
            # Movable Assets
            'total_assets',
            'bank_deposits',
            'shares_and_securities',
            'insurance_policies',
            'loans_received',
            'vehicles_count',
            'vehicles_value',
            'jewelry_value',
            'other_assets',
            # Immovable Assets
            'residential_property_count',
            'residential_property_value',
            'commercial_property_count',
            'commercial_property_value',
            'agricultural_land_acres',
            'agricultural_land_value',
            # Liabilities
            'total_liabilities',
            'personal_loans',
            'business_loans',
            'mortgage',
            'other_liabilities',
            # Metadata
            'is_verified',
            'notes',
        ]
        read_only_fields = fields
    
    def get_politician_name(self, obj):
        """Get politician name in requested language."""
        lang = get_request_language(self.context.get('request'), self.context)
        return get_bilingual_field(obj.politician, 'full_name', lang)


# =============================================================================
# Legal Record Serializers
# =============================================================================

class LegalRecordSerializer(ReadOnlyModelSerializer):
    """
    Read-only serializer for Legal/Criminal Records.
    """
    
    politician_name = serializers.SerializerMethodField()
    case_status_display = serializers.CharField(source='get_case_status_display', read_only=True)
    
    class Meta:
        model = LegalRecord
        fields = [
            'id',
            'politician',
            'politician_name',
            'case_number',
            'police_station',
            'district',
            'fir_date',
            'case_status',
            'case_status_display',
            'ipc_sections',
            'other_sections',
            'description_en',
            'court_name',
            'case_type',
            'case_url',
            'next_hearing_date',
            'is_verified',
        ]
        read_only_fields = fields
    
    def get_politician_name(self, obj):
        """Get politician name in requested language."""
        lang = get_request_language(self.context.get('request'), self.context)
        return get_bilingual_field(obj.politician, 'full_name', lang)


class LegalRecordDetailSerializer(ReadOnlyModelSerializer):
    """
    Detailed legal record with complete case information.
    """
    
    politician_name = serializers.SerializerMethodField()
    case_status_display = serializers.CharField(source='get_case_status_display', read_only=True)
    
    class Meta:
        model = LegalRecord
        fields = [
            'id',
            'politician',
            'politician_name',
            'case_number',
            'police_station',
            'district',
            'fir_date',
            'registration_date',
            'case_status',
            'case_status_display',
            'ipc_sections',
            'other_sections',
            'description_en',
            'description_kn',
            'court_name',
            'case_type',
            'case_url',
            'next_hearing_date',
            # Outcome
            'conviction_date',
            'sentence_details',
            'fine_amount',
            'imprisonment_years',
            'imprisonment_months',
            # Source
            'source_url',
            'source_organization',
            'is_verified',
            'verification_date',
        ]
        read_only_fields = fields
    
    def get_politician_name(self, obj):
        """Get politician name in requested language."""
        lang = get_request_language(self.context.get('request'), self.context)
        return get_bilingual_field(obj.politician, 'full_name', lang)


# =============================================================================
# Public Record Serializers
# =============================================================================

class PublicRecordSerializer(ReadOnlyModelSerializer):
    """
    Read-only serializer for Public Records (speeches, allegations, etc.).
    """
    
    politician_name = serializers.SerializerMethodField()
    record_type_display = serializers.CharField(source='get_record_type_display', read_only=True)
    verification_status_display = serializers.CharField(
        source='get_verification_status_display', read_only=True
    )
    language_display = serializers.CharField(source='get_language_display', read_only=True)
    
    class Meta:
        model = PublicRecord
        fields = [
            'id',
            'politician',
            'politician_name',
            'record_type',
            'record_type_display',
            'title_en',
            'title_kn',
            'content_en',
            'content_kn',
            'summary_en',
            'summary_kn',
            'categories',
            'tags',
            'event_name',
            'event_date',
            'location',
            'verification_status',
            'verification_status_display',
            'verified_by',
            'verification_date',
            'sentiment_score',
            'word_count',
            'language',
            'language_display',
            'source_url',
            'source_organization',
            'is_verified',
        ]
        read_only_fields = fields
    
    def get_politician_name(self, obj):
        """Get politician name in requested language."""
        lang = get_request_language(self.context.get('request'), self.context)
        return get_bilingual_field(obj.politician, 'full_name', lang)


class PublicRecordDetailSerializer(ReadOnlyModelSerializer):
    """
    Detailed public record with verification details.
    """
    
    politician_name = serializers.SerializerMethodField()
    record_type_display = serializers.CharField(source='get_record_type_display', read_only=True)
    verification_status_display = serializers.CharField(
        source='get_verification_status_display', read_only=True
    )
    
    class Meta:
        model = PublicRecord
        fields = [
            'id',
            'politician',
            'politician_name',
            'record_type',
            'record_type_display',
            'title_en',
            'title_kn',
            'content_en',
            'content_kn',
            'summary_en',
            'summary_kn',
            'categories',
            'tags',
            'event_name',
            'event_date',
            'location',
            'verification_status',
            'verification_status_display',
            'verification_details',
            'verified_by',
            'verification_date',
            'sentiment_score',
            'word_count',
            'language',
            'source_url',
            'source_organization',
            'is_verified',
            'created_at',
        ]
        read_only_fields = fields
    
    def get_politician_name(self, obj):
        """Get politician name in requested language."""
        lang = get_request_language(self.context.get('request'), self.context)
        return get_bilingual_field(obj.politician, 'full_name', lang)


# =============================================================================
# Constituency Fund Serializers
# =============================================================================

class ConstituencyFundSerializer(ReadOnlyModelSerializer):
    """
    Read-only serializer for Constituency Funds.
    """
    
    constituency_name = serializers.SerializerMethodField()
    district_name = serializers.SerializerMethodField()
    fund_type_display = serializers.CharField(source='get_fund_type_display', read_only=True)
    project_status_display = serializers.CharField(source='get_project_status_display', read_only=True)
    remaining_amount = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    
    class Meta:
        model = ConstituencyFund
        fields = [
            'id',
            'constituency',
            'constituency_name',
            'district_name',
            'fund_type',
            'fund_type_display',
            'financial_year',
            'allocated_amount',
            'utilized_amount',
            'utilization_percentage',
            'remaining_amount',
            'project_name_en',
            'project_name_kn',
            'project_status',
            'project_status_display',
            'completion_percentage',
            'utilization_url',
        ]
        read_only_fields = fields
    
    def get_constituency_name(self, obj):
        """Get constituency name in requested language."""
        lang = get_request_language(self.context.get('request'), self.context)
        return get_bilingual_field(obj.constituency, 'constituency_name', lang)
    
    def get_district_name(self, obj):
        """Get district name in requested language."""
        lang = get_request_language(self.context.get('request'), self.context)
        return get_bilingual_field(obj.constituency.district, 'district_name', lang)


class ConstituencyFundDetailSerializer(ReadOnlyModelSerializer):
    """
    Detailed constituency fund with project information.
    """
    
    constituency_name = serializers.SerializerMethodField()
    district_name = serializers.SerializerMethodField()
    fund_type_display = serializers.CharField(source='get_fund_type_display', read_only=True)
    project_status_display = serializers.CharField(source='get_project_status_display', read_only=True)
    remaining_amount = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    
    class Meta:
        model = ConstituencyFund
        fields = [
            'id',
            'constituency',
            'constituency_name',
            'district_name',
            'fund_type',
            'fund_type_display',
            'financial_year',
            'allocated_amount',
            'allocated_date',
            'utilized_amount',
            'utilization_date',
            'utilization_percentage',
            'remaining_amount',
            'project_name_en',
            'project_name_kn',
            'project_description_en',
            'project_description_kn',
            'implementing_agency',
            'contractor_name',
            'project_status',
            'project_status_display',
            'completion_percentage',
            'fund_source_url',
            'utilization_url',
            'notes',
        ]
        read_only_fields = fields
    
    def get_constituency_name(self, obj):
        """Get constituency name in requested language."""
        lang = get_request_language(self.context.get('request'), self.context)
        return get_bilingual_field(obj.constituency, 'constituency_name', lang)
    
    def get_district_name(self, obj):
        """Get district name in requested language."""
        lang = get_request_language(self.context.get('request'), self.context)
        return get_bilingual_field(obj.constituency.district, 'district_name', lang)