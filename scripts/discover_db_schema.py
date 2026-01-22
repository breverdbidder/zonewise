#!/usr/bin/env python3
"""Discover development_bonuses and entitlement_timelines schemas"""

import os
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
print("ENTITLEMENT_TIMELINES")
print("=" * 60)

# Test with steps as array
et_tests = [
    {"jurisdiction_id": 1, "process_type": "Test", "steps": ["Step 1", "Step 2"]},
    {"jurisdiction_id": 1, "process_type": "Test2", "steps": []},
]

for i, payload in enumerate(et_tests):
    status, text = test_insert("entitlement_timelines", payload)
    print(f"Test {i+1}: {status}")
    if status == 201:
        print(f"  SUCCESS: {text[:300]}")
    else:
        print(f"  Error: {text}")


print("\n" + "=" * 60)
print("DEVELOPMENT_BONUSES")
print("=" * 60)

# Discover columns - try minimal then build up
status, text = test_insert("development_bonuses", {"jurisdiction_id": 1})
print(f"Minimal test: {status}")
print(f"Error: {text}")

# Try common column names
columns = ["name", "bonus_name", "incentive_type", "program_name", "district_code", "bonus_category"]
for col in columns:
    payload = {"jurisdiction_id": 1, col: "Test"}
    status, text = test_insert("development_bonuses", payload)
    if "PGRST204" not in text:
        print(f"\nColumn '{col}' exists: {status}")
        print(f"  Result: {text[:200]}")
