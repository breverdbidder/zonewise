# CLAUDE CODE MISSION: ZoneWise Sprint 1
## Weeks 1-3 | Foundation + Automation + Brevard Complete

**Mission Start:** January 22, 2026
**Mission End:** February 11, 2026
**Budget:** $220
**Autonomous Execution:** YES - Do not ask for permission

---

## 🎯 SPRINT 1 OBJECTIVES

| Objective | Success Criteria |
|-----------|------------------|
| Build automation infrastructure | 4/4 tools deployed |
| Complete Brevard Phase 4 | 273 districts × permitted uses |
| Complete Brevard Phases 7, 8 | Overlays + Bonuses |
| Pilot Orange County | Phases 2-3 complete |
| Accuracy | Brevard 95%+, Orange 90%+ |

---

## 🔑 CREDENTIALS

### Supabase (PRIMARY DATABASE)
```
URL: https://mocerqjnksmhcjzxrewo.supabase.co
SERVICE_KEY: $SUPABASE_KEY
```

### GitHub
```
REPO: breverdbidder/zonewise
TOKEN: $GITHUB_TOKEN
```

### Firecrawl (Web Scraping)
```
API_KEY: $FIRECRAWL_API_KEY
ENDPOINT: https://api.firecrawl.dev/v1/scrape
```

### Apify (Backup Scraping)
```
TOKEN: $APIFY_TOKEN
```

---

## 📊 EXISTING DATABASE STATE

### Tables with Data
| Table | Rows | Status |
|-------|------|--------|
| jurisdictions | 17 | ✅ Brevard complete |
| zoning_districts | 273 | ✅ With DIMS |
| dimensional_standards | 273 | ✅ Linked |

### Tables Need Population
| Table | Purpose | Sprint 1 Target |
|-------|---------|-----------------|
| permitted_uses | By-right uses | 273 districts × 50+ uses |
| overlay_districts | Special overlays | All Brevard overlays |
| development_bonuses | Incentive programs | Palm Bay + others |

---

## WEEK 1: AUTOMATION INFRASTRUCTURE

### Day 1: Modal.com Parallel Scraper

**Task:** Set up 10-concurrent Playwright scraper

```python
# File: src/scrapers/modal_scraper.py

import modal
import json
from datetime import datetime

stub = modal.Stub("zonewise-scraper")

image = modal.Image.debian_slim().pip_install(
    "playwright",
    "beautifulsoup4", 
    "httpx"
).run_commands(
    "playwright install chromium",
    "playwright install-deps chromium"
)

@stub.function(
    image=image,
    concurrency_limit=10,
    timeout=300,
    retries=2
)
async def scrape_municode_page(url: str, jurisdiction_id: int) -> dict:
    """Scrape a single Municode page with full JS rendering."""
    from playwright.async_api import async_playwright
    from bs4 import BeautifulSoup
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2000)  # Extra wait for dynamic content
            content = await page.content()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract main content
            main_content = soup.find('div', class_='chunk-content')
            if not main_content:
                main_content = soup.find('div', id='codebankContent')
            
            text = main_content.get_text(separator='\n') if main_content else ""
            
            # Extract tables
            tables = []
            for table in soup.find_all('table'):
                tables.append(str(table))
            
            return {
                "url": url,
                "jurisdiction_id": jurisdiction_id,
                "html": content,
                "text": text,
                "tables": tables,
                "scraped_at": datetime.utcnow().isoformat(),
                "success": True
            }
            
        except Exception as e:
            return {
                "url": url,
                "jurisdiction_id": jurisdiction_id,
                "error": str(e),
                "success": False
            }
        finally:
            await browser.close()


@stub.function(image=image, timeout=3600)
def batch_scrape(urls_with_ids: list[tuple[str, int]]) -> list[dict]:
    """Batch scrape multiple URLs in parallel."""
    results = []
    for result in scrape_municode_page.map(
        [u[0] for u in urls_with_ids],
        [u[1] for u in urls_with_ids]
    ):
        results.append(result)
    return results


@stub.local_entrypoint()
def main():
    """Test with a few Brevard jurisdictions."""
    test_urls = [
        ("https://library.municode.com/fl/melbourne/codes/code_of_ordinances", 1),
        ("https://library.municode.com/fl/palm_bay/codes/code_of_ordinances", 2),
        ("https://library.municode.com/fl/titusville/codes/code_of_ordinances", 4),
    ]
    
    results = batch_scrape.remote(test_urls)
    print(f"Scraped {len(results)} pages")
    for r in results:
        print(f"  - {r['url']}: {'✅' if r['success'] else '❌'}")
```

