#!/usr/bin/env python3
"""
MUNICODE ORDINANCE MONITOR
Tracks all chapters, detects new ordinances, parses bonus/incentive tables
Surpasses Zoneomics and Gridics ordinance monitoring

Created: 2026-01-21
"""

import os
import re
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import requests
from bs4 import BeautifulSoup

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Firecrawl for JS-rendered content
FIRECRAWL_KEY = os.getenv("FIRECRAWL_API_KEY", "fc-fa112951a2564765a2d146302774ac9b")

# Brevard County jurisdictions with Municode URLs
JURISDICTIONS = {
    1: {"name": "Melbourne", "municode_slug": "melbourne", "state": "fl"},
    2: {"name": "Palm Bay", "municode_slug": "palm_bay", "state": "fl"},
    3: {"name": "Indian Harbour Beach", "municode_slug": "indian_harbour_beach", "state": "fl"},
    4: {"name": "Satellite Beach", "municode_slug": "satellite_beach", "state": "fl"},
    5: {"name": "Indialantic", "municode_slug": "indialantic", "state": "fl"},
    6: {"name": "Melbourne Beach", "municode_slug": "melbourne_beach", "state": "fl"},
    7: {"name": "West Melbourne", "municode_slug": "west_melbourne", "state": "fl"},
    8: {"name": "Cocoa", "municode_slug": "cocoa", "state": "fl"},
    9: {"name": "Cocoa Beach", "municode_slug": "cocoa_beach", "state": "fl"},
    10: {"name": "Rockledge", "municode_slug": "rockledge", "state": "fl"},
    11: {"name": "Titusville", "municode_slug": "titusville", "state": "fl"},
    12: {"name": "Cape Canaveral", "municode_slug": "cape_canaveral", "state": "fl"},
    13: {"name": "Brevard County", "municode_slug": "brevard_county", "state": "fl"},
    14: {"name": "Malabar", "municode_slug": "malabar", "state": "fl"},
    15: {"name": "Palm Shores", "municode_slug": "palm_shores", "state": "fl"},
    16: {"name": "Grant-Valkaria", "municode_slug": "grant-valkaria", "state": "fl"},
    17: {"name": "Melbourne Village", "municode_slug": "melbourne_village", "state": "fl"},
}

# Chapters to monitor (beyond just zoning)
CHAPTERS_TO_MONITOR = [
    "zoning",
    "land development",
    "subdivision",
    "development standards",
    "building",
    "planning",
    "comprehensive plan",
    "overlay",
    "historic",
    "environmental",
    "flood",
    "stormwater",
    "impact fees",
    "concurrency",
]


@dataclass
class Ordinance:
    """Represents a municipal ordinance"""
    jurisdiction_id: int
    ordinance_number: str
    title: str
    chapter: Optional[str]
    section: Optional[str]
    passed_date: str
    effective_date: Optional[str]
    summary: Optional[str]
    full_text: Optional[str]
    source_url: str
    content_hash: str  # For change detection


@dataclass
class DevelopmentBonus:
    """Represents a development bonus/incentive"""
    jurisdiction_id: int
    ordinance_id: Optional[int]
    program_name: str
    feature_name: str
    density_bonus: Optional[str]
    intensity_bonus: Optional[str]
    height_bonus: Optional[str]
    parking_reduction: Optional[str]
    other_bonus: Optional[str]
    conditions: str
    min_requirement: Optional[str]
    commitment_period: Optional[str]
    table_reference: Optional[str]
    source_url: str


