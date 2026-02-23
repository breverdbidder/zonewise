#!/usr/bin/env python3
"""
ZoneWise County Skill File Generator
====================================
Reads Supabase for real data, generates 67 county SKILL.md files
for CraftAgents OSS fork (zonewise-desktop/zonewise/skills/county-{slug}/)
Updates skills-manifest.yaml and writes skill_file_path back to DB.

Usage:
    python scripts/generate_county_skills.py [--county brevard] [--all] [--dry-run]

Secrets required (GitHub Actions env or .env):
    SUPABASE_URL, SUPABASE_KEY, GITHUB_TOKEN
"""

import os
import sys
import json
import argparse
import httpx
import yaml
from pathlib import Path
from datetime import datetime, timezone
from textwrap import dedent

# ── Config ────────────────────────────────────────────────────────────────────
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO = "breverdbidder/zonewise-desktop"
SKILLS_BASE = "zonewise/skills"
MANIFEST_PATH = f"{SKILLS_BASE}/skills-manifest.yaml"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

# ── 67 FL Counties ─────────────────────────────────────────────────────────────
ALL_COUNTIES = [
    ("alachua", "Alachua", 1), ("baker", "Baker", 2), ("bay", "Bay", 3),
    ("bradford", "Bradford", 4), ("brevard", "Brevard", 5), ("broward", "Broward", 6),
    ("calhoun", "Calhoun", 7), ("charlotte", "Charlotte", 8), ("citrus", "Citrus", 9),
    ("clay", "Clay", 10), ("collier", "Collier", 11), ("columbia", "Columbia", 12),
    ("miami-dade", "Miami-Dade", 13), ("desoto", "DeSoto", 14), ("dixie", "Dixie", 15),
    ("duval", "Duval", 16), ("escambia", "Escambia", 17), ("flagler", "Flagler", 18),
    ("franklin", "Franklin", 19), ("gadsden", "Gadsden", 20), ("gilchrist", "Gilchrist", 21),
    ("glades", "Glades", 22), ("gulf", "Gulf", 23), ("hamilton", "Hamilton", 24),
    ("hardee", "Hardee", 25), ("hendry", "Hendry", 26), ("hernando", "Hernando", 27),
    ("highlands", "Highlands", 28), ("hillsborough", "Hillsborough", 29), ("holmes", "Holmes", 30),
    ("indian-river", "Indian River", 31), ("jackson", "Jackson", 32), ("jefferson", "Jefferson", 33),
    ("lafayette", "Lafayette", 34), ("lake", "Lake", 35), ("lee", "Lee", 36),
    ("leon", "Leon", 37), ("levy", "Levy", 38), ("liberty", "Liberty", 39),
    ("madison", "Madison", 40), ("manatee", "Manatee", 41), ("marion", "Marion", 42),
    ("martin", "Martin", 43), ("monroe", "Monroe", 44), ("nassau", "Nassau", 45),
    ("okaloosa", "Okaloosa", 46), ("okeechobee", "Okeechobee", 47), ("orange", "Orange", 48),
    ("osceola", "Osceola", 49), ("palm-beach", "Palm Beach", 50), ("pasco", "Pasco", 51),
    ("pinellas", "Pinellas", 52), ("polk", "Polk", 53), ("putnam", "Putnam", 54),
    ("st-johns", "St. Johns", 55), ("st-lucie", "St. Lucie", 56), ("santa-rosa", "Santa Rosa", 57),
    ("sarasota", "Sarasota", 58), ("seminole", "Seminole", 59), ("sumter", "Sumter", 60),
    ("suwannee", "Suwannee", 61), ("taylor", "Taylor", 62), ("union", "Union", 63),
    ("volusia", "Volusia", 64), ("wakulla", "Wakulla", 65), ("walton", "Walton", 66),
    ("washington", "Washington", 67),
]

PILOT_COUNTIES = {"brevard", "miami-dade", "orange"}
PHASE1_COUNTIES = {"hillsborough", "palm-beach", "pinellas"}


