#!/usr/bin/env python3
"""
Cloudflare Bypass Scraper for ZoneWise
Uses Firecrawl with waitFor parameter to handle Cloudflare protection

Key: waitFor=12000-15000ms allows Cloudflare challenge to complete
"""

import json
import urllib.request
import ssl
import time
import re

FIRECRAWL_KEY = "fc-fa112951a2564765a2d146302774ac9b"
FIRECRAWL_URL = "https://api.firecrawl.dev/v1/scrape"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Brevard County is on MUNICODE (not American Legal)
# These URLs are verified working with Cloudflare bypass
BREVARD_ZONING_URLS = {
    # Main zoning chapters
    "ARTICLE_VI_ZONING": "https://library.municode.com/fl/brevard_county/codes/code_of_ordinances?nodeId=COORBRCOFLVOII_CH62LADERE_ARTVIZORE",
    "DIV3_CLASSIFICATIONS": "https://library.municode.com/fl/brevard_county/codes/code_of_ordinances?nodeId=COORBRCOFLVOII_CH62LADERE_ARTVIZORE_DIV3ZOMACLGE",
    "DIV1_GENERAL": "https://library.municode.com/fl/brevard_county/codes/code_of_ordinances?nodeId=COORBRCOFLVOII_CH62LADERE_ARTVIZORE_DIV1GE",
    # Subdivision II - Residential districts
    "SUBDIV_II_RESIDENTIAL": "https://library.municode.com/fl/brevard_county/codes/code_of_ordinances?nodeId=COORBRCOFLVOII_CH62LADERE_ARTVIZORE_DIV4RESPCLASSEC62-1302--62-1589.7_SUDIIUNAGRE",
    # Subdivision III - Commercial
    "SUBDIV_III_COMMERCIAL": "https://library.municode.com/fl/brevard_county/codes/code_of_ordinances?nodeId=COORBRCOFLVOII_CH62LADERE_ARTVIZORE_DIV4RESPCLASSEC62-1302--62-1589.7_SUDIIICO",
    # Subdivision IV - Tourist
    "SUBDIV_IV_TOURIST": "https://library.municode.com/fl/brevard_county/codes/code_of_ordinances?nodeId=COORBRCOFLVOII_CH62LADERE_ARTVIZORE_DIV4RESPCLASSEC62-1302--62-1589.7_SUDIVTO",
    # Subdivision V - Industrial
    "SUBDIV_V_INDUSTRIAL": "https://library.municode.com/fl/brevard_county/codes/code_of_ordinances?nodeId=COORBRCOFLVOII_CH62LADERE_ARTVIZORE_DIV4RESPCLASSEC62-1302--62-1589.7_SUDVIN",
    # Dimensional standards
    "DIV6_SUPPLEMENTAL": "https://library.municode.com/fl/brevard_county/codes/code_of_ordinances?nodeId=COORBRCOFLVOII_CH62LADERE_ARTVIZORE_DIV6SURE",
}