**Validation:** Run `modal run src/scrapers/modal_scraper.py` and confirm 3 pages scraped.

---

### Day 2: Template Detector

**Task:** Classify ordinance structures into known templates

```python
# File: src/utils/template_detector.py

import re
from enum import Enum
from dataclasses import dataclass

class OrdinanceTemplate(Enum):
    TEMPLATE_A = "template_a"  # Article-based (Melbourne, Palm Bay)
    TEMPLATE_B = "template_b"  # Chapter 62 style (Brevard County)
    TEMPLATE_C = "template_c"  # Part III style (Titusville)
    CUSTOM = "custom"          # Manual review needed

@dataclass
class TemplateMatch:
    template: OrdinanceTemplate
    confidence: float
    patterns_matched: list[str]

TEMPLATE_PATTERNS = {
    OrdinanceTemplate.TEMPLATE_A: {
        "required": [
            r"Article\s+[IVX]+.*Zoning\s+Districts",
            r"Article\s+[IVX]+.*Use\s+Regulations"
        ],
        "optional": [
            r"Table\s+\d+.*Dimensional\s+Standards",
            r"Schedule\s+of\s+Uses"
        ]
    },
    OrdinanceTemplate.TEMPLATE_B: {
        "required": [
            r"Chapter\s+62.*Land\s+Development",
            r"Division\s+\d+.*Zoning"
        ],
        "optional": [
            r"Sec\.\s+62-\d+",
            r"Article\s+VI"
        ]
    },
    OrdinanceTemplate.TEMPLATE_C: {
        "required": [
            r"Part\s+III.*Land\s+Development\s+Code",
            r"Chapter\s+34.*Zoning"
        ],
        "optional": [
            r"Division\s+\d+",
            r"Sec\.\s+34-\d+"
        ]
    }
}

def detect_template(toc_html: str) -> TemplateMatch:
    """
    Detect which ordinance template a jurisdiction uses.
    Returns template type and confidence score.
    """
    text = toc_html.lower() if toc_html else ""
    
    best_match = None
    best_score = 0
    
    for template, patterns in TEMPLATE_PATTERNS.items():
        required_matches = sum(
            1 for p in patterns["required"] 
            if re.search(p, toc_html, re.IGNORECASE)
        )
        optional_matches = sum(
            1 for p in patterns["optional"]
            if re.search(p, toc_html, re.IGNORECASE)
        )
        
        required_count = len(patterns["required"])
        optional_count = len(patterns["optional"])
        
        # Score: 70% required, 30% optional
        if required_count > 0:
            score = (required_matches / required_count) * 0.7
            if optional_count > 0:
                score += (optional_matches / optional_count) * 0.3
            
            if score > best_score:
                best_score = score
                matched_patterns = [
                    p for p in patterns["required"] + patterns["optional"]
                    if re.search(p, toc_html, re.IGNORECASE)
                ]
                best_match = TemplateMatch(
                    template=template,
                    confidence=score,
                    patterns_matched=matched_patterns
                )
    
    if best_match and best_match.confidence >= 0.7:
        return best_match
    
    return TemplateMatch(
        template=OrdinanceTemplate.CUSTOM,
        confidence=0.0,
        patterns_matched=[]
    )


# Known Brevard jurisdictions and their templates
BREVARD_TEMPLATES = {
    1: OrdinanceTemplate.TEMPLATE_A,   # Melbourne
    2: OrdinanceTemplate.TEMPLATE_A,   # Palm Bay
    3: OrdinanceTemplate.TEMPLATE_A,   # Indian Harbour Beach
    4: OrdinanceTemplate.TEMPLATE_C,   # Titusville
    5: OrdinanceTemplate.TEMPLATE_A,   # Cocoa
    6: OrdinanceTemplate.TEMPLATE_A,   # Satellite Beach
    7: OrdinanceTemplate.TEMPLATE_A,   # Cocoa Beach
    8: OrdinanceTemplate.TEMPLATE_A,   # Rockledge
    9: OrdinanceTemplate.TEMPLATE_A,   # West Melbourne
    10: OrdinanceTemplate.TEMPLATE_A,  # Cape Canaveral
    11: OrdinanceTemplate.TEMPLATE_A,  # Indialantic
    12: OrdinanceTemplate.TEMPLATE_A,  # Melbourne Beach
    13: OrdinanceTemplate.TEMPLATE_B,  # Unincorporated Brevard
    14: OrdinanceTemplate.TEMPLATE_A,  # Malabar
    15: OrdinanceTemplate.TEMPLATE_A,  # Grant-Valkaria
    16: OrdinanceTemplate.TEMPLATE_A,  # Palm Shores
    17: OrdinanceTemplate.TEMPLATE_A,  # Melbourne Village
}
```

