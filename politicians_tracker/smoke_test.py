import os
import django
import json
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "politicians_tracker.settings")
django.setup()

from politicians_tracker.apps.core.models import Politician
from politicians_tracker.apps.core.intelligence_engine import PoliticalAnalyticsEngine

names = ['Siddaramaiah', 'D.K. Shivakumar', 'Basavaraj Bommai']
for name in names:
    pol = Politician.objects.filter(full_name_en__icontains=name).first()
    if pol:
        engine = PoliticalAnalyticsEngine(pol)
        report = engine.get_full_report()
        print(f"\n--- {pol.full_name_en} ---")
        print("Financial:", report['analytics']['financial_trajectory']['state'], report['analytics']['financial_trajectory']['cagr_pct'])
        print("HECI:", report['analytics']['historical_electoral_competitiveness'])
        print("Legal Summary:", report['legal_summary'])
