# ZoneWise 63 KPI Report Generator Skill

## Overview
Generate comprehensive 63 KPI development analysis reports for any Florida property using Supabase data and County APIs.

## Usage
```bash
# Generate report for a parcel
npm run --prefix reports generate -- --parcel "28-38-31-54-B-54"

# Or use the API
curl -X POST https://zonewise.ai/api/reports/generate \
  -H "Content-Type: application/json" \
  -d '{"parcelId": "28-38-31-54-B-54"}'
```

## 63 KPIs (10 Categories)

### Category 1: Site & Parcel Metrics (8 KPIs)
1. Parcel ID
2. Tax Account
3. Lot Area (Acres)
4. Lot Area (ft²)
5. Lot Type
6. Subdivision
7. Vacant Status
8. Legal Description

### Category 2: Existing Building (5 KPIs)
9. Existing Building Area
10. Total Sub Area
11. Existing Building Use
12. Year Built
13. Current Land Use Code

### Category 3: Zoning & Regulatory (10 KPIs)
14-23. Zoning Code, District, Category, Height, Stories, Historic, LEED, Live Local, TOD, Ordinance

### Category 4: Development Capacity (9 KPIs)
24-32. FAR, Max Building, Coverage, Footprint, Open Space, Unused Rights, Current FAR, Utilization, Expansion

### Category 5: Residential Capacity (4 KPIs)
33-36. Density, Max Area, Max Units, Allowed Uses

### Category 6: Lodging Capacity (4 KPIs)
37-40. Density, Max Area, Max Rooms, Allowed Uses

### Category 7: Commercial/Office (5 KPIs)
41-45. Max Office, Max Commercial, Expansion, Commercial Uses, Office Uses

### Category 8: Setback Requirements (5 KPIs)
46-50. Front, Side, Rear, Min Lot Size, Min Lot Width

### Category 9: Allowed Uses (6 KPIs)
51-56. Civic (Right/Warrant/Exception), Educational, Industrial, Infrastructure

### Category 10: Financial Opportunity (7 KPIs)
57-63. Market Value, Sale Price, Sale Date, Value/Acre, Value/SF, Untapped %, Buildable SF

## Data Sources

| Source | Data |
|--------|------|
| Supabase `parcel_zones` | Parcel ID, Zone Code, Zone Name |
| Supabase `zoning_districts` | Zone details, category, description |
| Supabase `dimensional_standards` | FAR, Height, Setbacks, Coverage |
| BCPAO API | Property details, sales, improvements |
| County GIS | Parcel geometry, coordinates |

## Output Formats
- **DOCX**: Professional report with tables, charts
- **JSON**: API response with all 63 KPIs
- **React**: Dashboard component (.jsx artifact)

## Key Formulas

```javascript
// Development Capacity
maxBuildingArea = lotSqFt × FAR
maxFootprint = lotSqFt × maxCoverage
unusedRights = maxBuildingArea - existingBldgArea
farUtilization = (existingBldgArea / lotSqFt) / FAR × 100
untappedPotential = 100 - farUtilization

// Financial
valuePerAcre = marketValue / acreage
valuePerSF = marketValue / lotSqFt
```

## Color Theme (DOCX)
```javascript
HEADER_NAVY: "#1E3A5F"
PRACTICE_GREEN: "#E8F5E9"
SKIP_RED: "#FFEBEE"
SHABBAT_ORANGE: "#FFF3E0"
UBRZATI_BLUE: "#E3F2FD"
GLEASON_PURPLE: "#F3E5F5"
```

## Repositories
- **zonewise-modal**: `reports/src/generate_63kpi_report.js`
- **zonewise-web**: `app/api/reports/generate/route.ts`
- **169-e-flagler**: Original template source

## Version
- v2.0.0 - Full 63 KPI deployment
- Last updated: 2026-02-04