**Validation:** Test on 5 jurisdictions, expect 85%+ accuracy.

---

### Day 3: Claude Batch Processor

**Task:** Set up overnight batch processing (50% cost savings)

```python
# File: src/llm/batch_processor.py

import anthropic
import json
import time
from datetime import datetime
from pathlib import Path

client = anthropic.Anthropic()

EXTRACTION_SYSTEM_PROMPT = """You are a zoning data extraction specialist. 
Extract permitted uses from municipal ordinance text into structured JSON.

Rules:
1. Only extract uses explicitly listed as "Permitted" or "P" or "By-right"
2. Standardize use names (e.g., "SFR" → "Single-family residential")
3. Include any conditions or footnotes
4. If uncertain, mark as "needs_review": true

Output JSON schema:
{
  "district_code": "R-1",
  "uses": [
    {
      "use_name": "Single-family residential",
      "use_category": "Residential",
      "permission_type": "P",
      "conditions": null,
      "needs_review": false
    }
  ]
}"""


def create_batch_requests(districts: list[dict]) -> list[dict]:
    """Create batch request objects for Claude API."""
    requests = []
    
    for district in districts:
        requests.append({
            "custom_id": f"district-{district['id']}",
            "params": {
                "model": "claude-sonnet-4-5-20250929",
                "max_tokens": 4096,
                "system": EXTRACTION_SYSTEM_PROMPT,
                "messages": [{
                    "role": "user",
                    "content": f"""Extract permitted uses from this zoning district:

District: {district['code']} - {district['name']}
Jurisdiction: {district['jurisdiction']}

Ordinance Text:
{district['ordinance_text'][:8000]}

Use Table (if present):
{district.get('use_table', 'No use table found')}

Return ONLY valid JSON."""
                }]
            }
        })
    
    return requests


def submit_batch(requests: list[dict]) -> str:
    """Submit batch to Claude API for overnight processing."""
    
    batch = client.batches.create(requests=requests)
    
    print(f"✅ Batch submitted: {batch.id}")
    print(f"   Status: {batch.processing_status}")
    print(f"   Requests: {len(requests)}")
    
    # Save batch ID for later retrieval
    batch_log = {
        "batch_id": batch.id,
        "submitted_at": datetime.utcnow().isoformat(),
        "request_count": len(requests),
        "status": batch.processing_status
    }
    
    Path("data/batches").mkdir(parents=True, exist_ok=True)
    with open(f"data/batches/{batch.id}.json", "w") as f:
        json.dump(batch_log, f, indent=2)
    
    return batch.id


def check_batch_status(batch_id: str) -> dict:
    """Check status of a submitted batch."""
    batch = client.batches.retrieve(batch_id)
    
    return {
        "id": batch.id,
        "status": batch.processing_status,
        "created_at": batch.created_at,
        "ended_at": batch.ended_at,
        "request_counts": {
            "total": batch.request_counts.total,
            "completed": batch.request_counts.completed,
            "failed": batch.request_counts.failed
        }
    }


def retrieve_batch_results(batch_id: str) -> list[dict]:
    """Retrieve results from completed batch."""
    batch = client.batches.retrieve(batch_id)
    
    if batch.processing_status != "ended":
        raise ValueError(f"Batch not complete: {batch.processing_status}")
    
    results = []
    for result in client.batches.results(batch_id):
        custom_id = result.custom_id
        
        if result.result.type == "succeeded":
            content = result.result.message.content[0].text
            try:
                parsed = json.loads(content)
                results.append({
                    "custom_id": custom_id,
                    "success": True,
                    "data": parsed
                })
            except json.JSONDecodeError:
                results.append({
                    "custom_id": custom_id,
                    "success": False,
                    "error": "JSON parse error",
                    "raw": content
                })
        else:
            results.append({
                "custom_id": custom_id,
                "success": False,
                "error": result.result.error.message
            })
    
    return results
```