def firecrawl_with_cloudflare_bypass(url: str, wait_ms: int = 12000) -> dict:
    """
    Scrape URL using Firecrawl with Cloudflare bypass
    
    Key settings:
    - waitFor: 12000-15000ms to complete Cloudflare challenge
    - timeout: 90000ms for slow-loading pages
    - onlyMainContent: true to skip navigation/footers
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
        response = urllib.request.urlopen(req, context=ctx, timeout=120)
        result = json.loads(response.read().decode())
        
        if "data" in result:
            content = result["data"].get("markdown", "")
            # Check if we got past Cloudflare
            if "enable javascript" in content.lower() or "just a moment" in content.lower():
                return {"success": False, "error": "Cloudflare challenge not bypassed", "url": url}
            return {"success": True, "content": content, "url": url, "chars": len(content)}
        return {"success": False, "error": str(result), "url": url}
    except Exception as e:
        return {"success": False, "error": str(e), "url": url}

def extract_zone_details(content: str) -> dict:
    """Extract zoning details from scraped content"""
    data = {
        "zones": [],
        "sections": [],
        "permitted_uses": [],
        "conditional_uses": [],
        "dimensional_standards": {}
    }
    
    # Extract zone codes
    zone_patterns = [
        r'\b(RU-[12]-\d+)\b',
        r'\b(RR-\d+)\b', 
        r'\b(BU-[12](?:-A)?)\b',
        r'\b(TR-\d+)\b',
        r'\b(TU-\d+)\b',
        r'\b(IU(?:-\d+)?)\b',
        r'\b(IN\([HL]\))\b',
        r'\b(GU|AU|SR|SEU|REU|PUD|EA|RP|RVP|PIP|GML)\b',
        r'\b(RRMH-[\d.]+)\b',
        r'\b(RA-2-\d+)\b',
    ]
    
    all_zones = set()
    for pattern in zone_patterns:
        matches = re.findall(pattern, content, re.I)
        all_zones.update(matches)
    data["zones"] = sorted(list(all_zones))
    
    # Extract section numbers (62-XXXX)
    sections = re.findall(r'\b(62-\d{4})\b', content)
    data["sections"] = sorted(list(set(sections)))
    
    # Extract permitted uses
    permitted_match = re.search(r'[Pp]ermitted\s+uses?[:\.]?\s*(.*?)(?=[Cc]onditional|[Ss]pecial\s+exception|[Dd]imensional|[Ss]etback|\n\n\n)', content, re.S)
    if permitted_match:
        text = permitted_match.group(1)
        uses = re.findall(r'(?:^|\n)\s*[\-\*•\d\.]+\s*([^\n]+)', text)
        data["permitted_uses"] = [u.strip() for u in uses if len(u.strip()) > 10][:20]
    
    # Extract conditional uses
    conditional_match = re.search(r'[Cc]onditional\s+uses?[:\.]?\s*(.*?)(?=[Dd]imensional|[Ss]etback|[Hh]eight|\n\n\n)', content, re.S)
    if conditional_match:
        text = conditional_match.group(1)
        uses = re.findall(r'(?:^|\n)\s*[\-\*•\d\.]+\s*([^\n]+)', text)
        data["conditional_uses"] = [u.strip() for u in uses if len(u.strip()) > 10][:15]
    
    # Extract dimensional standards
    patterns = {
        "min_lot_sf": r'(?:[Mm]inimum\s+)?[Ll]ot\s+(?:size|area)[:\s]+(\d[\d,]+)\s*(?:sq|sf|square)',
        "front_setback": r'[Ff]ront\s+(?:yard|setback)[:\s]+(\d+)',
        "side_setback": r'[Ss]ide\s+(?:yard|setback)[:\s]+(\d+)',
        "rear_setback": r'[Rr]ear\s+(?:yard|setback)[:\s]+(\d+)',
        "max_height": r'(?:[Mm]aximum\s+)?[Hh]eight[:\s]+(\d+)\s*(?:feet|ft)',
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, content)
        if match:
            val = match.group(1).replace(",", "")
            data["dimensional_standards"][key] = int(val)
    
    return data

def main():
    print("=" * 70)
    print("CLOUDFLARE BYPASS SCRAPER - BREVARD COUNTY ZONING")
    print("Using Firecrawl waitFor=12000ms")
    print("=" * 70)
    
    all_results = []
    all_zones = set()
    all_sections = set()
    total_content = 0
    
    for name, url in BREVARD_ZONING_URLS.items():
        print(f"\n📍 {name}")
        print(f"   {url[:60]}...")
        
        result = firecrawl_with_cloudflare_bypass(url, wait_ms=12000)
        
        if result["success"]:
            chars = result["chars"]
            
            if chars < 2000:
                print(f"   ⚠️ Content too short ({chars} chars), retrying with 15000ms...")
                result = firecrawl_with_cloudflare_bypass(url, wait_ms=15000)
                chars = result.get("chars", 0)
            
            if result["success"] and chars > 2000:
                content = result["content"]
                total_content += chars
                
                data = extract_zone_details(content)
                all_zones.update(data["zones"])
                all_sections.update(data["sections"])
                
                all_results.append({
                    "section": name,
                    "url": url,
                    "chars": chars,
                    "zones": data["zones"],
                    "sections_found": data["sections"][:10],
                    "permitted_uses": data["permitted_uses"][:5],
                    "conditional_uses": data["conditional_uses"][:3],
                    "raw_sample": content[:2500]
                })
                
                print(f"   ✅ {chars:,} chars | {len(data['zones'])} zones | {len(data['sections'])} sections")
            else:
                print(f"   ❌ Failed after retry: {result.get('error', 'Unknown')[:50]}")
        else:
            print(f"   ❌ {result.get('error', 'Unknown')[:50]}")
        
        time.sleep(2)
    
    # Summary
    print("\n" + "=" * 70)
    print("CLOUDFLARE BYPASS RESULTS")
    print("=" * 70)
    print(f"\nTotal content scraped: {total_content:,} chars")
    print(f"Successful sections: {len(all_results)}/{len(BREVARD_ZONING_URLS)}")
    print(f"\nUnique zones found ({len(all_zones)}):")
    for zone in sorted(all_zones):
        print(f"   {zone}")
    print(f"\nSection references found: {len(all_sections)}")
    
    # Save
    output = {
        "metadata": {
            "source": "Municode - Brevard County FL",
            "method": "Firecrawl with Cloudflare bypass (waitFor=12000ms)",
            "total_chars": total_content,
            "zones_found": len(all_zones),
            "sections_found": len(all_sections)
        },
        "all_zones": sorted(list(all_zones)),
        "all_sections": sorted(list(all_sections)),
        "results": all_results
    }
    
    with open("/home/claude/cloudflare_bypass_results.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Saved to cloudflare_bypass_results.json")
    return output

if __name__ == "__main__":
    main()
