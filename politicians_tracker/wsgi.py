"""
WSGI config for Karnataka Politicians Tracker.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'politicians_tracker.settings')

application = get_wsgi_application()
