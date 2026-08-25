import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "politicians_tracker.settings")
django.setup()
from politicians_tracker.apps.core.models import Politician, FinancialDeclaration

pol = Politician.objects.filter(full_name_en__icontains='Basavaraj Bommai').first()
decls = FinancialDeclaration.objects.filter(politician=pol)
print(f"Basavaraj Bommai Declarations: {len(decls)}")
for d in decls:
    print(d.declaration_year, d.total_assets)
