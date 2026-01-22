#!/usr/bin/env python3
"""Test entitlement_timelines and development_bonuses schemas"""

import os
import json
import httpx
from pathlib import Path

env_path = Path(__file__).parent.parent / "agents" / "verify" / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")


def test_insert(table, payload):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    client = httpx.Client(timeout=30)
    resp = client.post(f"{SUPABASE_URL}/rest/v1/{table}", headers=headers, json=payload)
    client.close()
    return resp.status_code, resp.text


print("=" * 60)
print("TESTING ENTITLEMENT_TIMELINES")
print("=" * 60)

et_tests = [
    {"jurisdiction_id": 1, "process_type": "Site Plan Review"},
    {"jurisdiction_id": 1, "process_type": "Rezoning", "source_url": "http://test.com"},
    {"jurisdiction_id": 1, "process_type": "Variance", "estimated_days_min": 30, "estimated_days_max": 90},
]

for i, payload in enumerate(et_tests):
    status, text = test_insert("entitlement_timelines", payload)
    print(f"Test {i+1}: {status}")
    if status == 201:
        print(f"  SUCCESS: {text[:200]}")
    else:
        print(f"  Error: {text[:200]}")

print("\n" + "=" * 60)
print("TESTING DEVELOPMENT_BONUSES")
print("=" * 60)

db_tests = [
    {"jurisdiction_id": 1, "bonus_type": "Density Bonus"},
    {"jurisdiction_id": 1, "bonus_type": "Height Bonus", "conditions": ["affordable housing"]},
    {"jurisdiction_id": 1, "bonus_type": "FAR Bonus", "source_url": "http://test.com"},
]

for i, payload in enumerate(db_tests):
    status, text = test_insert("development_bonuses", payload)
    print(f"Test {i+1}: {status}")
    if status == 201:
        print(f"  SUCCESS: {text[:200]}")
    else:
        print(f"  Error: {text[:200]}")