class MunicodeClient:
    """Client for scraping Municode municipal codes"""
    
    BASE_URL = "https://library.municode.com"
    
    def __init__(self, use_firecrawl: bool = True):
        self.use_firecrawl = use_firecrawl
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "ZoneWise-Bot/2.0 (Municipal Code Research; contact@zonewise.ai)"
        })
    
    def get_jurisdiction_url(self, state: str, slug: str) -> str:
        """Build Municode URL for a jurisdiction"""
        return f"{self.BASE_URL}/{state}/{slug}/codes/code_of_ordinances"
    
    def fetch_page(self, url: str) -> str:
        """Fetch page content, using Firecrawl for JS rendering"""
        if self.use_firecrawl and FIRECRAWL_KEY:
            return self._fetch_with_firecrawl(url)
        else:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
    
    def _fetch_with_firecrawl(self, url: str) -> str:
        """Use Firecrawl API for JS-rendered content"""
        response = requests.post(
            "https://api.firecrawl.dev/v1/scrape",
            headers={"Authorization": f"Bearer {FIRECRAWL_KEY}"},
            json={
                "url": url,
                "formats": ["html", "markdown"],
                "waitFor": 3000,  # Wait for JS to render
            },
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        return data.get("data", {}).get("html", "")
    
    def get_table_of_contents(self, state: str, slug: str) -> List[Dict]:
        """Get all chapters/sections from a jurisdiction's code"""
        url = self.get_jurisdiction_url(state, slug)
        html = self.fetch_page(url)
        soup = BeautifulSoup(html, 'html.parser')
        
        chapters = []
        
        # Find TOC elements (Municode structure varies)
        toc_items = soup.select('.toc-item, .chapter-item, [data-chapter]')
        
        for item in toc_items:
            title = item.get_text(strip=True)
            link = item.find('a')
            href = link.get('href') if link else None
            
            # Check if this is a chapter we want to monitor
            title_lower = title.lower()
            is_relevant = any(kw in title_lower for kw in CHAPTERS_TO_MONITOR)
            
            chapters.append({
                "title": title,
                "url": f"{self.BASE_URL}{href}" if href else None,
                "is_relevant": is_relevant
            })
        
        return chapters
    
    def find_ordinances_in_text(self, text: str) -> List[Dict]:
        """Extract ordinance references from text"""
        patterns = [
            # Ord. 2024-33, passed 9-19-24
            r'(?:Ord\.?|Ordinance)\s*(?:No\.?)?\s*(\d{4}[-/]\d+)[,\s]+(?:passed|adopted)\s+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            # (Ord. 2024-33, passed 9-19-24)
            r'\((?:Ord\.?|Ordinance)\s*(?:No\.?)?\s*(\d{4}[-/]\d+)[,\s]+(?:passed|adopted)\s+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\)',
            # Ordinance 24-33
            r'(?:Ord\.?|Ordinance)\s*(?:No\.?)?\s*(\d{2,4}[-/]\d+)',
        ]
        
        ordinances = []
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                ord_num = match.group(1)
                passed_date = match.group(2) if len(match.groups()) > 1 else None
                ordinances.append({
                    "number": ord_num,
                    "passed_date": passed_date,
                    "raw_match": match.group(0)
                })
        
        return ordinances
    
    def parse_development_bonus_table(self, html: str) -> List[Dict]:
        """Parse development bonus tables like Table 173-8"""
        soup = BeautifulSoup(html, 'html.parser')
        bonuses = []
        
        # Find tables with bonus-related headers
        tables = soup.find_all('table')
        
        for table in tables:
            # Check if this looks like a bonus table
            headers = [th.get_text(strip=True).lower() for th in table.find_all('th')]
            
            is_bonus_table = any(h in ' '.join(headers) for h in [
                'bonus', 'density', 'intensity', 'height', 'incentive'
            ])
            
            if not is_bonus_table:
                continue
            
            # Parse rows
            rows = table.find_all('tr')[1:]  # Skip header
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) < 2:
                    continue
                
                # Extract data (structure varies by table)
                bonus_data = {
                    "feature_name": cells[0].get_text(strip=True) if len(cells) > 0 else None,
                    "density_bonus": cells[1].get_text(strip=True) if len(cells) > 1 else None,
                    "intensity_bonus": cells[2].get_text(strip=True) if len(cells) > 2 else None,
                    "height_bonus": cells[3].get_text(strip=True) if len(cells) > 3 else None,
                    "other_bonus": cells[4].get_text(strip=True) if len(cells) > 4 else None,
                    "conditions": cells[-1].get_text(strip=True) if len(cells) > 5 else None,
                }
                
                if bonus_data["feature_name"]:
                    bonuses.append(bonus_data)
        
        return bonuses


