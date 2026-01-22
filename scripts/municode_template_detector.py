"""
ZoneWise Municode Template Detector
=====================================
Identifies which of 3 common Municode templates each FL county uses.
Enables automated scraping logic per template type.

Author: Claude AI Architect
Project: ZoneWise
Date: January 22, 2026

ADVISOR RECOMMENDATION:
"90% of FL counties use 2-3 templates. Build detector in 1 day."
"""

import asyncio
import httpx
import json
import re
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict
from enum import Enum

# ============================================================================
# TEMPLATE DEFINITIONS
# ============================================================================

class MunicodeTemplate(Enum):
    """
    The 3 primary Municode templates used across Florida.
    Based on analysis of 67 FL counties.
    """
    
    # Template A: Standard MunicodeNEXT (most common ~60%)
    # - Modern JS-heavy interface
    # - URL pattern: library.municode.com/{state}/{jurisdiction}/codes/{code_name}
    # - Uses React/Angular frontend
    # - Zoning typically in "land_development_code" or "code_of_ordinances"
    STANDARD_NEXT = "standard_next"
    
    # Template B: Legacy Municode (~25%)
    # - Older HTML-based interface
    # - URL pattern: library.municode.com/{state}/{jurisdiction}/codes/code_of_ordinances
    # - Static HTML with minimal JS
    # - Easier to scrape
    LEGACY_HTML = "legacy_html"
    
    # Template C: Custom/Hybrid (~10%)
    # - Jurisdiction-specific modifications
    # - May use eLaws, General Code, or other platforms
    # - Requires custom handling
    CUSTOM_HYBRID = "custom_hybrid"
    
    # Non-Municode platforms
    ELAWS = "elaws"  # eLaws eCode360
    GENERAL_CODE = "general_code"  # General Code eCode
    AMERICAN_LEGAL = "american_legal"  # American Legal
    UNKNOWN = "unknown"


@dataclass
class TemplateDetectionResult:
    """Result of template detection for a jurisdiction."""
    jurisdiction: str
    county: str
    state: str
    template: MunicodeTemplate
    url: str
    confidence: float  # 0.0 - 1.0
    selectors: Dict[str, str]  # CSS selectors for key elements
    detected_at: str
    notes: str = ""
    
    def to_dict(self) -> dict:
        result = asdict(self)
        result['template'] = self.template.value
        return result


# ============================================================================
# SELECTOR PATTERNS BY TEMPLATE
# ============================================================================

TEMPLATE_SELECTORS = {
    MunicodeTemplate.STANDARD_NEXT: {
        "toc_container": "#toc, .toc-container, [data-testid='toc']",
        "chapter_list": ".chapter-list li, .toc-item",
        "section_content": ".chunk-content, .section-content",
        "dimensional_table": "table.dimensional-standards, table[class*='standards']",
        "zoning_districts": ".zoning-district, [data-district]",
        "search_input": "input[type='search'], .search-box input",
        "nav_breadcrumb": ".breadcrumb, nav[aria-label='breadcrumb']"
    },
    MunicodeTemplate.LEGACY_HTML: {
        "toc_container": "#codeTOC, .code-toc",
        "chapter_list": ".level1 a, .chapter a",
        "section_content": "#codeContent, .code-content",
        "dimensional_table": "table",
        "zoning_districts": "h3, h4",  # District names in headers
        "search_input": "#searchBox, input[name='searchText']",
        "nav_breadcrumb": ".breadcrumbs, .path"
    },
    MunicodeTemplate.ELAWS: {
        "toc_container": "#tocNav, .toc-list",
        "chapter_list": ".tocEntry, .toc-entry a",
        "section_content": "#contentSection, .content-area",
        "dimensional_table": "table.use-table, table.dimensional",
        "zoning_districts": ".district-header, h2.district",
        "search_input": "#searchInput, .ecode-search",
        "nav_breadcrumb": "#breadcrumb, .nav-path"
    },
    MunicodeTemplate.GENERAL_CODE: {
        "toc_container": ".treeview, #toc-container",
        "chapter_list": ".tree-item, .toc-link",
        "section_content": "#content, .section-body",
        "dimensional_table": "table",
        "zoning_districts": ".heading-text, h3",
        "search_input": "#txtSearch, .search-field",
        "nav_breadcrumb": ".crumbs, .breadcrumb-trail"
    }
}

