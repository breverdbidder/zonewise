"""
ZoneWise Modal.com Parallel Scraper
====================================
10x parallel Playwright scraping using Modal.com serverless infrastructure.
Template-aware scraping based on Municode Template Detector results.

Author: Claude AI Architect
Project: ZoneWise
Date: January 22, 2026

ADVISOR RECOMMENDATION:
"Modal.com - 10x parallel Playwright - $200/mo, free tier available"
"""

import modal
import json
import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import os

# ============================================================================
# MODAL APP CONFIGURATION
# ============================================================================

app = modal.App("zonewise-municode-scraper")

# Playwright image with all browsers
playwright_image = modal.Image.debian_slim(python_version="3.11").run_commands(
    "apt-get update",
    "apt-get install -y wget gnupg",
    "pip install playwright httpx",
    "playwright install chromium",
    "playwright install-deps chromium",
).pip_install("supabase", "python-dotenv")


# ============================================================================
# TEMPLATE CONFIGURATIONS
# ============================================================================

TEMPLATE_CONFIGS = {
    "standard_next": {
        "name": "MunicodeNEXT (Standard)",
        "wait_strategy": "networkidle",
        "js_heavy": True,
        "selectors": {
            "toc_container": "#toc, .toc-container, [data-testid='toc']",
            "chapter_list": ".chapter-list li, .toc-item, .level1 a",
            "section_content": ".chunk-content, .section-content",
            "dimensional_table": "table",
            "zoning_header": "h2, h3, h4",
            "nav_breadcrumb": ".breadcrumb, nav[aria-label='breadcrumb']"
        },
        "zoning_keywords": ["zoning", "land development", "development code", "land use"],
        "district_patterns": [
            r"R-\d+",  # R-1, R-2, R-3
            r"C-\d+",  # C-1, C-2, C-3
            r"M-\d+",  # M-1, M-2
            r"PUD",
            r"A-\d+",  # Agricultural
            r"I-\d+",  # Industrial
        ]
    },
    "elaws": {
        "name": "eLaws eCode360",
        "wait_strategy": "domcontentloaded",
        "js_heavy": False,
        "selectors": {
            "toc_container": "#tocNav, .toc-list, #toc",
            "chapter_list": ".tocEntry a, .toc-entry a, .chapter-link",
            "section_content": "#contentSection, .content-area, .ecode-content",
            "dimensional_table": "table.use-table, table.dimensional, table",
            "zoning_header": ".district-header, h2.district, h2, h3",
            "nav_breadcrumb": "#breadcrumb, .nav-path"
        },
        "zoning_keywords": ["zoning", "land use", "district regulations"],
        "district_patterns": [
            r"R-\d+[A-Z]?",
            r"C-\d+[A-Z]?",
            r"[A-Z]{2,3}-\d+",
        ]
    },
    "legacy_html": {
        "name": "Municode Legacy HTML",
        "wait_strategy": "load",
        "js_heavy": False,
        "selectors": {
            "toc_container": "#codeTOC, .code-toc",
            "chapter_list": ".level1 a, .chapter a",
            "section_content": "#codeContent, .code-content",
            "dimensional_table": "table",
            "zoning_header": "h3, h4, .section-heading",
            "nav_breadcrumb": ".breadcrumbs, .path"
        },
        "zoning_keywords": ["zoning", "district", "land development"],
        "district_patterns": [
            r"[A-Z]-\d+",
            r"[A-Z]{2}-\d+",
        ]
    },
    "custom_hybrid": {
        "name": "Custom/Unknown Platform",
        "wait_strategy": "networkidle",
        "js_heavy": True,
        "selectors": {
            "toc_container": "nav, .toc, #toc, .sidebar",
            "chapter_list": "a[href*='zoning'], a[href*='code'], li a",
            "section_content": "main, .content, #content, article",
            "dimensional_table": "table",
            "zoning_header": "h1, h2, h3, h4",
            "nav_breadcrumb": ".breadcrumb, .crumbs"
        },
        "zoning_keywords": ["zoning", "ordinance", "code"],
        "district_patterns": [
            r"[A-Z]+-\d+",
        ]
    }
}


# ============================================================================
# SCRAPING RESULT DATACLASS
# ============================================================================

