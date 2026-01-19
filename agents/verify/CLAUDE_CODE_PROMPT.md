# ZONEWISE COMPLETE DATA VERIFICATION & UPDATE
## Autonomous 7-Hour Claude Code Session

---

## 🎯 MISSION

You are the AI Architect for ZoneWise, a zoning intelligence platform. Your mission is to **verify and complete 100% of zoning district data** for all 17 Brevard County, Florida jurisdictions in Supabase. This session runs autonomously with **ZERO human intervention**.

---

## ⚙️ CREDENTIALS & CONFIGURATION

```javascript
// Supabase
const SUPABASE_URL = 'https://mocerqjnksmhcjzxrewo.supabase.co';
const SUPABASE_KEY = '${SUPABASE_KEY}';

// Firecrawl
const FIRECRAWL_API_KEY = '${FIRECRAWL_API_KEY}';

// Apify (backup scraper)
const APIFY_TOKEN = '${APIFY_TOKEN}';

// GitHub (for checkpoints)
const GITHUB_TOKEN = '${GITHUB_TOKEN}';
const GITHUB_REPO = 'breverdbidder/zonewise';
```

---

## 📋 JURISDICTIONS TO VERIFY (17 Total)

| ID | Jurisdiction | Population | Priority |
|----|--------------|------------|----------|
| 1 | Melbourne | 84,000 | HIGH |
| 2 | Palm Bay | 119,000 | HIGH |
| 3 | Indian Harbour Beach | 8,500 | MEDIUM |
| 4 | Titusville | 48,000 | HIGH |
| 5 | Cocoa | 19,000 | MEDIUM |
| 6 | Satellite Beach | 11,000 | MEDIUM |
| 7 | Cocoa Beach | 11,000 | MEDIUM |
| 8 | Rockledge | 27,000 | HIGH |
| 9 | West Melbourne | 24,000 | HIGH |
| 10 | Cape Canaveral | 10,000 | MEDIUM |
| 11 | Indialantic | 3,000 | LOW |
| 12 | Melbourne Beach | 3,000 | LOW |
| 13 | Unincorporated Brevard | 300,000 | CRITICAL |
| 14 | Malabar | 3,000 | LOW |
| 15 | Grant-Valkaria | 4,000 | LOW |
| 16 | Palm Shores | 1,500 | LOW |
| 17 | Melbourne Village | 700 | LOW |

---

## 🔧 TOOLS & METHODS

### Primary: Vercel AI SDK + Firecrawl Agent
```bash
npm install ai @ai-sdk/anthropic @mendable/firecrawl-js @supabase/supabase-js
```

Use the Vercel agent pattern to autonomously:
1. Search for official zoning codes
2. Scrape with Firecrawl (handles JS rendering)
3. Extract district data
4. Compare against Supabase
5. Insert/update missing records

### Backup: Direct Scraping
If Firecrawl fails, use:
- Apify Playwright Scraper
- Direct fetch with puppeteer
- PDF extraction with pdfplumber

### Data Sources by Platform
| Platform | Jurisdictions |
|----------|---------------|
| Municode | Melbourne, Palm Bay, Titusville, Cocoa, Rockledge, West Melbourne, Cape Canaveral, Cocoa Beach |
| eLaws | Satellite Beach, Indian Harbour Beach, Brevard County, Melbourne Beach, Indialantic |
| City Direct | Malabar, Grant-Valkaria, Palm Shores, Melbourne Village |

---

## 📊 DATA SCHEMA

Each zoning district MUST have this structure:

```sql
{
  jurisdiction_id: INTEGER,        -- FK to jurisdictions table
  code: VARCHAR(20),               -- e.g., "R-1", "C-2", "PUD"
  name: VARCHAR(100),              -- e.g., "Single-Family Residential"
  category: VARCHAR(50),           -- Residential|Commercial|Industrial|Mixed Use|Other
  description: TEXT,               -- Human-readable + DIMS JSON
  ordinance_section: VARCHAR(50),  -- e.g., "§62.10"
  effective_date: DATE             -- Optional
}
```

### DIMS JSON Format (embedded in description)
```
<!--DIMS:{
  "min_lot_sqft": 10000,
  "min_lot_width_ft": 80,
  "max_height_ft": 35,
  "max_stories": 2,
  "coverage_pct": 35,
  "setbacks_ft": {"front": 25, "side": 8, "rear": 25, "corner": null},
  "density": 4,
  "floor_area_ratio": null,
  "source_url": "https://...",
  "source_section": "§62.10",
  "verified_date": "2026-01-19"
}-->
```

---

## 🚀 EXECUTION PROCESS

### Phase 1: Audit Current State (30 min)
```sql
-- Run this query to assess current state
SELECT 
  j.id,
  j.name,
  COUNT(zd.id) as district_count,
  SUM(CASE WHEN zd.description LIKE '%<!--DIMS:%' THEN 1 ELSE 0 END) as with_dims,
  j.data_completeness
FROM jurisdictions j
LEFT JOIN zoning_districts zd ON j.id = zd.jurisdiction_id
WHERE j.county = 'Brevard'
GROUP BY j.id, j.name, j.data_completeness
ORDER BY j.id;
```

Create a status tracker:
```javascript
const STATUS = {
  jurisdictions: {},
  started_at: new Date().toISOString(),
  checkpoints: [],
  errors: []
};
```

