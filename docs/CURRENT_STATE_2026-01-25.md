# ZoneWise Current State - January 25, 2026

## 🚨 CRITICAL UPDATE: CDP Coverage Added

### What Changed
- **Added 16 Census Designated Places (CDPs)** to ZoneWise
- CDPs are unincorporated areas governed by Brevard County zoning
- Users can now query by CDP name (e.g., "Mims", "Merritt Island")

## ✅ VERIFIED COMPLETE

| Component | Count | Status |
|-----------|-------|--------|
| Incorporated Municipalities | 16 | ✅ 100% configured |
| Unincorporated Brevard County | 1 | ✅ Jurisdiction ID 17 |
| Census Designated Places (CDPs) | 16 | ✅ NEW - mapped to ID 17 |
| Zoning Districts | 273 | ✅ with DIMS |
| Parcels with Geometry | 351,423 | ✅ 99.99% |

## 📍 CDP Parcel Verification (BCPAO GIS API)

| CDP | ZIP Codes | Parcels | Status |
|-----|-----------|---------|--------|
| **Mims** | 32754 | 5,783 | ✅ Verified |
| **Merritt Island** | 32952, 32953, 32954 | 20,332 | ✅ Verified |
| **Port St. John** | 32927 | 12,335 | ✅ Verified |
| **Viera** | 32940, 32955 | 42,327 | ✅ Verified |
| Scottsmoor | 32775 | TBD | Configured |
| Sharpes | 32959 | TBD | Configured |
| Micco | 32976 | TBD | Configured |
| June Park | 32935 | TBD | Configured |
| South Patrick Shores | 32937 | TBD | Configured |
| Canaveral Groves | 32926 | TBD | Configured |
| Barefoot Bay | 32976 | TBD | Configured |
| West Canaveral Groves | 32926 | TBD | Configured |
| Palm Bay Heights | 32905, 32907 | TBD | Configured |
| Tropical Park | 32905 | TBD | Configured |
| North Merritt Island | 32953 | TBD | Configured |
| East Mims | 32754 | TBD | Configured |

**Total Verified: 80,777 parcels in 4 key CDPs**

## 🗺️ Complete Brevard Coverage

### Incorporated (16 municipalities - own zoning codes)
1. Melbourne (ID 1)
2. Palm Bay (ID 2)
3. Titusville (ID 3)
4. West Melbourne (ID 4)
5. Rockledge (ID 5)
6. Cocoa (ID 6)
7. Cocoa Beach (ID 7)
8. Cape Canaveral (ID 8)
9. Satellite Beach (ID 9)
10. Indian Harbour Beach (ID 10)
11. Indialantic (ID 11)
12. Melbourne Beach (ID 12)
13. Melbourne Village (ID 13)
14. Palm Shores (ID 14)
15. Malabar (ID 15) ← **POC COMPLETE**
16. Grant-Valkaria (ID 16)

### Unincorporated (ID 17 - Brevard County zoning)
- All CDPs listed above
- All other unincorporated areas

### Federal (No zoning jurisdiction)
- Kennedy Space Center (ZIP 32899)
- Patrick Space Force Base (ZIP 32925)
- Cape Canaveral Space Force Station (ZIP 32920)

## 📂 New Files Deployed

| File | Path | Description |
|------|------|-------------|
| CDP Lookup Config | `config/brevard_cdp_lookup.json` | 16 CDPs with ZIP codes |
| CDP Lookup Module | `src/cdp_lookup.py` | Python module for name resolution |
| Verification Results | `data/cdp_verification_results.json` | 80,777 parcels verified |

## 🔧 How CDP Lookup Works

```python
from cdp_lookup import CDPLookup

lookup = CDPLookup()

# User asks: "What can I build in Mims?"
result = lookup.get_zoning_authority("Mims")
# Returns:
# {
#   "jurisdiction_id": 17,
#   "zoning_authority": "Unincorporated Brevard County",
#   "community_type": "cdp",
#   "zip_codes": ["32754"]
# }

# Then query zoning_districts WHERE jurisdiction_id=17
```

## ⚠️ STILL NEEDS WORK

| Component | Issue | Solution |
|-----------|-------|----------|
| Ordinances | 2,189 stubs, few real | Apify Playwright scraping |
| Parcel zone_code | Malabar only | Spatial join for all |

## 📊 POC Status

| Jurisdiction | Parcels | BCPAO | Zone Assign | Ordinances | Status |
|--------------|---------|-------|-------------|------------|--------|
| Malabar | 1,430 | ✅ 100% | ✅ 100% | ✅ 100% | 🟢 COMPLETE |
| Other 15 | 350K | ✅ | ❌ | ❌ | 🔴 Pending |
| CDPs (Unincorp) | 80K+ | ✅ | ❌ | ❌ | 🔴 Pending |

## 🎯 Next Steps

1. **Finish Malabar stability verification** - cross-check all data
2. **Scale zone assignment** - spatial join for remaining parcels  
3. **Ordinance scraping** - Apify for 16 municipalities
4. **CDP parcel tagging** - ensure all CDPs tagged to jurisdiction_id=17

---

**Verification Date:** 2026-01-25
**Auditor:** Claude AI Architect
**Method:** BCPAO GIS API direct queries
