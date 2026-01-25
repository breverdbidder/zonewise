#!/usr/bin/env python3
"""
ZONEWISE MUNICODE SCRAPER - CLOUDFLARE BYPASS STANDARD
======================================================
Hardcoded method for scraping all 67 Florida counties from Municode.

KEY TECHNIQUE: Firecrawl waitFor=12000ms bypasses Cloudflare protection.

This is the CANONICAL scraper for ZoneWise. Use this pattern for ALL
Municode scraping operations.

Author: Claude AI Architect
Date: 2026-01-25
"""

import json
import urllib.request
import ssl
import time
import re
import base64
from datetime import datetime
from typing import Optional, Dict, List, Any

# ============================================================================
# HARDCODED CONFIGURATION - DO NOT CHANGE
# ============================================================================

FIRECRAWL_KEY = "fc-fa112951a2564765a2d146302774ac9b"
FIRECRAWL_URL = "https://api.firecrawl.dev/v1/scrape"

# Cloudflare bypass settings - PROVEN WORKING
CLOUDFLARE_WAIT_MS = 12000      # 12 seconds - minimum for Cloudflare
CLOUDFLARE_RETRY_WAIT_MS = 15000  # 15 seconds on retry
REQUEST_TIMEOUT = 120           # 2 minutes max
RATE_LIMIT_DELAY = 3.0          # 3 seconds between requests

# SSL context for all requests
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

# ============================================================================
# FLORIDA 67 COUNTIES - MUNICODE URL PATTERNS
# ============================================================================

# Standard Municode URL pattern:
# https://library.municode.com/fl/{county_slug}/codes/code_of_ordinances?nodeId={node_id}

FLORIDA_COUNTIES = {
    # Brevard County - VERIFIED WORKING
    "brevard_county": {
        "name": "Brevard County",
        "jurisdiction_id": 17,
        "slug": "brevard_county",
        "zoning_chapter": "Chapter 62",
        "urls": {
            "MAIN_ZONING": "https://library.municode.com/fl/brevard_county/codes/code_of_ordinances?nodeId=COORBRCOFLVOII_CH62LADERE_ARTVIZORE",
            "DIV3_CLASSIFICATIONS": "https://library.municode.com/fl/brevard_county/codes/code_of_ordinances?nodeId=COORBRCOFLVOII_CH62LADERE_ARTVIZORE_DIV3ZOMACLGE",
            "DIV1_GENERAL": "https://library.municode.com/fl/brevard_county/codes/code_of_ordinances?nodeId=COORBRCOFLVOII_CH62LADERE_ARTVIZORE_DIV1GE",
            "DIV6_SUPPLEMENTAL": "https://library.municode.com/fl/brevard_county/codes/code_of_ordinances?nodeId=COORBRCOFLVOII_CH62LADERE_ARTVIZORE_DIV6SURE",
        }
    },
    # Orange County
    "orange_county": {
        "name": "Orange County",
        "jurisdiction_id": None,  # To be assigned
        "slug": "orange_county",
        "zoning_chapter": "Chapter 38",
        "urls": {
            "MAIN_ZONING": "https://library.municode.com/fl/orange_county/codes/code_of_ordinances?nodeId=PTIIORCOCO_CH38ZO",
        }
    },
    # Hillsborough County
    "hillsborough_county": {
        "name": "Hillsborough County",
        "jurisdiction_id": None,
        "slug": "hillsborough_county",
        "zoning_chapter": "Part 6",
        "urls": {
            "MAIN_ZONING": "https://library.municode.com/fl/hillsborough_county/codes/land_development_code?nodeId=PT6ZODIRE",
        }
    },
    # Miami-Dade County
    "miami-dade_county": {
        "name": "Miami-Dade County",
        "jurisdiction_id": None,
        "slug": "miami-dade_county",
        "zoning_chapter": "Chapter 33",
        "urls": {
            "MAIN_ZONING": "https://library.municode.com/fl/miami_-_dade_county/codes/code_of_ordinances?nodeId=PTIIICOOR_CH33ZO",
        }
    },
    # Broward County
    "broward_county": {
        "name": "Broward County",
        "jurisdiction_id": None,
        "slug": "broward_county",
        "zoning_chapter": "Article X",
        "urls": {
            "MAIN_ZONING": "https://library.municode.com/fl/broward_county/codes/code_of_ordinances?nodeId=PTIICOOR_CH39LADECO_ARTXZODI",
        }
    },
    # Add remaining 62 counties as discovered...
}

# ============================================================================
# CLOUDFLARE BYPASS SCRAPER - CORE FUNCTION
# ============================================================================

