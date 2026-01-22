# CLAUDE CODE MISSION: Ordinance Content POC - Malabar Only

## ⚠️ CRITICAL CONTEXT - READ FIRST

**Previous attempts FAILED because:**
1. V1-V2: Scraped TOC pages, got ordinance NUMBERS only (no content)
2. V3: Used Playwright but still only scraped navigation lists
3. Result: 2,158 stub records (title = ordinance number, no actual content)

**This POC must PROVE content extraction works before scaling.**

---

## 🎯 MISSION: Extract REAL Ordinance Content from Malabar

**Target:** Malabar, FL (jurisdiction_id = 14)
**Expected ordinances:** ~10-20
**Success criteria:** 80%+ have REAL content (not stubs)

---

## 📋 VALIDATION RULES (ENFORCE STRICTLY)

```python
def is_real_ordinance(record):
    """Returns True ONLY if this is real content, not a stub."""
    
    # RULE 1: Title must NOT equal ordinance number
    if record['title'] == record['ordinance_number']:
        return False  # STUB - reject
    
    # RULE 2: Title must be descriptive (>10 chars, not just a number)
    if len(record['title']) < 10:
        return False  # TOO SHORT - reject
    
    # RULE 3: Must have either summary OR full_text with real content
    has_summary = record.get('summary') and len(record['summary']) > 50
    has_full_text = record.get('full_text') and len(record['full_text']) > 200
    if not (has_summary or has_full_text):
        return False  # NO CONTENT - reject
    
    # RULE 4: Source URL must be specific (not just base municode URL)
    if 'nodeId=' not in record.get('source_url', ''):
        return False  # GENERIC URL - reject
    
    return True  # PASS - this is real content
```

**DO NOT INSERT ANY RECORD THAT FAILS VALIDATION.**

---

## 🔧 TECHNICAL APPROACH

### Step 1: Install Playwright
```bash
pip install playwright --break-system-packages
playwright install chromium
```

### Step 2: Navigate to Malabar Zoning Code
```
Base URL: https://library.municode.com/fl/malabar/codes/code_of_ordinances
Zoning Chapter: ?nodeId=PTIICOOR_CH50ZO
```

### Step 3: THE CRITICAL DIFFERENCE FROM V3

**V3 (FAILED):** Scraped the Table of Contents page
- Got: List of ordinance numbers
- Missing: Actual ordinance content

**V4 (THIS MISSION):** Navigate INTO each ordinance detail page
- Click each ordinance link
- Wait for JS to render content
- Extract: title, summary, full text, dates
- Validate BEFORE inserting

### Step 4: Playwright Navigation Pattern

```python
from playwright.sync_api import sync_playwright
import time

def scrape_ordinance_detail(page, ord_link):
    """Navigate INTO an ordinance and extract CONTENT."""
    
    # Click the ordinance link
    page.click(f'a:has-text("{ord_link}")')
    
    # CRITICAL: Wait for content to render (Municode uses Angular)
    page.wait_for_load_state('networkidle')
    time.sleep(3)  # Extra buffer for JS
    
    # Extract the ACTUAL content
    content = {
        'ordinance_number': None,
        'title': None,
        'summary': None,
        'full_text': None,
        'passed_date': None,
        'source_url': page.url
    }
    
    # Get the page title (should be descriptive, NOT just ord number)
    title_el = page.query_selector('h1.chunk-title, .document-title, h1')
    if title_el:
        content['title'] = title_el.inner_text().strip()
    
    # Get the main content body
    body_el = page.query_selector('.chunk-content, .document-content, article')
    if body_el:
        content['full_text'] = body_el.inner_text().strip()
    
    # Extract ordinance number from URL or content
    # Pattern: "Ord. No. 2024-33" or "Ordinance 2024-33"
    import re
    ord_match = re.search(r'Ord(?:inance)?\.?\s*(?:No\.?)?\s*(\d{2,4}-\d+)', 
                          content.get('full_text', ''))
    if ord_match:
        content['ordinance_number'] = ord_match.group(1)
    
    # Extract passed date
    date_match = re.search(r'(?:passed|adopted|effective)[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
                           content.get('full_text', ''), re.IGNORECASE)
    if date_match:
        content['passed_date'] = date_match.group(1)
    
    return content
```

---

## 📊 OUTPUT REQUIREMENTS

