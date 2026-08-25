import os
import sys
import json
import datetime
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'politicians_tracker.settings')
import django
django.setup()

from politicians_tracker.apps.core.models import Politician

AUDIT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audit')
os.makedirs(AUDIT_DIR, exist_ok=True)
timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

print("=== PHASE 10: API / FRONTEND PARITY ===")
from django.conf import settings
settings.ALLOWED_HOSTS = ['*']
client = Client(SERVER_NAME='localhost')
parity_results = []
hardcoded_findings = [
    {
        "file": "frontend/app/[lang]/layout.tsx",
        "line": 22,
        "content": "all 224 State Assembly MLAs",
        "issue": "Hardcoded counts that may drift (225 in DB)",
        "type": "count_hardcoding"
    },
    {
        "file": "frontend/app/[lang]/layout.tsx",
        "line": 31,
        "content": "DK Shivakumar net worth",
        "issue": "Hardcoded politician name in SEO tags",
        "type": "name_hardcoding"
    },
    {
        "file": "frontend/app/[lang]/layout.tsx",
        "line": 32,
        "content": "Siddaramaiah MLA assets",
        "issue": "Hardcoded politician name in SEO tags",
        "type": "name_hardcoding"
    }
]

for p in list(Politician.objects.all()[:50]):
    res = client.get(f'/api/politicians/{p.id}/')
    if res.status_code == 200:
        data = res.json()
        parity = {
            "politician_id": p.id,
            "name_match": data.get('full_name_en') == p.full_name_en,
            "party_match": data.get('current_party', {}).get('name_en') == getattr(p.current_party, 'name_en', None) if p.current_party else True,
            "house_match": data.get('representative_type') == p.representative_type,
            "minister_match": data.get('is_minister') == p.is_minister,
            "portfolio_match": data.get('portfolio_en') == p.portfolio_en
        }
        parity_results.append(parity)

with open(os.path.join(AUDIT_DIR, 'api_frontend_parity.json'), 'w') as f:
    json.dump({"parity": parity_results, "hardcoding": hardcoded_findings}, f, indent=2)

print("=== PHASE 11: PROVENANCE MODEL IMPROVEMENT PROPOSAL ===")
# Proposal documented in final output

print("=== SCRIPT COMPLETED SUCCESSFULLY ===")
