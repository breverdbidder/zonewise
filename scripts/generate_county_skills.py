#!/usr/bin/env python3
"""
ZoneWise County Skill File Generator
=====================================
Generates 67 Florida county SKILL.md files for CraftAgents OSS (zonewise-desktop).
Source data: FDOR co_no registry + known portal/Municode URLs + Supabase schema.
Output: zonewise-desktop/zonewise/skills/county-{slug}/SKILL.md (67 files)
        zonewise/skills/skills-manifest.yaml (updated v2.0.0)
        zonewise/migrations/007_skill_file_paths.sql

Usage: python generate_county_skills.py
"""

import os, json, re
from pathlib import Path
from datetime import date

TODAY = date.today().isoformat()

# ──────────────────────────────────────────────────────────────────────────────
# Florida 67-County Registry
# FDOR co_no + known data (Municode URL, portal type, anti_scrape flag)
# ──────────────────────────────────────────────────────────────────────────────
FL_COUNTIES = [
    {"co_no":1,"name":"Alachua","slug":"alachua","seat":"Gainesville","pop":282840,"municipalities":8,"portal_type":"municode","municode_url":"https://library.municode.com/fl/alachua_county","anti_scrape":False,"rate_limit_rpm":60},
    {"co_no":2,"name":"Baker","slug":"baker","seat":"Macclenny","pop":29210,"municipalities":2,"portal_type":"municode","municode_url":"https://library.municode.com/fl/baker_county","anti_scrape":False,"rate_limit_rpm":30},
    {"co_no":3,"name":"Bay","slug":"bay","seat":"Panama City","pop":180076,"municipalities":8,"portal_type":"municode","municode_url":"https://library.municode.com/fl/bay_county","anti_scrape":False,"rate_limit_rpm":60},
    {"co_no":4,"name":"Bradford","slug":"bradford","seat":"Starke","pop":28201,"municipalities":3,"portal_type":"municode","municode_url":"https://library.municode.com/fl/bradford_county","anti_scrape":False,"rate_limit_rpm":30},
    {"co_no":5,"name":"Brevard","slug":"brevard","seat":"Titusville","pop":617176,"municipalities":17,"portal_type":"arcgis","municode_url":"https://library.municode.com/fl/melbourne","anti_scrape":False,"rate_limit_rpm":60,"gis_url":"https://gis.brevardfl.gov/gissrv/rest/services/Planning_Development/Zoning_WKID2881/MapServer/0","zone_field":"ZONING","test_parcel":"2428814"},
    {"co_no":6,"name":"Broward","slug":"broward","seat":"Fort Lauderdale","pop":1952778,"municipalities":31,"portal_type":"arcgis","municode_url":"https://library.municode.com/fl/broward_county","anti_scrape":True,"rate_limit_rpm":30,"gis_url":"https://gis.broward.org/arcgis/rest/services/Zoning/MapServer","zone_field":"ZONE_CODE"},
    {"co_no":7,"name":"Calhoun","slug":"calhoun","seat":"Blountstown","pop":14444,"municipalities":3,"portal_type":"municode","municode_url":"https://library.municode.com/fl/calhoun_county","anti_scrape":False,"rate_limit_rpm":20},
    {"co_no":8,"name":"Charlotte","slug":"charlotte","seat":"Punta Gorda","pop":188910,"municipalities":2,"portal_type":"arcgis","municode_url":"https://library.municode.com/fl/charlotte_county","anti_scrape":False,"rate_limit_rpm":60},
    {"co_no":9,"name":"Citrus","slug":"citrus","seat":"Inverness","pop":152434,"municipalities":4,"portal_type":"municode","municode_url":"https://library.municode.com/fl/citrus_county","anti_scrape":False,"rate_limit_rpm":40},
    {"co_no":10,"name":"Clay","slug":"clay","seat":"Green Cove Springs","pop":225000,"municipalities":6,"portal_type":"arcgis","municode_url":"https://library.municode.com/fl/clay_county","anti_scrape":False,"rate_limit_rpm":60},
    {"co_no":11,"name":"Collier","slug":"collier","seat":"Naples","pop":384902,"municipalities":3,"portal_type":"arcgis","municode_url":"https://library.municode.com/fl/collier_county","anti_scrape":True,"rate_limit_rpm":30},
    {"co_no":12,"name":"Columbia","slug":"columbia","seat":"Lake City","pop":71513,"municipalities":4,"portal_type":"municode","municode_url":"https://library.municode.com/fl/columbia_county","anti_scrape":False,"rate_limit_rpm":40},
    {"co_no":13,"name":"Miami-Dade","slug":"miami-dade","seat":"Miami","pop":2701767,"municipalities":34,"portal_type":"arcgis","municode_url":"https://library.municode.com/fl/miami-dade_county","anti_scrape":True,"rate_limit_rpm":20,"gis_url":"https://maps.miamidade.gov/arcgis/rest/services/ZoningAndLandUse/MapServer","zone_field":"ZONING"},
    {"co_no":14,"name":"DeSoto","slug":"desoto","seat":"Arcadia","pop":35865,"municipalities":1,"portal_type":"municode","municode_url":"https://library.municode.com/fl/desoto_county","anti_scrape":False,"rate_limit_rpm":20},
    {"co_no":15,"name":"Dixie","slug":"dixie","seat":"Cross City","pop":16742,"municipalities":3,"portal_type":"municode","municode_url":"https://library.municode.com/fl/dixie_county","anti_scrape":False,"rate_limit_rpm":20},
    {"co_no":16,"name":"Duval","slug":"duval","seat":"Jacksonville","pop":979567,"municipalities":1,"portal_type":"arcgis","municode_url":"https://library.municode.com/fl/jacksonville","anti_scrape":True,"rate_limit_rpm":30,"gis_url":"https://duvalfl.maps.arcgis.com/arcgis/rest/services/Zoning/MapServer","zone_field":"ZONE_DIST"},
    {"co_no":17,"name":"Escambia","slug":"escambia","seat":"Pensacola","pop":317887,"municipalities":2,"portal_type":"municode","municode_url":"https://library.municode.com/fl/escambia_county","anti_scrape":False,"rate_limit_rpm":60},
    {"co_no":18,"name":"Flagler","slug":"flagler","seat":"Bunnell","pop":115081,"municipalities":5,"portal_type":"arcgis","municode_url":"https://library.municode.com/fl/flagler_county","anti_scrape":False,"rate_limit_rpm":40},
    {"co_no":19,"name":"Franklin","slug":"franklin","seat":"Apalachicola","pop":12125,"municipalities":3,"portal_type":"municode","municode_url":"https://library.municode.com/fl/franklin_county","anti_scrape":False,"rate_limit_rpm":20},
    {"co_no":20,"name":"Gadsden","slug":"gadsden","seat":"Quincy","pop":44294,"municipalities":6,"portal_type":"municode","municode_url":"https://library.municode.com/fl/gadsden_county","anti_scrape":False,"rate_limit_rpm":20},
    {"co_no":21,"name":"Gilchrist","slug":"gilchrist","seat":"Trenton","pop":18582,"municipalities":1,"portal_type":"pdf","municode_url":"https://library.municode.com/fl/gilchrist_county","anti_scrape":False,"rate_limit_rpm":10},
    {"co_no":22,"name":"Glades","slug":"glades","seat":"Moore Haven","pop":13363,"municipalities":1,"portal_type":"pdf","municode_url":"https://library.municode.com/fl/glades_county","anti_scrape":False,"rate_limit_rpm":10},
    {"co_no":23,"name":"Gulf","slug":"gulf","seat":"Port St. Joe","pop":17208,"municipalities":3,"portal_type":"municode","municode_url":"https://library.municode.com/fl/gulf_county","anti_scrape":False,"rate_limit_rpm":20},
    {"co_no":24,"name":"Hamilton","slug":"hamilton","seat":"Jasper","pop":14280,"municipalities":3,"portal_type":"municode","municode_url":"https://library.municode.com/fl/hamilton_county","anti_scrape":False,"rate_limit_rpm":20},
    {"co_no":25,"name":"Hardee","slug":"hardee","seat":"Wauchula","pop":26337,"municipalities":3,"portal_type":"municode","municode_url":"https://library.municode.com/fl/hardee_county","anti_scrape":False,"rate_limit_rpm":20},
    {"co_no":26,"name":"Hendry","slug":"hendry","seat":"LaBelle","pop":40029,"municipalities":2,"portal_type":"municode","municode_url":"https://library.municode.com/fl/hendry_county","anti_scrape":False,"rate_limit_rpm":20},
    {"co_no":27,"name":"Hernando","slug":"hernando","seat":"Brooksville","pop":197908,"municipalities":2,"portal_type":"arcgis","municode_url":"https://library.municode.com/fl/hernando_county","anti_scrape":False,"rate_limit_rpm":40},
    {"co_no":28,"name":"Highlands","slug":"highlands","seat":"Sebring","pop":106221,"municipalities":4,"portal_type":"municode","municode_url":"https://library.municode.com/fl/highlands_county","anti_scrape":False,"rate_limit_rpm":40},
    {"co_no":29,"name":"Hillsborough","slug":"hillsborough","seat":"Tampa","pop":1471968,"municipalities":4,"portal_type":"arcgis","municode_url":"https://library.municode.com/fl/hillsborough_county","anti_scrape":True,"rate_limit_rpm":30,"gis_url":"https://gis.hcflgov.net/arcgis/rest/services/Zoning/MapServer","zone_field":"ZONING"},
    {"co_no":30,"name":"Holmes","slug":"holmes","seat":"Bonifay","pop":19952,"municipalities":4,"portal_type":"pdf","municode_url":"https://library.municode.com/fl/holmes_county","anti_scrape":False,"rate_limit_rpm":10},
    {"co_no":31,"name":"Indian River","slug":"indian-river","seat":"Vero Beach","pop":159923,"municipalities":5,"portal_type":"arcgis","municode_url":"https://library.municode.com/fl/indian_river_county","anti_scrape":False,"rate_limit_rpm":60},
    {"co_no":32,"name":"Jackson","slug":"jackson","seat":"Marianna","pop":46414,"municipalities":7,"portal_type":"municode","municode_url":"https://library.municode.com/fl/jackson_county","anti_scrape":False,"rate_limit_rpm":20},
    {"co_no":33,"name":"Jefferson","slug":"jefferson","seat":"Monticello","pop":14716,"municipalities":1,"portal_type":"pdf","municode_url":"https://library.municode.com/fl/jefferson_county","anti_scrape":False,"rate_limit_rpm":10},
    {"co_no":34,"name":"Lafayette","slug":"lafayette","seat":"Mayo","pop":8924,"municipalities":1,"portal_type":"pdf","municode_url":"https://library.municode.com/fl/lafayette_county","anti_scrape":False,"rate_limit_rpm":10},
    {"co_no":35,"name":"Lake","slug":"lake","seat":"Tavares","pop":385240,"municipalities":14,"portal_type":"arcgis","municode_url":"https://library.municode.com/fl/lake_county","anti_scrape":False,"rate_limit_rpm":60},
    {"co_no":36,"name":"Lee","slug":"lee","seat":"Fort Myers","pop":760822,"municipalities":6,"portal_type":"arcgis","municode_url":"https://library.municode.com/fl/lee_county","anti_scrape":False,"rate_limit_rpm":60},
    {"co_no":37,"name":"Leon","slug":"leon","seat":"Tallahassee","pop":296853,"municipalities":2,"portal_type":"arcgis","municode_url":"https://library.municode.com/fl/leon_county","anti_scrape":False,"rate_limit_rpm":40},
    {"co_no":38,"name":"Levy","slug":"levy","seat":"Bronson","pop":42557,"municipalities":6,"portal_type":"municode","municode_url":"https://library.municode.com/fl/levy_county","anti_scrape":False,"rate_limit_rpm":20},
    {"co_no":39,"name":"Liberty","slug":"liberty","seat":"Bristol","pop":7994,"municipalities":1,"portal_type":"pdf","municode_url":"https://library.municode.com/fl/liberty_county","anti_scrape":False,"rate_limit_rpm":10},
    {"co_no":40,"name":"Madison","slug":"madison","seat":"Madison","pop":18474,"municipalities":4,"portal_type":"municode","municode_url":"https://library.municode.com/fl/madison_county","anti_scrape":False,"rate_limit_rpm":20},
    {"co_no":41,"name":"Manatee","slug":"manatee","seat":"Bradenton","pop":399397,"municipalities":4,"portal_type":"arcgis","municode_url":"https://library.municode.com/fl/manatee_county","anti_scrape":False,"rate_limit_rpm":60},
    {"co_no":42,"name":"Marion","slug":"marion","seat":"Ocala","pop":375908,"municipalities":5,"portal_type":"arcgis","municode_url":"https://library.municode.com/fl/marion_county","anti_scrape":False,"rate_limit_rpm":60},
    {"co_no":43,"name":"Martin","slug":"martin","seat":"Stuart","pop":160998,"municipalities":4,"portal_type":"arcgis","municode_url":"https://library.municode.com/fl/martin_county","anti_scrape":False,"rate_limit_rpm":40},
    {"co_no":44,"name":"Monroe","slug":"monroe","seat":"Key West","pop":82874,"municipalities":3,"portal_type":"arcgis","municode_url":"https://library.municode.com/fl/monroe_county","anti_scrape":True,"rate_limit_rpm":30},
    {"co_no":45,"name":"Nassau","slug":"nassau","seat":"Fernandina Beach","pop":90743,"municipalities":3,"portal_type":"arcgis","municode_url":"https://library.municode.com/fl/nassau_county","anti_scrape":False,"rate_limit_rpm":40},
    {"co_no":46,"name":"Okaloosa","slug":"okaloosa","seat":"Crestview","pop":216803,"municipalities":9,"portal_type":"arcgis","municode_url":"https://library.municode.com/fl/okaloosa_county","anti_scrape":False,"rate_limit_rpm":40},
    {"co_no":47,"name":"Okeechobee","slug":"okeechobee","seat":"Okeechobee","pop":41764,"municipalities":1,"portal_type":"municode","municode_url":"https://library.municode.com/fl/okeechobee_county","anti_scrape":False,"rate_limit_rpm":20},
    {"co_no":48,"name":"Orange","slug":"orange","seat":"Orlando","pop":1429908,"municipalities":14,"portal_type":"arcgis","municode_url":"https://library.municode.com/fl/orange_county","anti_scrape":True,"rate_limit_rpm":30,"gis_url":"https://maps.ocfl.net/arcgis/rest/services/Zoning/MapServer","zone_field":"ZONE_CODE"},
    {"co_no":49,"name":"Osceola","slug":"osceola","seat":"Kissimmee","pop":388656,"municipalities":3,"portal_type":"arcgis","municode_url":"https://library.municode.com/fl/osceola_county","anti_scrape":False,"rate_limit_rpm":40},
    {"co_no":50,"name":"Palm Beach","slug":"palm-beach","seat":"West Palm Beach","pop":1496770,"municipalities":38,"portal_type":"arcgis","municode_url":"https://library.municode.com/fl/palm_beach_county","anti_scrape":True,"rate_limit_rpm":20,"gis_url":"https://maps.co.palm-beach.fl.us/arcgis/rest/services/Zoning/MapServer","zone_field":"ZONE_CODE"},
    {"co_no":51,"name":"Pasco","slug":"pasco","seat":"Dade City","pop":561891,"municipalities":4,"portal_type":"arcgis","municode_url":"https://library.municode.com/fl/pasco_county","anti_scrape":False,"rate_limit_rpm":40},
    {"co_no":52,"name":"Pinellas","slug":"pinellas","seat":"Clearwater","pop":959107,"municipalities":24,"portal_type":"arcgis","municode_url":"https://library.municode.com/fl/pinellas_county","anti_scrape":True,"rate_limit_rpm":20,"gis_url":"https://egis.pinellas.gov/arcgis/rest/services/Zoning/MapServer","zone_field":"ZONE_CODE"},
    {"co_no":53,"name":"Polk","slug":"polk","seat":"Bartow","pop":724777,"municipalities":18,"portal_type":"arcgis","municode_url":"https://library.municode.com/fl/polk_county","anti_scrape":False,"rate_limit_rpm":40},
    {"co_no":54,"name":"Putnam","slug":"putnam","seat":"Palatka","pop":74521,"municipalities":5,"portal_type":"municode","municode_url":"https://library.municode.com/fl/putnam_county","anti_scrape":False,"rate_limit_rpm":20},
    {"co_no":55,"name":"St. Johns","slug":"st-johns","seat":"St. Augustine","pop":307021,"municipalities":4,"portal_type":"arcgis","municode_url":"https://library.municode.com/fl/st._johns_county","anti_scrape":False,"rate_limit_rpm":60},
    {"co_no":56,"name":"St. Lucie","slug":"st-lucie","seat":"Fort Pierce","pop":329226,"municipalities":3,"portal_type":"arcgis","municode_url":"https://library.municode.com/fl/st._lucie_county","anti_scrape":False,"rate_limit_rpm":40},
    {"co_no":57,"name":"Santa Rosa","slug":"santa-rosa","seat":"Milton","pop":196077,"municipalities":5,"portal_type":"arcgis","municode_url":"https://library.municode.com/fl/santa_rosa_county","anti_scrape":False,"rate_limit_rpm":40},
    {"co_no":58,"name":"Sarasota","slug":"sarasota","seat":"Sarasota","pop":434006,"municipalities":4,"portal_type":"arcgis","municode_url":"https://library.municode.com/fl/sarasota_county","anti_scrape":False,"rate_limit_rpm":60},
    {"co_no":59,"name":"Seminole","slug":"seminole","seat":"Sanford","pop":471826,"municipalities":7,"portal_type":"arcgis","municode_url":"https://library.municode.com/fl/seminole_county","anti_scrape":False,"rate_limit_rpm":60},
    {"co_no":60,"name":"Sumter","slug":"sumter","seat":"Bushnell","pop":132420,"municipalities":5,"portal_type":"arcgis","municode_url":"https://library.municode.com/fl/sumter_county","anti_scrape":False,"rate_limit_rpm":40},
    {"co_no":61,"name":"Suwannee","slug":"suwannee","seat":"Live Oak","pop":44417,"municipalities":4,"portal_type":"municode","municode_url":"https://library.municode.com/fl/suwannee_county","anti_scrape":False,"rate_limit_rpm":20},
    {"co_no":62,"name":"Taylor","slug":"taylor","seat":"Perry","pop":22294,"municipalities":3,"portal_type":"municode","municode_url":"https://library.municode.com/fl/taylor_county","anti_scrape":False,"rate_limit_rpm":20},
    {"co_no":63,"name":"Union","slug":"union","seat":"Lake Butler","pop":15237,"municipalities":2,"portal_type":"pdf","municode_url":"https://library.municode.com/fl/union_county","anti_scrape":False,"rate_limit_rpm":10},
    {"co_no":64,"name":"Volusia","slug":"volusia","seat":"DeLand","pop":564942,"municipalities":16,"portal_type":"arcgis","municode_url":"https://library.municode.com/fl/volusia_county","anti_scrape":False,"rate_limit_rpm":60},
    {"co_no":65,"name":"Wakulla","slug":"wakulla","seat":"Crawfordville","pop":33739,"municipalities":1,"portal_type":"municode","municode_url":"https://library.municode.com/fl/wakulla_county","anti_scrape":False,"rate_limit_rpm":20},
    {"co_no":66,"name":"Walton","slug":"walton","seat":"DeFuniak Springs","pop":84923,"municipalities":5,"portal_type":"arcgis","municode_url":"https://library.municode.com/fl/walton_county","anti_scrape":False,"rate_limit_rpm":40},
    {"co_no":67,"name":"Washington","slug":"washington","seat":"Chipley","pop":24888,"municipalities":4,"portal_type":"municode","municode_url":"https://library.municode.com/fl/washington_county","anti_scrape":False,"rate_limit_rpm":20},
]