def firecrawl_cloudflare_bypass(
    url: str, 
    wait_ms: int = CLOUDFLARE_WAIT_MS,
    retry_on_fail: bool = True
) -> Dict[str, Any]:
    """
    HARDCODED Cloudflare bypass using Firecrawl waitFor parameter.
    
    This is the STANDARD method for all Municode scraping.
    
    Args:
        url: Municode URL to scrape
        wait_ms: Milliseconds to wait for Cloudflare (default 12000)
        retry_on_fail: Retry with longer wait if first attempt fails
    
    Returns:
        Dict with keys: success, content, url, chars, error
    """
    payload = json.dumps({
        "url": url,
        "formats": ["markdown"],
        "onlyMainContent": True,
        "waitFor": wait_ms,
        "timeout": 90000,
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    }).encode()
    
    req = urllib.request.Request(
        FIRECRAWL_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {FIRECRAWL_KEY}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    
    try:
        response = urllib.request.urlopen(req, context=SSL_CTX, timeout=REQUEST_TIMEOUT)
        result = json.loads(response.read().decode())
        
        if "data" in result:
            content = result["data"].get("markdown", "")
            chars = len(content)
            
            # Verify we bypassed Cloudflare (content should be >2000 chars)
            if chars < 2000:
                if retry_on_fail:
                    # Retry with longer wait
                    time.sleep(2)
                    return firecrawl_cloudflare_bypass(
                        url, 
                        wait_ms=CLOUDFLARE_RETRY_WAIT_MS,
                        retry_on_fail=False
                    )
                return {
                    "success": False,
                    "error": f"Content too short ({chars} chars) - Cloudflare not bypassed",
                    "url": url,
                    "chars": chars
                }
            
            # Check for Cloudflare challenge page indicators
            cloudflare_indicators = [
                "enable javascript",
                "just a moment",
                "checking your browser",
                "ray id"
            ]
            content_lower = content.lower()
            for indicator in cloudflare_indicators:
                if indicator in content_lower:
                    if retry_on_fail:
                        time.sleep(2)
                        return firecrawl_cloudflare_bypass(
                            url,
                            wait_ms=CLOUDFLARE_RETRY_WAIT_MS,
                            retry_on_fail=False
                        )
                    return {
                        "success": False,
                        "error": "Cloudflare challenge page detected",
                        "url": url,
                        "chars": chars
                    }
            
            return {
                "success": True,
                "content": content,
                "url": url,
                "chars": chars
            }
        
        return {
            "success": False,
            "error": f"No data in response: {str(result)[:100]}",
            "url": url
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)[:200],
            "url": url
        }

# ============================================================================
# ZONE EXTRACTION PATTERNS
# ============================================================================

ZONE_PATTERNS = [
    # Residential
    r'\b(R-[1-5](?:-[A-Z])?)\b',           # R-1, R-1-A, R-2
    r'\b(RU-[12]-\d+)\b',                   # RU-1-7, RU-2-15
    r'\b(RS-[1-9])\b',                      # RS-1, RS-4
    r'\b(RM-[1-9]\d*)\b',                   # RM-1, RM-20
    r'\b(RR-\d+)\b',                        # RR-1
    r'\b(RRMH-[\d.]+)\b',                   # RRMH-1, RRMH-2.5
    r'\b(RA-2-\d+)\b',                      # RA-2-4
    r'\b(REU|SEU|SR)\b',                    # Estate/Suburban
    
    # Commercial
    r'\b(C-[1-5](?:-[A-Z])?)\b',           # C-1, C-2-A
    r'\b(BU-[12](?:-[A-Z])?)\b',           # BU-1, BU-2
    r'\b(CN|CG|CC|CBD)\b',                  # Commercial types
    r'\b(B-[1-5])\b',                       # B-1 through B-5
    
    # Industrial
    r'\b(I-[1-3])\b',                       # I-1, I-2
    r'\b(M-[1-3])\b',                       # M-1, M-2
    r'\b(IU(?:-\d+)?)\b',                   # IU, IU-1
    r'\b(IN\([HL]\))\b',                    # IN(H), IN(L)
    r'\b(PIP)\b',                           # Planned Industrial Park
    
    # Mixed Use / Special
    r'\b(MU-[1-5])\b',                      # MU-1
    r'\b(MXD|MXU)\b',                       # Mixed use
    r'\b(PUD|RPUD|CPUD)\b',                 # Planned Unit Development
    r'\b(TOD)\b',                           # Transit-Oriented
    
    # Agricultural / Rural
    r'\b(A-[1-5])\b',                       # A-1, A-2
    r'\b(AG(?:R)?)\b',                      # AG, AGR
    r'\b(AU)\b',                            # Agricultural Use
    
    # Tourist / Recreation
    r'\b(TR-[1-3])\b',                      # TR-1
    r'\b(TU-[1-2])\b',                      # TU-1
    r'\b(RVP|RTP)\b',                       # RV/Recreation Parks
    
    # Government / Conservation
    r'\b(GU|GC|GOV)\b',                     # Government Use
    r'\b(EA|CON|P)\b',                      # Environmental/Conservation/Parks
    r'\b(RP)\b',                            # Recreation Parks
    r'\b(GML(?:\([HIPU]\))?)\b',           # General Mixed Use Low
]

