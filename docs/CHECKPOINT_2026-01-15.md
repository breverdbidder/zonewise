# ZoneWise Extraction Checkpoint - January 15, 2026

## Current Status

### Extraction Progress (17 Jurisdictions)

| # | Jurisdiction | Platform | Status | Districts | Data Quality |
|---|--------------|----------|--------|-----------|--------------|
| 1 | Melbourne | Municode | ✅ Extracted | 20 | Partial - Missing setbacks |
| 2 | Satellite Beach | eLaws | ✅ Extracted | 12 | Poor - Missing most dims |
| 3 | Palm Bay | American Legal | ⏳ Supabase only | 1 | Partial |
| 4 | Cocoa | Municode | 🔄 Pending | 0 | - |
| 5 | Titusville | Municode | 🔄 Pending | 0 | - |
| 6 | Rockledge | Municode | 🔄 Pending | 0 | - |
| 7 | West Melbourne | Municode | 🔄 Pending | 0 | - |
| 8 | Brevard County | Municode | 🔄 Pending | 0 | - |
| 9 | Indian Harbour Beach | Municode | 🔄 Pending | 0 | - |
| 10 | Cape Canaveral | Municode | 🔄 Pending | 0 | - |
| 11 | Cocoa Beach | Municode | 🔄 Pending | 0 | - |
| 12 | Indialantic | eLaws | 🔄 Pending | 0 | - |
| 13 | Melbourne Beach | eLaws | 🔄 Pending | 0 | - |
| 14 | Malabar | eLaws | 🔄 Pending | 0 | - |
| 15 | Grant-Valkaria | PDF | ⏳ TBD | 0 | - |
| 16 | Melbourne Village | PDF | ⏳ TBD | 0 | - |
| 17 | Palm Shores | PDF | ⏳ TBD | 0 | - |

### Data Locations

1. **JSON File:** `zonewise_extraction_results.json` (32 rows - Melbourne + Satellite Beach)
2. **Supabase:** `zoning_districts` table (4 rows - Melbourne 4, Palm Bay 1)
3. **Target:** 189 rows (estimated across all 17 jurisdictions)

### Key Issues

1. **JSON→Supabase sync broken** - Different schemas between extractors
2. **Missing setback data** - Extraction capturing lot sizes but not setbacks
3. **Satellite Beach district_name malformed** - Contains URL fragments
4. **14 jurisdictions not started**

## Repository Structure

```
breverdbidder/zonewise
├── municipal_code_extractor.py          # Main extractor (JSON output)
├── supabase_integration.py              # Supabase client
├── zonewise_extraction_results.json     # Current extraction output
├── src/
│   ├── ingestion/
│   │   ├── firecrawl_scraper.py        # 17 jurisdiction configs
│   │   └── ordinance_parser.py         # Regex + LLM parsing
│   └── extractors/
│       └── zonewise_mcp_server.py      # MCP server extractor
└── .github/workflows/
    ├── continuous_extraction.yml        # Daily 11 PM EST
    └── daily-zonewize.yml              # Analysis workflow
```

## Supabase Connection

- **URL:** https://mocerqjnksmhcjzxrewo.supabase.co
- **Tables:** jurisdictions (17), zoning_districts (4 current)
- **Service Key:** eyJhbGci... (ends with fL255mO0V8-rrU0Il3L41cIdQXUau-HRQXiamTqp9nE)

## Next Steps for New Chat

### Priority 1: Fix Data Quality

1. **Enhance Melbourne extraction** - Parse Table 2A for setbacks
2. **Fix Satellite Beach parsing** - Clean district names, extract all dimensional fields
3. **Validate against source** - Spot check 3 districts per jurisdiction

### Priority 2: Complete 14 Remaining Jurisdictions

**Municode jurisdictions (9):**
- Cocoa, Titusville, Rockledge, West Melbourne, Brevard County
- Indian Harbour Beach, Cape Canaveral, Cocoa Beach

**eLaws jurisdictions (3):**
- Indialantic, Melbourne Beach, Malabar

**PDF jurisdictions (3):**
- Grant-Valkaria, Melbourne Village, Palm Shores

### Priority 3: Sync to Supabase

1. Align JSON schema with Supabase schema
2. Create upsert script to sync JSON → Supabase
3. Verify continuous_extraction.yml workflow

## Commands to Resume

```bash
# Check extraction status
curl -s "https://api.github.com/repos/breverdbidder/zonewise/contents/zonewise_extraction_results.json" \
  -H "Authorization: token [GITHUB_TOKEN]" \
  | jq -r '.content' | base64 -d | python3 -c "
import json, sys
data = json.load(sys.stdin)
for j, d in data.items(): print(f'{j}: {len(d)} districts')
print(f'Total: {sum(len(d) for d in data.values())} rows')
"

# Check Supabase count
curl -s "https://mocerqjnksmhcjzxrewo.supabase.co/rest/v1/zoning_districts?select=id" \
  -H "apikey: [SUPABASE_SERVICE_KEY]" | jq 'length'

# Trigger continuous extraction manually
curl -X POST "https://api.github.com/repos/breverdbidder/zonewise/actions/workflows/continuous_extraction.yml/dispatches" \
  -H "Authorization: token [GITHUB_TOKEN]" \
  -d '{"ref":"main","inputs":{"jurisdiction":"","force_update":"true"}}'
```

## Dimensional Standards Target Schema

```json
{
  "jurisdiction": "Melbourne",
  "district_code": "R-1AA",
  "district_name": "Single-Family Residential",
  "min_lot_area_sqft": 10000,
  "min_lot_width_ft": 85,
  "min_lot_depth_ft": null,
  "max_height_ft": 36,
  "max_stories": 2,
  "front_setback_ft": 25,
  "side_setback_ft": 7.5,
  "rear_setback_ft": 20,
  "max_lot_coverage_pct": 45,
  "max_impervious_pct": 65
}
```

## Session Context

- **Date:** January 15, 2026, 9:15 PM EST
- **Token Usage:** ~45K (within limit)
- **Next 11 PM run:** Tonight, monitor GitHub Actions
- **GitHub Actions to watch:**
  - continuous_extraction.yml (scheduled 4 AM UTC = 11 PM EST)
  - daily-zonewize.yml

---

*Checkpoint created for session continuity*
