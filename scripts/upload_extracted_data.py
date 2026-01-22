#!/usr/bin/env python3
"""
Upload extracted data to Supabase
Handles column mapping and schema differences
"""

import os
import json
import httpx
from pathlib import Path
from datetime import datetime

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
    if not files:
        print("No extraction files found")
        return None

    latest = max(files, key=lambda f: f.stat().st_mtime)
    print(f"Loading: {latest}")

    with open(latest) as f:
        return json.load(f)


def check_table_columns(table_name: str) -> list:
    """Check what columns exist in a table"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }

    client = httpx.Client(timeout=30)

    try:
        # Try to get one record to see columns
        resp = client.get(
            f"{SUPABASE_URL}/rest/v1/{table_name}?limit=0",
            headers=headers
        )
        print(f"  {table_name}: {resp.status_code}")

        # Check if table exists by looking at response
        if resp.status_code == 200:
            return True
        else:
            return False

    except Exception as e:
        print(f"  Error checking {table_name}: {e}")
        return False
    finally:
        client.close()


def upload_ordinances(records: list) -> int:
    """Upload ordinances with minimal columns"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

    client = httpx.Client(timeout=60)
    saved = 0

    for record in records:
        # Map to expected columns (without extra fields)
        clean_record = {
            "jurisdiction_id": record.get("jurisdiction_id"),
            "jurisdiction_name": record.get("jurisdiction_name"),
            "ordinance_number": record.get("ordinance_number"),
            "ordinance_type": record.get("ordinance_type"),
            "source_url": record.get("source_url"),
            "passed_date": record.get("passed_date"),
        }

        try:
            resp = client.post(
                f"{SUPABASE_URL}/rest/v1/ordinances",
                headers=headers,
                json=clean_record
            )

            if resp.status_code in (200, 201):
                saved += 1
            elif resp.status_code == 409:
                # Duplicate, that's ok
                pass
            else:
                print(f"    Error: {resp.status_code} - {resp.text[:100]}")

        except Exception as e:
            print(f"    Exception: {e}")

    client.close()
    return saved


def upload_overlays(records: list) -> int:
    """Upload overlay districts"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

    client = httpx.Client(timeout=60)
    saved = 0

    for record in records:
        clean_record = {
            "jurisdiction_id": record.get("jurisdiction_id"),
            "jurisdiction_name": record.get("jurisdiction_name"),
            "overlay_code": record.get("overlay_code"),
            "overlay_name": record.get("overlay_name"),
            "overlay_type": record.get("overlay_type"),
            "purpose": record.get("purpose"),
            "source_url": record.get("source_url"),
        }

        try:
            resp = client.post(
                f"{SUPABASE_URL}/rest/v1/overlay_districts",
                headers=headers,
                json=clean_record
            )

            if resp.status_code in (200, 201):
                saved += 1
            elif resp.status_code == 409:
                pass

        except Exception as e:
            print(f"    Exception: {e}")

    client.close()
    return saved


def upload_conditional_uses(records: list) -> int:
    """Upload conditional uses"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

    client = httpx.Client(timeout=60)
    saved = 0

    for record in records:
        clean_record = {
            "jurisdiction_id": record.get("jurisdiction_id"),
            "jurisdiction_name": record.get("jurisdiction_name"),
            "district_code": record.get("district_code"),
            "use_name": record.get("use_name"),
            "use_category": record.get("use_category"),
            "permit_type": record.get("permit_type"),
            "source_url": record.get("source_url"),
        }

        try:
            resp = client.post(
                f"{SUPABASE_URL}/rest/v1/conditional_uses",
                headers=headers,
                json=clean_record
            )

            if resp.status_code in (200, 201):
                saved += 1
            elif resp.status_code == 409:
                pass

        except Exception as e:
            print(f"    Exception: {e}")

    client.close()
    return saved


