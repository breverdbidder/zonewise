#!/usr/bin/env python3
"""Test development_bonuses full schema"""

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


def test_insert(payload):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    client = httpx.Client(timeout=30)
    resp = client.post(f"{SUPABASE_URL}/rest/v1/development_bonuses", headers=headers, json=payload)
    client.close()
    return resp.status_code, resp.text


print("Testing development_bonuses...")

# From error: "Failing row contains (9, 1, null, Test, null, null...)"
# Position: id=9, jurisdiction_id=1, (col2)=null, program_name=Test, (col4+)=null

# Try with program_name + other potential required columns
tests = [
    {"jurisdiction_id": 1, "program_name": "Test1"},
    {"jurisdiction_id": 1, "program_name": "Test2", "district_code": "R-1"},
    {"jurisdiction_id": 1, "program_name": "Test3", "bonus_percent": 10},
    {"jurisdiction_id": 1, "program_name": "Test4", "qualifying_criteria": ["criteria1"]},
    {"jurisdiction_id": 1, "program_name": "Test5", "conditions": ["condition1"]},
]

for i, payload in enumerate(tests):
    status, text = test_insert(payload)
    print(f"Test {i+1} ({list(payload.keys())}): {status}")
    if status == 201:
        print(f"  SUCCESS: {text[:250]}")
    else:
        print(f"  Error: {text[:300]}")
