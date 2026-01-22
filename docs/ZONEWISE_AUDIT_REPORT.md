# ZoneWise Data Quality Audit Report

**Generated:** 2026-01-22 16:54:10 UTC
**Scope:** Malabar POC + All Brevard County Data

---

## Executive Summary

| Component | Status | Count | Completeness |
|-----------|--------|-------|--------------|
| Jurisdictions | ✅ COMPLETE | 17 | 100% |
| Zoning Districts | ✅ COMPLETE | 273 | 100% with DIMS |
| Parcels | ✅ COMPLETE | 351,423 | 99% with geometry |
| Ordinances | ⚠️ PARTIAL | 2,190 | 1 real (0%) |
| Development Bonuses | ✅ | 81 | 100% |
| Overlay Districts | ✅ | 150 | 100% |
| Conditional Uses | ✅ | 627 | 100% |
| Entitlement Timelines | ✅ | 327 | 100% |

---

## 1. Jurisdictions (17/17)

All 17 Brevard County jurisdictions are configured:

| ID | Name | Districts | Status |
|----|------|-----------|--------|
| 1 | Melbourne | 26 | ✅ |
| 2 | Palm Bay | 25 | ✅ |
| 3 | Indian Harbour Beach | 12 | ✅ |
| 4 | Titusville | 30 | ✅ |
| 5 | Cocoa | 21 | ✅ |
| 6 | Satellite Beach | 8 | ✅ |
| 7 | Cocoa Beach | 12 | ✅ |
| 8 | Rockledge | 21 | ✅ |
| 9 | West Melbourne | 11 | ✅ |
| 10 | Cape Canaveral | 9 | ✅ |
| 11 | Indialantic | 8 | ✅ |
| 12 | Melbourne Beach | 8 | ✅ |
| 13 | Unincorporated Brevard County | 54 | ✅ |
| 14 | Malabar | 6 | ✅ |
| 15 | Grant-Valkaria | 6 | ✅ |
| 16 | Palm Shores | 4 | ✅ |
| 17 | Melbourne Village | 12 | ✅ |

---

## 2. Zoning Districts (273)

### Dimensional Data Coverage

All 273 districts have embedded DIMS data in the description field:

| Field | Coverage |
|-------|----------|
| zone_code | 100% |
| zone_name | 100% |
| min_lot_sqft | 100% (in DIMS) |
| max_height_ft | 100% (in DIMS) |
| setbacks | 100% (in DIMS) |
| source_url | 100% (in DIMS) |

### Sample District Data


**SR - Suburban Residential**
- Lot size: 10000 sqft
- Max height: 35 ft
- Setbacks: Front=25, Side=10, Rear=20
- Source: Brevard County LDC...

**TR-3 - Tourist Resort 3**
- Lot size: 7500 sqft
- Max height: 60 ft
- Setbacks: Front=25, Side=10, Rear=15
- Source: Brevard County LDC...

**RRMH-1 - Rural Residential Mobile Home**
- Lot size: 43560 sqft
- Max height: 35 ft
- Setbacks: Front=25, Side=15, Rear=20
- Source: Brevard County LDC Sec 62-1401...

---

## 3. Parcels (351,423)

| Metric | Count | Percentage |
|--------|-------|------------|
| Total parcels | 351,423 | 100% |
| With geometry | 351,421 | 99% |
| With jurisdiction_id | 351,423 | 100% |

### Note on Zone Assignment

Parcels have geometry polygons but zone_code assignment requires spatial join with zoning boundary shapefiles, which is a separate task.

---

## 4. Ordinances (2190)

### Current Status: ⚠️ NEEDS WORK

| Jurisdiction | Total | Real Content | Status |
|--------------|-------|--------------|--------|
| Melbourne | 690 | 0 | ❌ 0% |
| Palm Bay | 1 | 1 | ✅ 100% |
| Indian Harbour Beach | 134 | 0 | ❌ 0% |
| Cocoa | 24 | 0 | ❌ 0% |
| Cocoa Beach | 140 | 0 | ❌ 0% |
| Cape Canaveral | 10 | 0 | ❌ 0% |
| Malabar | 1 | 0 | ❌ 0% |
| Titusville | 0 | 0 | ❌ MISSING |
| Satellite Beach | 0 | 0 | ❌ MISSING |
| Rockledge | 0 | 0 | ❌ MISSING |
| West Melbourne | 0 | 0 | ❌ MISSING |
| Indialantic | 0 | 0 | ❌ MISSING |
| Melbourne Beach | 0 | 0 | ❌ MISSING |
| Unincorporated Brevard County | 0 | 0 | ❌ MISSING |
| Grant-Valkaria | 0 | 0 | ❌ MISSING |
| Palm Shores | 0 | 0 | ❌ MISSING |
| Melbourne Village | 0 | 0 | ❌ MISSING |

### Root Cause
Municode requires JavaScript rendering. Initial scraping captured ordinance numbers but not content.

### Solution Validated
Apify Playwright Scraper successfully extracts full content:
- POC on Malabar: 88% success rate with de-duplication
- Method: Apify Playwright → Wait for JS → Extract content → Validate → Insert

---

## 5. Related Tables

| Table | Records | Status |
|-------|---------|--------|
| development_bonuses | 81 | ✅ |
| overlay_districts | 150 | ✅ |
| conditional_uses | 627 | ✅ |
| entitlement_timelines | 327 | ✅ |

---

## 6. Data Quality Issues & Remediation

### Issue 1: Ordinance Content
**Problem:** 2189 ordinances are stubs (title = ordinance number)
**Solution:** Apify Playwright scraping (validated)
**Effort:** 2-4 hours for all 17 jurisdictions

### Issue 2: Dimensional Data Schema
**Problem:** DIMS data embedded in description field, not proper columns
**Solution:** Already extracted to `/home/claude/zoning_districts_dims.json`
**Effort:** 30 min to add columns and migrate

### Issue 3: Parcel Zone Assignment
**Problem:** Parcels don't have zone_code assigned
**Solution:** Spatial join with zoning boundary shapefiles
**Effort:** Requires boundary data from BCPAO

---

## 7. Files Generated

| File | Description |
|------|-------------|
| `zoning_districts_dims.json` | Extracted DIMS from 273 districts |
| `malabar_poc_v2_results.json` | Malabar POC with 88% success rate |
| `ZONEWISE_AUDIT_REPORT.md` | This report |

---

## 8. Next Steps

1. **Complete Ordinance Scraping** - Run Apify on remaining 16 jurisdictions
2. **Migrate DIMS Data** - Add columns to zoning_districts table
3. **Parcel Zone Assignment** - Obtain BCPAO shapefiles, run spatial join
4. **Verify with Greptile** - Automated code quality check

---

## Verification

- **Supabase URL:** mocerqjnksmhcjzxrewo.supabase.co
- **GitHub Repo:** breverdbidder/zonewise
- **Audit Date:** 2026-01-22
- **Auditor:** Claude AI (Opus 4.5)

