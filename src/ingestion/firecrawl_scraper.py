"""
ZoneWise Firecrawl Scraper
Scrapes municipal ordinances using Firecrawl API

Usage:
    from firecrawl_scraper import scrape_jurisdiction
    result = await scrape_jurisdiction('indian_harbour_beach')
"""

import httpx
import os
import json
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio

# Firecrawl API configuration
FIRECRAWL_API_KEY = os.environ.get('FIRECRAWL_API_KEY', 'fc-fa112951a2564765a2d146302774ac9b')
FIRECRAWL_BASE_URL = "https://api.firecrawl.dev/v1"

# Brevard County jurisdiction configurations
JURISDICTIONS = {
    'indian_harbour_beach': {
        'full_name': 'Indian Harbour Beach',
        'ordinance_url': 'https://library.municode.com/fl/indian_harbour_beach/codes/code_of_ordinances?nodeId=APXAZO',
        'parser_type': 'municode'
    },
    'melbourne': {
        'full_name': 'City of Melbourne',
        'ordinance_url': 'https://library.municode.com/fl/melbourne/codes/code_of_ordinances',
        'parser_type': 'municode'
    },
    'palm_bay': {
        'full_name': 'City of Palm Bay',
        'ordinance_url': 'https://library.municode.com/fl/palm_bay/codes/code_of_ordinances',
        'parser_type': 'municode'
    },
    'cocoa': {
        'full_name': 'City of Cocoa',
        'ordinance_url': 'https://library.municode.com/fl/cocoa/codes/code_of_ordinances',
        'parser_type': 'municode'
    },
    'cocoa_beach': {
        'full_name': 'City of Cocoa Beach',
        'ordinance_url': 'https://library.municode.com/fl/cocoa_beach/codes/code_of_ordinances',
        'parser_type': 'municode'
    },
    'rockledge': {
        'full_name': 'City of Rockledge',
        'ordinance_url': 'https://library.municode.com/fl/rockledge/codes/code_of_ordinances',
        'parser_type': 'municode'
    },
    'titusville': {
        'full_name': 'City of Titusville',
        'ordinance_url': 'https://library.municode.com/fl/titusville/codes/code_of_ordinances',
        'parser_type': 'municode'
    },
    'satellite_beach': {
        'full_name': 'City of Satellite Beach',
        'ordinance_url': 'https://library.municode.com/fl/satellite_beach/codes/code_of_ordinances',
        'parser_type': 'municode'
    },
    'west_melbourne': {
        'full_name': 'City of West Melbourne',
        'ordinance_url': 'https://library.municode.com/fl/west_melbourne/codes/code_of_ordinances',
        'parser_type': 'municode'
    },
    'cape_canaveral': {
        'full_name': 'City of Cape Canaveral',
        'ordinance_url': 'https://library.municode.com/fl/cape_canaveral/codes/code_of_ordinances',
        'parser_type': 'municode'
    },
    'malabar': {
        'full_name': 'Town of Malabar',
        'ordinance_url': 'https://library.municode.com/fl/malabar/codes/code_of_ordinances',
        'parser_type': 'municode'
    },
    'grant_valkaria': {
        'full_name': 'City of Grant-Valkaria',
        'ordinance_url': 'https://library.municode.com/fl/grant-valkaria/codes/code_of_ordinances',
        'parser_type': 'municode'
    },
    'indialantic': {
        'full_name': 'Town of Indialantic',
        'ordinance_url': 'https://library.municode.com/fl/indialantic/codes/code_of_ordinances',
        'parser_type': 'municode'
    },
    'melbourne_beach': {
        'full_name': 'Town of Melbourne Beach',
        'ordinance_url': 'https://library.municode.com/fl/melbourne_beach/codes/code_of_ordinances',
        'parser_type': 'municode'
    },
    'melbourne_village': {
        'full_name': 'Town of Melbourne Village',
        'ordinance_url': 'https://library.municode.com/fl/melbourne_village/codes/code_of_ordinances',
        'parser_type': 'municode'
    },
    'palm_shores': {
        'full_name': 'Town of Palm Shores',
        'ordinance_url': 'https://library.municode.com/fl/palm_shores/codes/code_of_ordinances',
        'parser_type': 'municode'
    },
    'brevard_county': {
        'full_name': 'Brevard County (Unincorporated)',
        'ordinance_url': 'https://library.municode.com/fl/brevard_county/codes/code_of_ordinances',
        'parser_type': 'municode'
    }
}


async def scrape_url(url: str, timeout: int = 60) -> Dict[str, Any]:
    """
    Scrape a single URL using Firecrawl API
    
    Args:
        url: URL to scrape
        timeout: Request timeout in seconds
        
    Returns:
        Dict with success, content, links, and metadata
    """
    headers = {
        "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "url": url,
        "formats": ["markdown", "links"],
        "onlyMainContent": True,
        "waitFor": 3000  # Wait for JS to render
    }
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            f"{FIRECRAWL_BASE_URL}/scrape",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'content': data.get('data', {}).get('markdown', ''),
                'links': data.get('data', {}).get('links', []),
                'metadata': {
                    'url': url,
                    'scraped_at': datetime.now().isoformat(),
                    'content_length': len(data.get('data', {}).get('markdown', ''))
                }
            }
        else:
            return {
                'success': False,
                'error': response.text,
                'status_code': response.status_code
            }