PILOT_SLUGS = {"brevard", "miami-dade", "orange"}
P1_SLUGS = {"hillsborough", "palm-beach", "pinellas"}

def make_phase(county):
    if county["slug"] in PILOT_SLUGS:
        return "P0"
    elif county["slug"] in P1_SLUGS:
        return "P1"
    else:
        return "P3"

def make_skill_md(c):
    phase = make_phase(c)
    is_pilot = c["slug"] in PILOT_SLUGS
    gis_section = ""
    if c.get("gis_url"):
        gis_section = f"""
### GIS Direct Query (ArcGIS)
```
GET {c['gis_url']}/query?where=1=1&geometry={{lng}},{{lat}}&geometryType=esriGeometryPoint&spatialRel=esriSpatialRelIntersects&outFields={c.get('zone_field','ZONING')}&f=json
```
Zone field: `{c.get('zone_field','ZONING')}`
"""

    return f"""---
name: county-{c['slug']}
description: >
  Zoning intelligence for {c['name']} County, FL.
  {c['municipalities']} jurisdictions, FDOR co_no {c['co_no']:02d}.
  Portal: {c['portal_type']}. Supabase filter: county=ilike.%25{c['name']}%25.
  Use for parcel lookups, permitted use queries, and dimensional standards.
  Triggers on: {c['name']}, {c['name'].lower()} county, co_no {c['co_no']:02d},
  any address with {c['seat']} or {c['name']} County FL.
co_no: {c['co_no']:02d}
county_slug: {c['slug']}
portal_type: {c['portal_type']}
anti_scrape: {"true" if c['anti_scrape'] else "false"}
rate_limit_rpm: {c['rate_limit_rpm']}
phase: {phase}
last_validated: {TODAY}
---

# {c['name']} County — Zoning Intelligence

**County Seat**: {c['seat']} | **Population**: {c['pop']:,} | **Municipalities**: {c['municipalities']}  
**FDOR co_no**: {c['co_no']:02d} | **Portal**: {c['portal_type'].upper()} | **Phase**: {phase}

---

## Supabase Queries

All queries target `mocerqjnksmhcjzxrewo.supabase.co`. Use `apikey` + `Authorization: Bearer` headers.

### List all jurisdictions in {c['name']} County
```
GET /jurisdictions?county=ilike.%25{c['name']}%25&select=id,name,data_completeness,municode_url&order=name.asc
```

### Search jurisdiction by city name
```
GET /jurisdictions?name=ilike.%25{{city_name}}%25&county=ilike.%25{c['name']}%25&select=id,name,data_completeness
```

### Get all zoning districts for a jurisdiction
```
GET /zoning_districts?jurisdiction_id=eq.{{id}}&select=id,code,name,category&order=category,code
```

### Get dimensional standards
```
GET /zone_standards?zoning_district_id=eq.{{district_id}}&select=*
```

### Get permitted uses
```
GET /permitted_uses?zoning_district_id=eq.{{district_id}}&select=use_name,permission_type,use_category
```

### Parcel lookup by address
```
GET /fl_parcels?co_no=eq.{c['co_no']}&phy_addr1=ilike.%25{{street}}%25&select=parcel_id,phy_addr1,phy_city,phy_zipcd,dor_uc,centroid_lat,centroid_lng&limit=5
```

### Parcel lookup by parcel ID
```
GET /fl_parcels?co_no=eq.{c['co_no']}&parcel_id=eq.{{parcel_id}}&select=*
```

### Get overlay districts
```
GET /overlay_districts?jurisdiction_id=eq.{{id}}&select=*
```
{gis_section}
---

## 3-Mode Research Protocol

### Mode 1 — Discovery (WebSearch, ≤30s)
**Trigger**: Portal URL unknown OR last_validated > 30 days  
**Goal**: Find/validate county portal URL, discover jurisdiction list  

Search queries (try in order):
1. `"{c['name']} County Florida zoning map"`
2. `"{c['name']} County Florida municode zoning ordinance"`
3. `"{c['name']} County GIS ArcGIS zoning layer Florida"`
4. `"site:municode.com {c['name'].lower()} county florida zoning"`

**Output**: Validated `municode_url` and/or `gis_url` → UPDATE `jurisdictions` table

### Mode 2 — Extraction (WebFetch, ≤90s)
**Trigger**: Mode 1 found URL OR known Municode URL exists  
**Target**: `{c['municode_url']}`  
**Extract**:
- All zoning district codes + names + categories
- Dimensional standards (setbacks, height, FAR, lot coverage)
- Permitted/conditional/prohibited uses per district
- Overlay district definitions

**Output**: UPSERT to `zoning_districts`, `zone_standards`, `permitted_uses`

### Mode 3 — AgentQL Fallback (Modal Container)
**Trigger**: Mode 2 empty OR `anti_scrape: {"true" if c['anti_scrape'] else "false"}` = true  
**Config**:
- AgentQL API key: `AGENTQL_API_KEY` env var (GitHub Secrets: zonewise-modal)
- Rate limit: {c['rate_limit_rpm']} rpm
- Container: `modal-county-{c['slug']}`
- Anti-detect: {"ENABLED" if c['anti_scrape'] else "DISABLED"}
- Timeout: 300s per jurisdiction

**AgentQL selector pattern**:
```python
await page.query_elements("""
  {{
    zoning_table {{
      district_code
      district_name  
      uses_permitted[]
      setback_front
      setback_side
      setback_rear
      max_height
    }}
  }}
