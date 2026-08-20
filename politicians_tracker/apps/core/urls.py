from django.urls import path, include
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from .views import (
    DistrictViewSet, ConstituencyViewSet, PartyViewSet,
    PoliticianViewSet, FinancialDeclarationViewSet,
    LegalRecordViewSet, PublicRecordViewSet,
    ConstituencyFundViewSet, api_root,
    PoliticianIntelligenceView, NetworkGraphView, DemographicChartView
)

# Create router
router = DefaultRouter()

# Register viewsets
router.register(r'districts', DistrictViewSet, basename='district')
router.register(r'constituencies', ConstituencyViewSet, basename='constituency')
router.register(r'parties', PartyViewSet, basename='party')
router.register(r'politicians', PoliticianViewSet, basename='politician')
router.register(r'financial-declarations', FinancialDeclarationViewSet, basename='financial-declaration')
router.register(r'legal-records', LegalRecordViewSet, basename='legal-record')
router.register(r'public-records', PublicRecordViewSet, basename='public-record')
router.register(r'constituency-funds', ConstituencyFundViewSet, basename='constituency-fund')

from .analytics_views import AnalyticsAPIView


# =============================================================================
# Health Check View (proper HttpResponse, not a dict)
# =============================================================================

def health_check(request):
    """
    Production-grade health check that verifies DB and cache connectivity.
    Returns JSON with component status for load balancer health probes.
    """
    health = {'status': 'ok', 'components': {}}

    # Check database connectivity
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        health['components']['database'] = 'ok'
    except Exception:
        health['components']['database'] = 'error'
        health['status'] = 'degraded'

    # Check Redis cache connectivity
    try:
        from django.core.cache import cache
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            health['components']['cache'] = 'ok'
        else:
            health['components']['cache'] = 'error'
            health['status'] = 'degraded'
    except Exception:
        health['components']['cache'] = 'error'
        health['status'] = 'degraded'

    status_code = 200 if health['status'] == 'ok' else 503
    return JsonResponse(health, status=status_code)


def api_info(request):
    """API info endpoint returning proper JsonResponse."""
    return JsonResponse({
        'version': '1.0.0',
        'name': 'Karnataka Politicians Tracker API',
        'description': 'Public tracker for Karnataka politicians with bilingual support',
        'read_only': True,
        'endpoints': {
            'districts': '/api/v1/districts/',
            'constituencies': '/api/v1/constituencies/',
            'politicians': '/api/v1/politicians/',
            'financial-declarations': '/api/v1/financial-declarations/',
            'legal-records': '/api/v1/legal-records/',
            'public-records': '/api/v1/public-records/',
            'constituency-funds': '/api/v1/constituency-funds/',
            'analytics': '/api/v1/analytics/',
        }
    })


# URL patterns
urlpatterns = [
    path('intelligence/politician/<slug:slug>/', PoliticianIntelligenceView.as_view(), name='politician-intelligence'),
    path('intelligence/network-graph/', NetworkGraphView.as_view(), name='network-graph'),
    path('charts/demographics/<int:constituency_id>/', DemographicChartView.as_view(), name='demographic-chart'),
    path('analytics/', AnalyticsAPIView.as_view(), name='analytics'),
    path('', include(router.urls)),

    # Health check endpoint (proper view, not lambda)
    path('health/', health_check, name='health-check'),

    # API info (proper view, not lambda)
    path('api-info/', api_info, name='api-info'),
]
