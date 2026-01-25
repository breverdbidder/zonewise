#!/usr/bin/env python3
"""
Brevard County LDC Ordinance Scraper
Scrapes zoning regulations from eLaws for all 56 zoning districts
"""

import json
import urllib.request
import urllib.parse
import ssl
import time
import re

# eLaws URL patterns for Brevard County Chapter 62, Article VI, Division 4
BASE_URL = "http://brevardcounty.elaws.us/code"

# Zoning section mappings (from eLaws structure)
ZONING_SECTIONS = {
    # SubDivision II - Unimproved, Agricultural and Residential
    "GU": {"section": "62-1305", "name": "General use"},
    "PA": {"section": "62-1310", "name": "Productive agricultural"},
    "AGR": {"section": "62-1315", "name": "Agricultural"},
    "AU": {"section": "62-1320", "name": "Agricultural residential"},
    "REU": {"section": "62-1325", "name": "Rural estate residential"},
    "RR-1": {"section": "62-1330", "name": "Rural residential"},
    "RRMH-1": {"section": "62-1331", "name": "Rural residential mobile home 1 acre"},
    "RRMH-2.5": {"section": "62-1332", "name": "Rural residential mobile home 2.5 acres"},
    "RRMH-5": {"section": "62-1333", "name": "Rural residential mobile home 5 acres"},
    "SEU": {"section": "62-1335", "name": "Suburban estate residential"},
    "SR": {"section": "62-1336", "name": "Suburban residential"},
    "RU-1-13": {"section": "62-1340", "name": "Single-family residential 13,000 sf"},
    "RU-1-11": {"section": "62-1340", "name": "Single-family residential 11,000 sf"},
    "RU-1-9": {"section": "62-1341", "name": "Single-family residential 9,000 sf"},
    "RU-1-7": {"section": "62-1342", "name": "Single-family residential 7,000 sf"},
    "RU-2-4": {"section": "62-1345", "name": "Multi-family 4 du/ac"},
    "RU-2-6": {"section": "62-1345", "name": "Multi-family 6 du/ac"},
    "RU-2-8": {"section": "62-1350", "name": "Multi-family 8 du/ac"},
    "RU-2-10": {"section": "62-1350", "name": "Multi-family 10 du/ac"},
    "RU-2-15": {"section": "62-1355", "name": "Multi-family 15 du/ac"},
    "RU-2-30": {"section": "62-1360", "name": "Multi-family 30 du/ac"},
    # SubDivision III - Commercial
    "BU-1": {"section": "62-1401", "name": "Retail commercial"},
    "BU-1-A": {"section": "62-1402", "name": "Retail commercial A"},
    "BU-2": {"section": "62-1405", "name": "General commercial"},
    # SubDivision IV - Tourist
    "TR-1": {"section": "62-1451", "name": "Tourist resort 1"},
    "TR-2": {"section": "62-1455", "name": "Tourist resort 2"},
    "TR-3": {"section": "62-1460", "name": "Tourist resort 3"},
    "TU-1": {"section": "62-1465", "name": "Tourist use 1"},
    "TU-2": {"section": "62-1470", "name": "Tourist use 2"},
    # SubDivision V - Industrial
    "IU": {"section": "62-1501", "name": "Industrial use"},
    "IU-1": {"section": "62-1505", "name": "Industrial use 1"},
    "IN(H)": {"section": "62-1510", "name": "Heavy industrial"},
    "IN(L)": {"section": "62-1515", "name": "Light industrial"},
    "PIP": {"section": "62-1520", "name": "Planned industrial park"},
    # SubDivision VI - Mixed Use
    "GML": {"section": "62-1530", "name": "General mixed use low"},
    "GML(H)": {"section": "62-1531", "name": "General mixed use low high"},
    "GML(I)": {"section": "62-1532", "name": "General mixed use low industrial"},
    "GML(P)": {"section": "62-1533", "name": "General mixed use low professional"},
    "GML(U)": {"section": "62-1534", "name": "General mixed use low urban"},
    # SubDivision IX - Special
    "PUD": {"section": "62-1561", "name": "Planned unit development"},
    "EA": {"section": "62-1571", "name": "Environmental area"},
    "RP": {"section": "62-1575", "name": "Recreation parks"},
    "RVP": {"section": "62-1580", "name": "Recreational vehicle park"},
}

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

FIRECRAWL_KEY = "fc-fa112951a2564765a2d146302774ac9b"

