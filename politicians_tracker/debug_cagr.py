import os, django, math
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "politicians_tracker.settings")
django.setup()
from politicians_tracker.apps.core.models import Politician, FinancialDeclaration
from politicians_tracker.apps.core.intelligence_engine import PoliticalAnalyticsEngine

p = Politician.objects.create(first_name_en="Debug", last_name_en="Pol")
FinancialDeclaration.objects.create(politician=p, declaration_year=2018, total_assets=50000000, total_liabilities=5000000)
FinancialDeclaration.objects.create(politician=p, declaration_year=2023, total_assets=100000000, total_liabilities=10000000)

engine = PoliticalAnalyticsEngine(p)
print(engine.analyze_financial_trajectory())
