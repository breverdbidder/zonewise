# Task: Sprint 5 — Enrichment Completion & Gap-Fill

## Source
- Context: BidDeed.AI multi-county auction pipeline
- Branch: `main` on `breverdbidder/zonewise`

## Objective
Fill all remaining enrichment gaps in `multi_county_auctions` table. Every row with a property address must have: parcel_id, year_built, lot_sqft, centroid_lat/lng, owner_name. Rows without addresses need BCPAO owner-name lookup (Brevard) or clerk page scraping (other counties).

## Infrastructure (VERIFIED — use directly, do NOT rediscover)

```
Supabase Project: mocerqjnksmhcjzxrewo
SQL Endpoint:     POST https://api.supabase.com/v1/projects/mocerqjnksmhcjzxrewo/database/query
Auth Header:      Authorization: Bearer $SUPABASE_MGMT_TOKEN  (from GitHub Secrets)
Body:             {"query": "SELECT ..."}
Note:             Supports SELECT, INSERT, UPDATE, DELETE. Returns JSON array.
```

```
BCPAO GIS API:    https://gis.brevardfl.gov/gissrv/rest/services/Base_Map/Parcel_New_WKID2881/MapServer/5/query
Key fields:       PARCEL_ID, OWNER_NAME1, OWNER_NAME2, STREET_NUMBER, STREET_NAME, STREET_TYPE, CITY, LIV_AREA, BLDG_VALUE, LAND_VALUE, ACRES
Owner search:     where=OWNER_NAME1 LIKE 'LASTNAME, FIRSTNAME%'
Geometry:         returnGeometry=true&outSR=4326 → rings → calculate centroid
Note:             bcpao.us/api/v1/search is Cloudflare-blocked. Use GIS only.
```

```
Mapbox Geocoding: https://api.mapbox.com/geocoding/v5/mapbox.places/{address}.json?access_token={TOKEN}&limit=1&country=US
Token:            $MAPBOX_TOKEN (from GitHub Secrets — account: everest18)
```

```
DOR fl_parcels table (Supabase):
  Columns: co_no, parcel_id, phy_addr1, phy_city, own_name, act_yr_blt, tot_lvg_ar, jv, lnd_val, lnd_sqfoot, centroid_lat, centroid_lng
  County codes: Brevard=15, Broward=16, Miami-Dade=23, Duval=26, Hillsborough=39, Lee=46, Orange=58, Palm Beach=60, Pinellas=62, Polk=63
  Coordinates: Only Brevard (co_no=15) has centroid_lat/lng populated. All others need Mapbox geocoding.
  Year built: Available for ALL counties.
  Address JOIN: UPPER(TRIM(fp.phy_addr1)) = UPPER(TRIM(split_part(mca.property_address, ',', 1)))
```

```
Brevard Clerk Foreclosure Page: http://vweb2.brevardclerk.us/Foreclosures/foreclosure_sales.html
  Format: HTML table with columns: case_number, case_title, comment, foreclosure_sale_date
  case_title: "PLAINTIFF VS DEFENDANT" — parse both sides
  Defendant → BCPAO OWNER_NAME1 lookup → parcel_id, address, building details
```

```
multi_county_auctions unique constraint: (county, case_number, auction_type)
  Upsert: ON CONFLICT (county, case_number, auction_type) DO UPDATE SET ...
```

## Current State (295 rows)

| County | Type | Tot | NoAddr | NoPar | NoYB | NoCoord | NoLot |
|--------|------|-----|--------|-------|------|---------|-------|
| Brevard | active | 90 | 8 | 8 | 10 | 8 | 8 |
| Brevard | cancelled | 6 | 0 | 0 | 0 | 0 | 0 |
| Brevard | foreclosure | 66 | 66 | 66 | 66 | 66 | 66 |
| Brevard | tax_deed | 20 | 11 | 0 | 14 | 11 | 11 |
| Broward | foreclosure | 14 | 1 | 0 | 1 | 1 | 4 |
| Duval | foreclosure | 7 | 0 | 0 | 0 | 0 | 0 |
| Hillsborough | foreclosure | 10 | 0 | 0 | 0 | 0 | 0 |
| Lee | foreclosure | 20 | 1 | 0 | 3 | 1 | 2 |
| Miami-Dade | foreclosure | 21 | 0 | 0 | 1 | 0 | 1 |
| Orange | foreclosure | 8 | 8 | 8 | 8 | 8 | 8 |
| Palm Beach | foreclosure | 15 | 1 | 0 | 1 | 1 | 4 |
| Pinellas | foreclosure | 8 | 0 | 0 | 1 | 0 | 4 |
| Polk | foreclosure | 10 | 0 | 0 | 0 | 0 | 0 |

## Tasks

### Task 1: Brevard 66 foreclosure rows — BCPAO owner-name lookup

