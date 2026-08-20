"""
ASGI config for Karnataka Politicians Tracker.

This module contains the ASGI application used for async request handling.
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'politicians_tracker.settings')

application = get_asgi_application()
