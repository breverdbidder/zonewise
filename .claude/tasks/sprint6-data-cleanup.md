# Sprint 6: Data Cleanup — COMPLETED 2026-02-28

## Objective
Clean up auction data quality: remove junk rows, add classification columns, annotate unresolvable records.

## Results
- 8 Orange County legacy rows deleted (backed up to insights table)
- `is_condo` column added: 4 condos flagged (3 Palm Beach, 1 Broward)
- 66 historical foreclosures annotated (case numbers not in GIS legal descriptions)
- 8 active rows annotated as NOT ON CLERK PAGE
- All 74 unresolvable Brevard rows annotated with reason codes
- BCPAO GIS Reference Doc created: `docs/BCPAO_GIS_REFERENCE.md`
- Final row count: 287 (down from 295)

## Key Decisions
- lot_sqft for condo units = 0 in DOR data by design (shared land)
- LEGAL_DESC search for historical rows: 0/66 matched — case numbers don't appear in GIS legal descriptions
- Only Brevard has PA building detail REST API; fl_parcels covers yr/sqft/quality for all counties

## Repo
- brevard-bidder-scraper (breverdbidder/brevard-bidder-scraper)
