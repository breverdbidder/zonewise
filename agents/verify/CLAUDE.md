# ZONEWISE AUTONOMOUS DATA COMPLETION MISSION

## MISSION OBJECTIVE
Verify and complete zoning district data for ALL 17 Brevard County jurisdictions to 100% accuracy. Run autonomously with ZERO human intervention for up to 7 hours.

---

## CRITICAL RULES

### NEVER ASK FOR PERMISSION
- Execute all tasks autonomously
- Make decisions independently
- Only stop if genuinely blocked after 5 retry attempts

### NEVER HALLUCINATE DATA
- Every district MUST come from an official source
- Every dimensional standard MUST be verified
- If data cannot be found, mark as "UNVERIFIED" with source gap noted

### PERSIST PROGRESS
- Checkpoint to Supabase `zonewise_verification_log` after EACH jurisdiction
- If session crashes, next run continues from last checkpoint
- Log all changes to `zonewise_audit_trail` table

---

## CREDENTIALS & ENDPOINTS

```javascript
const CONFIG = {
  supabase: {
    url: 'https://mocerqjnksmhcjzxrewo.supabase.co',
    key: '${SUPABASE_KEY}
  },
  firecrawl: {
    key: '${FIRECRAWL_API_KEY}'
  },
  apify: {
    key: '${APIFY_TOKEN}'
  }
};
```

---

## JURISDICTIONS TO VERIFY (17 TOTAL)

| ID | Jurisdiction | Priority | Known Code Platform |
|----|--------------|----------|---------------------|
| 1 | Melbourne | HIGH | Municode |
| 2 | Palm Bay | HIGH | Municode |
| 3 | Indian Harbour Beach | HIGH | Municode |
| 4 | Titusville | MEDIUM | Municode |
| 5 | Cocoa | MEDIUM | Municode |
| 6 | Satellite Beach | HIGH | Municode |
| 7 | Cocoa Beach | MEDIUM | Municode |
| 8 | Rockledge | HIGH | Municode |
| 9 | West Melbourne | MEDIUM | Municode |
| 10 | Cape Canaveral | LOW | Municode |
| 11 | Indialantic | LOW | Municode |
| 12 | Melbourne Beach | LOW | amlegal |
| 13 | Unincorporated Brevard | HIGH | eLaws/Brevard County |
| 14 | Malabar | LOW | Municode |
| 15 | Grant-Valkaria | LOW | Custom PDF |
| 16 | Palm Shores | LOW | Custom/Town website |
| 17 | Melbourne Village | LOW | Custom PDF |

---

## EXECUTION PHASES

### PHASE 1: AUDIT (Est. 30 min)
```
FOR EACH jurisdiction (1-17):
  1. Query Supabase: SELECT * FROM zoning_districts WHERE jurisdiction_id = {id}
  2. Count districts with valid DIMS data (contains "<!--DIMS:")
  3. Count districts missing DIMS data
  4. Log to zonewise_verification_log:
     - jurisdiction_id
     - total_districts
     - with_dims
     - missing_dims
     - audit_timestamp
  5. Generate priority queue (most gaps first)
```

### PHASE 2: RESEARCH & SCRAPE (Est. 4-5 hours)
```
FOR EACH jurisdiction (priority order):
  
  STEP 2.1: FIND OFFICIAL SOURCE
  - Search: "{jurisdiction} Florida zoning code land development regulations"
  - Try platforms in order:
    1. Municode: library.municode.com/fl/{jurisdiction}
    2. eLaws: {jurisdiction}-fl.elaws.us
    3. amlegal: codelibrary.amlegal.com/codes/{jurisdiction}
    4. City website: {jurisdiction}fl.gov or cityof{jurisdiction}.org
  - Use Firecrawl for JS-rendered pages
  - Use Apify Playwright for heavy anti-bot sites
  
  STEP 2.2: EXTRACT DISTRICT LIST
  - Find "Establishment of Districts" or "Zoning Classifications" section
  - Extract ALL district codes and names
  - Typical patterns:
    - "The following zoning districts are established:"
    - "Section 62.01 - Districts"
    - Table of contents with district sections
  
  STEP 2.3: EXTRACT DIMENSIONAL STANDARDS
  For EACH district found:
  - min_lot_sqft (minimum lot area)
  - min_lot_width_ft (minimum lot width)
  - max_height_ft (maximum building height)
  - max_stories (maximum number of stories)
  - coverage_pct (maximum lot coverage)
  - setbacks_ft: {front, side, rear, corner}
  - density (units per acre, if residential)
  - floor_area_ratio (FAR, if commercial)
  
  STEP 2.4: VALIDATE DATA
  - Cross-reference with at least 2 sources when possible
  - Check for recent ordinance amendments
  - Flag any conflicting data for manual review
  
  STEP 2.5: CHECKPOINT
  - Save progress to Supabase after each jurisdiction
  - Log: jurisdiction completed, districts found, time elapsed
```

### PHASE 3: UPDATE DATABASE (Est. 1 hour)
```
FOR EACH jurisdiction with changes:
  
  STEP 3.1: IDENTIFY CHANGES
  - New districts to INSERT
  - Existing districts to UPDATE (missing DIMS)
  - Potential duplicates to MERGE
  
  STEP 3.2: FORMAT DIMS DATA
  Each district description MUST contain:
  
  "{Human-readable summary}. <!--DIMS:{
    \"min_lot_sqft\": {number|null},
    \"min_lot_width_ft\": {number|null},
    \"max_height_ft\": {number|null},
    \"max_stories\": {number|null},
    \"coverage_pct\": {number|null},
    \"setbacks_ft\": {
      \"front\": {number|null},
      \"side\": {number|null},
      \"rear\": {number|null},
      \"corner\": {number|null}
    },
    \"density\": {number|null},
    \"floor_area_ratio\": {number|null},
    \"source_url\": \"{official_url}\",
    \"source_section\": \"{section_reference}\",
    \"verified_date\": \"{YYYY-MM-DD}\"
  }-->"
  
  STEP 3.3: EXECUTE UPDATES
  - Use Supabase REST API
  - Batch inserts (max 50 per request)
  - Individual updates for existing records
  - Log every change to audit trail
  
  STEP 3.4: VERIFY UPDATES
  - Re-query each jurisdiction
  - Confirm DIMS count matches expected
  - Report any failures
```