@dataclass
class ZoningDistrictResult:
    """Result for a single zoning district extraction."""
    jurisdiction: str
    county: str
    district_code: str
    district_name: str
    description: Optional[str] = None
    min_lot_size: Optional[str] = None
    max_height: Optional[str] = None
    max_density: Optional[str] = None
    front_setback: Optional[str] = None
    side_setback: Optional[str] = None
    rear_setback: Optional[str] = None
    lot_coverage: Optional[str] = None
    far: Optional[str] = None
    source_url: str = ""
    scraped_at: str = ""
    template_type: str = ""
    confidence: float = 0.0
    raw_data: Dict = None
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ScrapeJobResult:
    """Result for a complete scraping job."""
    jurisdiction: str
    county: str
    template_type: str
    url: str
    success: bool
    districts_found: int
    districts: List[Dict]
    errors: List[str]
    duration_seconds: float
    scraped_at: str


# ============================================================================
# MODAL FUNCTIONS
# ============================================================================

@app.function(
    image=playwright_image,
    timeout=300,  # 5 minute timeout per jurisdiction
    memory=2048,
    retries=2,
)
async def scrape_jurisdiction(
    jurisdiction: str,
    county: str,
    url: str,
    template_type: str = "standard_next"
) -> dict:
    """
    Scrape zoning districts from a single jurisdiction using Playwright.
    Template-aware scraping based on detected Municode template type.
    """
    from playwright.async_api import async_playwright
    import re
    import time
    
    start_time = time.time()
    config = TEMPLATE_CONFIGS.get(template_type, TEMPLATE_CONFIGS["standard_next"])
    selectors = config["selectors"]
    
    result = ScrapeJobResult(
        jurisdiction=jurisdiction,
        county=county,
        template_type=template_type,
        url=url,
        success=False,
        districts_found=0,
        districts=[],
        errors=[],
        duration_seconds=0,
        scraped_at=datetime.now(timezone.utc).isoformat()
    )
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                ]
            )
            
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080}
            )
            
            page = await context.new_page()
            
            # Navigate with appropriate wait strategy
            wait_until = config["wait_strategy"]
            await page.goto(url, wait_until=wait_until, timeout=60000)
            
            # Additional wait for JS-heavy sites
            if config["js_heavy"]:
                await page.wait_for_timeout(3000)
            
            # Find zoning section
            zoning_link = None
            for keyword in config["zoning_keywords"]:
                try:
                    links = await page.query_selector_all(f'a:has-text("{keyword}")')
                    if links:
                        zoning_link = links[0]
                        break
                except:
                    continue
            
            if zoning_link:
                try:
                    await zoning_link.click()
                    await page.wait_for_load_state(wait_until)
                    if config["js_heavy"]:
                        await page.wait_for_timeout(2000)
                except Exception as e:
                    result.errors.append(f"Failed to navigate to zoning: {str(e)}")
            
            # Extract tables
            tables = await page.query_selector_all(selectors["dimensional_table"])
            
            for table in tables:
                try:
                    rows = await table.query_selector_all("tr")
                    
                    headers = []
                    first_row = rows[0] if rows else None
                    if first_row:
                        header_cells = await first_row.query_selector_all("th, td")
                        headers = [await cell.inner_text() for cell in header_cells]
                    
                    for row in rows[1:]:  # Skip header row
                        cells = await row.query_selector_all("td")
                        if not cells:
                            continue
                            
                        cell_texts = [await cell.inner_text() for cell in cells]
                        
                        # Check if first cell looks like a district code
                        if cell_texts:
                            first_cell = cell_texts[0].strip()
                            is_district = any(
                                re.match(pattern, first_cell, re.IGNORECASE)
                                for pattern in config["district_patterns"]
                            )
                            
                            if is_district or "district" in first_cell.lower():
                                district = ZoningDistrictResult(
                                    jurisdiction=jurisdiction,
                                    county=county,
                                    district_code=first_cell,
                                    district_name=cell_texts[1] if len(cell_texts) > 1 else first_cell,
                                    source_url=url,
                                    scraped_at=datetime.now(timezone.utc).isoformat(),
                                    template_type=template_type,
                                    confidence=0.8,
                                    raw_data={"headers": headers, "values": cell_texts}
                                )
                                
                                # Try to map values to fields based on headers
                                for i, header in enumerate(headers):
                                    if i < len(cell_texts):
                                        header_lower = header.lower()
                                        value = cell_texts[i]
                                        
                                        if "lot" in header_lower and "size" in header_lower:
                                            district.min_lot_size = value
                                        elif "height" in header_lower:
                                            district.max_height = value
                                        elif "density" in header_lower:
                                            district.max_density = value
                                        elif "front" in header_lower and "setback" in header_lower:
                                            district.front_setback = value
                                        elif "side" in header_lower:
                                            district.side_setback = value
                                        elif "rear" in header_lower:
                                            district.rear_setback = value
                                        elif "coverage" in header_lower:
                                            district.lot_coverage = value
                                        elif "far" in header_lower or "floor area" in header_lower:
                                            district.far = value
                                
                                result.districts.append(district.to_dict())
                
                except Exception as e:
                    result.errors.append(f"Table extraction error: {str(e)}")
            
            # Also try extracting from headers/sections
            headers = await page.query_selector_all(selectors["zoning_header"])
            for header in headers:
                try:
                    text = await header.inner_text()
                    for pattern in config["district_patterns"]:
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match:
                            district_code = match.group()
                            # Check if we already have this district
                            if not any(d["district_code"] == district_code for d in result.districts):
                                district = ZoningDistrictResult(
                                    jurisdiction=jurisdiction,
                                    county=county,
                                    district_code=district_code,
                                    district_name=text.strip(),
                                    source_url=url,
                                    scraped_at=datetime.now(timezone.utc).isoformat(),
                                    template_type=template_type,
                                    confidence=0.6,
                                )
                                result.districts.append(district.to_dict())
                except:
                    continue
            
            await browser.close()
            
            result.success = True
            result.districts_found = len(result.districts)
    
    except Exception as e:
        result.errors.append(f"Scraping failed: {str(e)}")
    
    result.duration_seconds = round(time.time() - start_time, 2)
    
    return asdict(result)