**Validation:** Submit test batch of 10 districts, retrieve next morning.

---

### Day 4: Validation Pipeline

**Task:** GitHub Actions daily accuracy check

```yaml
# File: .github/workflows/validate.yml

name: Daily Data Validation

on:
  schedule:
    - cron: '0 6 * * *'  # 6 AM UTC daily
  workflow_dispatch:  # Manual trigger

env:
  SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
  SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}

jobs:
  validate:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install httpx supabase anthropic
      
      - name: Sample 50 random districts
        id: sample
        run: |
          python scripts/sample_districts.py
          echo "sample_file=data/validation/sample_$(date +%Y%m%d).json" >> $GITHUB_OUTPUT
      
      - name: Validate against source
        id: validate
        run: |
          python scripts/validate_accuracy.py ${{ steps.sample.outputs.sample_file }}
      
      - name: Update accuracy metrics
        run: |
          python scripts/update_metrics.py
      
      - name: Create issues for errors
        if: ${{ steps.validate.outputs.error_count > 0 }}
        run: |
          python scripts/create_issues.py ${{ steps.sample.outputs.sample_file }}
      
      - name: Upload validation report
        uses: actions/upload-artifact@v4
        with:
          name: validation-report-${{ github.run_number }}
          path: data/validation/
```

```python
# File: scripts/sample_districts.py

import httpx
import json
import random
from datetime import datetime
from pathlib import Path

SUPABASE_URL = "https://mocerqjnksmhcjzxrewo.supabase.co"
SUPABASE_KEY = "$SUPABASE_KEY"

def sample_districts(n: int = 50) -> list[dict]:
    """Sample n random districts from database."""
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    
    # Get total count
    response = httpx.get(
        f"{SUPABASE_URL}/rest/v1/zoning_districts",
        headers={**headers, "Prefer": "count=exact"},
        params={"select": "id", "limit": 1}
    )
    
    total = int(response.headers.get("content-range", "0-0/0").split("/")[1])
    
    # Random sample
    sample_ids = random.sample(range(1, total + 1), min(n, total))
    
    # Fetch sampled districts
    response = httpx.get(
        f"{SUPABASE_URL}/rest/v1/zoning_districts",
        headers=headers,
        params={
            "select": "id,code,name,jurisdiction_id,source_url,dims_data",
            "id": f"in.({','.join(map(str, sample_ids))})"
        }
    )
    
    districts = response.json()
    
    # Save sample
    Path("data/validation").mkdir(parents=True, exist_ok=True)
    output_file = f"data/validation/sample_{datetime.now().strftime('%Y%m%d')}.json"
    
    with open(output_file, "w") as f:
        json.dump({
            "sampled_at": datetime.utcnow().isoformat(),
            "count": len(districts),
            "districts": districts
        }, f, indent=2)
    
    print(f"✅ Sampled {len(districts)} districts → {output_file}")
    return districts


if __name__ == "__main__":
    sample_districts(50)
```

**Validation:** Run manually, confirm 50 districts sampled.

---

### Day 5: Ground Truth Dataset

**Task:** Manually verify 50 Brevard districts as validation baseline

