#!/usr/bin/env python3
"""Discover entitlement_timelines schema"""

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
    resp = client.post(f"{SUPABASE_URL}/rest/v1/entitlement_timelines", headers=headers, json=payload)
    client.close()
    return resp.status_code, resp.text


print("Discovering entitlement_timelines required columns...")

# Try common column names
column_tests = [
    "entitlement_type",
    "approval_type",
    "timeline_type",
    "step_name",
    "phase_name",
    "review_type",
]

base = {"jurisdiction_id": 1, "process_type": "Test"}

for col in column_tests:
    payload = {**base, col: "test_value"}
    status, text = test_insert(payload)
    if "PGRST204" not in text:  # Column exists
        print(f"Column '{col}' exists: {status}")
        print(f"  Result: {text[:250]}")
    else:
        print(f"Column '{col}' does NOT exist")

# Try with longer error message
print("\n\nFull error with minimal payload:")
status, text = test_insert({"jurisdiction_id": 1, "process_type": "Test"})
print(f"Status: {status}")
print(f"Full error: {text}")
