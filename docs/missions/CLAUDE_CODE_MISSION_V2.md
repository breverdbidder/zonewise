# CLAUDE CODE MISSION V2: ZoneWise REAL Ordinance Data
## 7-Hour Autonomous Session - Zero Human Intervention

---

## ⚠️ CRITICAL RULES - READ FIRST

### FORBIDDEN ACTIONS (Instant Failure)
- ❌ NEVER generate, fabricate, or synthesize data
- ❌ NEVER use placeholder, template, or example values  
- ❌ NEVER insert data without raw scraped text as proof
- ❌ NEVER claim completion without verification passing
- ❌ NEVER skip a jurisdiction
- ❌ NEVER ask for permission - all permissions granted below

### REQUIRED FOR EVERY RECORD
- ✅ MUST have source_url pointing to exact Municode page
- ✅ MUST have raw_scraped_text field with actual page content
- ✅ MUST match content that exists on the Municode website
- ✅ MUST be verifiable by re-visiting the source URL

### HOW TO KNOW IF DATA IS REAL vs FAKE
```
REAL: "Ord. 2024-33, passed 9-19-24" scraped from Municode
FAKE: "Ord. 2024-001" generated because it looks plausible

REAL: "2 stories" bonus for "Vertical mixed-use" from Table 173-8  
FAKE: "LEED Certification" bonus because it sounds reasonable
```

---

## CREDENTIALS

Get from environment variables or GitHub Secrets:
- SUPABASE_URL
- SUPABASE_SERVICE_KEY
- FIRECRAWL_API_KEY
- GITHUB_TOKEN

Jina Reader needs no API key: https://r.jina.ai/{url}

---

## VALIDATION: Palm Bay Table 173-8

Your scraper MUST find these 9 bonuses from Ord. 2024-33:

1. Vertical mixed-use → 2 stories
2. Affordable housing → 2 stories + Max FLU density
3. Public Open Space → 1 story per 3,000 sf
4. Parking garage → 1 floor per garage level
5. Waterfront access (Turkey Creek, IRL) → 1 additional floor
6. Low Impact Design → 2 du/acre
7. Emergency storm shelters → 2 du/acre
8. Living shoreline → 10% parking reduction
9. Co-location water-dependent → 10% parking reduction

**If your scraper finds < 7 of these, STOP and fix the parser.**

---

## 17 JURISDICTIONS

Melbourne, Palm Bay, Indian Harbour Beach, Satellite Beach,
Indialantic, Melbourne Beach, West Melbourne, Cocoa, Cocoa Beach,
Rockledge, Titusville, Cape Canaveral, Brevard County, Malabar,
Palm Shores, Grant-Valkaria, Melbourne Village

URL pattern: https://library.municode.com/fl/{slug}/codes/code_of_ordinances

---

## WHAT TO EXTRACT

1. **Ordinances** - Pattern: "(Ord. YYYY-NN, passed M-D-YY)"
2. **Development Bonuses** - Look for TABLES with bonus/incentive programs
3. **Overlay Districts** - Historic, flood, coastal, airport overlays
4. **Conditional Uses** - Special exceptions, CUPs by district
5. **Entitlement Timelines** - Application processes, review timelines

---

## SUCCESS CRITERIA

| Table | Minimum |
|-------|---------|
| ordinances | 200 |
| development_bonuses | 30 |
| overlay_districts | 20 |
| conditional_uses | 100 |
| entitlement_timelines | 50 |

Plus: Palm Bay MUST have 9 bonuses matching Table 173-8

---

## EXECUTION

1. Verify Palm Bay has 9 bonuses (already inserted)
2. Scrape Melbourne → verify real data
3. Continue through all 17 jurisdictions
4. Run verification checks
5. Do NOT stop until complete

**Previous attempt failed because data was GENERATED not SCRAPED.**
**This attempt succeeds when every record is verifiable.**