class SupabaseClient:
    """Client for Supabase operations"""
    
    def __init__(self):
        self.url = SUPABASE_URL
        self.key = SUPABASE_KEY
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
    
    def upsert_ordinance(self, ordinance: Ordinance) -> Dict:
        """Insert or update an ordinance"""
        data = asdict(ordinance)
        response = requests.post(
            f"{self.url}/rest/v1/ordinances",
            headers={**self.headers, "Prefer": "resolution=merge-duplicates"},
            json=data,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def upsert_development_bonus(self, bonus: DevelopmentBonus) -> Dict:
        """Insert or update a development bonus"""
        data = asdict(bonus)
        response = requests.post(
            f"{self.url}/rest/v1/development_bonuses",
            headers=self.headers,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def get_ordinance_by_hash(self, content_hash: str) -> Optional[Dict]:
        """Check if ordinance content already exists"""
        response = requests.get(
            f"{self.url}/rest/v1/ordinances",
            headers=self.headers,
            params={"content_hash": f"eq.{content_hash}"},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        return data[0] if data else None
    
    def log_scrape(self, jurisdiction_id: int, status: str, details: Dict):
        """Log scraping activity"""
        data = {
            "jurisdiction_id": jurisdiction_id,
            "municode_url": details.get("url", ""),
            "chapters_scraped": details.get("chapters", []),
            "ordinances_found": details.get("total", 0),
            "new_ordinances": details.get("new", 0),
            "amended_ordinances": details.get("amended", 0),
            "scrape_status": status,
            "error_message": details.get("error"),
            "started_at": details.get("started"),
            "completed_at": datetime.utcnow().isoformat(),
        }
        
        response = requests.post(
            f"{self.url}/rest/v1/municode_scrape_log",
            headers=self.headers,
            json=data,
            timeout=30
        )
        return response.status_code == 201


class OrdinanceMonitor:
    """Main orchestrator for ordinance monitoring"""
    
    def __init__(self):
        self.municode = MunicodeClient()
        self.supabase = SupabaseClient()
    
    def monitor_jurisdiction(self, jurisdiction_id: int) -> Dict:
        """Monitor a single jurisdiction for ordinance changes"""
        if jurisdiction_id not in JURISDICTIONS:
            return {"error": f"Unknown jurisdiction: {jurisdiction_id}"}
        
        jurisdiction = JURISDICTIONS[jurisdiction_id]
        started = datetime.utcnow().isoformat()
        
        print(f"\n{'='*60}")
        print(f"Monitoring: {jurisdiction['name']}")
        print(f"{'='*60}")
        
        results = {
            "jurisdiction": jurisdiction["name"],
            "started": started,
            "chapters": [],
            "ordinances_found": 0,
            "new_ordinances": 0,
            "bonuses_found": 0,
            "errors": []
        }
        
        try:
            # Get table of contents
            chapters = self.municode.get_table_of_contents(
                jurisdiction["state"], 
                jurisdiction["municode_slug"]
            )
            
            relevant_chapters = [c for c in chapters if c["is_relevant"]]
            print(f"Found {len(relevant_chapters)} relevant chapters to scan")
            
            for chapter in relevant_chapters:
                if not chapter["url"]:
                    continue
                    
                print(f"  Scanning: {chapter['title'][:50]}...")
                results["chapters"].append(chapter["title"])
                
                try:
                    # Fetch chapter content
                    html = self.municode.fetch_page(chapter["url"])
                    
                    # Find ordinance references
                    ordinances = self.municode.find_ordinances_in_text(html)
                    results["ordinances_found"] += len(ordinances)
                    
                    for ord_ref in ordinances:
                        # Create content hash for change detection
                        content_hash = hashlib.md5(
                            f"{jurisdiction_id}:{ord_ref['number']}:{html[:5000]}".encode()
                        ).hexdigest()
                        
                        # Check if this is new or changed
                        existing = self.supabase.get_ordinance_by_hash(content_hash)
                        if not existing:
                            results["new_ordinances"] += 1
                    
                    # Parse development bonus tables
                    bonuses = self.municode.parse_development_bonus_table(html)
                    results["bonuses_found"] += len(bonuses)
                    
                except Exception as e:
                    results["errors"].append(f"Chapter error: {str(e)}")
            
            # Log successful scrape
            self.supabase.log_scrape(jurisdiction_id, "success", {
                "url": self.municode.get_jurisdiction_url(
                    jurisdiction["state"], 
                    jurisdiction["municode_slug"]
                ),
                "chapters": results["chapters"],
                "total": results["ordinances_found"],
                "new": results["new_ordinances"],
                "started": started
            })
            
        except Exception as e:
            results["errors"].append(str(e))
            self.supabase.log_scrape(jurisdiction_id, "failed", {
                "error": str(e),
                "started": started
            })
        
        return results
    
    def monitor_all_jurisdictions(self) -> List[Dict]:
        """Monitor all Brevard County jurisdictions"""
        all_results = []
        
        for jid in JURISDICTIONS:
            results = self.monitor_jurisdiction(jid)
            all_results.append(results)
        
        return all_results


def main():
    """Main entry point"""
    print("=" * 70)
    print("ZONEWISE ORDINANCE MONITOR")
    print("Surpassing Zoneomics & Gridics")
    print("=" * 70)
    
    monitor = OrdinanceMonitor()
    
    # For testing, just do Palm Bay (jurisdiction_id=2)
    results = monitor.monitor_jurisdiction(2)
    
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
