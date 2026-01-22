#!/usr/bin/env python3
"""Test conditional_uses schema - more detailed"""

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


def test_insert(payload):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    client = httpx.Client(timeout=30)
    resp = client.post(f"{SUPABASE_URL}/rest/v1/conditional_uses", headers=headers, json=payload)
    client.close()
    return resp.status_code, resp.text


print("Testing conditional_uses - finding required columns...")

# The column order from error suggests: id, jurisdiction_id, district_code, use_name, use_category, ?, conditions...
# Let's try progressively adding columns

tests = [
    # Try with conditions as array
    {"jurisdiction_id": 1, "district_code": "T1", "use_name": "Test", "conditions": ["condition1"]},
    # Try adding more fields
    {"jurisdiction_id": 1, "district_code": "T2", "use_name": "Test", "use_category": "residential", "conditions": ["c1"]},
    # Try with permit_type
    {"jurisdiction_id": 1, "district_code": "T3", "use_name": "Test", "permit_type": "conditional_use", "conditions": []},
    # Try with minimum_lot_size
    {"jurisdiction_id": 1, "district_code": "T4", "use_name": "Test", "minimum_lot_size": "5000 sqft", "conditions": []},
    # Try with approval_criteria
    {"jurisdiction_id": 1, "district_code": "T5", "use_name": "Test", "approval_criteria": "Some criteria", "conditions": []},
    # Try with review_body
    {"jurisdiction_id": 1, "district_code": "T6", "use_name": "Test", "review_body": "Planning Board", "conditions": []},
]

for i, payload in enumerate(tests):
    status, text = test_insert(payload)
    keys = list(payload.keys())
    print(f"Test {i+1} ({keys}):")
    print(f"  Status: {status}")
    if status != 201:
        print(f"  Error: {text[:300]}")
    else:
        print(f"  SUCCESS!")
        print(f"  Result: {text[:200]}")