### Phase 2: Verify Each Jurisdiction (5-6 hours)

For EACH jurisdiction, execute this loop:

```
┌─────────────────────────────────────────────────────────────┐
│  FOR EACH JURISDICTION:                                     │
├─────────────────────────────────────────────────────────────┤
│  1. GET existing districts from Supabase                    │
│  2. SEARCH for official zoning code URL                     │
│  3. SCRAPE zoning classifications section                   │
│  4. EXTRACT all district codes, names, and DIMS             │
│  5. COMPARE against existing data                           │
│  6. INSERT missing districts                                │
│  7. UPDATE districts with incomplete DIMS                   │
│  8. VERIFY all districts have DIMS data                     │
│  9. LOG completion status                                   │
│  10. CHECKPOINT to Supabase                                 │
└─────────────────────────────────────────────────────────────┘
```

### Phase 3: Quality Assurance (30 min)
```javascript
// Final verification query
const audit = await supabase
  .from('zoning_districts')
  .select('id, jurisdiction_id, code, description')
  .in('jurisdiction_id', [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]);

const total = audit.data.length;
const withDims = audit.data.filter(d => d.description?.includes('<!--DIMS:')).length;
const coverage = (withDims / total * 100).toFixed(1);

console.log(`FINAL AUDIT: ${withDims}/${total} (${coverage}%) districts have DIMS data`);

if (coverage < 100) {
  // Identify and fix gaps
  const missing = audit.data.filter(d => !d.description?.includes('<!--DIMS:'));
  // ... fix each one
}
```

---

## 🔄 CHECKPOINTING

Save progress every 30 minutes to Supabase:

```javascript
async function checkpoint(status) {
  await supabase
    .from('claude_context_checkpoints')
    .insert({
      session_type: 'zonewise_verification',
      checkpoint_data: status,
      created_at: new Date().toISOString()
    });
  console.log(`📍 Checkpoint saved at ${new Date().toISOString()}`);
}
```

If session is interrupted, resume from last checkpoint:
```javascript
const lastCheckpoint = await supabase
  .from('claude_context_checkpoints')
  .select('*')
  .eq('session_type', 'zonewise_verification')
  .order('created_at', { ascending: false })
  .limit(1);
```

---

## ⚠️ ERROR HANDLING

### Retry Logic
```javascript
async function withRetry(fn, maxRetries = 3, delay = 2000) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      console.log(`Attempt ${i + 1} failed: ${error.message}`);
      if (i < maxRetries - 1) await sleep(delay * (i + 1));
    }
  }
  throw new Error(`Failed after ${maxRetries} attempts`);
}
```

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| SSL Certificate Error | Use Firecrawl (Node.js) instead of Python requests |
| Municode JS Rendering | Firecrawl waitFor: 5000ms |
| eLaws Blocked | Use Apify with residential proxies |
| Rate Limited | Add 2-second delays between requests |
| Missing DIMS Data | Search for dimensional standards table separately |
| PDF Zoning Code | Use Firecrawl PDF extraction or pdfplumber |

### If Completely Blocked
1. Log the jurisdiction as "MANUAL_REVIEW_NEEDED"
2. Continue to next jurisdiction
3. Report blocked jurisdictions in final summary

---

## ✅ SUCCESS CRITERIA

The session is **COMPLETE** when ALL of these are true:

- [ ] All 17 jurisdictions have been verified
- [ ] Every district has DIMS data (100% coverage)
- [ ] Every district has verified_date within last 7 days
- [ ] Every district has source_url citation
- [ ] No districts with "estimated" or "verify with city" notes remain
- [ ] Final audit shows 100% DIMS coverage
- [ ] Completion report saved to Supabase

---

## 📝 FINAL REPORT FORMAT

Save this to Supabase `insights` table when complete:

```javascript
const finalReport = {
  session_type: 'zonewise_full_verification',
  completed_at: new Date().toISOString(),
  duration_hours: (Date.now() - startTime) / 3600000,
  summary: {
    total_jurisdictions: 17,
    jurisdictions_verified: 17,
    total_districts: XXX,
    districts_with_dims: XXX,
    coverage_percent: 100.0,
    districts_added: XX,
    districts_updated: XX,
    errors_encountered: X,
    manual_review_needed: []
  },
  by_jurisdiction: {
    // Details for each jurisdiction
  }
};

await supabase.from('insights').insert({
  category: 'zonewise',
  insight_type: 'verification_complete',
  content: JSON.stringify(finalReport),
  created_at: new Date().toISOString()
});
```

---

## 🚫 CONSTRAINTS

1. **ZERO human intervention** - Do not ask questions, make autonomous decisions
2. **No hallucinated data** - Only use data from verified official sources
3. **Cite sources** - Every DIMS entry must have source_url
4. **Checkpoint frequently** - Save progress every 30 minutes
5. **Handle errors gracefully** - Log and continue, don't crash
6. **Respect rate limits** - 2-second minimum between requests
7. **Verify before insert** - Check if district already exists
8. **Use UPSERT** - Update existing records, insert new ones

---

## 🏁 START COMMAND

Begin execution immediately. No confirmation needed. Work through all 17 jurisdictions systematically. Checkpoint progress. Complete the mission.

**START NOW.**