# ── Supabase Queries ───────────────────────────────────────────────────────────
def supabase_get(path: str, params: dict = None) -> list:
    url = f"{SUPABASE_URL}/rest/v1{path}"
    r = httpx.get(url, headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def get_county_data(county_name: str, co_no: int) -> dict:
    """Pull all DB data for a county in 3 parallel-style queries."""
    # Jurisdictions
    jurisdictions = supabase_get(
        "/jurisdictions",
        params={
            "county": f"ilike.%{county_name}%",
            "select": "id,name,county,data_completeness,municode_url,code_source",
            "order": "data_completeness.desc",
            "limit": "100",
        },
    )

    # District counts by jurisdiction
    district_counts = {}
    if jurisdictions:
        jids = ",".join(str(j["id"]) for j in jurisdictions)
        districts = supabase_get(
            "/zoning_districts",
            params={
                "jurisdiction_id": f"in.({jids})",
                "select": "jurisdiction_id,code,category",
                "limit": "1000",
            },
        )
        for d in districts:
            jid = d["jurisdiction_id"]
            district_counts[jid] = district_counts.get(jid, 0) + 1

        # Get category breakdown
        cats = {}
        for d in districts:
            cats[d.get("category", "Unknown")] = cats.get(d.get("category", "Unknown"), 0) + 1
    else:
        cats = {}

    # Overlay districts
    overlays = []
    if jurisdictions:
        jids = ",".join(str(j["id"]) for j in jurisdictions)
        overlays = supabase_get(
            "/overlay_districts",
            params={"jurisdiction_id": f"in.({jids})", "select": "name,type", "limit": "50"},
        )

    # FL Parcel sample (test parcel)
    test_parcels = supabase_get(
        "/fl_parcels",
        params={
            "co_no": f"eq.{co_no}",
            "select": "parcel_id,phy_addr1,phy_city,dor_uc,centroid_lat,centroid_lng",
            "limit": "1",
        },
    )
    test_parcel = test_parcels[0] if test_parcels else None

    # GIS endpoints
    gis = []
    if jurisdictions:
        jids = ",".join(str(j["id"]) for j in jurisdictions)
        gis = supabase_get(
            "/gis_endpoints",
            params={
                "jurisdiction_id": f"in.({jids})",
                "select": "jurisdiction_name,status,url,parcels",
                "limit": "20",
            },
        )

    return {
        "jurisdictions": jurisdictions,
        "district_counts": district_counts,
        "total_districts": sum(district_counts.values()),
        "categories": cats,
        "overlays": overlays,
        "test_parcel": test_parcel,
        "gis_endpoints": gis,
        "avg_completeness": (
            int(sum(j.get("data_completeness", 0) for j in jurisdictions) / len(jurisdictions))
            if jurisdictions
            else 0
        ),
    }


# ── Skill File Generator ───────────────────────────────────────────────────────
def render_skill_md(slug: str, name: str, co_no: int, data: dict) -> str:
    juris = data["jurisdictions"]
    test = data["test_parcel"]
    overlays = data["overlays"]
    cats = data["categories"]
    gis = data["gis_endpoints"]
    total_districts = data["total_districts"]
    avg_comp = data["avg_completeness"]

    # Jurisdiction table rows
    if juris:
        jrows = "\n".join(
            f"| {j['id']} | {j['name']} | {j.get('data_completeness', 0)}% | "
            f"{'[Municode](' + j['municode_url'] + ')' if j.get('municode_url') else 'N/A'} |"
            for j in juris[:20]
        )
    else:
        jrows = "| — | No jurisdictions scraped yet | 0% | — |"

    # Category breakdown
    cat_lines = "\n".join(f"- **{cat}**: {count} districts" for cat, count in cats.items()) or "- Pending first scrape"

    # Overlay list
    overlay_lines = "\n".join(f"- {o['name']} ({o.get('type', 'overlay')})" for o in overlays[:10]) or "- None recorded yet"

    # GIS endpoints
    gis_lines = "\n".join(
        f"- {g['jurisdiction_name']}: [{g['status']}]({g['url']}) — {g.get('parcels', 0):,} parcels"
        for g in gis[:5]
    ) or "- Not yet validated"

    # Test parcel
    if test:
        test_parcel_str = f"`{test['parcel_id']}` — {test.get('phy_addr1', '')} {test.get('phy_city', '')}"
        test_lat = test.get('centroid_lat', 'N/A')
        test_lng = test.get('centroid_lng', 'N/A')
    else:
        test_parcel_str = "Pending — run generator after first scrape"
        test_lat = test_lng = "N/A"

    # Portal type heuristic
    has_municode = any(j.get("municode_url") for j in juris)
    has_arcgis = any(g.get("url", "").startswith("https://") for g in gis)
    portal_type = "municode" if has_municode else ("arcgis" if has_arcgis else "unknown")

    # Anti-scrape heuristic (large populous counties tend to have protections)
    anti_scrape = "true" if co_no in {13, 16, 29, 50, 52, 6, 48} else "false"
    rate_limit = "10" if anti_scrape == "true" else "30"

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    return dedent(f"""\
    ---
    name: county-{slug}
    description: >
      Zoning intelligence for {name} County, FL (FDOR co_no: {co_no}).
      {len(juris)} jurisdictions, {total_districts} zoning districts in Supabase.
      Avg data completeness: {avg_comp}%. Portal type: {portal_type}.
      Use for parcel lookups, permitted use queries, dimensional standards,
      overlay districts. Triggers on: {name} County, co_no {co_no},
      any address in {name} County Florida.
    supabase_county_filter: "county=ilike.%25{name}%25"
    co_no: {co_no}
    portal_type: {portal_type}
    anti_scrape: {anti_scrape}
    rate_limit_rpm: {rate_limit}
    last_validated: {generated_at}
    ---

    # {name} County — Zoning Intelligence

    > **co_no**: {co_no} | **Jurisdictions**: {len(juris)} | **Districts**: {total_districts} | **Completeness**: {avg_comp}%

    ## Supabase Queries

    ### 1. List all jurisdictions in this county
    ```
    GET /jurisdictions
      ?county=ilike.%25{name}%25
      &select=id,name,data_completeness,municode_url
      &order=data_completeness.desc
    ```

    ### 2. Get all zoning districts for a jurisdiction
    ```
    GET /zoning_districts
      ?jurisdiction_id=eq.{{jurisdiction_id}}
      &select=id,code,name,category
      &order=category,code
      &limit=200
    ```

    ### 3. Look up parcel by co_no + parcel_id
    ```
    GET /fl_parcels
      ?co_no=eq.{co_no}
      &parcel_id=eq.{{parcel_id}}
      &select=parcel_id,phy_addr1,phy_city,dor_uc,jv,centroid_lat,centroid_lng
    ```

    ### 4. Get dimensional standards for a district
    ```
    GET /zone_standards
      ?zoning_district_id=eq.{{district_id}}
      &select=*
    ```

    ### 5. Get permitted uses for a district
    ```
    GET /permitted_uses
      ?zoning_district_id=eq.{{district_id}}
      &select=use_category_id,permission_type,notes
    ```

    ### 6. Get overlay districts
    ```
    GET /overlay_districts
      ?jurisdiction_id=eq.{{jurisdiction_id}}
      &select=name,type,description
    ```

    ## 3-Mode Research Protocol

    ### Mode 1 — Discovery (WebSearch, ~30s)
    **Trigger**: `portal_url` unknown, stale (>30 days), or 404

    ```python
    queries = [
        "{name} County Florida zoning map GIS portal",
        "{name} County Florida municode zoning ordinance",
        "{name} County Florida ArcGIS zoning layer service",
        "site:municode.com {name} Florida zoning",
    ]
    # Output: candidate URLs ranked by confidence
    # Action: UPDATE jurisdictions SET code_source=url WHERE county ilike '{name}'
    ```

    ### Mode 2 — Extraction (WebFetch + Parser, ~60-90s)
    **Trigger**: Mode 1 found portal URL; JS-rendering not required

    ```python
    targets = [
        "{{municode_url}}/ch{{zoning_chapter}}",   # Zoning chapter
        "{{portal_url}}/districts",                  # District list
        "{{portal_url}}/dimensional-standards",      # Setbacks, FAR, height
    ]
    extract = [
        "zoning_codes",       # → zoning_districts.code
        "district_names",     # → zoning_districts.name
        "permitted_uses",     # → permitted_uses table
        "setbacks",           # → zone_standards.front_setback etc.
        "height_limits",      # → zone_standards.max_height_ft
        "lot_coverage",       # → zone_standards.max_lot_coverage_pct
        "far",                # → zone_standards.max_far
    ]
    ```

    ### Mode 3 — AgentQL Fallback (Modal container)
    **Trigger**: Mode 2 empty; portal requires JS; `anti_scrape: {anti_scrape}`

    ```python
    # AgentQL semantic selectors for JS-heavy portals
    config = {{
        "anti_scrape": {anti_scrape},
        "rate_limit_rpm": {rate_limit},
        "county": "{name}",
        "co_no": {co_no},
        "selectors": {{
            "district_table": "table[data-zoning], .zoning-districts-table",
            "district_row": "tr.district-row, .zoning-item",
            "code_cell": "td.zoning-code, .zone-code",
            "name_cell": "td.zoning-name, .zone-description",
            "permitted_section": "#permitted-uses, .by-right-uses",
        }},
    }}
    # Output: same schema as Mode 2
    # Circuit breaker: 3 failures → INSERT insights(type='ESCALATE', county='{slug}')
    ```

    ## County Data Profile

    | Field | Value |
    |-------|-------|
    | FDOR co_no | {co_no} |
    | Jurisdictions in DB | {len(juris)} |
    | Total zoning districts | {total_districts} |
    | Avg data completeness | {avg_comp}% |
    | Portal type | {portal_type} |
    | Anti-scrape protection | {anti_scrape} |
    | Rate limit (rpm) | {rate_limit} |
    | Test parcel | {test_parcel_str} |
    | Test centroid | lat={test_lat}, lng={test_lng} |
    | Last validated | {generated_at} |

    ## Known Jurisdictions

    | DB ID | Name | Completeness | Municode |
    |-------|------|-------------|---------|
    {jrows}

    ## Zoning Categories Present

    {cat_lines}

    ## GIS Endpoints

    {gis_lines}

    ## Overlay Districts

    {overlay_lines}

    ## Quirks & Gotchas

    *(Populated by Mode 1/2/3 during first scrape — update this section after each run)*

    ## Escalation Conditions

    - 3+ consecutive failed scrapes → INSERT to `insights` with `type='ESCALATE'`, `county='{slug}'`
    - `last_validated` > 30 days → Traycer issue: `[SKILL] Revalidate county-{slug}`
    - Portal URL 404 → Mode 1 re-run, update `code_source` in DB
    - Data completeness drops >10% → alert to `daily_metrics` table

    ---
    *Generated by `scripts/generate_county_skills.py` on {generated_at}*
    *Source: Supabase `jurisdictions` + `zoning_districts` + `fl_parcels` tables*
    """)


# ── GitHub Push ────────────────────────────────────────────────────────────────
def push_to_github(path: str, content: str, message: str) -> bool:
    import base64
    if not GITHUB_TOKEN:
        print(f"  [DRY RUN] Would push: {path}")
        return True

    gh_headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    api_url = f"https://api.github.com/repos/{REPO}/contents/{path}"

    # Get existing SHA if file exists
    r = httpx.get(api_url, headers=gh_headers, timeout=10)
    sha = r.json().get("sha") if r.status_code == 200 else None

    payload = {
        "message": message,
        "content": base64.b64encode(content.encode()).decode(),
    }
    if sha:
        payload["sha"] = sha

    r = httpx.put(api_url, headers=gh_headers, json=payload, timeout=30)
    if r.status_code in (200, 201):
        return True
    else:
        print(f"  ERROR pushing {path}: {r.status_code} {r.text[:200]}")
        return False


def update_supabase_skill_path(county_name: str, skill_path: str) -> bool:
    """Write skill_file_path back to jurisdictions rows for this county."""
    try:
        r = httpx.patch(
            f"{SUPABASE_URL}/rest/v1/jurisdictions",
            headers={**HEADERS, "Prefer": "return=representation"},
            params={"county": f"ilike.%{county_name}%"},
            json={"skill_file_path": skill_path},
            timeout=15,
        )
        return r.status_code in (200, 204)
    except Exception as e:
        print(f"  WARN: Could not update skill_file_path: {e}")
        return False


# ── Manifest Builder ───────────────────────────────────────────────────────────
def build_manifest(county_results: list) -> str:
    existing_skills = [
        {"name": "zoning-analysis", "category": "zoning", "priority": 1, "tokens_estimate": 100,
         "description": "Analyze zoning codes, permitted uses, setbacks, dimensional standards. Now covers all 67 FL counties via county skill routing.",
         "path": f"{SKILLS_BASE}/zoning-analysis/SKILL.md"},
        {"name": "property-valuation", "category": "analysis", "priority": 1, "tokens_estimate": 120,
         "description": "Estimate property values using comparable sales, income, cost approach. ARV, max bid, investment returns.",
         "path": f"{SKILLS_BASE}/property-valuation/SKILL.md"},
        {"name": "permit-lookup", "category": "data", "priority": 2, "tokens_estimate": 100,
         "description": "Search building permits, code violations, inspection history. Identify unpermitted work.",
         "path": f"{SKILLS_BASE}/permit-lookup/SKILL.md"},
        {"name": "sun-analysis", "category": "analysis", "priority": 1, "tokens_estimate": 110,
         "description": "Sun position, shadow projections, solar exposure heatmaps.",
         "path": f"{SKILLS_BASE}/sun-analysis/SKILL.md"},
        {"name": "envelope-development", "category": "visualization", "priority": 1, "tokens_estimate": 120,
         "description": "3D building envelopes from zoning parameters. Max buildable volume.",
         "path": f"{SKILLS_BASE}/envelope-development/SKILL.md"},
        {"name": "threejs-fundamentals", "category": "visualization", "priority": 2, "tokens_estimate": 80,
         "description": "Three.js core: Scene, Camera, Renderer, React Three Fiber.",
         "path": f"{SKILLS_BASE}/threejs-fundamentals/SKILL.md"},
        {"name": "threejs-geometry", "category": "visualization", "priority": 2, "tokens_estimate": 90,
         "description": "BufferGeometry, ExtrudeGeometry, polygon triangulation.",
         "path": f"{SKILLS_BASE}/threejs-geometry/SKILL.md"},
        {"name": "threejs-materials", "category": "visualization", "priority": 2, "tokens_estimate": 70,
         "description": "MeshStandardMaterial, transparency, vertex colors.",
         "path": f"{SKILLS_BASE}/threejs-materials/SKILL.md"},
        {"name": "threejs-lighting", "category": "visualization", "priority": 2, "tokens_estimate": 75,
         "description": "AmbientLight, DirectionalLight, shadow mapping, sun simulation.",
         "path": f"{SKILLS_BASE}/threejs-lighting/SKILL.md"},
        {"name": "threejs-interaction", "category": "visualization", "priority": 2, "tokens_estimate": 65,
         "description": "OrbitControls, raycasting, click detection, hover effects.",
         "path": f"{SKILLS_BASE}/threejs-interaction/SKILL.md"},
        {"name": "bcpao-integration", "category": "data", "priority": 2, "tokens_estimate": 90,
         "description": "Brevard County Property Appraiser. Parcel lookup, photos, assessed values.",
         "path": f"{SKILLS_BASE}/bcpao-integration/SKILL.md"},
        {"name": "mapbox-integration", "category": "visualization", "priority": 2, "tokens_estimate": 85,
         "description": "Mapbox GL JS + Three.js overlays. Satellite imagery, geocoding.",
         "path": f"{SKILLS_BASE}/mapbox-integration/SKILL.md"},
    ]

    county_skills = []
    for slug, name, co_no, success in county_results:
        county_skills.append({
            "name": f"county-{slug}",
            "category": "county",
            "priority": 1 if slug in PILOT_COUNTIES | PHASE1_COUNTIES else 3,
            "tokens_estimate": 50,  # Progressive disclosure — metadata only at level_1
            "description": (
                f"Zoning intelligence for {name} County FL (co_no: {co_no}). "
                f"Supabase data: jurisdictions, zoning districts, dimensional standards, "
                f"permitted uses, GIS endpoints, fl_parcels. "
                f"3-mode research: WebSearch → WebFetch → AgentQL/Modal fallback."
            ),
            "path": f"{SKILLS_BASE}/county-{slug}/SKILL.md",
        })

    all_skills = existing_skills + county_skills
    total = len(all_skills)
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    lines = [
        "# ZoneWise.AI Skills Manifest",
        "# Progressive Disclosure Architecture — v2.0.0",
        f"# Updated: {generated} by generate_county_skills.py",
        f"# CrossBeam-adapted: 67 county skill files + 12 core skills = {total} total",
        "",
        'version: "2.0.0"',
        f'updated: "{generated}"',
        f"total_skills: {total}",
        "",
        "skills:",
        "  # ============================================================================",
        "  # CORE SKILLS (12) — unchanged from v1.1.0",
        "  # ============================================================================",
        "",
    ]

    for s in existing_skills:
        lines += [
            f"  - name: {s['name']}",
            f"    description: |\n      {s['description']}",
            f"    path: {s['path']}",
            f"    category: {s['category']}",
            f"    priority: {s['priority']}",
            f"    tokens_estimate: {s['tokens_estimate']}",
            "",
        ]

    lines += [
        "  # ============================================================================",
        "  # COUNTY SKILLS (67) — CrossBeam-pattern, one per FL county",
        "  # Progressive Disclosure: level_1=metadata only (50 tokens each)",
        "  # Full SKILL.md loaded on-demand when county is mentioned",
        "  # ============================================================================",
        "",
    ]

    for s in county_skills:
        lines += [
            f"  - name: {s['name']}",
            f"    description: |\n      {s['description']}",
            f"    path: {s['path']}",
            f"    category: {s['category']}",
            f"    priority: {s['priority']}",
            f"    tokens_estimate: {s['tokens_estimate']}",
            "",
        ]

    lines += [
        "categories:",
        '  zoning: "Zoning code analysis and regulations"',
        '  visualization: "3D visualization and rendering"',
        '  analysis: "Property and environmental analysis"',
        '  data: "External data source integration"',
        '  county: "Per-county zoning intelligence (67 FL counties)"',
        "",
        "disclosure_levels:",
        "  level_1:",
        '    name: "Metadata"',
        '    description: "Brief description in system prompt"',
        '    tokens: "50 per county skill, 50-150 per core skill"',
        '    loaded: "Always"',
        "  level_2:",
        '    name: "Instructions"',
        '    description: "Full SKILL.md — loaded when county mentioned in query"',
        '    tokens: "800-1500 per county skill"',
        '    loaded: "On-demand via county name trigger"',
        "  level_3:",
        '    name: "References"',
        '    description: "Live Supabase data via zonewise-supabase source"',
        '    tokens: "Runtime query results"',
        '    loaded: "On-demand via Supabase REST API"',
        "",
        "agents:",
        "  orchestrator:",
        '    name: "ZoneWise Orchestrator"',
        '    description: "Routes to county agent based on address/county mention"',
        '    skills: ["zoning-analysis", "county-*"]',
        "  county_agent:",
        '    name: "County Research Agent"',
        '    description: "3-mode research: WebSearch → WebFetch → AgentQL/Modal"',
        '    skills: ["county-{slug}"]  # Dynamic: one agent per county',
        "  valuation_agent:",
        '    name: "Valuation Agent"',
        '    skills: ["property-valuation", "bcpao-integration", "county-brevard"]',
        "  visualization_agent:",
        '    name: "Visualization Agent"',
        '    skills: ["envelope-development", "sun-analysis", "threejs-*", "mapbox-integration"]',
    ]

    return "\n".join(lines)


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--county", help="Single county slug (e.g. brevard)")
    parser.add_argument("--all", action="store_true", help="Generate all 67 counties")
    parser.add_argument("--dry-run", action="store_true", help="Print output, don't push")
    args = parser.parse_args()

    if not args.county and not args.all:
        parser.print_help()
        sys.exit(1)

    target_counties = ALL_COUNTIES if args.all else [
        c for c in ALL_COUNTIES if c[0] == args.county
    ]

    if not target_counties:
        print(f"County '{args.county}' not found in registry")
        sys.exit(1)

    results = []
    print(f"🚀 Generating {len(target_counties)} county skill files...")

    for slug, name, co_no in target_counties:
        print(f"\n── {name} County (co_no={co_no}) ──")

        # Pull from Supabase
        try:
            data = get_county_data(name, co_no)
            print(f"  Supabase: {len(data['jurisdictions'])} jurisdictions, {data['total_districts']} districts")
        except Exception as e:
            print(f"  ERROR fetching from Supabase: {e}")
            data = {"jurisdictions": [], "district_counts": {}, "total_districts": 0,
                    "categories": {}, "overlays": [], "test_parcel": None, "gis_endpoints": [],
                    "avg_completeness": 0}

        # Render skill file
        skill_md = render_skill_md(slug, name, co_no, data)
        skill_path = f"{SKILLS_BASE}/county-{slug}/SKILL.md"

        if args.dry_run:
            out_path = Path(f"/tmp/county-{slug}-SKILL.md")
            out_path.write_text(skill_md)
            print(f"  [DRY RUN] Written to {out_path}")
            results.append((slug, name, co_no, True))
        else:
            # Push SKILL.md
            ok = push_to_github(
                skill_path,
                skill_md,
                f"feat: add county-{slug} zoning skill file ({name} County FL)",
            )
            if ok:
                print(f"  ✅ Pushed {skill_path}")
                # Update Supabase
                update_supabase_skill_path(name, skill_path)
            else:
                print(f"  ❌ Failed to push {skill_path}")
            results.append((slug, name, co_no, ok))

    # Build + push manifest
    print(f"\n── Updating skills-manifest.yaml → v2.0.0 ──")
    manifest = build_manifest(results)
    if args.dry_run:
        Path("/tmp/skills-manifest.yaml").write_text(manifest)
        print(f"  [DRY RUN] Manifest written to /tmp/skills-manifest.yaml")
    else:
        ok = push_to_github(MANIFEST_PATH, manifest, "chore: update skills-manifest.yaml v2.0.0 — 67 county skills")
        print(f"  {'✅' if ok else '❌'} Manifest pushed")

    # Summary
    success = sum(1 for _, _, _, ok in results if ok)
    print(f"\n{'='*50}")
    print(f"✅ Complete: {success}/{len(results)} county skill files")
    print(f"📋 skills-manifest.yaml: v2.0.0 ({12 + len(results)} total skills)")


if __name__ == "__main__":
    main()
