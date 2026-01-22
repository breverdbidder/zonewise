#!/usr/bin/env python3
"""
Final upload with exact schema matching
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


def get_latest_extraction():
    """Find the latest extraction JSON file"""
    data_dir = Path(__file__).parent.parent / "data"
    files = list(data_dir.glob("enhanced_extraction_*.json"))
    if not files:
        files = list(data_dir.glob("comprehensive_extraction_*.json"))
    if files:
        latest = max(files, key=lambda f: f.stat().st_mtime)
        with open(latest) as f:
            return json.load(f)
    return None


def upload_batch(table_name: str, records: list) -> int:
    """Upload records to a table"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

    client = httpx.Client(timeout=60)
    saved = 0
    errors = 0

    for record in records:
        try:
            resp = client.post(
                f"{SUPABASE_URL}/rest/v1/{table_name}",
                headers=headers,
                json=record
            )

            if resp.status_code in (200, 201):
                saved += 1
            elif resp.status_code == 409:
                pass  # duplicate
            else:
                errors += 1
                if errors <= 3:
                    print(f"    Error: {resp.status_code} - {resp.text[:150]}")

        except Exception as e:
            errors += 1

    client.close()
    return saved


def main():
    print("="*60)
    print("FINAL UPLOAD WITH EXACT SCHEMA")
    print("="*60)

    data = get_latest_extraction()
    if not data:
        print("No data found")
        return

    results = {}

    # Upload conditional_uses
    # Schema: jurisdiction_id, source_url, district_code, use_name, use_category, conditions
    print("\n--- CONDITIONAL_USES ---")
    cu_records = []
    for record in data["data"].get("conditional_uses", []):
        cu_records.append({
            "jurisdiction_id": record.get("jurisdiction_id"),
            "source_url": record.get("source_url"),
            "district_code": record.get("district_code"),
            "use_name": record.get("use_name"),
            "use_category": record.get("use_category"),
        })

    print(f"  Records to upload: {len(cu_records)}")
    results["conditional_uses"] = upload_batch("conditional_uses", cu_records)
    print(f"  Saved: {results['conditional_uses']}")

    # Upload entitlement_timelines
    # Schema: jurisdiction_id, source_url, process_type
    print("\n--- ENTITLEMENT_TIMELINES ---")
    et_records = []
    for record in data["data"].get("entitlement_timelines", []):
        et_records.append({
            "jurisdiction_id": record.get("jurisdiction_id"),
            "source_url": record.get("source_url"),
            "process_type": record.get("entitlement_type") or record.get("process_name"),
        })

    print(f"  Records to upload: {len(et_records)}")
    results["entitlement_timelines"] = upload_batch("entitlement_timelines", et_records)
    print(f"  Saved: {results['entitlement_timelines']}")

    # Upload development_bonuses
    # Schema: jurisdiction_id, ordinance_id, source_url, conditions
    print("\n--- DEVELOPMENT_BONUSES ---")
    db_records = []
    for record in data["data"].get("development_bonuses", []):
        db_records.append({
            "jurisdiction_id": record.get("jurisdiction_id"),
            "source_url": record.get("source_url"),
            # 'conditions' might be required, use qualifying_criteria
            "conditions": record.get("qualifying_criteria") or record.get("bonus_name"),
        })

    print(f"  Records to upload: {len(db_records)}")
    results["development_bonuses"] = upload_batch("development_bonuses", db_records)
    print(f"  Saved: {results['development_bonuses']}")

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    total = sum(results.values())
    for table, count in results.items():
        print(f"  {table}: {count}")
    print(f"\n  TOTAL: {total} records uploaded in this run")

    # Query totals
    print("\n--- CHECKING DATABASE TOTALS ---")
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }
    client = httpx.Client(timeout=30)

    tables = ["ordinances", "overlay_districts", "conditional_uses",
              "entitlement_timelines", "development_bonuses"]

    for table in tables:
        try:
            resp = client.get(
                f"{SUPABASE_URL}/rest/v1/{table}?select=id",
                headers={**headers, "Prefer": "count=exact"}
            )
            count = resp.headers.get("Content-Range", "0").split("/")[-1]
            print(f"  {table}: {count} records in DB")
        except:
            pass

    client.close()


if __name__ == "__main__":
    main()