def scrape_section_firecrawl(section_id: str, zone_code: str) -> dict:
    """Scrape a section using Firecrawl"""
    url = f"{BASE_URL}/coorbrcoflvoii_ch62_artvi_div4_subdivii_sec{section_id}"
    
    # Try different subdivision paths based on zone type
    subdiv_map = {
        "BU": "subdiviii",   # Commercial
        "TR": "subdiviv",    # Tourist
        "TU": "subdiviv",    # Tourist
        "IU": "subdivv",     # Industrial
        "IN": "subdivv",     # Industrial
        "PIP": "subdivv",    # Industrial
        "GML": "subdivvi",   # Mixed Use
        "PUD": "subdivix",   # Special
        "EA": "subdivix",    # Special
        "RP": "subdivix",    # Special
        "RVP": "subdivix",   # Special
    }
    
    # Determine subdivision
    prefix = zone_code.split("-")[0].split("(")[0]
    subdiv = subdiv_map.get(prefix, "subdivii")  # Default to residential
    
    url = f"{BASE_URL}/coorbrcoflvoii_ch62_artvi_div4_{subdiv}_sec{section_id}"
    
    data = json.dumps({
        "url": url,
        "formats": ["markdown"],
        "onlyMainContent": True
    }).encode()
    
    req = urllib.request.Request(
        "https://api.firecrawl.dev/v1/scrape",
        data=data,
        headers={
            "Authorization": f"Bearer {FIRECRAWL_KEY}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    
    try:
        response = urllib.request.urlopen(req, context=ctx, timeout=60)
        result = json.loads(response.read().decode())
        
        if "data" in result:
            markdown = result["data"].get("markdown", "")
            return {
                "url": url,
                "content": markdown,
                "success": True
            }
        return {"url": url, "error": str(result), "success": False}
    except Exception as e:
        return {"url": url, "error": str(e), "success": False}

def extract_permitted_uses(markdown: str) -> list:
    """Extract permitted uses from markdown content"""
    uses = []
    in_permitted = False
    
    for line in markdown.split("\n"):
        line = line.strip()
        if "permitted use" in line.lower():
            in_permitted = True
            continue
        if in_permitted:
            if line.startswith("-") or line.startswith("*") or line.startswith("•"):
                use = line.lstrip("-*• ").strip()
                if use and len(use) > 3:
                    uses.append(use)
            elif "conditional" in line.lower() or "special exception" in line.lower():
                break
    
    return uses

def extract_conditional_uses(markdown: str) -> list:
    """Extract conditional uses from markdown content"""
    uses = []
    in_conditional = False
    
    for line in markdown.split("\n"):
        line = line.strip()
        if "conditional use" in line.lower() or "special exception" in line.lower():
            in_conditional = True
            continue
        if in_conditional:
            if line.startswith("-") or line.startswith("*") or line.startswith("•"):
                use = line.lstrip("-*• ").strip()
                if use and len(use) > 3:
                    uses.append(use)
            elif "dimensional" in line.lower() or "setback" in line.lower() or "height" in line.lower():
                break
    
    return uses

def main():
    print("=" * 70)
    print("BREVARD COUNTY ORDINANCE SCRAPER")
    print("Scraping zoning regulations from eLaws")
    print("=" * 70)
    
    # Get unique sections (some zones share sections)
    unique_sections = {}
    for zone, info in ZONING_SECTIONS.items():
        section = info["section"]
        if section not in unique_sections:
            unique_sections[section] = {"zones": [zone], "name": info["name"]}
        else:
            unique_sections[section]["zones"].append(zone)
    
    print(f"\nFound {len(unique_sections)} unique sections for {len(ZONING_SECTIONS)} zoning codes")
    
    ordinances = []
    
    # Scrape each unique section
    for section_id, info in list(unique_sections.items())[:5]:  # Limit to 5 for testing
        zones = info["zones"]
        print(f"\n  Scraping §{section_id} ({', '.join(zones)})...")
        
        result = scrape_section_firecrawl(section_id, zones[0])
        
        if result["success"]:
            content = result["content"]
            permitted = extract_permitted_uses(content)
            conditional = extract_conditional_uses(content)
            
            ordinance = {
                "section_id": section_id,
                "zone_codes": zones,
                "name": info["name"],
                "url": result["url"],
                "content_length": len(content),
                "permitted_uses_count": len(permitted),
                "conditional_uses_count": len(conditional),
                "permitted_uses": permitted[:10],  # First 10
                "conditional_uses": conditional[:10],
                "raw_content": content[:3000]  # First 3000 chars
            }
            ordinances.append(ordinance)
            
            print(f"    ✅ {len(content)} chars, {len(permitted)} permitted, {len(conditional)} conditional")
        else:
            print(f"    ❌ Error: {result.get('error', 'Unknown')[:50]}")
        
        time.sleep(1)  # Rate limit
    
    # Save results
    output = {
        "metadata": {
            "jurisdiction": "Unincorporated Brevard County",
            "jurisdiction_id": 17,
            "source": "Brevard County eLaws",
            "chapter": "62 - Land Development Regulations",
            "article": "VI - Zoning Regulations",
            "scraped_sections": len(ordinances),
            "total_sections": len(unique_sections)
        },
        "ordinances": ordinances
    }
    
    with open("/home/claude/brevard_ordinances.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")
    print(f"Scraped: {len(ordinances)}/{len(unique_sections)} sections")
    print(f"Saved to brevard_ordinances.json")
    
    return ordinances

if __name__ == "__main__":
    main()
