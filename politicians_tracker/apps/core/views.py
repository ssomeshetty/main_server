"""
Django REST Framework ViewSets for Read-Only Public API
========================================================
Optimized for high-scale read performance with cursor pagination and N+1 prevention.
Hardened against SQL injection, input manipulation, and crash vectors.
"""

import logging
from datetime import date

from rest_framework import viewsets, mixins, status as http_status
from rest_framework.response import Response
from rest_framework.pagination import CursorPagination
from rest_framework.throttling import ScopedRateThrottle
from django.db.models import Prefetch, Count, Q, F, Subquery, OuterRef, IntegerField
from django.db.models.functions import Coalesce
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.core.cache import cache

from .models import (
    District, Constituency, Politician, Party,
    FinancialDeclaration, LegalRecord, PublicRecord, ConstituencyFund
)
from .serializers import (
    DistrictSerializer, DistrictListSerializer,
    ConstituencySerializer, ConstituencyListSerializer,
    PartySerializer,
    PoliticianListSerializer, PoliticianDetailSerializer,
    FinancialDeclarationSerializer, FinancialDeclarationDetailSerializer,
    LegalRecordSerializer, LegalRecordDetailSerializer,
    PublicRecordSerializer, PublicRecordDetailSerializer,
    ConstituencyFundSerializer, ConstituencyFundDetailSerializer,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Input Validation Helpers (prevent injection + crash vectors)
# =============================================================================

def safe_int(value, default=None):
    """Safely parse an integer from query param. Returns default on failure."""
    if value is None:
        return default
    try:
        result = int(value)
        return result if result >= 0 else default
    except (ValueError, TypeError):
        return default


def safe_float(value, default=None, min_val=None, max_val=None):
    """Safely parse a float with optional bounds."""
    if value is None:
        return default
    try:
        result = float(value)
        if min_val is not None and result < min_val:
            return default
        if max_val is not None and result > max_val:
            return default
        return result
    except (ValueError, TypeError):
        return default


def safe_date(value):
    """Safely parse ISO date string. Returns None on failure."""
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def sanitize_search(value, max_length=200):
    """Sanitize search input: strip, truncate, remove null bytes."""
    if not value:
        return None
    cleaned = value.strip().replace('\x00', '')[:max_length]
    return cleaned if cleaned else None


def validate_ordering(requested, allowed_fields, default='-id'):
    """
    Whitelist-validate an ordering parameter against allowed fields.
    Prevents SQL injection via .order_by() with arbitrary field names.
    """
    if not requested:
        return default
    # Build full allow-set including descending variants
    allowed = set()
    for f in allowed_fields:
        allowed.add(f)
        allowed.add(f'-{f}')
    if requested in allowed:
        return requested
    return default


# =============================================================================
# Custom Cursor Pagination (Optimized for MySQL Performance)
# =============================================================================

class BaseCursorPagination(CursorPagination):
    """
    Base cursor pagination with ordering by created_at for consistent pagination.
    Uses '-created_at, id' ordering for forward/backward navigation.
    """
    ordering = '-id'
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 300

    def get_ordering(self, request, queryset, view):
        ordering = request.query_params.get('ordering')
        if not ordering:
            default_ord = getattr(view, 'default_ordering', self.ordering)
            return (default_ord,) if isinstance(default_ord, str) else tuple(default_ord)

        # Whitelist validation - only allow known indexed fields
        allowed = getattr(view, 'allowed_ordering_fields', [])
        validated = validate_ordering(ordering, allowed, self.ordering)

        # Cursor pagination requires a tie-breaker for non-unique fields
        if validated.startswith('-'):
            return (validated, '-id')
        return (validated, 'id')


class PoliticianCursorPagination(BaseCursorPagination):
    """Pagination optimized for politician lists."""
    page_size = 20
    max_page_size = 300
    page_size_query_param = 'page_size'


class DistrictCursorPagination(BaseCursorPagination):
    """Pagination optimized for district lists."""
    page_size = 30


class ConstituencyCursorPagination(BaseCursorPagination):
    """Pagination optimized for constituency lists."""
    page_size = 50


class RecordsCursorPagination(BaseCursorPagination):
    """Pagination optimized for financial/legal/public records."""
    page_size = 25


# =============================================================================
# Read-Only ViewSet Mixin
# =============================================================================

class ReadOnlyViewSetMixin:
    """
    Mixin that disables all write operations.
    Ensures API is read-only for public data.
    """
    
    def get_queryset(self):
        """Return read-only queryset."""
        queryset = super().get_queryset()
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Disable POST operations."""
        return self._disabled_response('POST')
    
    def update(self, request, *args, **kwargs):
        """Disable PUT operations."""
        return self._disabled_response('PUT')
    
    def partial_update(self, request, *args, **kwargs):
        """Disable PATCH operations."""
        return self._disabled_response('PATCH')
    
    def destroy(self, request, *args, **kwargs):
        """Disable DELETE operations."""
        return self._disabled_response('DELETE')
    
    def _disabled_response(self, method):
        """Return 405 Method Not Allowed response."""
        from rest_framework.views import exception_handler
        from rest_framework.response import Response
        from rest_framework import status
        
        return Response(
            {'error': f'{method} operations are disabled. This is a read-only API.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


# =============================================================================
# District ViewSet
# =============================================================================

class DistrictViewSet(ReadOnlyViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    Read-only API endpoint for Districts.
    
    List: GET /api/districts/
    Detail: GET /api/districts/{id}/
    
    Supports ?lang=kn for Kannada language responses.
    Uses cursor pagination for consistent performance.
    """
    serializer_class = DistrictSerializer
    lookup_field = 'id'
    default_ordering = 'district_name_en'
    
    def get_queryset(self):
        """Optimized queryset with select_related."""
        queryset = District.objects.all()
        
        # Annotate politician count for each district
        queryset = queryset.annotate(
            politician_count=Subquery(
                Politician.objects.filter(
                    current_constituency__district=OuterRef('pk')
                ).values('current_constituency__district').annotate(
                    cnt=Count('id')
                ).values('cnt')[:1]
            )
        )
        
        return queryset.order_by('district_name_en')
    
    def get_serializer_class(self):
        """Use lighter serializer for list view."""
        if self.action == 'list':
            return DistrictListSerializer
        return DistrictSerializer
    
    def list(self, request, *args, **kwargs):
        """List districts with optional filtering."""
        queryset = self.get_queryset()
        
        # Region filter
        region = request.query_params.get('region')
        if region:
            queryset = queryset.filter(region=region)
        
        # Search filter
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(district_name_en__icontains=search) |
                Q(district_name_kn__icontains=search)
            )
        
        # Apply pagination
        paginator = DistrictCursorPagination()
        page = paginator.paginate_queryset(queryset, request, self)
        
        serializer = DistrictListSerializer(
            page, many=True, context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """Get district detail with constituencies."""
        instance = self.get_object()
        
        # Prefetch constituencies for detail view
        constituencies = Constituency.objects.filter(
            district=instance
        ).order_by('constituency_number')
        
        # Add constituency count
        instance.constituency_count = constituencies.count()
        instance._prefetched_constituencies = constituencies
        
        serializer = DistrictSerializer(instance, context={'request': request})
        return Response(serializer.data)


# =============================================================================
# Constituency ViewSet
# =============================================================================

class ConstituencyViewSet(ReadOnlyViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    Read-only API endpoint for Constituencies.
    
    List: GET /api/constituencies/
    Detail: GET /api/constituencies/{id}/
    
    Supports ?lang=kn for Kannada language responses.
    Supports filtering by district_id, constituency_type.
    """
    serializer_class = ConstituencySerializer
    lookup_field = 'id'
    default_ordering = 'constituency_number'
    
    def get_queryset(self):
        """Optimized queryset with select_related for district."""
        queryset = Constituency.objects.select_related('district').all()
        
        # Filter by district
        district_id = self.request.query_params.get('district')
        if district_id:
            queryset = queryset.filter(district_id=district_id)
        
        # Filter by type
        const_type = self.request.query_params.get('type')
        if const_type:
            queryset = queryset.filter(constituency_type=const_type)
        
        # Filter by region (via district)
        region = self.request.query_params.get('region')
        if region:
            queryset = queryset.filter(district__region=region)
        
        # Search filter
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(constituency_name_en__icontains=search) |
                Q(constituency_name_kn__icontains=search)
            )
        
        return queryset.order_by('constituency_number')
    
    def get_serializer_class(self):
        """Use lighter serializer for list view."""
        if self.action == 'list':
            return ConstituencyListSerializer
        return ConstituencySerializer
    
    def list(self, request, *args, **kwargs):
        """List constituencies with pagination."""
        queryset = self.get_queryset()
        
        # Apply pagination
        paginator = ConstituencyCursorPagination()
        page = paginator.paginate_queryset(queryset, request, self)
        
        serializer = ConstituencyListSerializer(
            page, many=True, context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)


# =============================================================================
# Party ViewSet
# =============================================================================

class PartyViewSet(ReadOnlyViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    Read-only API endpoint for Political Parties.
    
    List: GET /api/parties/
    Detail: GET /api/parties/{id}/
    
    Supports ?lang=kn for Kannada language responses.
    """
    serializer_class = PartySerializer
    lookup_field = 'id'
    default_ordering = 'party_name_en'
    
    def get_queryset(self):
        """Optimized queryset with active filter."""
        queryset = Party.objects.filter(is_active=True)
        
        # Filter by type
        party_type = self.request.query_params.get('type')
        if party_type:
            queryset = queryset.filter(party_type=party_type)
        
        # Search filter
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(party_name_en__icontains=search) |
                Q(party_name_kn__icontains=search) |
                Q(party_short_name_en__icontains=search) |
                Q(party_short_name_kn__icontains=search)
            )
        
        return queryset.order_by('party_name_en')
    
    def list(self, request, *args, **kwargs):
        """List parties."""
        queryset = self.get_queryset()
        
        # Apply pagination
        paginator = DistrictCursorPagination()
        page = paginator.paginate_queryset(queryset, request, self)
        
        serializer = PartySerializer(
            page, many=True, context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)


# =============================================================================
# Politician ViewSet
# =============================================================================

class PoliticianViewSet(ReadOnlyViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    Read-only API endpoint for Politicians.
    
    List: GET /api/politicians/
    Detail: GET /api/politicians/{id}/
    
    Supports ?lang=kn for Kannada language responses.
    Optimized with select_related/prefetch_related to prevent N+1 queries.
    """
    serializer_class = PoliticianDetailSerializer
    lookup_field = 'slug'
    pagination_class = PoliticianCursorPagination
    allowed_ordering_fields = [
        'full_name_en',
        'full_name_kn',
        'total_terms_won',
        'total_terms_contested',
        'created_at',
    ]
    default_ordering = 'full_name_en'
    
    def get_queryset(self):
        """
        Optimized queryset with prefetch for related data.
        Uses select_related for ForeignKey and prefetch_related for reverse FK.
        """
        queryset = Politician.objects.select_related(
            'current_party',
            'current_constituency',
            'current_constituency__district',
        ).filter(is_active=True)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by verification
        is_verified = self.request.query_params.get('is_verified')
        if is_verified is not None:
            queryset = queryset.filter(is_verified=is_verified.lower() == 'true')
        
        # Filter by party
        party_id = self.request.query_params.get('party')
        if party_id:
            queryset = queryset.filter(current_party_id=party_id)
        
        # Filter by constituency
        constituency_id = self.request.query_params.get('constituency')
        if constituency_id:
            queryset = queryset.filter(current_constituency_id=constituency_id)
        
        # Filter by district (via constituency)
        district_id = self.request.query_params.get('district')
        if district_id:
            queryset = queryset.filter(current_constituency__district_id=district_id)
        
        # Filter by gender
        gender = self.request.query_params.get('gender')
        if gender:
            queryset = queryset.filter(gender=gender)
        
        # Filter by minister status (supports both is_minister and minister)
        is_minister = self.request.query_params.get('is_minister') or self.request.query_params.get('minister')
        if is_minister is not None:
            if str(is_minister).lower() in ['true', '1']:
                queryset = queryset.filter(is_minister=True)
            elif str(is_minister).lower() in ['false', '0']:
                queryset = queryset.filter(is_minister=False)

        # Filter by union minister status
        is_union_minister = self.request.query_params.get('is_union_minister')
        if is_union_minister is not None:
            if str(is_union_minister).lower() in ['true', '1']:
                queryset = queryset.filter(is_union_minister=True)
            elif str(is_union_minister).lower() in ['false', '0']:
                queryset = queryset.filter(is_union_minister=False)

        # Filter by representative type (mla, mp_ls, mp_rs, mp, union_minister, state_minister)
        rep_type = self.request.query_params.get('representative_type') or self.request.query_params.get('type')
        if rep_type:
            if rep_type == 'mp':
                queryset = queryset.filter(representative_type__in=['mp_ls', 'mp_rs'])
            elif rep_type == 'union_minister':
                queryset = queryset.filter(is_union_minister=True)
            elif rep_type == 'state_minister':
                queryset = queryset.filter(is_minister=True)
            else:
                queryset = queryset.filter(representative_type=rep_type)
        
        # Search filter (bilingual name, party, constituency)
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(full_name_en__icontains=search) |
                Q(full_name_kn__icontains=search) |
                Q(first_name_en__icontains=search) |
                Q(last_name_en__icontains=search) |
                Q(current_party__party_name_en__icontains=search) |
                Q(current_party__party_short_name_en__icontains=search) |
                Q(current_constituency__constituency_name_en__icontains=search) |
                Q(current_constituency__constituency_name_kn__icontains=search)
            )
        
        # Ordering
        ordering = self.request.query_params.get('ordering', 'full_name_en')
        valid_orderings = [
            'full_name_en', '-full_name_en',
            'full_name_kn', '-full_name_kn',
            'total_terms_won', '-total_terms_won',
            'total_terms_contested', '-total_terms_contested',
            'created_at', '-created_at',
        ]
        if ordering in valid_orderings:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by('full_name_en')
        
        return queryset
    
    def get_serializer_class(self):
        """Use lighter serializer for list view."""
        if self.action == 'list':
            return PoliticianListSerializer
        return PoliticianDetailSerializer
    
    @method_decorator(cache_page(300))  # 5 min Redis cache
    @method_decorator(vary_on_headers('Accept-Language'))
    def list(self, request, *args, **kwargs):
        """List politicians with filtering and pagination."""
        queryset = self.get_queryset()
        
        # Apply pagination
        paginator = PoliticianCursorPagination()
        page = paginator.paginate_queryset(queryset, request, self)
        
        serializer = PoliticianListSerializer(
            page, many=True, context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)

    def get_object(self):
        from django.shortcuts import get_object_or_404
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_value = self.kwargs[lookup_url_kwarg]
        
        if filter_value.isdigit():
            filter_kwargs = {'id': filter_value}
        else:
            filter_kwargs = {self.lookup_field: filter_value}
            
        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj
    
    @method_decorator(cache_page(300))  # 5 min Redis cache
    @method_decorator(vary_on_headers('Accept-Language'))
    def retrieve(self, request, *args, **kwargs):
        """Get politician detail with all related data (N+1 safe)."""
        instance = self.get_object()

        # Prefetch related data into instance's cache for serializer to use
        # This avoids 3 separate queries per detail request
        from django.db.models import Prefetch
        prefetched = Politician.objects.filter(pk=instance.pk).prefetch_related(
            Prefetch(
                'financial_declarations',
                queryset=FinancialDeclaration.objects.order_by('-declaration_year')
            ),
            Prefetch(
                'legal_records',
                queryset=LegalRecord.objects.order_by('-fir_date')
            ),
            Prefetch(
                'public_records',
                queryset=PublicRecord.objects.order_by('-event_date')
            ),
        ).select_related(
            'current_party',
            'current_constituency',
            'current_constituency__district',
        ).first()

        if prefetched is None:
            from django.http import Http404
            raise Http404

        serializer = PoliticianDetailSerializer(
            prefetched, context={'request': request}
        )
        return Response(serializer.data)

# =============================================================================
# Financial Declaration ViewSet
# =============================================================================

class FinancialDeclarationViewSet(ReadOnlyViewSetMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Read-only API endpoint for Financial Declarations.
    
    List: GET /api/financial-declarations/
    Detail: GET /api/financial-declarations/{id}/
    
    Supports filtering by politician_id, year.
    Optimized with select_related for politician and party.
    """
    serializer_class = FinancialDeclarationSerializer
    lookup_field = 'id'
    pagination_class = RecordsCursorPagination
    allowed_ordering_fields = ['declaration_year', 'total_assets', 'total_liabilities', 'id']
    default_ordering = '-declaration_year'
    
    def get_queryset(self):
        """
        Optimized queryset with select_related for politician and party.
        """
        queryset = FinancialDeclaration.objects.select_related(
            'politician',
            'politician__current_party',
        ).all()
        
        # Filter by politician
        politician_id = self.request.query_params.get('politician')
        if politician_id:
            queryset = queryset.filter(politician_id=politician_id)
        
        # Filter by year (safe int parsing)
        year = safe_int(self.request.query_params.get('year'))
        if year:
            queryset = queryset.filter(declaration_year=year)

        # Year range filter (safe int parsing)
        year_gte = safe_int(self.request.query_params.get('year_gte'))
        if year_gte:
            queryset = queryset.filter(declaration_year__gte=year_gte)

        year_lte = safe_int(self.request.query_params.get('year_lte'))
        if year_lte:
            queryset = queryset.filter(declaration_year__lte=year_lte)

        # Filter by declaration type
        decl_type = self.request.query_params.get('type')
        if decl_type:
            queryset = queryset.filter(declaration_type=decl_type)

        # Ordering (whitelist-validated to prevent SQL injection)
        ordering = validate_ordering(
            self.request.query_params.get('ordering'),
            ['declaration_year', 'total_assets', 'total_liabilities', 'id'],
            default='-declaration_year'
        )
        queryset = queryset.order_by(ordering)
        
        return queryset
    
    def get_serializer_class(self):
        """Use detail serializer for single object view."""
        if self.action == 'list':
            return FinancialDeclarationSerializer
        return FinancialDeclarationDetailSerializer
    
    def list(self, request, *args, **kwargs):
        """List financial declarations with filtering."""
        queryset = self.get_queryset()
        
        # Apply pagination
        paginator = RecordsCursorPagination()
        page = paginator.paginate_queryset(queryset, request, self)
        
        serializer = FinancialDeclarationSerializer(
            page, many=True, context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)


# =============================================================================
# Legal Record ViewSet
# =============================================================================

class LegalRecordViewSet(ReadOnlyViewSetMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Read-only API endpoint for Legal/Criminal Records.
    
    List: GET /api/legal-records/
    Detail: GET /api/legal-records/{id}/
    
    Supports filtering by politician_id, case_status, district.
    Optimized with select_related for politician.
    """
    serializer_class = LegalRecordSerializer
    lookup_field = 'id'
    pagination_class = RecordsCursorPagination
    allowed_ordering_fields = ['fir_date', 'case_status', 'id']
    default_ordering = '-fir_date'
    
    def get_queryset(self):
        """
        Optimized queryset with select_related for politician.
        """
        queryset = LegalRecord.objects.select_related(
            'politician',
            'politician__current_party',
            'politician__current_constituency',
        ).all()
        
        # Filter by politician
        politician_id = self.request.query_params.get('politician')
        if politician_id:
            queryset = queryset.filter(politician_id=politician_id)
        
        # Filter by case status
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(case_status=status)
        
        # Filter by district
        district = self.request.query_params.get('district')
        if district:
            queryset = queryset.filter(district=district)
        
        # Filter by police station
        police_station = self.request.query_params.get('police_station')
        if police_station:
            queryset = queryset.filter(police_station__icontains=police_station)
        
        # Filter by verification
        is_verified = self.request.query_params.get('is_verified')
        if is_verified is not None:
            queryset = queryset.filter(is_verified=is_verified.lower() == 'true')
        
        # Search in description
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(description_en__icontains=search) |
                Q(case_number__icontains=search)
            )
        
        # Ordering (whitelist-validated)
        ordering = validate_ordering(
            self.request.query_params.get('ordering'),
            ['fir_date', 'case_status', 'id'],
            default='-fir_date'
        )
        queryset = queryset.order_by(ordering)

        return queryset
    
    def get_serializer_class(self):
        """Use detail serializer for single object view."""
        if self.action == 'list':
            return LegalRecordSerializer
        return LegalRecordDetailSerializer
    
    def list(self, request, *args, **kwargs):
        """List legal records with filtering."""
        queryset = self.get_queryset()
        
        # Apply pagination
        paginator = RecordsCursorPagination()
        page = paginator.paginate_queryset(queryset, request, self)
        
        serializer = LegalRecordSerializer(
            page, many=True, context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)


# =============================================================================
# Public Record ViewSet
# =============================================================================

class PublicRecordViewSet(ReadOnlyViewSetMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Read-only API endpoint for Public Records (speeches, allegations, etc.).
    
    List: GET /api/public-records/
    Detail: GET /api/public-records/{id}/
    
    Supports filtering by politician_id, record_type, verification_status.
    Optimized with select_related for politician.
    """
    serializer_class = PublicRecordSerializer
    lookup_field = 'id'
    pagination_class = RecordsCursorPagination
    allowed_ordering_fields = ['event_date', 'record_type', 'id']
    default_ordering = '-event_date'
    
    def get_queryset(self):
        """
        Optimized queryset with select_related for politician.
        """
        queryset = PublicRecord.objects.select_related(
            'politician',
            'politician__current_party',
            'politician__current_constituency',
        ).all()
        
        # Filter by politician
        politician_id = self.request.query_params.get('politician')
        if politician_id:
            queryset = queryset.filter(politician_id=politician_id)
        
        # Filter by record type
        record_type = self.request.query_params.get('type')
        if record_type:
            queryset = queryset.filter(record_type=record_type)
        
        # Filter by verification status
        verification = self.request.query_params.get('verification')
        if verification:
            queryset = queryset.filter(verification_status=verification)
        
        # Filter by categories (JSON array field)
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(categories__contains=[category])
        
        # Filter by tags (JSON array field)
        tag = self.request.query_params.get('tag')
        if tag:
            queryset = queryset.filter(tags__contains=[tag])
        
        # Filter by language
        language = self.request.query_params.get('language')
        if language:
            queryset = queryset.filter(language=language)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(event_date__gte=date_from)
        
        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(event_date__lte=date_to)
        
        # Search in content
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title_en__icontains=search) |
                Q(content_en__icontains=search) |
                Q(summary_en__icontains=search)
            )
        
        # Ordering (whitelist-validated)
        ordering = validate_ordering(
            self.request.query_params.get('ordering'),
            ['event_date', 'record_type', 'id'],
            default='-event_date'
        )
        queryset = queryset.order_by(ordering)

        return queryset
    
    def get_serializer_class(self):
        """Use detail serializer for single object view."""
        if self.action == 'list':
            return PublicRecordSerializer
        return PublicRecordDetailSerializer
    
    def list(self, request, *args, **kwargs):
        """List public records with filtering."""
        queryset = self.get_queryset()
        
        # Apply pagination
        paginator = RecordsCursorPagination()
        page = paginator.paginate_queryset(queryset, request, self)
        
        serializer = PublicRecordSerializer(
            page, many=True, context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)


# =============================================================================
# Constituency Fund ViewSet
# =============================================================================

class ConstituencyFundViewSet(ReadOnlyViewSetMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Read-only API endpoint for Constituency Funds.
    
    List: GET /api/constituency-funds/
    Detail: GET /api/constituency-funds/{id}/
    
    Supports filtering by constituency_id, financial_year, fund_type.
    Optimized with select_related for constituency and district.
    """
    serializer_class = ConstituencyFundSerializer
    lookup_field = 'id'
    pagination_class = RecordsCursorPagination
    allowed_ordering_fields = ['financial_year', 'allocated_amount', 'utilized_amount', 'utilization_percentage', 'id']
    default_ordering = '-financial_year'
    
    def get_queryset(self):
        """
        Optimized queryset with select_related for constituency and district.
        """
        queryset = ConstituencyFund.objects.select_related(
            'constituency',
            'constituency__district',
        ).all()
        
        # Filter by constituency
        constituency_id = self.request.query_params.get('constituency')
        if constituency_id:
            queryset = queryset.filter(constituency_id=constituency_id)
        
        # Filter by district
        district_id = self.request.query_params.get('district')
        if district_id:
            queryset = queryset.filter(constituency__district_id=district_id)
        
        # Filter by financial year
        financial_year = self.request.query_params.get('year')
        if financial_year:
            queryset = queryset.filter(financial_year=financial_year)
        
        # Filter by fund type
        fund_type = self.request.query_params.get('type')
        if fund_type:
            queryset = queryset.filter(fund_type=fund_type)
        
        # Filter by project status
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(project_status=status)
        
        # Filter by utilization percentage range (safe float parsing)
        util_min = safe_float(self.request.query_params.get('util_min'), min_val=0, max_val=100)
        if util_min is not None:
            queryset = queryset.filter(utilization_percentage__gte=util_min)

        util_max = safe_float(self.request.query_params.get('util_max'), min_val=0, max_val=100)
        if util_max is not None:
            queryset = queryset.filter(utilization_percentage__lte=util_max)

        # Ordering (whitelist-validated)
        ordering = validate_ordering(
            self.request.query_params.get('ordering'),
            ['financial_year', 'allocated_amount', 'utilized_amount', 'utilization_percentage', 'id'],
            default='-financial_year'
        )
        queryset = queryset.order_by(ordering)

        return queryset
    
    def get_serializer_class(self):
        """Use detail serializer for single object view."""
        if self.action == 'list':
            return ConstituencyFundSerializer
        return ConstituencyFundDetailSerializer
    
    def list(self, request, *args, **kwargs):
        """List constituency funds with filtering."""
        queryset = self.get_queryset()
        
        # Apply pagination
        paginator = RecordsCursorPagination()
        page = paginator.paginate_queryset(queryset, request, self)
        
        serializer = ConstituencyFundSerializer(
            page, many=True, context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)


# =============================================================================
# API Root View
# =============================================================================

from rest_framework.decorators import api_view

@api_view(['GET'])
def api_root(request, format=None):
    """
    API Root endpoint showing available endpoints.
    """
    return Response({
        'districts': {
            'list': '/api/districts/',
            'detail': '/api/districts/{id}/',
        },
        'constituencies': {
            'list': '/api/constituencies/',
            'detail': '/api/constituencies/{id}/',
        },
        'parties': {
            'list': '/api/parties/',
            'detail': '/api/parties/{id}/',
        },
        'politicians': {
            'list': '/api/politicians/',
            'detail': '/api/politicians/{id}/',
        },
        'financial-declarations': {
            'list': '/api/financial-declarations/',
            'detail': '/api/financial-declarations/{id}/',
        },
        'legal-records': {
            'list': '/api/legal-records/',
            'detail': '/api/legal-records/{id}/',
        },
        'public-records': {
            'list': '/api/public-records/',
            'detail': '/api/public-records/{id}/',
        },
        'constituency-funds': {
            'list': '/api/constituency-funds/',
            'detail': '/api/constituency-funds/{id}/',
        },
    })

# =============================================================================
# Combined ViewSets for Enhanced Views
# =============================================================================

class DistrictConstituencyViewSet(ReadOnlyViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """District with its constituencies."""
    serializer_class = DistrictSerializer
    lookup_field = 'id'
    
    def get_queryset(self):
        return District.objects.all().prefetch_related('constituencies').order_by('district_name_en')
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        paginator = DistrictCursorPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = DistrictSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = DistrictDetailSerializer(instance, context={'request': request})
        return Response(serializer.data)


class PoliticianByConstituencyViewSet(ReadOnlyViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """Politicians by constituency."""
    serializer_class = PoliticianListSerializer
    pagination_class = PoliticianCursorPagination
    
    def get_queryset(self):
        constituency_id = self.kwargs.get('constituency_pk')
        return Politician.objects.filter(current_constituency_id=constituency_id).select_related(
            'current_party', 'current_constituency', 'current_constituency__district'
        ).filter(is_active=True).order_by('full_name_en')
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        paginator = PoliticianCursorPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = PoliticianListSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)


# =============================================================================
# Palantir Intelligence Data Engine Views
# =============================================================================

from rest_framework.views import APIView
from rest_framework import status as drf_status
from politicians_tracker.apps.core.intelligence_engine import PalantirIntelligenceEngine


class PoliticianIntelligenceView(APIView):
    """
    Palantir Intelligence Analytics Engine Endpoint for a specific politician.
    GET /api/v1/intelligence/politician/{slug}/

    Cached for 30 minutes (expensive multi-query aggregation).
    """
    permission_classes = []

    def get(self, request, slug, format=None):
        # Check cache first
        cache_key = f'intelligence:politician:{slug}'
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached, status=drf_status.HTTP_200_OK)

        try:
            if slug.isdigit():
                pol = Politician.objects.get(id=int(slug))
            else:
                pol = Politician.objects.get(slug=slug)
        except Politician.DoesNotExist:
            return Response({'error': 'Politician profile not found.'}, status=drf_status.HTTP_404_NOT_FOUND)

        engine = PalantirIntelligenceEngine(pol)
        report = engine.get_full_intelligence_report()

        # Cache for 30 minutes
        cache.set(cache_key, report, 1800)
        return Response(report, status=drf_status.HTTP_200_OK)


class NetworkGraphView(APIView):
    """
    Knowledge Graph Topology Endpoint.
    GET /api/v1/intelligence/network-graph/?slug={slug}

    Cached for 30 minutes.
    """
    permission_classes = []

    def get(self, request, format=None):
        slug = request.query_params.get('slug')
        if not slug:
            pol = Politician.objects.first()
            if not pol:
                return Response({'error': 'No politicians available'}, status=drf_status.HTTP_404_NOT_FOUND)
        else:
            try:
                pol = Politician.objects.get(slug=slug) if not slug.isdigit() else Politician.objects.get(id=int(slug))
            except Politician.DoesNotExist:
                return Response({'error': 'Politician not found.'}, status=drf_status.HTTP_404_NOT_FOUND)

        # Check cache
        cache_key = f'intelligence:network:{pol.slug}'
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached, status=drf_status.HTTP_200_OK)

        engine = PalantirIntelligenceEngine(pol)
        graph = engine.generate_knowledge_graph()

        cache.set(cache_key, graph, 1800)
        return Response(graph, status=drf_status.HTTP_200_OK)


# =============================================================================
# Python High-Level Visualization Chart Views (Matplotlib & Seaborn)
# =============================================================================

from django.http import HttpResponse
from politicians_tracker.apps.core.chart_generator import generate_demographic_donut_chart, generate_electoral_bar_chart


class DemographicChartView(APIView):
    """
    Generates a high-level Python Matplotlib/Seaborn demographic SVG chart.
    GET /api/v1/charts/demographics/<constituency_id>/

    Cached for 2 hours (demographic data is static Census 2011 data).
    """
    permission_classes = []

    def get(self, request, constituency_id, format=None):
        # Check cache first (demographic data is static)
        cache_key = f'chart:demographics:{constituency_id}'
        cached_svg = cache.get(cache_key)
        if cached_svg is not None:
            return HttpResponse(cached_svg, content_type='image/svg+xml')

        try:
            constituency = Constituency.objects.select_related('district').get(id=constituency_id)
        except Constituency.DoesNotExist:
            return Response({'error': 'Constituency not found.'}, status=drf_status.HTTP_404_NOT_FOUND)

        demo_data = {
            'constituency_name': constituency.constituency_name_en,
            'district_name': constituency.district.district_name_en if constituency.district else '',
            'religion_composition': {
                'hindu_pct': float(constituency.pop_hindu_pct or 0),
                'muslim_pct': float(constituency.pop_muslim_pct or 0),
                'christian_pct': float(constituency.pop_christian_pct or 0),
                'jain_pct': float(constituency.pop_jain_pct or 0),
                'buddhist_pct': float(constituency.pop_buddhist_pct or 0),
                'sikh_pct': float(constituency.pop_sikh_pct or 0),
            }
        }

        svg_chart = generate_demographic_donut_chart(demo_data)

        # Cache for 2 hours
        cache.set(cache_key, svg_chart, 7200)
        return HttpResponse(svg_chart, content_type='image/svg+xml')
