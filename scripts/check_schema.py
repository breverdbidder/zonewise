#!/usr/bin/env python3
"""
Check the actual Supabase table schema
"""

import os
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


def check_table_schema():
    """Check the actual schema of tables via API"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }

    client = httpx.Client(timeout=30)

    tables = [
        "ordinances",
        "overlay_districts",
        "conditional_uses",
        "entitlement_timelines",
        "development_bonuses",
        "municode_scrape_log",
        "ordinance_changes",
    ]

    print("="*60)
    print("CHECKING SUPABASE TABLE SCHEMAS")
    print("="*60)

    for table in tables:
        print(f"\n--- {table.upper()} ---")
        try:
            # Get OpenAPI spec which includes column info
            resp = client.options(
                f"{SUPABASE_URL}/rest/v1/{table}",
                headers=headers
            )
            print(f"  OPTIONS status: {resp.status_code}")

            # Try a GET to see what columns come back
            resp = client.get(
                f"{SUPABASE_URL}/rest/v1/{table}?limit=1",
                headers=headers
            )
            print(f"  GET status: {resp.status_code}")

            if resp.status_code == 200:
                data = resp.json()
                if data:
                    print(f"  Columns: {list(data[0].keys())}")
                else:
                    print("  (empty table)")

                    # Try inserting minimal record to discover columns
                    test_resp = client.post(
                        f"{SUPABASE_URL}/rest/v1/{table}",
                        headers={**headers, "Content-Type": "application/json", "Prefer": "return=minimal"},
                        json={}
                    )
                    print(f"  Empty insert response: {test_resp.status_code}")
                    if test_resp.status_code != 201:
                        print(f"  Error details: {test_resp.text[:300]}")
            else:
                print(f"  Error: {resp.text[:200]}")

        except Exception as e:
            print(f"  Exception: {e}")

    client.close()


if __name__ == "__main__":
    check_table_schema()
