#!/usr/bin/env python3
"""
Probe table schemas to find required columns
"""

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

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")


def test_insert(table, payload):
    """Test inserting with given payload"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    client = httpx.Client(timeout=30)
    resp = client.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=headers,
        json=payload
    )
    client.close()

    return resp.status_code, resp.text


def main():
    print("=" * 60)
    print("SCHEMA PROBE - Finding Required Columns")
    print("=" * 60)

    # Test ordinances with progressively more columns
    print("\n--- ORDINANCES ---")

    # First, get an existing record to see the structure
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }
    client = httpx.Client(timeout=30)
    resp = client.get(
        f"{SUPABASE_URL}/rest/v1/ordinances?limit=1",
        headers=headers
    )
    print(f"Sample record: {resp.text[:500]}")
    client.close()

    # Try with title added
    test_cases = [
        {"jurisdiction_id": 1, "ordinance_number": "TEST-001"},
        {"jurisdiction_id": 1, "ordinance_number": "TEST-002", "title": "Test Ordinance"},
        {"jurisdiction_id": 1, "ordinance_number": "TEST-003", "title": "Test", "source_url": "http://test.com"},
    ]

    for i, payload in enumerate(test_cases):
        status, text = test_insert("ordinances", payload)
        print(f"Test {i+1}: {status} - {text[:150]}")

    # Check conditional_uses
    print("\n--- CONDITIONAL_USES ---")
    resp = client.get(
        f"{SUPABASE_URL}/rest/v1/conditional_uses?limit=1",
        headers=headers
    )
    print(f"Sample: {resp.text[:300]}")

    # Check entitlement_timelines
    print("\n--- ENTITLEMENT_TIMELINES ---")
    resp = client.get(
        f"{SUPABASE_URL}/rest/v1/entitlement_timelines?limit=1",
        headers=headers
    )
    print(f"Sample: {resp.text[:300]}")

    # Check development_bonuses
    print("\n--- DEVELOPMENT_BONUSES ---")
    resp = client.get(
        f"{SUPABASE_URL}/rest/v1/development_bonuses?limit=1",
        headers=headers
    )
    print(f"Sample: {resp.text[:300]}")


if __name__ == "__main__":
    main()
