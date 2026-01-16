# ZoneWise Extraction Checkpoint - January 16, 2026 (v6)

## Session Summary

**Session Start:** 9:21 PM EST, January 15, 2026
**Previous Checkpoint:** v5 (47 districts, 5 jurisdictions)

### Current Status: NO CHANGE
- **47 districts** across **5 jurisdictions** (24.9% of ~189 estimated)
- All blockers remain in place

### Investigation Results

#### Browserless Analysis
- **Titusville SUCCESS**: 657K chars, 32 `chunk-content` divs with actual zoning data
- **All others FAIL**: ~130K chars, 0 `chunk-content` divs (Angular shell only)
- **Root cause**: Municode sites have different rendering configurations
  - Titusville uses alphanumeric nodeIds (TILADERE_CH28ZO_ARTVIZODIST)
  - Others use numeric nodeIds (12237, 11693)
  - Angular content loading triggered differently per client

#### eLaws Status: ALL DOWN (HTTP 503)
| Site | Status |
|------|--------|
| brevardcounty.elaws.us | 503 |
| indialantic.elaws.us | 503 |
| melbournebeach.elaws.us | 503 |
| malabar.elaws.us | 503 |
| rockledge-fl.elaws.us | 503 |
| westmelbourne-fl.elaws.us | 503 |
| **satellitebeach.elaws.us** | **200 ✅** |

#### Apify Web Scraper Test
- Attempted Rockledge via Apify web-scraper
- Result: 0 chars returned (Municode blocks content extraction)

### Current Extraction Status

| # | Jurisdiction | Platform | Status | Districts |
|---|--------------|----------|--------|-----------|
| 1 | Melbourne | Municode | ✅ Complete | 10 |
| 2 | Satellite Beach | eLaws | ✅ Complete | 9 |
| 3 | Indian Harbour Beach | Municode | ✅ Complete | 9 |
| 4 | Cocoa | Municode | ✅ Complete | 9 |
| 5 | Titusville | Municode | ✅ Complete | 10 |
| 6 | Rockledge | eLaws/Municode | 🔴 Blocked | 0 |
| 7 | Palm Bay | AMLegal | 🔴 CAPTCHA | 0 |
| 8 | West Melbourne | Municode | 🔴 No content | 0 |
| 9 | Brevard County | eLaws | 🔴 503 | 0 |
| 10 | Cape Canaveral | Municode | 🔴 No content | 0 |
| 11 | Cocoa Beach | Municode | 🔴 No content | 0 |
| 12 | Indialantic | eLaws | 🔴 503 | 0 |
| 13 | Melbourne Beach | eLaws | 🔴 503 | 0 |
| 14 | Malabar | eLaws | 🔴 503 | 0 |
| 15 | Grant-Valkaria | PDF | ⏳ TBD | 0 |
| 16 | Melbourne Village | PDF | ⏳ TBD | 0 |
| 17 | Palm Shores | PDF | ⏳ TBD | 0 |

### Technical Findings

#### Why Titusville Works
```
Titusville URL structure:
library.municode.com/fl/titusville/codes/land_development_regulations?nodeId=TILADERE_CH28ZO_ARTVIZODIST
- Uses full alphanumeric path: TILADERE_CH28ZO_ARTVIZODIST
- This references specific "Article VI - Zoning Districts"
- Angular pre-renders content for this node type

Other cities:
library.municode.com/fl/rockledge/codes/land_development_regulations?nodeId=LADERE_CH2ZODI
- Uses abbreviated nodeId: LADERE_CH2ZODI  
- Angular does NOT pre-render, loads via AJAX
- Browserless captures shell but not AJAX content
```

### Recommended Strategy

#### Immediate (This Week)
1. **Monitor eLaws daily** - If recovery, immediately extract:
   - Brevard County (~15 districts)
   - Rockledge (~10 districts)
   - Indialantic (~5 districts)
   - Melbourne Beach (~5 districts)
   - Malabar (~5 districts)

2. **PDF Extraction** for small jurisdictions:
   - Grant-Valkaria (contact planning dept)
   - Melbourne Village (contact planning dept)
   - Palm Shores (contact planning dept)

#### Medium-term (1-2 Weeks)
3. **Puppeteer with extended waits** for Municode
   - Use 30-60 second wait for AJAX content
   - Target specific content selectors
   - May need Cloudflare Workers for server-side Puppeteer

4. **Reverse engineer Municode API**
   - Analyze network calls in browser DevTools
   - Find AJAX endpoint that returns content
   - Direct API calls would bypass Angular

#### Long-term
5. **Build city contacts list** for PDF requests
6. **Consider Zoneomics partnership** - they have some data

### API/Tool Status

| Tool | Status | Notes |
|------|--------|-------|
| Browserless | ✅ Active | Key: 2TVXSZeWLkFYROe996... |
| Apify | ✅ Active | Key: apify_api_8J7MoR... |
| Firecrawl | ✅ Active | Key: fc-fa112951a... |
| Jina Reader | ✅ FREE | Works for static sites |

### Cost Summary
- **Browserless**: ~$0.50 used this session
- **Apify**: ~$0.10 used this session
- **Total session cost**: ~$0.60

---

## Next Session Prompt
```
Resume ZoneWise extraction. Current: 47 districts (5 jurisdictions, ~25%).
BLOCKERS: 
- eLaws 503 (6 sites including rockledge-fl)
- Municode Angular (West Melbourne, Cape Canaveral, Cocoa Beach) - content loads via AJAX
- AMLegal CAPTCHA (Palm Bay)
WORKING: Titusville via Browserless (unique nodeId format)
STRATEGY: Monitor eLaws recovery, try extended Puppeteer waits
```

---
*Session End: January 16, 2026, 9:30 PM EST*
