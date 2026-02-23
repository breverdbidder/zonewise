#!/usr/bin/env python3
"""
County Research Agent — 3-Mode Research (CrossBeam pattern adapted for ZoneWise)
Mode 1: WebSearch  →  Mode 2: WebFetch  →  Mode 3: AgentQL/Modal fallback
Called by nightly-county-scrape.yml GitHub Action
"""
import os, sys, json, argparse, httpx
from pathlib import Path
from datetime import datetime, timezone

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

SUPABASE_H = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

def mode1_discovery(county: str, co_no: int) -> dict:
    """WebSearch: find portal URLs for this county."""
    queries = [
        f"{county} County Florida zoning ordinance municode",
        f"{county} County Florida GIS zoning layer ArcGIS service",
        f"site:municode.com {county} county florida",
    ]
    # In production: call search API (Brave/SerpAPI) for each query
    # Validate URLs, rank by confidence, return best candidates
    # For now: stub returns Municode pattern
    municode_slug = county.lower().replace(" ", "_").replace("-", "_")
    candidate_url = f"https://library.municode.com/fl/{municode_slug}"
    try:
        r = httpx.head(candidate_url, timeout=10, follow_redirects=True)
        valid = r.status_code == 200
    except Exception:
        valid = False
    return {
        "county": county, "co_no": co_no, "mode": 1,
        "portal_url": candidate_url if valid else None,
        "portal_valid": valid,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

def mode2_extraction(county: str, co_no: int, portal_url: str) -> dict:
    """WebFetch: extract zoning data from portal URL."""
    if not portal_url:
        return {"mode": 2, "success": False, "reason": "No portal URL from Mode 1"}
    try:
        r = httpx.get(portal_url, timeout=30, follow_redirects=True)
        if r.status_code != 200:
            return {"mode": 2, "success": False, "reason": f"HTTP {r.status_code}"}
        # Parse zoning chapters, district codes, dimensional standards
        # In production: use Claude API for structured extraction
        return {
            "mode": 2, "success": True,
            "source_url": portal_url,
            "content_length": len(r.text),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {"mode": 2, "success": False, "reason": str(e)}

def upsert_to_supabase(county: str, data: dict):
    """Write extracted data to Supabase jurisdictions + zone_standards."""
    # Update last_validated timestamp for all jurisdictions in this county
    r = httpx.patch(
        f"{SUPABASE_URL}/rest/v1/jurisdictions",
        headers={**SUPABASE_H, "Prefer": "return=representation"},
        params={"county": f"ilike.%{county}%"},
        json={"skill_validated_at": datetime.now(timezone.utc).isoformat()},
        timeout=15,
    )
    return r.status_code in (200, 204)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--county", required=True)
    parser.add_argument("--co-no", type=int, required=True)
    parser.add_argument("--mode", type=int, choices=[1,2,3], default=1)
    parser.add_argument("--input", help="JSON result from previous mode")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    prev = json.loads(Path(args.input).read_text()) if args.input and Path(args.input).exists() else {}

    if args.mode == 1:
        result = mode1_discovery(args.county, args.co_no)
    elif args.mode == 2:
        portal_url = prev.get("portal_url")
        result = mode2_extraction(args.county, args.co_no, portal_url)
    else:
        # Mode 3: AgentQL — invoked via Modal in workflow
        result = {"mode": 3, "note": "Invoked by modal run in workflow, not here"}

    Path(args.output).write_text(json.dumps(result, indent=2))
    print(f"Mode {args.mode} complete: {result.get('success', result.get('portal_valid', 'N/A'))}")

if __name__ == "__main__":
    main()