```python
# File: scripts/create_ground_truth.py

"""
MANUAL TASK: Verify these 50 districts against source ordinances.

For each district:
1. Open source_url
2. Verify dims_data matches ordinance
3. Mark as verified or flag errors

Output: data/ground_truth/brevard_50.json
"""

GROUND_TRUTH_DISTRICTS = [
    # Melbourne (10)
    {"id": 1, "code": "R-1A", "expected_min_lot": 7500, "expected_front_setback": 25},
    {"id": 2, "code": "R-1AA", "expected_min_lot": 9000, "expected_front_setback": 25},
    {"id": 3, "code": "R-1AAA", "expected_min_lot": 15000, "expected_front_setback": 30},
    # ... add 47 more with known correct values
    
    # Palm Bay (10)
    {"id": 50, "code": "RS-1", "expected_min_lot": 7500, "expected_front_setback": 25},
    
    # Titusville (10)
    # Cocoa (10)
    # Brevard County (10)
]

# After manual verification, this becomes the test set
# for automated validation pipeline
```

**Action Required:** Claude Code should OUTPUT a checklist for human verification, not auto-generate fake ground truth.

---

## WEEK 2: BREVARD PHASE 4 (PERMITTED USES)

### Day 1-2: Structured Output Schema

```python
# File: src/schemas/permitted_uses.py

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class PermissionType(str, Enum):
    PERMITTED = "P"           # By-right
    CONDITIONAL = "C"         # Requires CUP
    SPECIAL_EXCEPTION = "S"   # Requires special exception
    ACCESSORY = "A"           # Accessory use only
    PROHIBITED = "X"          # Not allowed

class UseCategory(str, Enum):
    RESIDENTIAL = "Residential"
    COMMERCIAL = "Commercial"
    INDUSTRIAL = "Industrial"
    INSTITUTIONAL = "Institutional"
    AGRICULTURAL = "Agricultural"
    RECREATION = "Recreation"
    UTILITY = "Utility"
    MIXED_USE = "Mixed Use"

class PermittedUse(BaseModel):
    use_name: str = Field(..., description="Standardized use name")
    use_category: UseCategory
    permission_type: PermissionType
    conditions: Optional[str] = Field(None, description="Any conditions or footnotes")
    min_lot_size: Optional[int] = Field(None, description="Minimum lot size if use-specific")
    max_density: Optional[float] = Field(None, description="Max units/acre if specified")
    parking_required: Optional[str] = Field(None, description="Parking requirement if specified")
    needs_review: bool = Field(False, description="Flag for manual review")
    source_section: Optional[str] = Field(None, description="Ordinance section reference")

class DistrictUses(BaseModel):
    district_id: int
    district_code: str
    jurisdiction_id: int
    uses: list[PermittedUse]
    extracted_at: str
    extraction_confidence: float = Field(..., ge=0, le=1)


# Standard use taxonomy (merge variations)
USE_TAXONOMY = {
    # Residential
    "single-family": ["SFR", "single family", "detached dwelling", "one-family"],
    "two-family": ["duplex", "two-family", "2-family"],
    "townhouse": ["townhome", "attached dwelling", "row house"],
    "multi-family": ["apartments", "multi-family", "MFR"],
    "mobile-home": ["manufactured home", "mobile home", "MH"],
    "adu": ["accessory dwelling", "ADU", "granny flat", "in-law suite"],
    
    # Commercial
    "retail": ["retail store", "shop", "store"],
    "restaurant": ["eating establishment", "food service", "cafe"],
    "office": ["professional office", "business office", "office building"],
    "hotel": ["motel", "lodging", "inn", "bed and breakfast"],
    
    # Add more categories...
}

def standardize_use_name(raw_name: str) -> str:
    """Convert raw use name to standardized taxonomy."""
    raw_lower = raw_name.lower().strip()
    
    for standard, variations in USE_TAXONOMY.items():
        if raw_lower in [v.lower() for v in variations]:
            return standard
        if any(v.lower() in raw_lower for v in variations):
            return standard
    
    return raw_name  # Return original if no match
```

### Day 3-4: Extract 5 Pilot Jurisdictions

**Target:** Melbourne, Palm Bay, Titusville, Cocoa, Brevard County