@app.function(
    image=playwright_image,
    timeout=1800,  # 30 minute timeout for batch
    memory=1024,
)
async def scrape_batch(jurisdictions: List[dict]) -> List[dict]:
    """
    Scrape multiple jurisdictions in parallel using Modal's distributed compute.
    This is the 10x speedup the advisor recommended.
    """
    
    # Launch all scraping tasks in parallel
    futures = []
    for j in jurisdictions:
        future = scrape_jurisdiction.spawn(
            jurisdiction=j["jurisdiction"],
            county=j["county"],
            url=j["url"],
            template_type=j.get("template_type", "standard_next")
        )
        futures.append(future)
    
    # Gather results
    results = []
    for future in futures:
        try:
            result = await future.get.aio()
            results.append(result)
        except Exception as e:
            results.append({
                "jurisdiction": "unknown",
                "success": False,
                "errors": [str(e)]
            })
    
    return results


@app.function(
    image=playwright_image,
    timeout=3600,  # 1 hour for full Florida scrape
    memory=1024,
)
async def scrape_all_florida(template_config_path: str = None) -> dict:
    """
    Scrape all Florida jurisdictions using template-aware parallel processing.
    """
    
    # Load template detection results
    if template_config_path:
        with open(template_config_path) as f:
            config = json.load(f)
    else:
        # Default jurisdictions
        config = {
            "results": [
                {"jurisdiction": "melbourne", "county": "Brevard", "url": "https://library.municode.com/fl/melbourne/codes/code_of_ordinances", "template": "standard_next"},
                {"jurisdiction": "palm_bay", "county": "Brevard", "url": "https://library.municode.com/fl/palm_bay/codes/code_of_ordinances", "template": "standard_next"},
                {"jurisdiction": "satellite_beach", "county": "Brevard", "url": "https://ecode360.com/SA2513", "template": "elaws"},
            ]
        }
    
    jurisdictions = [
        {
            "jurisdiction": r["jurisdiction"],
            "county": r["county"],
            "url": r["url"],
            "template_type": r["template"]
        }
        for r in config.get("results", [])
        if r.get("url")
    ]
    
    # Batch into groups of 10 for parallel processing
    batch_size = 10
    all_results = []
    
    for i in range(0, len(jurisdictions), batch_size):
        batch = jurisdictions[i:i + batch_size]
        print(f"Processing batch {i//batch_size + 1} ({len(batch)} jurisdictions)")
        
        batch_results = await scrape_batch.remote.aio(batch)
        all_results.extend(batch_results)
    
    # Compile summary
    successful = sum(1 for r in all_results if r.get("success"))
    total_districts = sum(r.get("districts_found", 0) for r in all_results)
    
    summary = {
        "total_jurisdictions": len(jurisdictions),
        "successful_scrapes": successful,
        "failed_scrapes": len(jurisdictions) - successful,
        "total_districts_found": total_districts,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "results": all_results
    }
    
    return summary


