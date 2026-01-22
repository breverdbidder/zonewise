# CLAUDE CODE MISSION V3: ZoneWise Complete Ordinance Scraping
## 7-Hour Autonomous Session - PLAYWRIGHT REQUIRED

---

## MANDATORY: USE PLAYWRIGHT FOR MUNICODE

```
⚠️ MUNICODE REQUIRES JAVASCRIPT RENDERING
⚠️ JINA READER WILL NOT WORK
⚠️ FIRECRAWL WILL NOT WORK FULLY
⚠️ YOU MUST USE PLAYWRIGHT
```

### Step 1: Install Playwright FIRST
```bash
pip install playwright --break-system-packages
playwright install chromium
```

### Step 2: Use This Scraping Pattern
```python
from playwright.sync_api import sync_playwright

def scrape_municode(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until='networkidle')
        page.wait_for_timeout(3000)  # Wait for JS to render
        
        # Get fully rendered HTML
        content = page.content()
        
        # Also get text for parsing
        text = page.inner_text('body')
        
        browser.close()
        return content, text
```

### Why This Matters
- Municode pages are ~4KB without JS rendering (just navigation)
- Municode pages are ~300-500KB WITH JS rendering (actual ordinance text)
- Previous attempts got 4KB shells, not real content
- Playwright renders JavaScript like a real browser

---

## CREDENTIALS

### Supabase
```
URL: https://mocerqjnksmhcjzxrewo.supabase.co
SERVICE_KEY: ${SUPABASE_SERVICE_KEY}
```

### GitHub
```
TOKEN: ${GITHUB_TOKEN}
REPO: breverdbidder/zonewise
```

---

## TARGET: 100 ORDINANCES PER JURISDICTION

| ID | Jurisdiction | Target | Municode Slug |
|----|--------------|--------|---------------|
| 1 | Melbourne | 100 | melbourne |
| 2 | Palm Bay | 100 | palm_bay |
| 3 | Indian Harbour Beach | 100 | indian_harbour_beach |
| 4 | Satellite Beach | 100 | satellite_beach |
| 5 | Indialantic | 100 | indialantic |
| 6 | Melbourne Beach | 100 | melbourne_beach |
| 7 | West Melbourne | 100 | west_melbourne |
| 8 | Cocoa | 100 | cocoa |
| 9 | Cocoa Beach | 100 | cocoa_beach |
| 10 | Rockledge | 100 | rockledge |
| 11 | Titusville | 100 | titusville |
| 12 | Cape Canaveral | 100 | cape_canaveral |
| 13 | Brevard County | 100 | brevard_county |
| 14 | Malabar | 100 | malabar |
| 15 | Palm Shores | 100 | palm_shores |
| 16 | Grant-Valkaria | 100 | grant-valkaria |
| 17 | Melbourne Village | 100 | melbourne_village |

**TOTAL TARGET: 1,700 ordinances**

Note: Smaller jurisdictions may have fewer than 100. That's fine IF you scraped everything available.

---

## SCRAPING STRATEGY WITH PLAYWRIGHT

### 1. Get Table of Contents
```python
url = f"https://library.municode.com/fl/{slug}/codes/code_of_ordinances"
content, text = scrape_municode(url)

# Parse TOC to find all chapter links
soup = BeautifulSoup(content, 'html.parser')
chapters = soup.select('a[href*="nodeId="]')
```

### 2. Crawl Each Chapter
```python
for chapter_link in chapters:
    chapter_url = "https://library.municode.com" + chapter_link['href']
    chapter_content, chapter_text = scrape_municode(chapter_url)
    
    # Find all section links within chapter
    sections = soup.select('a[href*="nodeId="]')
    
    for section in sections:
        section_url = ...
        section_content, section_text = scrape_municode(section_url)
        
        # NOW you have the actual ordinance text
        # Parse for ordinance references
```

