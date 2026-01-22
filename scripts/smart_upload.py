#!/usr/bin/env python3
"""
Smart upload that discovers schema and uploads data
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


def discover_columns(client, headers, table_name: str) -> list:
    """Discover valid columns by trying different combinations"""
    # Common columns that might exist
    all_possible_columns = {
        "ordinances": ["jurisdiction_id", "ordinance_number", "title", "chapter", "section",
                      "article", "passed_date", "effective_date", "ordinance_type", "summary",
                      "full_text", "source_url", "status"],
        "overlay_districts": ["jurisdiction_id", "overlay_code", "overlay_name", "overlay_type",
                             "purpose", "source_url", "requirements", "geographic_boundary"],
        "conditional_uses": ["jurisdiction_id", "district_code", "district_name", "use_name",
                            "use_category", "permit_type", "approval_authority", "source_url",
                            "requirements", "conditions"],
        "entitlement_timelines": ["jurisdiction_id", "entitlement_type", "process_name",
                                 "estimated_days_minimum", "estimated_days_maximum",
                                 "estimated_days_typical", "public_hearing_required",
                                 "review_authority", "source_url", "application_fee"],
        "development_bonuses": ["jurisdiction_id", "bonus_name", "bonus_type",
                               "qualifying_criteria", "requirements", "source_url",
                               "effective_date", "expiration_date"],
    }

    columns = all_possible_columns.get(table_name, ["jurisdiction_id"])

    # Try a test insert to see which columns are valid
    valid_columns = []
    for col in columns:
        test_val = 1 if col == "jurisdiction_id" else "test"
        test_record = {col: test_val}

        resp = client.post(
            f"{SUPABASE_URL}/rest/v1/{table_name}",
            headers={**headers, "Prefer": "return=minimal"},
            json=test_record
        )

        if "Could not find the" not in resp.text:
            valid_columns.append(col)

    return valid_columns


def upload_to_table(records: list, table_name: str, field_mapping: dict) -> int:
    """Upload records to a table with field mapping"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal,resolution=merge-duplicates"
    }

    client = httpx.Client(timeout=60)
    saved = 0
    errors = 0

    print(f"  Uploading {len(records)} records to {table_name}...")

    for record in records:
        # Map record fields to table columns
        clean_record = {}
        for table_col, source_field in field_mapping.items():
            if source_field in record and record[source_field] is not None:
                clean_record[table_col] = record[source_field]

        # Must have jurisdiction_id
        if "jurisdiction_id" not in clean_record:
            continue

        try:
            resp = client.post(
                f"{SUPABASE_URL}/rest/v1/{table_name}",
                headers=headers,
                json=clean_record
            )

            if resp.status_code in (200, 201):
                saved += 1
            elif resp.status_code == 409:
                # Duplicate
                pass
            else:
                errors += 1
                if errors <= 3:
                    print(f"    Error: {resp.status_code} - {resp.text[:150]}")

        except Exception as e:
            errors += 1
            if errors <= 3:
                print(f"    Exception: {e}")

    client.close()
    print(f"    Saved: {saved}, Errors: {errors}")
    return saved


def main():
    print("="*60)
    print("SMART UPLOAD TO SUPABASE")
    print("="*60)

    # Load extraction data
    data = get_latest_extraction()
    if not data:
        return

    print(f"\nExtracted data:")
    for key, records in data.get("data", {}).items():
        print(f"  {key}: {len(records)}")

    results = {}

    # Upload ordinances
    if "ordinances" in data.get("data", {}):
        print(f"\n--- ORDINANCES ---")
        mapping = {
            "jurisdiction_id": "jurisdiction_id",
            "ordinance_number": "ordinance_number",
            "ordinance_type": "ordinance_type",
            "source_url": "source_url",
            "passed_date": "passed_date",
        }
        results["ordinances"] = upload_to_table(
            data["data"]["ordinances"],
            "ordinances",
            mapping
        )

    # Upload overlay_districts
    if "overlay_districts" in data.get("data", {}):
        print(f"\n--- OVERLAY_DISTRICTS ---")
        mapping = {
            "jurisdiction_id": "jurisdiction_id",
            "overlay_code": "overlay_code",
            "overlay_name": "overlay_name",
            "overlay_type": "overlay_type",
            "purpose": "purpose",
            "source_url": "source_url",
        }
        results["overlay_districts"] = upload_to_table(
            data["data"]["overlay_districts"],
            "overlay_districts",
            mapping
        )

    # Upload conditional_uses
    if "conditional_uses" in data.get("data", {}):
        print(f"\n--- CONDITIONAL_USES ---")
        mapping = {
            "jurisdiction_id": "jurisdiction_id",
            "district_code": "district_code",
            "use_name": "use_name",
            "use_category": "use_category",
            "permit_type": "permit_type",
            "source_url": "source_url",
        }
        results["conditional_uses"] = upload_to_table(
            data["data"]["conditional_uses"],
            "conditional_uses",
            mapping
        )

    # Upload entitlement_timelines
    if "entitlement_timelines" in data.get("data", {}):
        print(f"\n--- ENTITLEMENT_TIMELINES ---")
        mapping = {
            "jurisdiction_id": "jurisdiction_id",
            "entitlement_type": "entitlement_type",
            "process_name": "process_name",
            "estimated_days_typical": "estimated_days_typical",
            "estimated_days_minimum": "estimated_days_minimum",
            "estimated_days_maximum": "estimated_days_maximum",
            "public_hearing_required": "public_hearing_required",
            "review_authority": "review_authority",
            "source_url": "source_url",
        }
        results["entitlement_timelines"] = upload_to_table(
            data["data"]["entitlement_timelines"],
            "entitlement_timelines",
            mapping
        )

    # Upload development_bonuses
    if "development_bonuses" in data.get("data", {}):
        print(f"\n--- DEVELOPMENT_BONUSES ---")
        mapping = {
            "jurisdiction_id": "jurisdiction_id",
            "bonus_name": "bonus_name",
            "bonus_type": "bonus_type",
            "qualifying_criteria": "qualifying_criteria",
            "source_url": "source_url",
        }
        results["development_bonuses"] = upload_to_table(
            data["data"]["development_bonuses"],
            "development_bonuses",
            mapping
        )

    # Summary
    print("\n" + "="*60)
    print("UPLOAD SUMMARY")
    print("="*60)
    total = 0
    for table, count in results.items():
        print(f"  {table}: {count}")
        total += count
    print(f"\n  TOTAL: {total} records uploaded")


if __name__ == "__main__":
    main()