These 66 rows have case_numbers but ZERO data (no address, no parcel, no plaintiff, no owner). They came from the old scraper.

**Steps:**
1. Query the 66 case_numbers: `SELECT case_number FROM multi_county_auctions WHERE county = 'Brevard' AND auction_type = 'foreclosure'`
2. For each, search the clerk page HTML for matching case_number to get defendant name
3. Reformat defendant to BCPAO format: "WILLIAM G LITZ" → search `OWNER_NAME1 LIKE 'LITZ, WILLIAM%'`
4. From BCPAO GIS result, extract: PARCEL_ID, address (STREET_NUMBER + STREET_NAME + STREET_TYPE + CITY), LIV_AREA, BLDG_VALUE, LAND_VALUE
5. Then enrich year_built from fl_parcels: `WHERE co_no = 15 AND parcel_id = '{matched_parcel}'`
6. Geocode address or calc centroid from GIS geometry
7. UPDATE multi_county_auctions with all fields

**Name parsing rules:**
- "WILLIAM G LITZ" → search `OWNER_NAME1 LIKE 'LITZ, WILLIAM%'`
- "J MASCETTA" → search `OWNER_NAME1 LIKE 'MASCETTA, J%'`
- Multi-word last: "ROBERTO C MARTINEZ" → try `MARTINEZ, ROBERTO%`
- Entities (LLC, INC, TRUST, ESTATE, BANK, HOA, CONDO, VILLAS): search `OWNER_NAME1 LIKE '%ENTITY_NAME%'`
- "UNKNOWN SPOUSES", "RED KEY" → will not match, skip

**If case_number not on clerk page** (past auctions): these are historical — either delete or leave as-is. Ask Ariel.

### Task 2: Brevard 8 active rows with no address

These 8 are the unmatched defendants from the BCPAO owner-name lookup (entities/edge cases):
- UNKNOWN SPOUSES, ESTATE SPEED, RED KEY, WAGNER DA SILVA, WILLIAM CADY, DWIGHT J BARTON J, GO ECO HOMES, ESTATE R JOE

**Steps:**
1. Try AcclaimWeb case file lookup by case_number to find property legal description
2. Use legal description → BCPAO parcel search
3. Or try alternate name spellings in BCPAO GIS

### Task 3: Brevard 11 tax_deed rows with no address

These have parcel_ids but no addresses. Tax deed parcels are often vacant land.

**Steps:**
1. Query BCPAO GIS by PARCEL_ID to get STREET_NUMBER, STREET_NAME, etc.
2. Build address string, update property_address
3. Fill year_built from fl_parcels co_no=15

### Task 4: Orange County 8 rows — scraper fix

All 8 have zero data. Source scraper not extracting addresses for Orange County.

**Steps:**
1. Check source_url for these rows
2. Scrape the Orange County clerk page for case details
3. Look up owner in fl_parcels co_no=58 by address match

### Task 5: Fill lot_sqft gaps (19 rows across Broward, Lee, Palm Beach, Pinellas, Miami-Dade)

**SQL:**
```sql
UPDATE multi_county_auctions mca
SET lot_sqft = CAST(fp.lnd_sqfoot AS numeric)
FROM fl_parcels fp
WHERE fp.co_no = {CO_NO}
  AND UPPER(TRIM(fp.phy_addr1)) = UPPER(TRIM(split_part(mca.property_address, ',', 1)))
  AND mca.county = '{COUNTY}'
  AND (mca.lot_sqft IS NULL OR mca.lot_sqft = 0)
```

### Task 6: Commit and push

Commit all new scripts to `src/enrichment/` with descriptive messages. Update TODO.md.

## Acceptance Criteria
- [ ] Brevard foreclosure rows: ≥50/66 matched (remaining are historical not on clerk page)
- [ ] Brevard active 8 unmatched: attempted via AcclaimWeb or alternate lookup
- [ ] Brevard tax_deed 11: addresses filled from BCPAO GIS parcel lookup
- [ ] Orange 8: investigated, either fixed or documented as scraper blocker
- [ ] lot_sqft gaps: ≤5 remaining across all counties
- [ ] All scripts committed to `src/enrichment/` on `main`
- [ ] TODO.md updated with Sprint 5 status

## Files to Create/Touch
- `src/enrichment/bcpao_owner_lookup.py` — Brevard defendant → BCPAO parcel matching
- `src/enrichment/enrich_building_details.py` — Update with address-based DOR JOIN
- `src/enrichment/geocode_addresses.py` — Mapbox batch geocoder
- `TODO.md` — Sprint 5 task tracking

## Constraints
- Use Management API SQL for all Supabase operations (REST API keys expired)
- BCPAO search API (bcpao.us) is Cloudflare-blocked — use GIS REST API only
- Mapbox geocoding: 100K free/month, no rate limit concern at this scale
- Do NOT ask for permission — execute autonomously and report results
