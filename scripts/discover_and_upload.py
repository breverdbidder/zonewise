#!/usr/bin/env python3
"""
Discover actual table schema and upload data
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

# All possible column names to try
COLUMN_CANDIDATES = [
    "jurisdiction_id", "jurisdiction_name",
    "ordinance_number", "ordinance_type", "ordinance_id",
    "title", "name", "description",
    "chapter", "section", "article",
    "passed_date", "effective_date", "date",
    "summary", "full_text", "text", "content",
    "source_url", "url", "source",
    "status", "type", "category",
    "overlay_code", "overlay_name", "overlay_type",
    "district_code", "district_name",
    "use_name", "use_category", "use_type",
    "permit_type", "approval_authority",
    "entitlement_type", "process_name", "process_type",
    "estimated_days", "days_minimum", "days_maximum", "days_typical",
    "estimated_days_minimum", "estimated_days_maximum", "estimated_days_typical",
    "public_hearing_required", "public_hearing",
    "review_authority", "authority",
    "bonus_name", "bonus_type", "bonus_amount",
    "qualifying_criteria", "criteria", "requirements",
    "code", "zone_code",
    "purpose", "notes", "requirements",
    "geographic_boundary", "boundary",
    "conditions", "special_requirements",
]


def discover_valid_columns(table_name: str) -> list:
    """Discover which columns exist in a table"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

    client = httpx.Client(timeout=30)
    valid = []

    for col in COLUMN_CANDIDATES:
        # Try inserting with just this column + jurisdiction_id
        test_record = {"jurisdiction_id": 999999}
        if col != "jurisdiction_id":
            test_record[col] = "test_value" if not col.endswith("_id") else 1

        try:
            resp = client.post(
                f"{SUPABASE_URL}/rest/v1/{table_name}",
                headers=headers,
                json=test_record
            )

            # If the column doesn't exist, we'll get PGRST204
            if "Could not find the" not in resp.text:
                valid.append(col)
                # Delete test record
                client.delete(
                    f"{SUPABASE_URL}/rest/v1/{table_name}?jurisdiction_id=eq.999999",
                    headers={**headers, "Content-Type": "application/json"}
                )

        except Exception as e:
            pass

    client.close()
    return valid


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


def upload_records(table_name: str, records: list, valid_columns: list, field_map: dict) -> int:
    """Upload records using only valid columns"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

    client = httpx.Client(timeout=60)
    saved = 0

    for record in records:
        clean_record = {}

        # Map fields
        for table_col in valid_columns:
            source_field = field_map.get(table_col, table_col)
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

        except:
            pass

    client.close()
    return saved


def main():
    print("="*60)
    print("DISCOVER AND UPLOAD")
    print("="*60)

    # Discover columns for each table
    tables_to_check = [
        "ordinances",
        "overlay_districts",
        "conditional_uses",
        "entitlement_timelines",
        "development_bonuses"
    ]

    print("\nDiscovering table schemas...")
    table_columns = {}
    for table in tables_to_check:
        cols = discover_valid_columns(table)
        table_columns[table] = cols
        print(f"  {table}: {cols}")

    # Load data
    data = get_latest_extraction()
    if not data:
        print("No extraction data found")
        return

    print(f"\nExtracted data:")
    for key, records in data.get("data", {}).items():
        print(f"  {key}: {len(records)}")

    # Define field mappings (source field -> might map to multiple table columns)
    field_maps = {
        "ordinances": {
            "jurisdiction_id": "jurisdiction_id",
            "ordinance_number": "ordinance_number",
            "title": "ordinance_number",  # fallback
            "source_url": "source_url",
            "passed_date": "passed_date",
            "type": "ordinance_type",
            "category": "ordinance_type",
        },
        "overlay_districts": {
            "jurisdiction_id": "jurisdiction_id",
            "overlay_code": "overlay_code",
            "overlay_name": "overlay_name",
            "name": "overlay_name",
            "code": "overlay_code",
            "overlay_type": "overlay_type",
            "type": "overlay_type",
            "source_url": "source_url",
        },
        "conditional_uses": {
            "jurisdiction_id": "jurisdiction_id",
            "district_code": "district_code",
            "use_name": "use_name",
            "name": "use_name",
            "use_category": "use_category",
            "category": "use_category",
            "source_url": "source_url",
        },
        "entitlement_timelines": {
            "jurisdiction_id": "jurisdiction_id",
            "entitlement_type": "entitlement_type",
            "type": "entitlement_type",
            "process_name": "process_name",
            "name": "process_name",
            "source_url": "source_url",
        },
        "development_bonuses": {
            "jurisdiction_id": "jurisdiction_id",
            "bonus_name": "bonus_name",
            "name": "bonus_name",
            "bonus_type": "bonus_type",
            "type": "bonus_type",
            "source_url": "source_url",
        }
    }

    # Upload data
    print("\n" + "="*60)
    print("UPLOADING DATA")
    print("="*60)

    results = {}
    for table in tables_to_check:
        data_key = table
        if data_key not in data.get("data", {}):
            continue

        records = data["data"][data_key]
        valid_cols = table_columns.get(table, ["jurisdiction_id"])
        field_map = field_maps.get(table, {})

        print(f"\n{table}:")
        print(f"  Valid columns: {valid_cols}")
        print(f"  Records to upload: {len(records)}")

        saved = upload_records(table, records, valid_cols, field_map)
        results[table] = saved
        print(f"  Saved: {saved}")

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    total = sum(results.values())
    for table, count in results.items():
        print(f"  {table}: {count}")
    print(f"\n  TOTAL: {total} records")


if __name__ == "__main__":
    main()
