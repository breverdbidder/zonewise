#!/usr/bin/env python3
"""Test conditional_uses schema"""

import os
import json
import httpx
from pathlib import Path

# Load credentials
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


print("Testing conditional_uses schema...")

# Test various payloads to discover schema
tests = [
    # Minimal
    {"jurisdiction_id": 1, "district_code": "TEST", "use_name": "Test Use"},
    # With use_category
    {"jurisdiction_id": 1, "district_code": "TEST2", "use_name": "Test Use 2", "use_category": "residential"},
    # With conditions
    {"jurisdiction_id": 1, "district_code": "TEST3", "use_name": "Test Use 3", "conditions": "Some conditions"},
    # With source_url
    {"jurisdiction_id": 1, "district_code": "TEST4", "use_name": "Test Use 4", "source_url": "http://test.com"},
]

for i, payload in enumerate(tests):
    status, text = test_insert("conditional_uses", payload)
    print(f"Test {i+1} ({list(payload.keys())}): {status}")
    if status != 201:
        print(f"  Error: {text[:200]}")
    else:
        print(f"  OK: {text[:150]}")