### 3. Extract Ordinances
Pattern to find: `(Ord. No. YYYY-NN, § X, M-D-YY)` or `(Ord. YYYY-NN, passed M-D-YY)`

```python
import re

ordinance_pattern = r'\(Ord\.?\s*(?:No\.?)?\s*(\d{2,4}[-–]\d+)[,\s]+(?:§\s*\d+[,\s]+)?(?:passed\s+)?(\d{1,2}[-–/]\d{1,2}[-–/]\d{2,4})\)'

matches = re.findall(ordinance_pattern, section_text)
for ord_num, passed_date in matches:
    # Insert to Supabase with:
    # - ordinance_number
    # - passed_date
    # - section (where found)
    # - source_url (the actual Municode URL)
    # - full_text (the surrounding paragraph)
```

### 4. Extract Development Bonuses
Look for tables with these headers:
- "Bonus" or "Incentive"
- "Density" or "Units"
- "Height" or "Stories"
- "FAR" or "Intensity"

```python
tables = soup.find_all('table')
for table in tables:
    headers = [th.get_text().lower() for th in table.find_all('th')]
    if any(word in ' '.join(headers) for word in ['bonus', 'incentive', 'density']):
        # This is likely a bonus table - parse it
        rows = table.find_all('tr')[1:]  # Skip header
        for row in rows:
            cells = row.find_all('td')
            # Extract feature_name, bonuses, conditions
```

### 5. Extract Overlay Districts
Search for sections containing:
- "overlay district"
- "historic preservation"
- "flood zone"
- "coastal high hazard"
- "airport approach"

### 6. Extract Conditional Uses
Look for tables in zoning chapters that list uses by district with columns like:
- "P" = Permitted
- "C" or "CU" = Conditional Use
- "SE" = Special Exception

---

## VALIDATION CHECKPOINT

### Palm Bay Ground Truth (Already in DB)
Before scraping, verify these 9 bonuses exist:

1. Vertical mixed-use → 2 stories
2. Affordable housing → 2 stories
3. Public Open Space → 1 story per 3,000 sf
4. Parking garage → 1 floor per level
5. Waterfront (Turkey Creek) → 1 additional floor
6. Low Impact Design → 2 du/acre
7. Emergency storm shelters → 2 du/acre
8. Living shoreline → 10% parking reduction
9. Co-location water-dependent → 10% parking reduction

**DO NOT delete or modify these. They are verified correct.**

### After Scraping Palm Bay
Your scraper should find Ord. 2024-33 in the text. If it doesn't find ordinance references with dates, your parser is wrong.

---

## DATABASE SCHEMA

Tables already exist. Insert to:

### ordinances
```sql
jurisdiction_id, ordinance_number, title, chapter, section,
passed_date, source_url, full_text, status
```

### development_bonuses
```sql
jurisdiction_id, program_name, feature_name, density_bonus,
intensity_bonus, height_bonus, parking_reduction, conditions,
table_reference, source_url
```

### overlay_districts
```sql
jurisdiction_id, overlay_code, overlay_name, overlay_type,
additional_restrictions, source_url
```

### conditional_uses
```sql
jurisdiction_id, district_code, use_name, approval_type,
conditions, source_url
```

### entitlement_timelines
```sql
jurisdiction_id, process_type, typical_days_min, typical_days_max,
steps (JSONB), source_url
```

---

## EXECUTION FLOW