### Console Output (REQUIRED)
```
============================================================
MALABAR ORDINANCE SCRAPING - POC V4
============================================================

[1/12] Navigating to: Ord. 2023-05
  URL: https://library.municode.com/fl/malabar/...?nodeId=PTIICOOR_CH50ZO_S50-1
  Title extracted: "Establishment of Zoning Districts"
  Title length: 35 chars
  Full text length: 2,847 chars
  Has passed_date: Yes (2023-05-15)
  VALIDATION: ✅ PASS - Real content

[2/12] Navigating to: Ord. 2022-18
  URL: https://library.municode.com/fl/malabar/...
  Title extracted: "2022-18"
  Title length: 7 chars
  Full text length: 0 chars
  Has passed_date: No
  VALIDATION: ❌ FAIL - Title equals ord number (stub)
  SKIPPING INSERT

...

============================================================
FINAL RESULTS
============================================================
Total ordinances found: 12
Passed validation: 9 (75%)
Failed validation: 3 (25%)
  - Stub (title=number): 2
  - No content: 1

INSERTED TO SUPABASE: 9 records

SUCCESS RATE: 75% (below 80% threshold)
⚠️ REVIEW NEEDED BEFORE SCALING
============================================================
```

### Proof File (REQUIRED)
Save to: `/home/claude/malabar_poc_results.json`

```json
{
  "jurisdiction": "Malabar",
  "jurisdiction_id": 14,
  "scrape_date": "2026-01-22T15:00:00Z",
  "total_found": 12,
  "passed_validation": 9,
  "failed_validation": 3,
  "success_rate": 0.75,
  "threshold": 0.80,
  "passed_threshold": false,
  "records": [
    {
      "ordinance_number": "2023-05",
      "title": "Establishment of Zoning Districts",
      "title_length": 35,
      "full_text_length": 2847,
      "has_summary": true,
      "has_passed_date": true,
      "source_url": "https://...",
      "validation_passed": true,
      "validation_reason": "Real content"
    },
    {
      "ordinance_number": "2022-18",
      "title": "2022-18",
      "title_length": 7,
      "full_text_length": 0,
      "has_summary": false,
      "has_passed_date": false,
      "source_url": "https://...",
      "validation_passed": false,
      "validation_reason": "Title equals ord number (stub)"
    }
  ]
}
```

---

## 🗄️ DATABASE

### Supabase Credentials
```
URL: https://mocerqjnksmhcjzxrewo.supabase.co
SERVICE_KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1vY2VycWpua3NtaGNqenhyZXdvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDUzMjUyNiwiZXhwIjoyMDgwMTA4NTI2fQ.fL255mO0V8-rrU0Il3L41cIdQXUau-HRQXiamTqp9nE
```

### Insert ONLY Validated Records
```python
def insert_ordinance(record):
    """Insert ONLY if validation passes."""
    
    if not is_real_ordinance(record):
        print(f"  SKIPPING: {record['ordinance_number']} - failed validation")
        return False
    
    # Insert to Supabase
    response = supabase.table('ordinances').insert({
        'jurisdiction_id': 14,  # Malabar
        'ordinance_number': record['ordinance_number'],
        'title': record['title'],
        'summary': record.get('summary'),
        'full_text': record.get('full_text'),
        'passed_date': record.get('passed_date'),
        'source_url': record['source_url'],
        'status': 'active'
    }).execute()
    
    return True
```

---

## ⛔ FAILURE CONDITIONS

**STOP AND REPORT if:**
1. Playwright cannot render Municode pages (JS issue)
2. Zero ordinances pass validation
3. Cannot find ordinance detail pages (only TOC available)

**DO NOT:**
- Insert stub records (title = ordinance number)
- Insert records without content
- Fake the success rate
- Proceed to other jurisdictions without explicit approval

---

## ✅ SUCCESS CRITERIA

| Metric | Threshold | Action |
|--------|-----------|--------|
| Success rate ≥ 80% | PASS | Report results, await approval to scale |
| Success rate 50-79% | PARTIAL | Report issues, propose fixes |
| Success rate < 50% | FAIL | Stop, report root cause |

---

## 🚨 MANDATORY DELIVERABLES

1. **Console log** showing each ordinance's validation status
2. **JSON proof file** at `/home/claude/malabar_poc_results.json`
3. **Sample content** - show ACTUAL extracted text for 3 ordinances (first 500 chars each)
4. **Honest assessment** - if it's not working, say so

---

## 📞 ESCALATION

If Municode blocks scraping or Playwright fails:
1. Try Jina Reader as fallback: `https://r.jina.ai/{municode_url}`
2. Try Firecrawl API: `fc-fa112951a2564765a2d146302774ac9b`
3. If all fail, report: "Content extraction not possible with available tools"

---

## START NOW

1. Install Playwright
2. Navigate to Malabar zoning code
3. Find ALL ordinance links in the TOC
4. Navigate INTO each one (not just scrape the list)
5. Extract CONTENT
6. Validate BEFORE inserting
7. Report results with proof

**DO NOT COMPLETE THIS MISSION CLAIMING SUCCESS WITHOUT THE JSON PROOF FILE.**