### PHASE 4: FINAL AUDIT (Est. 30 min)
```
1. Query ALL districts: SELECT * FROM zoning_districts
2. Calculate metrics:
   - Total districts
   - Districts with DIMS (should be 100%)
   - Districts by jurisdiction
   - Districts by category
3. Generate summary report
4. Save to zonewise_completion_report table
5. Create downloadable audit file
```

---

## SCRAPING STRATEGIES BY PLATFORM

### MUNICODE (Most Common)
```javascript
// Direct URL pattern
const url = `https://library.municode.com/fl/${city}/codes/code_of_ordinances`;
// Or land development code
const url = `https://library.municode.com/fl/${city}/codes/land_development_code`;

// Use Firecrawl with wait for JS
await firecrawl.scrapeUrl(url, {
  formats: ['markdown'],
  waitFor: 5000
});

// Navigate to zoning section (usually Part/Article VI or similar)
// Look for nodeId parameter in URLs
```

### ELAWS
```javascript
// URL pattern
const url = `https://${city}-fl.elaws.us/code`;
// Or Brevard County
const url = `https://brevardcounty.elaws.us/code`;

// May require subscription - use search fallback
// Extract from Google cached versions if blocked
```

### AMLEGAL
```javascript
// URL pattern
const url = `https://codelibrary.amlegal.com/codes/${city}/latest/overview`;

// Similar to Municode - wait for JS
```

### CUSTOM CITY WEBSITES
```javascript
// Search for PDF downloads
// Common patterns:
// - /documents/zoning-ordinance.pdf
// - /planning/land-development-code
// - /government/ordinances

// Use Apify for PDF extraction if needed
```

---

## ERROR HANDLING

### SCRAPE FAILURES
```
IF scrape fails:
  1. Retry with longer wait time (10s, 15s, 20s)
  2. Try alternate URL patterns
  3. Try different scraping tool (Firecrawl → Apify)
  4. Search for cached/archived versions
  5. After 5 failures: log as "SOURCE_UNAVAILABLE" and continue
```

### DATA CONFLICTS
```
IF conflicting data found:
  1. Prefer most recent ordinance date
  2. Prefer official city source over third-party
  3. Log conflict to audit trail
  4. Use most conservative value (higher setbacks, lower density)
```

### RATE LIMITS
```
- Firecrawl: 2-second delay between requests
- Apify: Use existing actor runs when possible
- Supabase: Batch writes, max 50 per request
- Overall: 5-second delay between jurisdictions
```

---

## EXPECTED OUTPUT

### Database State After Completion
```sql
-- All districts should have DIMS data
SELECT 
  j.name as jurisdiction,
  COUNT(*) as total_districts,
  SUM(CASE WHEN d.description LIKE '%<!--DIMS:%' THEN 1 ELSE 0 END) as with_dims,
  ROUND(
    SUM(CASE WHEN d.description LIKE '%<!--DIMS:%' THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
    1
  ) as pct_complete
FROM zoning_districts d
JOIN jurisdictions j ON d.jurisdiction_id = j.id
WHERE j.county = 'Brevard'
GROUP BY j.name
ORDER BY pct_complete DESC;

-- Expected result: ALL jurisdictions at 100%
```

### Completion Report Format
```json
{
  "mission": "ZoneWise Brevard County Complete",
  "completed_at": "2026-01-19T21:00:00Z",
  "duration_hours": 5.2,
  "jurisdictions": {
    "total": 17,
    "completed": 17,
    "failed": 0
  },
  "districts": {
    "total": 280,
    "with_dims": 280,
    "added": 14,
    "updated": 32,
    "unchanged": 234
  },
  "data_quality": {
    "dims_coverage": "100%",
    "source_citations": "100%",
    "verified_date": "100%"
  },
  "sources_used": [
    "Municode (12 jurisdictions)",
    "eLaws (3 jurisdictions)",
    "City websites (2 jurisdictions)"
  ],
  "issues_logged": 0,
  "manual_review_needed": []
}
```

---

## EXECUTION COMMAND

Run this mission in Claude Code with:

```bash
# Install dependencies
npm install ai @ai-sdk/anthropic @mendable/firecrawl-js @supabase/supabase-js

# Execute mission
node zonewise-complete-mission.js
```

---

## SUCCESS CRITERIA

✅ All 17 jurisdictions verified against official sources  
✅ All districts have valid DIMS data with source citations  
✅ 100% coverage in Supabase zoning_districts table  
✅ Audit trail logged for all changes  
✅ Completion report generated  
✅ Zero manual intervention required  

---

## AUTONOMOUS AGENT BEHAVIOR

You are an autonomous data engineering agent. Your purpose is to ensure ZoneWise has complete, accurate zoning data for Brevard County.

**DO NOT:**
- Ask for clarification
- Wait for approval
- Skip jurisdictions due to difficulty
- Hallucinate any data values

**DO:**
- Execute systematically through all 17 jurisdictions
- Retry failed operations up to 5 times
- Log all progress and decisions
- Use multiple data sources for verification
- Complete the mission regardless of obstacles

**START NOW. REPORT ONLY WHEN 100% COMPLETE.**
