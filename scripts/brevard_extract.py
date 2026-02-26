#!/usr/bin/env python3
"""
Brevard County Zone Standards Extractor
Fetches dimensional standards from Municode for all 13 Brevard jurisdictions
Uses Jina reader + Claude API for structured extraction
Upserts to Supabase zone_standards table
"""
import os, sys, json, re, time, httpx
from datetime import datetime, timezone

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

SB_H = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

client = httpx.Client(timeout=90, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0"})

# ── Jurisdiction config: name → Municode nodeId URL for dimensional standards ─
JURISDICTIONS = {
    "Melbourne":          "https://library.municode.com/fl/melbourne/codes/code_of_ordinances?nodeId=PTIIILADERE_APXBZO_ARTVDIRE_S2DIUSDIST",
    "Palm Bay":           "https://library.municode.com/fl/palm_bay/codes/code_of_ordinances",
    "Titusville":         "https://library.municode.com/fl/titusville/codes/code_of_ordinances",
    "Rockledge":          "https://library.municode.com/fl/rockledge/codes/land_development_regulations_?nodeId=SPBLADERE_CH118PLZODI_ARTIVZODI",
    "West Melbourne":     "https://library.municode.com/fl/west_melbourne/codes/code_of_ordinances?nodeId=PTIICOOR_CH98ZO_ARTIIIDI",
    "Cocoa":              "https://library.municode.com/fl/cocoa/codes/code_of_ordinances",
    "Cocoa Beach":        "https://library.municode.com/fl/cocoa_beach/codes/land_development_code?nodeId=APXBLADECO_CHIIZODI",
    "Cape Canaveral":     "https://library.municode.com/fl/cape_canaveral/codes/code_of_ordinances?nodeId=SPBLADECO_CH110ZO",
    "Indian Harbour Beach": "https://library.municode.com/fl/indian_harbour_beach/codes/code_of_ordinances",
    "Malabar":            "https://library.municode.com/fl/malabar/codes/code_of_ordinances",
    "Melbourne Beach":    "https://library.municode.com/fl/melbourne_beach/codes/code_of_ordinances",
    "Indialantic":        "https://library.municode.com/fl/indialantic/codes/code_of_ordinances",
    "Brevard County (Unincorporated)": "https://library.municode.com/fl/brevard_county/codes/code_of_ordinances?nodeId=COORBRCOFLVOII_CH62LADERE_ARTVIZORE",
}


def jina_fetch(url: str) -> str:
    """Fetch Municode page via Jina reader (handles JS rendering)."""
    r = client.get(f"https://r.jina.ai/{url}", timeout=60)
    return r.text if r.status_code == 200 else ""


def claude_extract(content: str, jurisdiction: str) -> list:
    """Use Claude API to extract structured zone_standards from ordinance text."""
    # Trim to 80K chars to stay within token limits
    trimmed = content[:80000]
    
    prompt = f"""You are extracting zoning dimensional standards from the {jurisdiction} municipal code.

From the text below, extract ALL zoning district dimensional standards tables. Return ONLY a JSON array.
Each object must have these exact keys (use null for missing values):
- district_code: string (e.g. "R-1", "C-2", "MF-1")
- district_name: string or null
- min_lot_sqft: number or null (convert acres: 1 acre = 43560 sqft)
- min_lot_width_ft: number or null
- min_lot_depth_ft: number or null
- max_height_ft: number or null (convert stories: 1 story = 12ft)
- front_setback_ft: number or null
- side_setback_ft: number or null  
- rear_setback_ft: number or null
- corner_setback_ft: number or null
- max_lot_coverage_pct: number or null
- max_far: number or null
- max_density_du_acre: number or null

Rules:
- Only extract rows that are clearly zoning districts (R-1, C-2, etc.)
- Skip overlay districts, special purpose districts unless clearly dimensional
- If a value has multiple sub-values (e.g. SF vs MF), use the single-family/base value
- Extract ALL districts found, even if data is sparse
- Return ONLY the JSON array, no explanation

ORDINANCE TEXT:
{trimmed}"""

    r = client.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        },
        json={
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}]
        },
        timeout=60
    )
    
    if r.status_code != 200:
        print(f"  Claude API error: {r.status_code} {r.text[:200]}")
        return []
    
    text = r.json()["content"][0]["text"].strip()
    # Strip markdown fences if present
    text = re.sub(r'^```(?:json)?\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"  JSON parse error: {e}")
        print(f"  Response preview: {text[:500]}")
        return []


def get_jurisdiction_id(name: str) -> int | None:
    """Get jurisdiction ID from Supabase."""
    r = client.get(
        f"{SUPABASE_URL}/rest/v1/jurisdictions",
        headers=SB_H,
        params={"name": f"eq.{name}", "select": "id,name", "limit": "1"}
    )
    rows = r.json()
    return rows[0]["id"] if rows else None


def get_districts(jurisdiction_id: int) -> dict:
    """Get zoning districts for jurisdiction. Returns {code: id}"""
    r = client.get(
        f"{SUPABASE_URL}/rest/v1/zoning_districts",
        headers=SB_H,
        params={"jurisdiction_id": f"eq.{jurisdiction_id}", "select": "id,code", "limit": "200"}
    )
    return {d["code"].upper(): d["id"] for d in r.json()}


def upsert_standards(district_id: int, data: dict, source_url: str) -> bool:
    """Upsert zone_standards row."""
    payload = {
        "zoning_district_id": district_id,
        "min_lot_sqft": data.get("min_lot_sqft"),
        "min_lot_width_ft": data.get("min_lot_width_ft"),
        "min_lot_depth_ft": data.get("min_lot_depth_ft"),
        "max_height_ft": data.get("max_height_ft"),
        "front_setback_ft": data.get("front_setback_ft"),
        "side_setback_ft": data.get("side_setback_ft"),
        "rear_setback_ft": data.get("rear_setback_ft"),
        "corner_setback_ft": data.get("corner_setback_ft"),
        "max_lot_coverage_pct": data.get("max_lot_coverage_pct"),
        "max_far": data.get("max_far"),
        "max_density_du_acre": data.get("max_density_du_acre"),
        "source_url": source_url,
        "confidence_score": 0.82,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
    }
    # Remove None values to avoid overwriting existing data
    payload = {k: v for k, v in payload.items() if v is not None}
    
    # Check if standards already exist
    existing = client.get(
        f"{SUPABASE_URL}/rest/v1/zone_standards",
        headers=SB_H,
        params={"zoning_district_id": f"eq.{district_id}", "select": "id", "limit": "1"}
    ).json()
    
    if existing:
        # Update
        r = client.patch(
            f"{SUPABASE_URL}/rest/v1/zone_standards",
            headers={**SB_H, "Prefer": "return=minimal"},
            params={"zoning_district_id": f"eq.{district_id}"},
            json=payload
        )
    else:
        # Insert
        r = client.post(
            f"{SUPABASE_URL}/rest/v1/zone_standards",
            headers=SB_H,
            json=payload
        )
    
    return r.status_code in (200, 201, 204)


def update_completeness(jurisdiction_id: int, name: str):
    """Recalculate and update data_completeness for a jurisdiction."""
    districts = client.get(
        f"{SUPABASE_URL}/rest/v1/zoning_districts",
        headers=SB_H,
        params={"jurisdiction_id": f"eq.{jurisdiction_id}", "select": "id"}
    ).json()
    
    if not districts:
        return
    
    total = len(districts)
    has_standards = 0
    for d in districts:
        s = client.get(
            f"{SUPABASE_URL}/rest/v1/zone_standards",
            headers=SB_H,
            params={"zoning_district_id": f"eq.{d['id']}", "select": "id", "limit": "1"}
        ).json()
        if s:
            has_standards += 1
    
    completeness = round((has_standards / total) * 100, 1)
    
    client.patch(
        f"{SUPABASE_URL}/rest/v1/jurisdictions",
        headers={**SB_H, "Prefer": "return=minimal"},
        params={"id": f"eq.{jurisdiction_id}"},
        json={
            "data_completeness": completeness,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "skill_last_validated": datetime.now(timezone.utc).isoformat(),
        }
    )
    print(f"  → Updated completeness: {has_standards}/{total} districts = {completeness}%")


def process_jurisdiction(name: str, url: str) -> dict:
    """Full pipeline for one jurisdiction."""
    print(f"\n{'='*60}")
    print(f"Processing: {name}")
    print(f"URL: {url[:80]}")
    
    # Get jurisdiction ID
    jid = get_jurisdiction_id(name)
    if not jid:
        print(f"  ❌ Jurisdiction not found in DB")
        return {"name": name, "status": "not_found"}
    
    # Get existing districts
    districts = get_districts(jid)
    print(f"  Districts in DB: {len(districts)}")
    
    if not districts:
        print(f"  ⚠️  No districts found, skipping")
        return {"name": name, "status": "no_districts"}
    
    # Fetch Municode content
    print(f"  Fetching via Jina...")
    content = jina_fetch(url)
    print(f"  Content size: {len(content)} chars")
    
    if len(content) < 1000:
        print(f"  ❌ Content too small, likely fetch failed")
        return {"name": name, "status": "fetch_failed", "size": len(content)}
    
    # Extract with Claude
    print(f"  Extracting with Claude API...")
    extracted = claude_extract(content, name)
    print(f"  Extracted: {len(extracted)} district standards")
    
    if not extracted:
        return {"name": name, "status": "no_extraction"}
    
    # Match extracted to DB districts and upsert
    matched = 0
    unmatched = []
    
    for row in extracted:
        code = (row.get("district_code") or "").upper().strip()
        if not code:
            continue
        
        # Try exact match first, then fuzzy
        dist_id = districts.get(code)
        if not dist_id:
            # Try without hyphens
            dist_id = districts.get(code.replace("-", ""))
        if not dist_id:
            # Try common variations
            for db_code in districts:
                if db_code.replace("-", "").replace(" ", "") == code.replace("-", "").replace(" ", ""):
                    dist_id = districts[db_code]
                    break
        
        if dist_id:
            success = upsert_standards(dist_id, row, url)
            if success:
                matched += 1
                print(f"    ✅ {code}: lot={row.get('min_lot_sqft')} height={row.get('max_height_ft')} front={row.get('front_setback_ft')}")
        else:
            unmatched.append(code)
    
    if unmatched:
        print(f"  ⚠️  Unmatched codes (not in DB): {unmatched[:10]}")
    
    # Update completeness
    update_completeness(jid, name)
    
    return {
        "name": name, "status": "success",
        "extracted": len(extracted), "matched": matched,
        "unmatched": len(unmatched)
    }


def main():
    target = os.environ.get("TARGET_JURISDICTION", "all")
    
    if target == "all":
        targets = JURISDICTIONS
    else:
        targets = {k: v for k, v in JURISDICTIONS.items() if k.lower() == target.lower()}
        if not targets:
            print(f"Unknown jurisdiction: {target}")
            sys.exit(1)
    
    print(f"ZoneWise Brevard Extractor — {len(targets)} jurisdiction(s)")
    print(f"Started: {datetime.now(timezone.utc).isoformat()}")
    
    results = []
    for name, url in targets.items():
        try:
            result = process_jurisdiction(name, url)
            results.append(result)
            time.sleep(2)  # Rate limit between jurisdictions
        except Exception as e:
            print(f"  ❌ EXCEPTION: {e}")
            results.append({"name": name, "status": "exception", "error": str(e)})
    
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    total_matched = 0
    for r in results:
        status_icon = "✅" if r["status"] == "success" else "❌"
        matched = r.get("matched", 0)
        total_matched += matched
        print(f"  {status_icon} {r['name']}: {r['status']} | matched={matched}")
    
    print(f"\nTotal standards upserted: {total_matched}")
    print(f"Finished: {datetime.now(timezone.utc).isoformat()}")
    
    # Exit non-zero if all failed
    successes = sum(1 for r in results if r["status"] == "success")
    if successes == 0 and len(results) > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