# ============================================================================
# LOCAL ENTRYPOINT FOR TESTING
# ============================================================================

@app.local_entrypoint()
def main():
    """Local entrypoint for testing."""
    
    print("=" * 60)
    print("ZoneWise Modal.com Parallel Scraper")
    print("=" * 60)
    
    # Test with Brevard County jurisdictions
    test_jurisdictions = [
        {
            "jurisdiction": "melbourne",
            "county": "Brevard",
            "url": "https://library.municode.com/fl/melbourne/codes/code_of_ordinances",
            "template_type": "standard_next"
        },
        {
            "jurisdiction": "palm_bay",
            "county": "Brevard", 
            "url": "https://library.municode.com/fl/palm_bay/codes/code_of_ordinances",
            "template_type": "standard_next"
        },
        {
            "jurisdiction": "satellite_beach",
            "county": "Brevard",
            "url": "https://ecode360.com/SA2513",
            "template_type": "elaws"
        }
    ]
    
    print(f"\nTesting with {len(test_jurisdictions)} jurisdictions...")
    
    results = scrape_batch.remote(test_jurisdictions)
    
    print("\nResults:")
    for r in results:
        status = "✅" if r.get("success") else "❌"
        districts = r.get("districts_found", 0)
        errors = len(r.get("errors", []))
        duration = r.get("duration_seconds", 0)
        print(f"  {status} {r.get('jurisdiction', 'unknown')}: {districts} districts, {duration}s, {errors} errors")
    
    print("\nDone!")


# ============================================================================
# GITHUB ACTIONS INTEGRATION
# ============================================================================

def generate_github_workflow() -> str:
    """Generate GitHub Actions workflow for scheduled scraping."""
    
    workflow = '''name: ZoneWise Municode Scraper (Modal.com)

on:
  schedule:
    # Run daily at 3 AM EST (8 AM UTC)
    - cron: '0 8 * * *'
  workflow_dispatch:
    inputs:
      counties:
        description: 'Counties to scrape (comma-separated, or "all")'
        required: false
        default: 'brevard'
      template_type:
        description: 'Template type filter'
        required: false
        default: 'all'

env:
  MODAL_TOKEN_ID: ${{ secrets.MODAL_TOKEN_ID }}
  MODAL_TOKEN_SECRET: ${{ secrets.MODAL_TOKEN_SECRET }}
  SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
  SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}

jobs:
  scrape-municode:
    runs-on: ubuntu-latest
    timeout-minutes: 60

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install modal supabase

      - name: Run Modal scraper
        run: |
          modal run modal_template_scraper.py

      - name: Upload results to Supabase
        run: |
          python scripts/upload_scrape_results.py

      - name: Generate report
        run: |
          echo "## Scrape Report" >> $GITHUB_STEP_SUMMARY
          echo "- **Counties:** ${{ github.event.inputs.counties || 'brevard' }}" >> $GITHUB_STEP_SUMMARY
          echo "- **Timestamp:** $(date -u)" >> $GITHUB_STEP_SUMMARY
'''
    
    return workflow


if __name__ == "__main__":
    # Generate GitHub workflow
    workflow = generate_github_workflow()
    with open("/home/claude/zonewise_modal_workflow.yml", "w") as f:
        f.write(workflow)
    print("GitHub workflow generated: zonewise_modal_workflow.yml")