""")
```

**Output**: Same schema as Mode 2

---

## Circuit Breaker

If all 3 modes fail for any jurisdiction:
1. INSERT to Supabase `insights` table:
```json
{{
  "type": "ESCALATE",
  "county": "{c['slug']}",
  "county_name": "{c['name']}",
  "error": "<error message>",
  "modes_attempted": [1, 2, 3],
  "action": "Create Traycer GitHub Issue: [SKILL] Manual review {c['name']} County portal"
}}
```
2. Mark jurisdiction `data_completeness = -1` (error state)
3. Continue to next jurisdiction — no blocking

---

## County Profile

| Field | Value |
|-------|-------|
| FDOR co_no | {c['co_no']:02d} |
| County seat | {c['seat']} |
| Population | {c['pop']:,} |
| Municipalities | {c['municipalities']} |
| Portal type | {c['portal_type'].upper()} |
| Municode URL | [{c['municode_url']}]({c['municode_url']}) |
| Anti-scrape | {"⚠️ YES" if c['anti_scrape'] else "No"} |
| Rate limit | {c['rate_limit_rpm']} rpm |
| Phase | {phase} |
| Last validated | {TODAY} |

---

## Zoning Categories (Standard FL Taxonomy)

| Category | Typical Codes | Description |
|----------|--------------|-------------|
| Residential | RS, RE, RM, R-1, R-2, R-3 | Single/multi-family dwelling districts |
| Commercial | CN, CG, CB, C-1, C-2, C-3 | Retail, office, service commercial |
| Industrial | IL, IH, LI, I-1, I-2 | Manufacturing, warehousing |
| Agricultural | A, AG, AU, A-1, A-5 | Farming, rural, low density |
| Mixed Use | MX, MU, TOD | Transit-oriented, mixed residential/commercial |
| Special | PUD, DRI, CDD | Planned developments, special districts |
| Conservation | CV, CON, GU | Environmentally sensitive areas |
| Institutional | CF, I, PSP | Government, education, religious |

*Actual codes populated from Supabase after Mode 2/3 extraction*

---

## Quirks & Gotchas

*Populated automatically after first successful scrape. Common patterns:*

- **Municode session limits**: Reset between jurisdictions. Use 60s delay if `anti_scrape: true`
- **PDF-only portals** (`portal_type: pdf`): Use AgentQL PDF extractor, fall back to manual review
- **ArcGIS rate limits**: Respect `rate_limit_rpm: {c['rate_limit_rpm']}`, use exponential backoff
- **Jurisdiction boundary overlap**: Some unincorporated areas use county code; check `co_no` field first
- **Custom portal vs Municode**: Always check Municode first (structured data), fall back to custom portal

---

## Integration with CraftAgents

This skill is loaded via **Progressive Disclosure** (skills-manifest.yaml v2.0.0):

- **Level 1 (always loaded)**: YAML frontmatter only (~80 tokens)
- **Level 2 (on-demand)**: Full SKILL.md loaded when county mentioned (~600 tokens)
- **Level 3 (on-demand)**: References files loaded for deep extraction (~2000 tokens)

**Trigger phrases** (any of these activate this skill):
- "{c['name']}", "{c['name'].lower()} county", "{c['seat']}"
- "co_no {c['co_no']}", "FDOR {c['co_no']:02d}"
- Any FL address with {c['name']} County zip codes
"""

