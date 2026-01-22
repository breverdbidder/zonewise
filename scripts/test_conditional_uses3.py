#!/usr/bin/env python3
"""Test conditional_uses with approval_type"""

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


print("Testing with approval_type...")

tests = [
    # With approval_type
    {"jurisdiction_id": 1, "district_code": "T1", "use_name": "Test", "approval_type": "conditional_use", "conditions": ["test"]},
    # Without conditions
    {"jurisdiction_id": 1, "district_code": "T2", "use_name": "Test2", "approval_type": "conditional_use"},
    # With empty conditions
    {"jurisdiction_id": 1, "district_code": "T3", "use_name": "Test3", "approval_type": "permitted"},
    # Full record
    {"jurisdiction_id": 1, "district_code": "T4", "use_name": "Test4", "use_category": "residential", "approval_type": "special_exception", "source_url": "http://test.com"},
]

for i, payload in enumerate(tests):
    status, text = test_insert(payload)
    print(f"Test {i+1}: {status}")
    if status == 201:
        print(f"  SUCCESS: {text[:200]}")
    else:
        print(f"  Error: {text[:200]}")