```python
# File: scripts/extract_permitted_uses.py

import asyncio
import json
from src.scrapers.modal_scraper import scrape_municode_page
from src.llm.batch_processor import create_batch_requests, submit_batch
from src.schemas.permitted_uses import DistrictUses, standardize_use_name

PILOT_JURISDICTIONS = [
    {"id": 1, "name": "Melbourne", "use_table_url": "..."},
    {"id": 2, "name": "Palm Bay", "use_table_url": "..."},
    {"id": 4, "name": "Titusville", "use_table_url": "..."},
    {"id": 5, "name": "Cocoa", "use_table_url": "..."},
    {"id": 13, "name": "Brevard County", "use_table_url": "..."},
]

async def extract_pilot_uses():
    """Extract permitted uses for pilot jurisdictions."""
    
    # Step 1: Scrape use tables
    print("📥 Scraping use tables...")
    for jurisdiction in PILOT_JURISDICTIONS:
        result = await scrape_municode_page.remote(
            jurisdiction["use_table_url"],
            jurisdiction["id"]
        )
        jurisdiction["scraped_content"] = result
    
    # Step 2: Get districts for each jurisdiction
    # ... fetch from Supabase
    
    # Step 3: Create batch extraction requests
    requests = create_batch_requests(districts)
    
    # Step 4: Submit batch (overnight processing)
    batch_id = submit_batch(requests)
    
    print(f"✅ Batch submitted: {batch_id}")
    print("   Results available tomorrow morning")
    
    return batch_id


if __name__ == "__main__":
    asyncio.run(extract_pilot_uses())
```

### Day 5: QA and Iterate

**Task:** Review batch results, fix extraction errors

```python
# File: scripts/qa_permitted_uses.py

from src.llm.batch_processor import retrieve_batch_results

def qa_batch_results(batch_id: str):
    """QA batch extraction results."""
    
    results = retrieve_batch_results(batch_id)
    
    stats = {
        "total": len(results),
        "success": 0,
        "failed": 0,
        "needs_review": 0,
        "errors": []
    }
    
    for result in results:
        if result["success"]:
            stats["success"] += 1
            
            # Check for low confidence extractions
            data = result["data"]
            for use in data.get("uses", []):
                if use.get("needs_review"):
                    stats["needs_review"] += 1
        else:
            stats["failed"] += 1
            stats["errors"].append({
                "id": result["custom_id"],
                "error": result.get("error")
            })
    
    print(f"""
    📊 Batch QA Results
    ==================
    Total:        {stats['total']}
    Success:      {stats['success']} ({stats['success']/stats['total']*100:.1f}%)
    Failed:       {stats['failed']}
    Needs Review: {stats['needs_review']}
    """)
    
    if stats["errors"]:
        print("❌ Errors:")
        for e in stats["errors"][:10]:
            print(f"   - {e['id']}: {e['error']}")
    
    return stats
```

---

## WEEK 3: BREVARD PHASES 7, 8 + ORANGE PILOT

### Days 1-2: Brevard Overlay Districts (Phase 7)

**Target overlays by jurisdiction:**

| Jurisdiction | Known Overlays |
|--------------|----------------|
| Melbourne | Historic Downtown, Eau Gallie Arts, Airport |
| Cocoa | Historic Cocoa Village, Airport |
| Titusville | Historic Downtown, Airport (KSC) |
| Cocoa Beach | Downtown, Coastal High Hazard |
| Satellite Beach | Coastal High Hazard |
| Brevard County | Airport, Environmental, SJRWMD |

```python
# File: src/schemas/overlay_districts.py

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class OverlayType(str, Enum):
    HISTORIC = "Historic"
    FLOOD = "Flood"
    AIRPORT = "Airport"
    ENVIRONMENTAL = "Environmental"
    DOWNTOWN = "Downtown/CRA"
    CORRIDOR = "Corridor"
    TOD = "Transit-Oriented"
    COASTAL = "Coastal High Hazard"

class OverlayDistrict(BaseModel):
    jurisdiction_id: int
    overlay_code: str
    overlay_name: str
    overlay_type: OverlayType
    base_districts_affected: list[str]
    additional_setbacks: Optional[dict] = None
    height_restrictions: Optional[dict] = None
    additional_requirements: list[str] = Field(default_factory=list)
    design_standards_url: Optional[str] = None
    bonuses_available: Optional[dict] = None
    source_url: str
    source_section: str
    verified_date: str
```

