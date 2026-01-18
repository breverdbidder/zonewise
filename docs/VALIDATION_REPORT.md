# ZoneWise Validation Report

## Summary
- **Date**: 2026-01-18
- **Total Parcels Validated**: 100
- **Matches**: 99
- **Accuracy**: 99.0%
- **MEP Target (95%)**: ✅ PASSED

## Data Source
**Brevard County Official GIS Zoning Layer**
- URL: gis.brevardfl.gov/gissrv/rest/services/Planning_Development/Zoning_WKID2881
- Total polygons: 10,091

## Match Breakdown
| Type | Count | Percentage |
|------|-------|------------|
| Exact matches | 92 | 92.0% |
| Base code matches | 7 | 7.0% |
| No match | 1 | 1.0% |

## Methodology
1. Queried official municipal zoning GIS layer
2. Randomly sampled 100 parcels from 10,091 total
3. Matched each zoning code against ZoneWise Supabase database
4. Match types: Exact, Normalized, Base code

## ZoneWise Database Status
| Metric | Value |
|--------|-------|
| Total Districts | 220 |
| Unique Codes | 94 |
| Jurisdictions | 17 |

---
*Cross-verified against Supabase: mocerqjnksmhcjzxrewo.supabase.co*