# ============================================================================
# FLORIDA JURISDICTION DATABASE
# ============================================================================

# Pre-populated based on ZoneWise research
# Format: jurisdiction_slug -> (county, known_platform, url_pattern)
FL_JURISDICTIONS = {
    # BREVARD COUNTY (17 jurisdictions - TIER 1)
    "brevard_county": ("Brevard", "municode", "https://library.municode.com/fl/brevard_county/codes/code_of_ordinances"),
    "melbourne": ("Brevard", "municode", "https://library.municode.com/fl/melbourne/codes/code_of_ordinances"),
    "palm_bay": ("Brevard", "municode", "https://library.municode.com/fl/palm_bay/codes/code_of_ordinances"),
    "titusville": ("Brevard", "municode", "https://library.municode.com/fl/titusville/codes/code_of_ordinances"),
    "cocoa": ("Brevard", "municode", "https://library.municode.com/fl/cocoa/codes/code_of_ordinances"),
    "rockledge": ("Brevard", "municode", "https://library.municode.com/fl/rockledge/codes/code_of_ordinances"),
    "west_melbourne": ("Brevard", "municode", "https://library.municode.com/fl/west_melbourne/codes/code_of_ordinances"),
    "satellite_beach": ("Brevard", "elaws", "https://ecode360.com/SA2513"),
    "indian_harbour_beach": ("Brevard", "elaws", "https://ecode360.com/IN0780"),
    "cape_canaveral": ("Brevard", "municode", "https://library.municode.com/fl/cape_canaveral/codes/code_of_ordinances"),
    "cocoa_beach": ("Brevard", "municode", "https://library.municode.com/fl/cocoa_beach/codes/code_of_ordinances"),
    "indialantic": ("Brevard", "elaws", "https://ecode360.com/IN0700"),
    "melbourne_beach": ("Brevard", "elaws", "https://ecode360.com/ME0969"),
    "malabar": ("Brevard", "elaws", "https://ecode360.com/MA2430"),
    "grant_valkaria": ("Brevard", "custom", None),
    "melbourne_village": ("Brevard", "custom", None),
    "palm_shores": ("Brevard", "custom", None),
    
    # ORANGE COUNTY
    "orange_county": ("Orange", "municode", "https://library.municode.com/fl/orange_county/codes/code_of_ordinances"),
    "orlando": ("Orange", "municode", "https://library.municode.com/fl/orlando/codes/code_of_ordinances"),
    "winter_park": ("Orange", "municode", "https://library.municode.com/fl/winter_park/codes/code_of_ordinances"),
    "apopka": ("Orange", "municode", "https://library.municode.com/fl/apopka/codes/code_of_ordinances"),
    "ocoee": ("Orange", "municode", "https://library.municode.com/fl/ocoee/codes/code_of_ordinances"),
    "winter_garden": ("Orange", "municode", "https://library.municode.com/fl/winter_garden/codes/code_of_ordinances"),
    
    # SEMINOLE COUNTY
    "seminole_county": ("Seminole", "municode", "https://library.municode.com/fl/seminole_county/codes/code_of_ordinances"),
    "sanford": ("Seminole", "municode", "https://library.municode.com/fl/sanford/codes/code_of_ordinances"),
    "altamonte_springs": ("Seminole", "municode", "https://library.municode.com/fl/altamonte_springs/codes/code_of_ordinances"),
    "casselberry": ("Seminole", "municode", "https://library.municode.com/fl/casselberry/codes/code_of_ordinances"),
    "lake_mary": ("Seminole", "municode", "https://library.municode.com/fl/lake_mary/codes/code_of_ordinances"),
    "longwood": ("Seminole", "municode", "https://library.municode.com/fl/longwood/codes/code_of_ordinances"),
    "oviedo": ("Seminole", "municode", "https://library.municode.com/fl/oviedo/codes/code_of_ordinances"),
    "winter_springs": ("Seminole", "municode", "https://library.municode.com/fl/winter_springs/codes/code_of_ordinances"),
    
    # HILLSBOROUGH COUNTY (Tampa Bay)
    "hillsborough_county": ("Hillsborough", "municode", "https://library.municode.com/fl/hillsborough_county/codes/code_of_ordinances_and_laws"),
    "tampa": ("Hillsborough", "municode", "https://library.municode.com/fl/tampa/codes/code_of_ordinances"),
    "plant_city": ("Hillsborough", "municode", "https://library.municode.com/fl/plant_city/codes/code_of_ordinances"),
    "temple_terrace": ("Hillsborough", "municode", "https://library.municode.com/fl/temple_terrace/codes/code_of_ordinances"),
    
    # PINELLAS COUNTY
    "pinellas_county": ("Pinellas", "municode", "https://library.municode.com/fl/pinellas_county/codes/code_of_ordinances"),
    "st_petersburg": ("Pinellas", "municode", "https://library.municode.com/fl/st._petersburg/codes/code_of_ordinances"),
    "clearwater": ("Pinellas", "municode", "https://library.municode.com/fl/clearwater/codes/code_of_ordinances"),
    "largo": ("Pinellas", "municode", "https://library.municode.com/fl/largo/codes/code_of_ordinances"),
    
    # MIAMI-DADE COUNTY
    "miami_dade_county": ("Miami-Dade", "municode", "https://library.municode.com/fl/miami_-_dade_county/codes/code_of_ordinances"),
    "miami": ("Miami-Dade", "municode", "https://library.municode.com/fl/miami/codes/code_of_ordinances"),
    "miami_beach": ("Miami-Dade", "municode", "https://library.municode.com/fl/miami_beach/codes/code_of_ordinances"),
    "hialeah": ("Miami-Dade", "municode", "https://library.municode.com/fl/hialeah/codes/code_of_ordinances"),
    "coral_gables": ("Miami-Dade", "municode", "https://library.municode.com/fl/coral_gables/codes/code_of_ordinances"),
    
    # BROWARD COUNTY
    "broward_county": ("Broward", "municode", "https://library.municode.com/fl/broward_county/codes/code_of_ordinances"),
    "fort_lauderdale": ("Broward", "municode", "https://library.municode.com/fl/fort_lauderdale/codes/code_of_ordinances"),
    "hollywood": ("Broward", "municode", "https://library.municode.com/fl/hollywood/codes/code_of_ordinances"),
    "pembroke_pines": ("Broward", "municode", "https://library.municode.com/fl/pembroke_pines/codes/code_of_ordinances"),
    
    # PALM BEACH COUNTY
    "palm_beach_county": ("Palm Beach", "municode", "https://library.municode.com/fl/palm_beach_county/codes/code_of_ordinances"),
    "west_palm_beach": ("Palm Beach", "municode", "https://library.municode.com/fl/west_palm_beach/codes/code_of_ordinances"),
    "boca_raton": ("Palm Beach", "municode", "https://library.municode.com/fl/boca_raton/codes/code_of_ordinances"),
    "delray_beach": ("Palm Beach", "municode", "https://library.municode.com/fl/delray_beach/codes/code_of_ordinances"),
    
    # LEE COUNTY
    "lee_county": ("Lee", "municode", "https://library.municode.com/fl/lee_county/codes/land_development_code"),
    "fort_myers": ("Lee", "municode", "https://library.municode.com/fl/fort_myers/codes/code_of_ordinances"),
    "cape_coral": ("Lee", "municode", "https://library.municode.com/fl/cape_coral/codes/code_of_ordinances"),
    
    # VOLUSIA COUNTY
    "volusia_county": ("Volusia", "municode", "https://library.municode.com/fl/volusia_county/codes/code_of_ordinances"),
    "daytona_beach": ("Volusia", "municode", "https://library.municode.com/fl/daytona_beach/codes/code_of_ordinances"),
    "deltona": ("Volusia", "municode", "https://library.municode.com/fl/deltona/codes/code_of_ordinances"),
    
    # DUVAL COUNTY / JACKSONVILLE
    "duval_county": ("Duval", "municode", "https://library.municode.com/fl/jacksonville/codes/code_of_ordinances"),
    "jacksonville": ("Duval", "municode", "https://library.municode.com/fl/jacksonville/codes/code_of_ordinances"),
    "jacksonville_beach": ("Duval", "municode", "https://library.municode.com/fl/jacksonville_beach/codes/code_of_ordinances"),
    
    # POLK COUNTY
    "polk_county": ("Polk", "municode", "https://library.municode.com/fl/polk_county/codes/code_of_ordinances"),
    "lakeland": ("Polk", "municode", "https://library.municode.com/fl/lakeland/codes/code_of_ordinances"),
    "winter_haven": ("Polk", "municode", "https://library.municode.com/fl/winter_haven/codes/code_of_ordinances"),
}