def upload_timelines(records: list) -> int:
    """Upload entitlement timelines"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

    client = httpx.Client(timeout=60)
    saved = 0

    for record in records:
        clean_record = {
            "jurisdiction_id": record.get("jurisdiction_id"),
            "jurisdiction_name": record.get("jurisdiction_name"),
            "entitlement_type": record.get("entitlement_type"),
            "process_name": record.get("process_name"),
            "estimated_days_typical": record.get("estimated_days_typical"),
            "estimated_days_minimum": record.get("estimated_days_minimum"),
            "estimated_days_maximum": record.get("estimated_days_maximum"),
            "public_hearing_required": record.get("public_hearing_required"),
            "review_authority": record.get("review_authority"),
            "source_url": record.get("source_url"),
        }

        try:
            resp = client.post(
                f"{SUPABASE_URL}/rest/v1/entitlement_timelines",
                headers=headers,
                json=clean_record
            )

            if resp.status_code in (200, 201):
                saved += 1
            elif resp.status_code == 409:
                pass

        except Exception as e:
            print(f"    Exception: {e}")

    client.close()
    return saved


def upload_bonuses(records: list) -> int:
    """Upload development bonuses"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

    client = httpx.Client(timeout=60)
    saved = 0

    for record in records:
        clean_record = {
            "jurisdiction_id": record.get("jurisdiction_id"),
            "jurisdiction_name": record.get("jurisdiction_name"),
            "bonus_name": record.get("bonus_name"),
            "bonus_type": record.get("bonus_type"),
            "qualifying_criteria": record.get("qualifying_criteria"),
            "source_url": record.get("source_url"),
        }

        try:
            resp = client.post(
                f"{SUPABASE_URL}/rest/v1/development_bonuses",
                headers=headers,
                json=clean_record
            )

            if resp.status_code in (200, 201):
                saved += 1
            elif resp.status_code == 409:
                pass

        except Exception as e:
            print(f"    Exception: {e}")

    client.close()
    return saved


def main():
    print("="*60)
    print("UPLOAD EXTRACTED DATA TO SUPABASE")
    print("="*60)

    # Check tables exist
    print("\nChecking tables...")
    tables = ["ordinances", "overlay_districts", "conditional_uses",
              "entitlement_timelines", "development_bonuses"]
    for table in tables:
        exists = check_table_columns(table)
        print(f"  {table}: {'EXISTS' if exists else 'NOT FOUND'}")

    # Load extraction data
    print("\nLoading extraction data...")
    data = get_latest_extraction()
    if not data:
        return

    print(f"\nExtracted data summary:")
    for key, records in data.get("data", {}).items():
        print(f"  {key}: {len(records)}")

    # Upload each table
    print("\n" + "="*60)
    print("UPLOADING TO SUPABASE")
    print("="*60)

    results = {}

    if "ordinances" in data.get("data", {}):
        print("\nUploading ordinances...")
        results["ordinances"] = upload_ordinances(data["data"]["ordinances"])
        print(f"  Saved: {results['ordinances']}")

    if "overlay_districts" in data.get("data", {}):
        print("\nUploading overlay_districts...")
        results["overlay_districts"] = upload_overlays(data["data"]["overlay_districts"])
        print(f"  Saved: {results['overlay_districts']}")

    if "conditional_uses" in data.get("data", {}):
        print("\nUploading conditional_uses...")
        results["conditional_uses"] = upload_conditional_uses(data["data"]["conditional_uses"])
        print(f"  Saved: {results['conditional_uses']}")

    if "entitlement_timelines" in data.get("data", {}):
        print("\nUploading entitlement_timelines...")
        results["entitlement_timelines"] = upload_timelines(data["data"]["entitlement_timelines"])
        print(f"  Saved: {results['entitlement_timelines']}")

    if "development_bonuses" in data.get("data", {}):
        print("\nUploading development_bonuses...")
        results["development_bonuses"] = upload_bonuses(data["data"]["development_bonuses"])
        print(f"  Saved: {results['development_bonuses']}")

    # Summary
    print("\n" + "="*60)
    print("UPLOAD SUMMARY")
    print("="*60)
    for table, count in results.items():
        print(f"  {table}: {count} records")

    total = sum(results.values())
    print(f"\n  TOTAL: {total} records uploaded")


if __name__ == "__main__":
    main()
