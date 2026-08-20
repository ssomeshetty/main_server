"""
Analytics API Endpoint for Karnataka Politicians Tracker.
Provides aggregate metrics, net worth leaderboards, party distribution, and demographics.

Optimized: All aggregation done at DB level (no Python-side loops loading all rows).
Cached for 30 minutes since aggregate data changes infrequently.
"""
from decimal import Decimal
from django.db.models import Count, Sum, Avg, Case, When, Value, IntegerField
from django.core.cache import cache
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.throttling import ScopedRateThrottle

from .models import Politician, FinancialDeclaration, Party, LegalRecord
from .serializers import get_request_language, get_bilingual_field


ANALYTICS_CACHE_TTL = getattr(settings, 'CACHE_TTL_ANALYTICS', 1800)


class AnalyticsAPIView(APIView):
    """
    GET /api/v1/analytics/
    Returns analytical insights, top asset rankings, party seat shares, and demographic data.

    Rate-limited to 10 req/min per IP (expensive aggregation queries).
    Cached for 30 minutes.
    """
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'analytics'

    def get(self, request, format=None):
        lang = get_request_language(request)

        # Check cache first (keyed by language)
        cache_key = f'analytics:v2:{lang}'
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        # 1. Total Summary Stats (single query with aggregation)
        summary_stats = Politician.objects.filter(is_active=True).aggregate(
            total_mlas=Count('id'),
            avg_age=Avg('age'),
        )
        total_mlas = summary_stats['total_mlas'] or 0
        avg_age_val = summary_stats['avg_age'] or 55.0

        # Financial aggregates (single query)
        fin_stats = FinancialDeclaration.objects.filter(
            politician__is_active=True
        ).aggregate(
            total_assets=Sum('total_assets'),
            total_liabilities=Sum('total_liabilities'),
        )
        total_assembly_assets = fin_stats['total_assets'] or Decimal('0')
        total_assembly_liabilities = fin_stats['total_liabilities'] or Decimal('0')

        total_legal_cases = LegalRecord.objects.filter(
            politician__is_active=True
        ).count()

        # 2. Top 10 Richest (single query with select_related)
        top_richest = self._build_ranking(
            FinancialDeclaration.objects.select_related(
                'politician', 'politician__current_party',
                'politician__current_constituency'
            ).filter(politician__is_active=True).order_by('-total_assets')[:10],
            lang
        )

        # 3. Top 10 Most Indebted
        top_indebted = self._build_ranking(
            FinancialDeclaration.objects.select_related(
                'politician', 'politician__current_party',
                'politician__current_constituency'
            ).filter(politician__is_active=True).order_by('-total_liabilities')[:10],
            lang
        )

        # 4. Party Distribution (single aggregate query, no Python loops)
        party_qs = Politician.objects.filter(is_active=True).values(
            'current_party__id',
            'current_party__party_short_name_en',
            'current_party__party_short_name_kn'
        ).annotate(seats=Count('id')).order_by('-seats')

        party_colors = {
            'INC': '#19AAED', 'BJP': '#FF9933', 'JD(S)': '#008000',
            'IND': '#888888', 'Ind': '#888888',
            'KRPP': '#9b59b6', 'SKP': '#e67e22',
        }
        party_distribution = []
        for item in party_qs:
            party_code = item.get('current_party__party_short_name_en') or 'Others'
            party_name = item.get(f'current_party__party_short_name_{lang}') or party_code
            seats = item['seats']
            pct = round((seats / total_mlas) * 100, 1) if total_mlas else 0.0
            party_distribution.append({
                'party_code': party_code,
                'party_name': party_name,
                'seats': seats,
                'percentage': pct,
                'color': party_colors.get(party_code, '#3b82f6'),
            })

        # 5. Age Demographics (DB-level aggregation with Case/When — no Python loop)
        age_agg = Politician.objects.filter(
            is_active=True, age__isnull=False
        ).aggregate(
            under_40=Count(Case(When(age__lt=40, then=1), output_field=IntegerField())),
            age_40_50=Count(Case(When(age__gte=40, age__lte=50, then=1), output_field=IntegerField())),
            age_51_60=Count(Case(When(age__gte=51, age__lte=60, then=1), output_field=IntegerField())),
            age_61_70=Count(Case(When(age__gte=61, age__lte=70, then=1), output_field=IntegerField())),
            over_70=Count(Case(When(age__gt=70, then=1), output_field=IntegerField())),
        )
        age_demographics = [
            {'bracket': k, 'count': v, 'percentage': round((v / total_mlas) * 100, 1) if total_mlas else 0}
            for k, v in [
                ('< 40', age_agg['under_40']),
                ('40 - 50', age_agg['age_40_50']),
                ('51 - 60', age_agg['age_51_60']),
                ('61 - 70', age_agg['age_61_70']),
                ('70+', age_agg['over_70']),
            ]
        ]

        # 6. Education Breakdown (static for now — MLA-only data covering 224 assembly seats)
        edu_counts = {
            'Doctorate / PhD': 6,
            'Post Graduate': 28,
            'Graduate / Professional': 142,
            'Higher Secondary (12th / PUC)': 32,
            'Secondary (10th / SSLC)': 16,
        }
        total_edu_base = 224  # Education data covers 224 assembly MLAs only
        education_demographics = [
            {'level': k, 'count': v, 'percentage': round((v / total_edu_base) * 100, 1)}
            for k, v in edu_counts.items()
        ]

        result = {
            'summary': {
                'total_mlas': total_mlas,
                'total_assembly_assets_cr': round(float(total_assembly_assets) / 10000000.0, 1),
                'total_assembly_liabilities_cr': round(float(total_assembly_liabilities) / 10000000.0, 1),
                'average_age': round(float(avg_age_val), 1),
                'total_legal_cases': total_legal_cases,
            },
            'top_richest': top_richest,
            'top_indebted': top_indebted,
            'party_distribution': party_distribution,
            'age_demographics': age_demographics,
            'education_demographics': education_demographics,
        }

        # Cache the result
        cache.set(cache_key, result, ANALYTICS_CACHE_TTL)

        return Response(result)

    def _build_ranking(self, queryset, lang):
        """Build ranking list from financial declaration queryset."""
        ranking = []
        for idx, item in enumerate(queryset, 1):
            pol = item.politician
            party_name = (
                get_bilingual_field(pol.current_party, 'party_short_name', lang)
                if pol.current_party else 'IND'
            )
            const_name = (
                get_bilingual_field(pol.current_constituency, 'constituency_name', lang)
                if pol.current_constituency else ''
            )
            ranking.append({
                'rank': idx,
                'id': pol.id,
                'slug': pol.slug,
                'name': get_bilingual_field(pol, 'full_name', lang),
                'photo_url': pol.photo_url or '',
                'party': party_name,
                'constituency': const_name,
                'total_assets_cr': round(float(item.total_assets) / 10000000.0, 2),
                'total_liabilities_cr': round(float(item.total_liabilities) / 10000000.0, 2),
            })
        return ranking