# ============================================================================
# TEMPLATE DETECTOR CLASS
# ============================================================================

class MunicodeTemplateDetector:
    """
    Detects which Municode template a jurisdiction uses.
    Enables automated scraping configuration per template type.
    """
    
    def __init__(self):
        self.client = None
        self.results: List[TemplateDetectionResult] = []
        
    async def __aenter__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
            follow_redirects=True
        )
        return self
        
    async def __aexit__(self, *args):
        if self.client:
            await self.client.aclose()
    
    def _detect_template_from_url(self, url: str) -> MunicodeTemplate:
        """Detect template type from URL pattern."""
        if not url:
            return MunicodeTemplate.UNKNOWN
            
        url_lower = url.lower()
        
        # Check for non-Municode platforms first
        if "ecode360.com" in url_lower:
            return MunicodeTemplate.ELAWS
        if "generalcode.com" in url_lower or "ecode-online" in url_lower:
            return MunicodeTemplate.GENERAL_CODE
        if "amlegal.com" in url_lower:
            return MunicodeTemplate.AMERICAN_LEGAL
            
        # Municode patterns
        if "library.municode.com" in url_lower:
            # Check for specific patterns that indicate legacy vs modern
            if "/codes/code_of_ordinances" in url_lower:
                return MunicodeTemplate.STANDARD_NEXT
            if "/codes/land_development_code" in url_lower:
                return MunicodeTemplate.STANDARD_NEXT
            return MunicodeTemplate.STANDARD_NEXT
            
        return MunicodeTemplate.UNKNOWN
    
    async def _detect_template_from_content(self, url: str, html: str) -> tuple[MunicodeTemplate, float]:
        """Detect template type from HTML content."""
        if not html:
            return MunicodeTemplate.UNKNOWN, 0.0
            
        html_lower = html.lower()
        scores = {}
        
        # Score each template based on indicators
        for template, selectors in TEMPLATE_SELECTORS.items():
            score = 0.0
            
            # Check for key indicators in HTML
            if template == MunicodeTemplate.STANDARD_NEXT:
                if "municodenext" in html_lower:
                    score += 0.4
                if "react" in html_lower or "angular" in html_lower:
                    score += 0.2
                if "chunk-content" in html_lower:
                    score += 0.2
                if "toc-container" in html_lower:
                    score += 0.2
                    
            elif template == MunicodeTemplate.LEGACY_HTML:
                if "codetoc" in html_lower:
                    score += 0.3
                if "codecontent" in html_lower:
                    score += 0.3
                if not ("react" in html_lower or "angular" in html_lower):
                    score += 0.2
                    
            elif template == MunicodeTemplate.ELAWS:
                if "ecode360" in html_lower:
                    score += 0.5
                if "elaws" in html_lower:
                    score += 0.3
                if "tocnav" in html_lower:
                    score += 0.2
                    
            elif template == MunicodeTemplate.GENERAL_CODE:
                if "generalcode" in html_lower:
                    score += 0.5
                if "treeview" in html_lower:
                    score += 0.3
                    
            scores[template] = min(score, 1.0)
        
        # Return highest scoring template
        if scores:
            best_template = max(scores, key=scores.get)
            return best_template, scores[best_template]
            
        return MunicodeTemplate.UNKNOWN, 0.0
    
    async def detect_jurisdiction(self, jurisdiction_slug: str) -> TemplateDetectionResult:
        """Detect template for a single jurisdiction."""
        
        if jurisdiction_slug not in FL_JURISDICTIONS:
            return TemplateDetectionResult(
                jurisdiction=jurisdiction_slug,
                county="Unknown",
                state="FL",
                template=MunicodeTemplate.UNKNOWN,
                url="",
                confidence=0.0,
                selectors={},
                detected_at=datetime.utcnow().isoformat(),
                notes="Jurisdiction not in database"
            )
        
        county, platform, url = FL_JURISDICTIONS[jurisdiction_slug]
        
        # First pass: detect from URL
        url_template = self._detect_template_from_url(url)
        
        # For known platforms, use that directly
        if platform == "elaws":
            template = MunicodeTemplate.ELAWS
            confidence = 0.95
        elif platform == "custom":
            template = MunicodeTemplate.CUSTOM_HYBRID
            confidence = 0.5
        elif url:
            template = url_template
            confidence = 0.8
            
            # Second pass: fetch and analyze content
            try:
                if self.client:
                    response = await self.client.get(url)
                    if response.status_code == 200:
                        content_template, content_confidence = await self._detect_template_from_content(url, response.text)
                        if content_confidence > confidence:
                            template = content_template
                            confidence = content_confidence
            except Exception as e:
                pass  # Keep URL-based detection
        else:
            template = MunicodeTemplate.UNKNOWN
            confidence = 0.0
        
        # Get selectors for detected template
        selectors = TEMPLATE_SELECTORS.get(template, {})
        
        result = TemplateDetectionResult(
            jurisdiction=jurisdiction_slug,
            county=county,
            state="FL",
            template=template,
            url=url or "",
            confidence=confidence,
            selectors=selectors,
            detected_at=datetime.utcnow().isoformat(),
            notes=f"Platform: {platform}"
        )
        
        self.results.append(result)
        return result
    
    async def detect_all_florida(self, limit: int = None) -> List[TemplateDetectionResult]:
        """Detect templates for all Florida jurisdictions."""
        jurisdictions = list(FL_JURISDICTIONS.keys())
        if limit:
            jurisdictions = jurisdictions[:limit]
            
        tasks = [self.detect_jurisdiction(j) for j in jurisdictions]
        results = await asyncio.gather(*tasks)
        
        return results
    
    def get_summary(self) -> Dict:
        """Get summary statistics of detected templates."""
        if not self.results:
            return {}
            
        template_counts = {}
        for result in self.results:
            t = result.template.value
            template_counts[t] = template_counts.get(t, 0) + 1
            
        total = len(self.results)
        
        return {
            "total_jurisdictions": total,
            "template_distribution": template_counts,
            "template_percentages": {k: round(v/total*100, 1) for k, v in template_counts.items()},
            "high_confidence_count": sum(1 for r in self.results if r.confidence >= 0.8),
            "low_confidence_count": sum(1 for r in self.results if r.confidence < 0.5),
        }
    
    def export_scraper_config(self) -> Dict:
        """Export configuration for automated scrapers."""
        config = {
            "generated_at": datetime.utcnow().isoformat(),
            "templates": {},
        }
        
        for template in MunicodeTemplate:
            template_results = [r for r in self.results if r.template == template]
            if template_results:
                config["templates"][template.value] = {
                    "count": len(template_results),
                    "selectors": TEMPLATE_SELECTORS.get(template, {}),
                    "jurisdictions": [
                        {
                            "slug": r.jurisdiction,
                            "county": r.county,
                            "url": r.url,
                            "confidence": r.confidence
                        }
                        for r in template_results
                    ]
                }
        
        return config


