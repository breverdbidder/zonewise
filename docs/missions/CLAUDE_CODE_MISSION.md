# CLAUDE CODE MISSION: ZoneWise Complete Ordinance Data Population

## CRITICAL CONTEXT
This mission is to COMPLETE the work, not build more infrastructure.

**Current State:**
- 273 zoning districts in Supabase (base dimensional data only)
- 0 ordinances tracked
- 0 development bonuses captured
- 0 overlay districts mapped
- 0 conditional uses documented
- 0 entitlement timelines recorded

**Required End State:**
- ALL ordinances from ALL 17 jurisdictions catalogued
- ALL development bonus programs extracted
- ALL overlay districts mapped
- ALL conditional use requirements documented
- ALL entitlement timelines captured

---

## CREDENTIALS

Get from GitHub Secrets or environment:
- SUPABASE_URL
- SUPABASE_SERVICE_KEY  
- FIRECRAWL_API_KEY
- GITHUB_TOKEN

---

## PHASE 1: DEPLOY SCHEMA (15 min)

Execute SQL from: `sql/ordinance_monitoring_schema.sql`

Creates tables: ordinances, development_bonuses, overlay_districts, conditional_uses, ordinance_changes, entitlement_timelines, municode_scrape_log

---

## PHASE 2: SCRAPE ALL 17 JURISDICTIONS (5-6 hours)

### Jurisdictions & Municode URLs

| ID | Name | Municode Slug |
|----|------|---------------|
| 1 | Melbourne | melbourne |
| 2 | Palm Bay | palm_bay |
| 3 | Indian Harbour Beach | indian_harbour_beach |
| 4 | Satellite Beach | satellite_beach |
| 5 | Indialantic | indialantic |
| 6 | Melbourne Beach | melbourne_beach |
| 7 | West Melbourne | west_melbourne |
| 8 | Cocoa | cocoa |
| 9 | Cocoa Beach | cocoa_beach |
| 10 | Rockledge | rockledge |
| 11 | Titusville | titusville |
| 12 | Cape Canaveral | cape_canaveral |
| 13 | Brevard County | brevard_county |
| 14 | Malabar | malabar |
| 15 | Palm Shores | palm_shores |
| 16 | Grant-Valkaria | grant-valkaria |
| 17 | Melbourne Village | melbourne_village |

URL pattern: `https://library.municode.com/fl/{slug}/codes/code_of_ordinances`

### For EACH Jurisdiction, Extract:

#### 2.1 Ordinances
- Find ALL ordinance references (pattern: "Ord. YYYY-NN")
- Extract: ordinance_number, title, chapter, section, passed_date
- **Target: 850-3,400 total**

#### 2.2 Development Bonuses
Search for: "Development Bonus", "Density Bonus", "Incentive Zoning", "Affordable Housing Incentives", "Height Bonuses", "Parking Reductions"
- **Target: 85-340 total**

#### 2.3 Overlay Districts  
Search for: Historic, Flood, Coastal, Airport, Environmental, Waterfront, Redevelopment, Downtown overlays
- **Target: 51-170 total**

#### 2.4 Conditional Uses
For each district: Special Exceptions, Conditional Use Permits, Site Plan Review uses
- **Target: 340-1,700 total**

#### 2.5 Entitlement Timelines
Site Plan, Rezoning, Variance, Special Exception, Subdivision, PUD timelines
- **Target: 85-170 total**

---

## MINIMUM SUCCESS CRITERIA

| Table | Minimum | Target |
|-------|---------|--------|
| ordinances | 500 | 2,000+ |
| development_bonuses | 50 | 200+ |
| overlay_districts | 30 | 100+ |
| conditional_uses | 200 | 1,000+ |
| entitlement_timelines | 50 | 150+ |

---

## EXECUTION RULES

- ❌ Do NOT stop at "infrastructure complete"
- ❌ Do NOT skip jurisdictions
- ❌ Do NOT use placeholder data
- ❌ Do NOT mark complete until queries pass
- ✅ Execute autonomously
- ✅ Report progress hourly
- ✅ Continue until ALL data populated

---

## ESTIMATED TIME: 6-7 hours

**START NOW. Do not stop until complete.**
