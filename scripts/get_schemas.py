#!/usr/bin/env python3
"""Get actual table schemas by querying empty tables"""

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

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
}

client = httpx.Client(timeout=30)

tables = ["entitlement_timelines", "development_bonuses", "conditional_uses"]

for table in tables:
    print(f"\n--- {table} ---")
    # Try to get one record with all columns
    resp = client.get(f"{SUPABASE_URL}/rest/v1/{table}?limit=1", headers=headers)
    print(f"Status: {resp.status_code}")
    print(f"Data: {resp.text}")

client.close()
