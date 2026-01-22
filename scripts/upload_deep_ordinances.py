#!/usr/bin/env python3
"""
Upload deep extraction ordinances to Supabase
Uses upsert to handle duplicates
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


def main():
    print("=" * 60)
    print("UPLOAD DEEP EXTRACTION ORDINANCES")
    print("=" * 60)

    # Load data
    data_dir = Path(__file__).parent.parent / "data"
    files = list(data_dir.glob("deep_ordinances_*.json"))
    if not files:
        print("No deep extraction files found")
        return

    latest = max(files, key=lambda f: f.stat().st_mtime)
    print(f"Loading: {latest.name}")

    with open(latest) as f:
        data = json.load(f)

    ordinances = data.get("ordinances", [])
    print(f"Found {len(ordinances)} ordinances to upload")

    # Upload with detailed error logging
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=representation"
    }

    client = httpx.Client(timeout=60)
    saved = 0
    duplicates = 0
    errors = 0

    for i, record in enumerate(ordinances):
        try:
            # Only include valid columns - title is required!
            ord_num = record["ordinance_number"]
            payload = {
                "jurisdiction_id": record["jurisdiction_id"],
                "ordinance_number": ord_num,
                "title": ord_num,  # Use ordinance number as title
                "source_url": record.get("source_url"),
            }

            # Add passed_date if present
            if record.get("passed_date"):
                payload["passed_date"] = record["passed_date"]

            resp = client.post(
                f"{SUPABASE_URL}/rest/v1/ordinances",
                headers=headers,
                json=payload
            )

            if resp.status_code in (200, 201):
                saved += 1
                if saved % 10 == 0:
                    print(f"  Saved {saved}...")
            elif resp.status_code == 409:
                duplicates += 1
            else:
                errors += 1
                if errors <= 5:
                    print(f"  Error {resp.status_code}: {resp.text[:200]}")

        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"  Exception: {e}")

    client.close()

    print(f"\nResults:")
    print(f"  Saved: {saved}")
    print(f"  Duplicates: {duplicates}")
    print(f"  Errors: {errors}")

    # Check total in DB
    print("\nChecking database totals...")
    headers_get = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Prefer": "count=exact"
    }

    client = httpx.Client(timeout=30)
    tables = ["ordinances", "overlay_districts", "conditional_uses",
              "entitlement_timelines", "development_bonuses"]

    for table in tables:
        try:
            resp = client.get(
                f"{SUPABASE_URL}/rest/v1/{table}?select=id",
                headers=headers_get
            )
            count = resp.headers.get("Content-Range", "0").split("/")[-1]
            print(f"  {table}: {count}")
        except:
            pass

    client.close()


if __name__ == "__main__":
    main()