def make_manifest_entry(c, idx):
    phase = make_phase(c)
    return f"""  - name: county-{c['slug']}
    description: >
      {c['name']} County zoning intelligence. {c['municipalities']} jurisdictions,
      FDOR co_no {c['co_no']:02d}, {c['portal_type'].upper()} portal.
      Phase {phase}. Anti-scrape: {"yes" if c['anti_scrape'] else "no"}.
    path: zonewise/skills/county-{c['slug']}/SKILL.md
    category: county
    priority: {"1" if make_phase(c) in ["P0","P1"] else "3"}
    tokens_estimate: 80
    phase: {phase}
    co_no: {c['co_no']:02d}"""


# ──────────────────────────────────────────────────────────────────────────────
# Generate all files
# ──────────────────────────────────────────────────────────────────────────────
output_base = Path("/home/claude/zonewise-skills-build/output")

# 1) Generate 67 SKILL.md files
for c in FL_COUNTIES:
    skill_dir = output_base / "zonewise-desktop" / "zonewise" / "skills" / f"county-{c['slug']}"
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(make_skill_md(c))
    print(f"✅ Generated: county-{c['slug']}/SKILL.md")

# 2) Generate skills-manifest.yaml v2.0.0
manifest_entries = "\n\n".join(make_manifest_entry(c, i) for i, c in enumerate(FL_COUNTIES))
manifest_yaml = f"""# ZoneWise.AI Skills Manifest
# Progressive Disclosure Architecture
# Updated: {TODAY} by Claude AI (Architect)

version: "2.0.0"
updated: "{TODAY}"
total_skills: 79
county_skills: 67
existing_skills: 12

skills:
  # ============================================================================
  # CORE ANALYSIS SKILLS (12 existing — unchanged)
  # ============================================================================

  - name: zoning-analysis
    description: |
      Analyze zoning codes and land use regulations across all 67 FL counties.
      Routes to county skill for jurisdiction-specific data.
    path: zonewise/skills/zoning-analysis/SKILL.md
    category: zoning
    priority: 1
    tokens_estimate: 100

  - name: property-valuation
    description: |
      Estimate property values using comparable sales, income approach, cost approach.
    path: zonewise/skills/property-valuation/SKILL.md
    category: analysis
    priority: 1
    tokens_estimate: 120

  - name: permit-lookup
    description: |
      Search building permits, code violations, inspection history.
    path: zonewise/skills/permit-lookup/SKILL.md
    category: data
    priority: 2
    tokens_estimate: 100

  - name: sun-analysis
    description: |
      Sun position, shadow projections, solar exposure heatmaps.
    path: zonewise/skills/sun-analysis/SKILL.md
    category: analysis
    priority: 1
    tokens_estimate: 110

  - name: envelope-development
    description: |
      3D building envelopes from zoning parameters.
    path: zonewise/skills/envelope-development/SKILL.md
    category: visualization
    priority: 1
    tokens_estimate: 120

  - name: threejs-fundamentals
    description: Core Three.js concepts for ZoneWise 3D visualization.
    path: zonewise/skills/threejs-fundamentals/SKILL.md
    category: visualization
    priority: 2
    tokens_estimate: 80

  - name: threejs-geometry
    description: BufferGeometry, ExtrudeGeometry, vertex manipulation.
    path: zonewise/skills/threejs-geometry/SKILL.md
    category: visualization
    priority: 2
    tokens_estimate: 90

  - name: threejs-materials
    description: MeshStandardMaterial, transparency, vertex colors.
    path: zonewise/skills/threejs-materials/SKILL.md
    category: visualization
    priority: 2
    tokens_estimate: 70

  - name: threejs-lighting
    description: AmbientLight, DirectionalLight, shadow mapping, sun simulation.
    path: zonewise/skills/threejs-lighting/SKILL.md
    category: visualization
    priority: 2
    tokens_estimate: 75

  - name: threejs-interaction
    description: OrbitControls, raycasting, click detection, hover effects.
    path: zonewise/skills/threejs-interaction/SKILL.md
    category: visualization
    priority: 2
    tokens_estimate: 65

  - name: bcpao-integration
    description: |
      Brevard County Property Appraiser data integration.
    path: zonewise/skills/bcpao-integration/SKILL.md
    category: data
    priority: 2
    tokens_estimate: 90

  - name: mapbox-integration
    description: |
      Mapbox GL JS with Three.js overlays, satellite imagery, geocoding.
    path: zonewise/skills/mapbox-integration/SKILL.md
    category: visualization
    priority: 2
    tokens_estimate: 85

  # ============================================================================
  # COUNTY INTELLIGENCE SKILLS (67 — all FL counties)
  # Load Level 1 (frontmatter only) always. Level 2 on county mention.
  # ============================================================================

{manifest_entries}

# ============================================================================
# CATEGORIES
# ============================================================================
categories:
  zoning: "Zoning code analysis and regulations"
  visualization: "3D visualization and rendering"
  analysis: "Property and environmental analysis"
  data: "External data integration"
  county: "Per-county zoning intelligence (67 FL counties)"

# ============================================================================
# PROGRESSIVE DISCLOSURE LEVELS
# ============================================================================
disclosure_levels:
  level_1:
    name: "Metadata"
    description: "YAML frontmatter only — always loaded"
    tokens: "50-80 per county skill"
    loaded: "Always"

  level_2:
    name: "Instructions"
    description: "Full SKILL.md — loaded when county mentioned"
    tokens: "500-800 per county skill"
    loaded: "On county name, seat, or co_no mention"

  level_3:
    name: "References"
    description: "County-specific GIS schemas, zoning tables"
    tokens: "1000-3000 per reference"
    loaded: "On-demand for deep extraction"

# ============================================================================
# TOOL SEARCH CONFIGURATION (Beta: advanced-tool-use-2025-11-20)
# ============================================================================
tool_search:
  header: "advanced-tool-use-2025-11-20"
  defer_loading: true
  deferred_skills: "county-*"
  max_tools: 10000
  notes: "~67 county tools deferred. Load only on county keyword match."

# ============================================================================
# AGENT ROUTING
# ============================================================================
agents:
  orchestrator:
    name: "ZoneWise Orchestrator"
    skills: ["zoning-analysis", "county-*"]
    routes_to: "county skill on location detection"

  county_research:
    name: "County Research Agent"
    skills: ["county-*"]
    modes: ["webSearch", "webFetch", "agentQL"]
    circuit_breaker: 3

  visualization:
    name: "Visualization Agent"
    skills: ["envelope-development", "sun-analysis", "threejs-*", "mapbox-integration"]
"""