async def find_zoning_chapter(base_url: str) -> Optional[str]:
    """
    Find the zoning chapter URL from a Municode base URL
    
    Args:
        base_url: Base Municode ordinance URL
        
    Returns:
        URL of zoning chapter or None
    """
    result = await scrape_url(base_url)
    
    if not result['success']:
        return None
    
    links = result.get('links', [])
    
    # Look for zoning-related links
    zoning_keywords = ['ZO', 'ZONING', 'APXAZO', 'LAND', 'LADERE']
    
    for link in links:
        link_upper = link.upper()
        if any(kw in link_upper for kw in zoning_keywords):
            return link
    
    return None


async def scrape_jurisdiction(
    jurisdiction_id: str,
    include_subpages: bool = False
) -> Dict[str, Any]:
    """
    Scrape all zoning ordinance content for a jurisdiction
    
    Args:
        jurisdiction_id: Jurisdiction identifier (e.g., 'indian_harbour_beach')
        include_subpages: Whether to scrape linked subpages
        
    Returns:
        Dict with jurisdiction data, content, and metadata
    """
    if jurisdiction_id not in JURISDICTIONS:
        return {
            'success': False,
            'error': f'Unknown jurisdiction: {jurisdiction_id}'
        }
    
    config = JURISDICTIONS[jurisdiction_id]
    print(f"📄 Scraping {config['full_name']}...")
    
    # First, find the zoning chapter
    base_url = config['ordinance_url']
    
    # If URL already points to zoning appendix, use it directly
    if 'APXAZO' in base_url or 'ZO' in base_url:
        zoning_url = base_url
    else:
        zoning_url = await find_zoning_chapter(base_url)
        if not zoning_url:
            zoning_url = base_url  # Fallback to base
    
    print(f"   Zoning URL: {zoning_url}")
    
    # Scrape main content
    result = await scrape_url(zoning_url)
    
    if not result['success']:
        return {
            'success': False,
            'jurisdiction_id': jurisdiction_id,
            'error': result.get('error', 'Unknown error')
        }
    
    output = {
        'success': True,
        'jurisdiction_id': jurisdiction_id,
        'jurisdiction_name': config['full_name'],
        'ordinance_url': zoning_url,
        'content': result['content'],
        'content_length': len(result['content']),
        'links': result.get('links', []),
        'scraped_at': datetime.now().isoformat(),
        'subpages': []
    }
    
    # Optionally scrape subpages
    if include_subpages:
        subpage_links = [l for l in result.get('links', []) if 'nodeId' in l][:5]
        
        for link in subpage_links:
            print(f"   Scraping subpage: {link[:60]}...")
            subresult = await scrape_url(link)
            if subresult['success']:
                output['subpages'].append({
                    'url': link,
                    'content': subresult['content'],
                    'content_length': len(subresult['content'])
                })
            await asyncio.sleep(1)  # Rate limiting
    
    print(f"   ✅ Scraped {output['content_length']:,} chars")
    return output


async def scrape_all_jurisdictions(
    jurisdictions: Optional[list] = None
) -> Dict[str, Any]:
    """
    Scrape all Brevard County jurisdictions
    
    Args:
        jurisdictions: List of jurisdiction IDs to scrape (default: all)
        
    Returns:
        Dict with results for each jurisdiction
    """
    if jurisdictions is None:
        jurisdictions = list(JURISDICTIONS.keys())
    
    results = {}
    total = len(jurisdictions)
    
    print(f"🏛️ Scraping {total} jurisdictions...")
    print("=" * 60)
    
    for i, jid in enumerate(jurisdictions, 1):
        print(f"\n[{i}/{total}] {jid}")
        try:
            result = await scrape_jurisdiction(jid)
            results[jid] = result
        except Exception as e:
            results[jid] = {
                'success': False,
                'jurisdiction_id': jid,
                'error': str(e)
            }
        
        # Rate limiting between jurisdictions
        await asyncio.sleep(2)
    
    # Summary
    successful = sum(1 for r in results.values() if r.get('success'))
    print(f"\n{'=' * 60}")
    print(f"✅ Completed: {successful}/{total} jurisdictions scraped")
    
    return {
        'success': True,
        'total': total,
        'successful': successful,
        'results': results,
        'scraped_at': datetime.now().isoformat()
    }


# CLI interface
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        jurisdiction = sys.argv[1]
        result = asyncio.run(scrape_jurisdiction(jurisdiction))
    else:
        # Default: scrape IHB
        result = asyncio.run(scrape_jurisdiction('indian_harbour_beach'))
    
    print(json.dumps({k: v for k, v in result.items() if k != 'content'}, indent=2))
