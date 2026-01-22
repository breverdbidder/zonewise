#!/usr/bin/env python3
"""
Upload all extracted data to Supabase with correct schema mappings
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

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")


def upload_batch(table_name: str, records: list, show_errors: int = 3) -> dict:
    """Upload records to a table"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

    client = httpx.Client(timeout=60)
    saved = 0
    duplicates = 0
    errors = 0
    error_samples = []

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
                duplicates += 1
            else:
                errors += 1
                if len(error_samples) < show_errors:
                    error_samples.append(f"{resp.status_code}: {resp.text[:150]}")

        except Exception as e:
            errors += 1

    client.close()
    return {"saved": saved, "duplicates": duplicates, "errors": errors, "error_samples": error_samples}


def get_db_count(table_name: str) -> int:
    """Get current count in table"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Prefer": "count=exact"
    }
    client = httpx.Client(timeout=30)
    try:
        resp = client.get(f"{SUPABASE_URL}/rest/v1/{table_name}?select=id", headers=headers)
        count = int(resp.headers.get("Content-Range", "0/0").split("/")[-1])
    except:
        count = 0
    client.close()
    return count


def main():
    print("=" * 60)
    print("COMPREHENSIVE DATA UPLOAD")
    print("=" * 60)

    # Load extraction data
    data_dir = Path(__file__).parent.parent / "data"
    files = list(data_dir.glob("enhanced_extraction_*.json"))
    if not files:
        print("No extraction files found")
        return

    latest = max(files, key=lambda f: f.stat().st_mtime)
    print(f"Loading: {latest.name}")

    with open(latest) as f:
        extraction = json.load(f)

    data = extraction.get("data", {})

    # 1. CONDITIONAL USES
    # Required: jurisdiction_id, district_code, use_name, approval_type
    print("\n" + "-" * 40)
    print("CONDITIONAL_USES")
    print("-" * 40)
    print(f"Before: {get_db_count('conditional_uses')} records")

    cu_records = []
    for record in data.get("conditional_uses", []):
        cu_records.append({
            "jurisdiction_id": record["jurisdiction_id"],
            "district_code": record.get("district_code", "UNKNOWN"),
            "use_name": record.get("use_name", "Unknown Use"),
            "use_category": record.get("use_category"),
            "approval_type": record.get("permit_type", "conditional_use"),  # Map permit_type -> approval_type
            "source_url": record.get("source_url"),
        })

    print(f"Records to upload: {len(cu_records)}")
    result = upload_batch("conditional_uses", cu_records)
    print(f"Saved: {result['saved']}, Duplicates: {result['duplicates']}, Errors: {result['errors']}")
    if result['error_samples']:
        for e in result['error_samples']:
            print(f"  Error sample: {e}")
    print(f"After: {get_db_count('conditional_uses')} records")

    # 2. ENTITLEMENT TIMELINES
    # Required: jurisdiction_id, process_type, steps (array)
    print("\n" + "-" * 40)
    print("ENTITLEMENT_TIMELINES")
    print("-" * 40)
    print(f"Before: {get_db_count('entitlement_timelines')} records")

    et_records = []
    for record in data.get("entitlement_timelines", []):
        et_records.append({
            "jurisdiction_id": record["jurisdiction_id"],
            "process_type": record.get("entitlement_type") or record.get("process_name", "Unknown Process"),
            "steps": record.get("steps", []),  # Required array, default empty
            "source_url": record.get("source_url"),
        })

    print(f"Records to upload: {len(et_records)}")
    result = upload_batch("entitlement_timelines", et_records)
    print(f"Saved: {result['saved']}, Duplicates: {result['duplicates']}, Errors: {result['errors']}")
    if result['error_samples']:
        for e in result['error_samples']:
            print(f"  Error sample: {e}")
    print(f"After: {get_db_count('entitlement_timelines')} records")

    # 3. DEVELOPMENT BONUSES
    # Required: jurisdiction_id, program_name, feature_name
    print("\n" + "-" * 40)
    print("DEVELOPMENT_BONUSES")
    print("-" * 40)
    print(f"Before: {get_db_count('development_bonuses')} records")

    db_records = []
    for record in data.get("development_bonuses", []):
        db_records.append({
            "jurisdiction_id": record["jurisdiction_id"],
            "program_name": record.get("bonus_name", "Development Incentive"),
            "feature_name": record.get("qualifying_criteria") or record.get("bonus_type", "Incentive"),
            "conditions": record.get("conditions"),
            "source_url": record.get("source_url"),
        })

    print(f"Records to upload: {len(db_records)}")
    result = upload_batch("development_bonuses", db_records)
    print(f"Saved: {result['saved']}, Duplicates: {result['duplicates']}, Errors: {result['errors']}")
    if result['error_samples']:
        for e in result['error_samples']:
            print(f"  Error sample: {e}")
    print(f"After: {get_db_count('development_bonuses')} records")

    # SUMMARY
    print("\n" + "=" * 60)
    print("FINAL DATABASE COUNTS")
    print("=" * 60)

    tables = ["ordinances", "overlay_districts", "conditional_uses",
              "entitlement_timelines", "development_bonuses"]

    targets = {
        "ordinances": 500,
        "overlay_districts": 30,
        "conditional_uses": 200,
        "entitlement_timelines": 50,
        "development_bonuses": 50
    }

    for table in tables:
        count = get_db_count(table)
        target = targets.get(table, 0)
        status = "✓ PASS" if count >= target else "✗ NEED MORE"
        print(f"  {table}: {count} (target: {target}) {status}")


if __name__ == "__main__":
    main()