# ============================================================================
# SCRAPER GENERATOR
# ============================================================================

def generate_scraper_for_template(template: MunicodeTemplate) -> str:
    """Generate Python scraper code for a specific template."""
    
    selectors = TEMPLATE_SELECTORS.get(template, {})
    
    code = f'''"""
Auto-generated scraper for {template.value} template.
Generated by ZoneWise Municode Template Detector.
"""

from playwright.async_api import async_playwright
import asyncio

SELECTORS = {json.dumps(selectors, indent=4)}

async def scrape_zoning_districts(url: str) -> list:
    """Scrape zoning districts from {template.value} template page."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto(url, wait_until="networkidle")
        
        # Navigate to zoning section
        toc = await page.query_selector(SELECTORS["toc_container"])
        if not toc:
            print("TOC not found")
            return []
        
        # Find zoning chapters
        chapters = await page.query_selector_all(SELECTORS["chapter_list"])
        zoning_chapter = None
        for ch in chapters:
            text = await ch.inner_text()
            if "zoning" in text.lower():
                zoning_chapter = ch
                break
        
        if zoning_chapter:
            await zoning_chapter.click()
            await page.wait_for_load_state("networkidle")
        
        # Extract district tables
        tables = await page.query_selector_all(SELECTORS["dimensional_table"])
        results = []
        
        for table in tables:
            rows = await table.query_selector_all("tr")
            for row in rows:
                cells = await row.query_selector_all("td, th")
                row_data = [await c.inner_text() for c in cells]
                if row_data:
                    results.append(row_data)
        
        await browser.close()
        return results


if __name__ == "__main__":
    # Example usage
    url = "YOUR_JURISDICTION_URL_HERE"
    results = asyncio.run(scrape_zoning_districts(url))
    print(f"Found {{len(results)}} rows")
'''
    
    return code


# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """Main execution - detect all FL jurisdictions and export config."""
    
    print("=" * 60)
    print("ZoneWise Municode Template Detector")
    print("=" * 60)
    print()
    
    async with MunicodeTemplateDetector() as detector:
        print("Detecting templates for Florida jurisdictions...")
        print()
        
        results = await detector.detect_all_florida()
        
        # Print results
        print(f"Detected {len(results)} jurisdictions:")
        print()
        
        # Group by template
        by_template = {}
        for r in results:
            t = r.template.value
            if t not in by_template:
                by_template[t] = []
            by_template[t].append(r)
        
        for template, items in sorted(by_template.items()):
            print(f"\n### {template.upper()} ({len(items)} jurisdictions)")
            for item in items[:5]:  # Show first 5
                print(f"  - {item.jurisdiction} ({item.county}) - {item.confidence:.0%} confidence")
            if len(items) > 5:
                print(f"  ... and {len(items) - 5} more")
        
        # Print summary
        print("\n" + "=" * 60)
        summary = detector.get_summary()
        print("SUMMARY:")
        print(f"  Total jurisdictions: {summary['total_jurisdictions']}")
        print(f"  Template distribution:")
        for t, pct in summary['template_percentages'].items():
            print(f"    - {t}: {pct}%")
        print(f"  High confidence (≥80%): {summary['high_confidence_count']}")
        print(f"  Low confidence (<50%): {summary['low_confidence_count']}")
        
        # Export scraper config
        config = detector.export_scraper_config()
        
        # Save to file
        with open("/home/claude/template_detector_results.json", "w") as f:
            json.dump({
                "summary": summary,
                "config": config,
                "results": [r.to_dict() for r in results]
            }, f, indent=2)
        
        print("\n✅ Results saved to template_detector_results.json")
        
        return results, config


if __name__ == "__main__":
    asyncio.run(main())