def extract_zones_from_content(content: str) -> List[str]:
    """Extract all zone codes from scraped content"""
    all_zones = set()
    for pattern in ZONE_PATTERNS:
        matches = re.findall(pattern, content, re.I)
        all_zones.update([m.upper() for m in matches])
    return sorted(list(all_zones))

def extract_sections_from_content(content: str) -> List[str]:
    """Extract section references (e.g., 62-1340)"""
    sections = re.findall(r'\b(\d{2}-\d{4}(?:\.\d+)?)\b', content)
    return sorted(list(set(sections)))

# ============================================================================
# COUNTY SCRAPER
# ============================================================================

def scrape_county(county_key: str, verbose: bool = True) -> Dict[str, Any]:
    """
    Scrape all zoning data for a single county.
    
    Uses hardcoded Cloudflare bypass method.
    """
    if county_key not in FLORIDA_COUNTIES:
        return {"success": False, "error": f"Unknown county: {county_key}"}
    
    county = FLORIDA_COUNTIES[county_key]
    
    if verbose:
        print(f"\n{'='*70}")
        print(f"SCRAPING: {county['name']}")
        print(f"Chapter: {county['zoning_chapter']}")
        print(f"{'='*70}")
    
    results = {
        "county": county["name"],
        "jurisdiction_id": county["jurisdiction_id"],
        "timestamp": datetime.now().isoformat(),
        "sections_scraped": [],
        "all_zones": [],
        "all_sections": [],
        "total_chars": 0
    }
    
    all_zones = set()
    all_sections = set()
    
    for section_name, url in county["urls"].items():
        if verbose:
            print(f"\n  📍 {section_name}")
        
        # Use hardcoded Cloudflare bypass
        result = firecrawl_cloudflare_bypass(url)
        
        if result["success"]:
            content = result["content"]
            chars = result["chars"]
            results["total_chars"] += chars
            
            # Extract data
            zones = extract_zones_from_content(content)
            sections = extract_sections_from_content(content)
            
            all_zones.update(zones)
            all_sections.update(sections)
            
            results["sections_scraped"].append({
                "name": section_name,
                "url": url,
                "chars": chars,
                "zones": zones,
                "sections": sections[:20],
                "sample": content[:3000]
            })
            
            if verbose:
                print(f"     ✅ {chars:,} chars | {len(zones)} zones | {len(sections)} sections")
        else:
            if verbose:
                print(f"     ❌ {result.get('error', 'Unknown')[:60]}")
        
        time.sleep(RATE_LIMIT_DELAY)
    
    results["all_zones"] = sorted(list(all_zones))
    results["all_sections"] = sorted(list(all_sections))
    
    return results

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """
    Main scraper - currently configured for Brevard County.
    Extend to all 67 counties as URLs are discovered.
    """
    print("=" * 70)
    print("ZONEWISE MUNICODE SCRAPER - CLOUDFLARE BYPASS STANDARD")
    print("=" * 70)
    print(f"\nMethod: Firecrawl waitFor={CLOUDFLARE_WAIT_MS}ms")
    print(f"Timeout: {REQUEST_TIMEOUT}s | Rate limit: {RATE_LIMIT_DELAY}s")
    print(f"Counties configured: {len(FLORIDA_COUNTIES)}")
    
    # Scrape Brevard County (verified working)
    results = scrape_county("brevard_county")
    
    # Summary
    print(f"\n{'='*70}")
    print("SCRAPE COMPLETE")
    print(f"{'='*70}")
    print(f"County: {results['county']}")
    print(f"Total content: {results['total_chars']:,} chars")
    print(f"Zones found: {len(results['all_zones'])}")
    print(f"Sections found: {len(results['all_sections'])}")
    print(f"\nZones: {results['all_zones']}")
    
    # Save
    output_file = "/home/claude/municode_scrape_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Saved to {output_file}")
    
    return results

if __name__ == "__main__":
    main()
