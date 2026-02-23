#!/usr/bin/env python3
"""
Merge Mode 1/2/3 results → upsert to Supabase
Called by nightly-county-scrape.yml after all modes complete
"""
import os, sys, json, argparse, httpx
from pathlib import Path
from datetime import datetime, timezone

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
H = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}

def load_result(path):
    if path and Path(path).exists():
        return json.loads(Path(path).read_text())
    return {}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--county", required=True)
    parser.add_argument("--co-no", type=int, required=True)
    parser.add_argument("--mode1"); parser.add_argument("--mode2"); parser.add_argument("--mode3")
    args = parser.parse_args()

    m1 = load_result(args.mode1)
    m2 = load_result(args.mode2)
    m3 = load_result(args.mode3)

    # Merge: prefer Mode 2 data, fall back to Mode 3, use Mode 1 for portal URL
    portal_url = m1.get("portal_url") or m2.get("source_url") or m3.get("source_url")
    success = m2.get("success") or m3.get("success", False)

    if portal_url:
        r = httpx.patch(
            f"{SUPABASE_URL}/rest/v1/jurisdictions",
            headers={**H, "Prefer": "return=representation"},
            params={"county": f"ilike.%{args.county}%"},
            json={"code_source": portal_url, "skill_validated_at": datetime.now(timezone.utc).isoformat()},
            timeout=15,
        )
        print(f"Updated jurisdictions.code_source: {r.status_code}")

    # TODO: Insert extracted zoning_districts + zone_standards + permitted_uses
    # This is populated by Claude API structured extraction in Mode 2/3
    print(f"Upsert complete: county={args.county}, success={success}")
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
