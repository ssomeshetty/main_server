"""
URL configuration for Karnataka Politicians Tracker.

This file routes all API endpoints to their respective viewsets.
Admin URL is randomized via environment variable for security.
"""
import os
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

# Randomized admin path — set ADMIN_URL_PREFIX env var in production
# Default: 'mgmt-admin' (never use plain 'admin/' in production)
ADMIN_URL_PREFIX = os.environ.get('ADMIN_URL_PREFIX', 'mgmt-admin')

urlpatterns = [
    # Admin (hidden path — not at default /admin/)
    path(f'{ADMIN_URL_PREFIX}/', admin.site.urls),

    # API
    path('api/v1/', include('apps.core.urls')),

    # Root — returns API info as JSON (no template dependency)
    path('', lambda request: JsonResponse({
        'service': 'Karnataka Politicians Tracker API',
        'version': '1.0.0',
        'api': '/api/v1/',
        'health': '/api/v1/health/',
    }), name='home'),
]