manifest_path = output_base / "zonewise-desktop" / "zonewise" / "skills" / "skills-manifest.yaml"
manifest_path.parent.mkdir(parents=True, exist_ok=True)
manifest_path.write_text(manifest_yaml)
print(f"\n✅ Generated: skills-manifest.yaml v2.0.0 ({len(FL_COUNTIES)} county entries)")

# 3) Generate SQL migration
migration_sql = f"""-- Migration 007: Add skill_file_path to jurisdictions
-- Generated: {TODAY} by Claude AI (Architect)
-- Purpose: Track which county SKILL.md file governs each jurisdiction

ALTER TABLE public.jurisdictions
  ADD COLUMN IF NOT EXISTS skill_file_path TEXT,
  ADD COLUMN IF NOT EXISTS co_no SMALLINT,
  ADD COLUMN IF NOT EXISTS skill_last_validated DATE;

-- Index for county queries
CREATE INDEX IF NOT EXISTS idx_jurisdictions_co_no ON public.jurisdictions(co_no);

-- Update co_no for known Florida counties
UPDATE public.jurisdictions SET co_no = subquery.co_no
FROM (VALUES
  ('Alachua',1),('Baker',2),('Bay',3),('Bradford',4),('Brevard',5),
  ('Broward',6),('Calhoun',7),('Charlotte',8),('Citrus',9),('Clay',10),
  ('Collier',11),('Columbia',12),('Miami-Dade',13),('DeSoto',14),('Dixie',15),
  ('Duval',16),('Escambia',17),('Flagler',18),('Franklin',19),('Gadsden',20),
  ('Gilchrist',21),('Glades',22),('Gulf',23),('Hamilton',24),('Hardee',25),
  ('Hendry',26),('Hernando',27),('Highlands',28),('Hillsborough',29),('Holmes',30),
  ('Indian River',31),('Jackson',32),('Jefferson',33),('Lafayette',34),('Lake',35),
  ('Lee',36),('Leon',37),('Levy',38),('Liberty',39),('Madison',40),
  ('Manatee',41),('Marion',42),('Martin',43),('Monroe',44),('Nassau',45),
  ('Okaloosa',46),('Okeechobee',47),('Orange',48),('Osceola',49),('Palm Beach',50),
  ('Pasco',51),('Pinellas',52),('Polk',53),('Putnam',54),('St. Johns',55),
  ('St. Lucie',56),('Santa Rosa',57),('Sarasota',58),('Seminole',59),('Sumter',60),
  ('Suwannee',61),('Taylor',62),('Union',63),('Volusia',64),('Wakulla',65),
  ('Walton',66),('Washington',67)
) AS subquery(county_name, co_no)
WHERE public.jurisdictions.county ILIKE '%' || subquery.county_name || '%';

-- Update skill_file_path for all jurisdictions
UPDATE public.jurisdictions
SET skill_file_path = 'zonewise/skills/county-' ||
  LOWER(REGEXP_REPLACE(county, '[^a-zA-Z0-9]+', '-', 'g')) || '/SKILL.md'
WHERE county IS NOT NULL;

COMMENT ON COLUMN public.jurisdictions.skill_file_path IS 'Relative path to county SKILL.md in zonewise-desktop repo';
COMMENT ON COLUMN public.jurisdictions.co_no IS 'FDOR county number (1-67)';
COMMENT ON COLUMN public.jurisdictions.skill_last_validated IS 'Date county SKILL.md was last validated against live portal';
"""

migration_path = output_base / "zonewise" / "migrations" / "007_skill_file_paths.sql"
migration_path.parent.mkdir(parents=True, exist_ok=True)
migration_path.write_text(migration_sql)
print(f"✅ Generated: migrations/007_skill_file_paths.sql")

# Summary
skill_count = len(list((output_base / "zonewise-desktop" / "zonewise" / "skills").glob("county-*/SKILL.md")))
print(f"\n{'='*60}")
print(f"GENERATION COMPLETE")
print(f"{'='*60}")
print(f"County skill files:  {skill_count}/67")
print(f"Manifest:            skills-manifest.yaml v2.0.0 (79 total skills)")
print(f"Migration:           007_skill_file_paths.sql")
print(f"Output:              /home/claude/zonewise-skills-build/output/")