```
PHASE 0: SETUP (15 min)
├── pip install playwright --break-system-packages
├── playwright install chromium
├── Test on one Municode page - verify content > 100KB
└── If content < 10KB, Playwright not working - FIX BEFORE CONTINUING

PHASE 1: VALIDATION (30 min)  
├── Verify Palm Bay has 9 bonuses (don't delete them)
├── Scrape Palm Bay with Playwright
├── Verify you find Ord. 2024-33 in scraped text
└── If not found, FIX PARSER before continuing

PHASE 2: LARGE JURISDICTIONS (3 hours)
├── Melbourne (largest)
├── Palm Bay
├── Brevard County
├── Titusville
├── Cocoa
└── Target: 500+ ordinances after this phase

PHASE 3: MEDIUM JURISDICTIONS (2.5 hours)
├── West Melbourne, Rockledge, Cocoa Beach
├── Cape Canaveral, Satellite Beach, IHB
├── Indialantic, Melbourne Beach
└── Target: 1,200+ ordinances after this phase

PHASE 4: SMALL JURISDICTIONS (1 hour)
├── Malabar, Palm Shores
├── Grant-Valkaria, Melbourne Village
└── Target: 1,400+ ordinances total

PHASE 5: VERIFICATION (30 min)
├── Count ordinances per jurisdiction
├── Verify source_urls are valid
├── Log summary to municode_scrape_log
└── Report final numbers
```

---

## PROGRESS LOGGING

```
[SETUP] Installing Playwright...
[SETUP] ✅ Playwright installed
[SETUP] Testing Municode scrape...
[SETUP] ✅ Got 347KB from Melbourne TOC (JS rendered correctly)

[1/17] Melbourne
  - Pages scraped: 234
  - Content size: 45MB total
  - Ordinances found: 156
  - Bonuses found: 12
  - Overlays found: 5
  ✅ Complete

[2/17] Palm Bay
  - Pages scraped: 189
  - Ordinances found: 134 (including 2024-33 ✓)
  ...
```

---

## ERROR HANDLING

```python
# If page doesn't load
for attempt in range(3):
    try:
        page.goto(url, wait_until='networkidle', timeout=30000)
        break
    except:
        if attempt == 2:
            log_error(url)
            continue  # Skip this page, don't stop

# If Playwright crashes
try:
    scrape_jurisdiction(jid)
except Exception as e:
    log_to_db(jid, 'failed', str(e))
    # RESTART browser and continue to next jurisdiction
    browser = p.chromium.launch(headless=True)
```

---

## SUCCESS CRITERIA

| Metric | Minimum | Target |
|--------|---------|--------|
| Total ordinances | 1,000 | 1,700 |
| Jurisdictions with data | 17/17 | 17/17 |
| Avg per jurisdiction | 60 | 100 |
| Palm Bay bonuses | 9 | 9 (already done) |

### Quality Checks
```python
# Every ordinance has source_url
assert all(r['source_url'] for r in ordinances)

# Every ordinance has valid date
assert all(r['passed_date'] for r in ordinances)

# No jurisdiction has 0 ordinances
for jid in range(1, 18):
    count = len([r for r in ordinances if r['jurisdiction_id'] == jid])
    assert count > 0, f"Jurisdiction {jid} has no ordinances"
```

---

## FORBIDDEN ACTIONS

```
❌ DO NOT use Jina Reader (won't render JS)
❌ DO NOT use Firecrawl as primary (backup only)
❌ DO NOT generate/fabricate any data
❌ DO NOT insert without source_url
❌ DO NOT delete Palm Bay's 9 bonuses
❌ DO NOT stop for errors - log and continue
❌ DO NOT ask for permission - all granted
```

---

## PRE-APPROVED PERMISSIONS

You have FULL authority to:
- Install any pip packages
- Run Playwright browser automation
- Make unlimited HTTP requests
- Insert/update Supabase data
- Create/modify files
- Run for 7 hours continuously
- Skip individual pages that fail
- Continue without human intervention

---

## START COMMAND

```bash
# 1. Install Playwright
pip install playwright --break-system-packages
playwright install chromium

# 2. Verify it works
python -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://library.municode.com/fl/melbourne/codes/code_of_ordinances')
    page.wait_for_timeout(5000)
    print(f'Content length: {len(page.content())} bytes')
    browser.close()
"
# Should print > 100,000 bytes

# 3. Run scraper
python scripts/playwright_ordinance_scraper.py
```

**BEGIN NOW. Do not stop until all 17 jurisdictions are scraped.**