### Days 3-4: Brevard Development Bonuses (Phase 8)

**Key source:** Palm Bay Table 173-8

```python
# File: src/schemas/development_bonuses.py

from pydantic import BaseModel, Field
from typing import Optional

class DevelopmentBonus(BaseModel):
    jurisdiction_id: int
    bonus_name: str
    bonus_type: str  # Density, Height, Parking, FAR
    base_requirement: str
    bonus_amount: str
    conditions: list[str]
    eligible_districts: list[str]
    application_process: Optional[str] = None
    source_url: str
    source_section: str
    verified_date: str


# Known Palm Bay bonuses from Table 173-8
PALM_BAY_BONUSES = [
    {
        "bonus_name": "Affordable Housing Density Bonus",
        "bonus_type": "Density",
        "base_requirement": "Standard density per zoning",
        "bonus_amount": "Up to 25% density increase",
        "conditions": ["20% units at 80% AMI", "Recorded covenant"],
        "eligible_districts": ["RM-10", "RM-15", "MU-1", "MU-2"]
    },
    # Add more from actual Table 173-8
]
```

### Day 5: Orange County Pilot (Phases 2-3)

**Target:** Base zoning + dimensional standards for Orange County

```python
# Orange County Municode URL
ORANGE_COUNTY_URL = "https://library.municode.com/fl/orange_county/codes/code_of_ordinances"

# Known Orange County zoning districts to extract
ORANGE_DISTRICTS = [
    "R-1", "R-1A", "R-1AA", "R-2", "R-3",  # Residential
    "C-1", "C-2", "C-3",                    # Commercial
    "I-1", "I-2",                           # Industrial
    "PD", "PUD",                            # Planned Development
]
```

---

## SUCCESS CRITERIA

| Metric | Target | Validation |
|--------|--------|------------|
| Automation tools | 4/4 deployed | Each tool runs without error |
| Brevard Phase 4 | 273 districts with uses | `SELECT COUNT(*) FROM permitted_uses WHERE jurisdiction_id IN (1-17)` |
| Brevard Phase 7 | All overlays mapped | Manual review of overlay table |
| Brevard Phase 8 | Palm Bay + 3 others | Bonuses table populated |
| Orange Phases 2-3 | ~50 districts | Districts in database with DIMS |
| Accuracy | 95% Brevard, 90% Orange | Validation pipeline results |
| Budget | ≤$220 | API cost tracking |

---

## CHECKPOINTS

| Day | Checkpoint | Action if Failed |
|-----|------------|------------------|
| Day 3 | Modal scraper works | Debug Playwright, try Firecrawl fallback |
| Day 5 | Ground truth ready | Pause, complete manual verification |
| Day 8 | Phase 4 pilot extracts | Rewrite prompts, add examples |
| Day 12 | Batch results valid | Manual review, fix schema |
| Day 15 | Orange pilot works | Apply Brevard learnings |

---

## COST TRACKING

```python
# Track costs in Supabase
cost_entry = {
    "date": "2026-01-22",
    "service": "claude_batch",
    "operation": "phase_4_extraction",
    "requests": 273,
    "tokens_in": 500000,
    "tokens_out": 200000,
    "cost_usd": 0.85,
    "sprint": 1
}
```

**Budget checkpoint:** If costs exceed $150 by Day 10, reduce Orange scope.

---

## DELIVERABLES

By February 11, 2026:

1. **Code:**
   - `src/scrapers/modal_scraper.py` - Parallel scraper
   - `src/utils/template_detector.py` - Ordinance classifier
   - `src/llm/batch_processor.py` - Claude Batch integration
   - `.github/workflows/validate.yml` - Daily validation
   - `src/schemas/*.py` - All data schemas

2. **Data:**
   - Brevard: 14/20 phases populated
   - Orange: 6/20 phases populated
   - ~5,000 districts in database

3. **Documentation:**
   - Ground truth dataset (50 verified districts)
   - Accuracy report
   - Cost report

---

*Mission Version: 1.0*
*Created: January 22, 2026*
*Owner: Claude Code (Autonomous)*
*Oversight: Ariel Shapira (20 min/day)*
