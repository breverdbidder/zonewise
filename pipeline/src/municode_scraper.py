"""
ZoneWise Municode Scraper
Uses Firecrawl API to scrape zoning ordinances from Municode
"""

import os
import json
import time
import httpx
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

# Firecrawl API configuration
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
FIRECRAWL_BASE_URL = "https://api.firecrawl.dev/v1"

@dataclass
class ScrapeResult:
    """Result from scraping a jurisdiction"""
    jurisdiction_id: int
    jurisdiction_name: str
    url: str
    success: bool
    content: Optional[str] = None
    markdown: Optional[str] = None
    error: Optional[str] = None
    scraped_at: Optional[str] = None
    

class MunicodeScraper:
    """Scraper for Municode zoning ordinances using Firecrawl"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or FIRECRAWL_API_KEY
        if not self.api_key:
            raise ValueError("FIRECRAWL_API_KEY environment variable not set")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.rate_limit_delay = 6  # seconds between requests (10/min limit)
        
    def scrape_url(self, url: str, wait_for_selector: str = None) -> Dict[str, Any]:
        """
        Scrape a single URL using Firecrawl
        
        Args:
            url: URL to scrape
            wait_for_selector: Optional CSS selector to wait for
            
        Returns:
            Firecrawl response dict
        """
        payload = {
            "url": url,
            "formats": ["markdown", "html"],
            "onlyMainContent": True,
            "waitFor": 5000,  # Wait 5s for JS rendering
        }
        
        if wait_for_selector:
            payload["waitForSelector"] = wait_for_selector
            
        try:
            with httpx.Client(timeout=120) as client:
                response = client.post(
                    f"{FIRECRAWL_BASE_URL}/scrape",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException:
            return {"success": False, "error": "Request timeout"}
        except httpx.HTTPStatusError as e:
            return {"success": False, "error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def crawl_zoning_article(self, base_url: str, max_pages: int = 50) -> Dict[str, Any]:
        """
        Crawl an entire zoning article using Firecrawl's crawl endpoint
        
        Args:
            base_url: Starting URL for the zoning article
            max_pages: Maximum pages to crawl
            
        Returns:
            Crawl job result
        """
        payload = {
            "url": base_url,
            "limit": max_pages,
            "scrapeOptions": {
                "formats": ["markdown"],
                "onlyMainContent": True
            }
        }
        
        try:
            with httpx.Client(timeout=30) as client:
                # Start crawl job
                response = client.post(
                    f"{FIRECRAWL_BASE_URL}/crawl",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                job_data = response.json()
                
                if not job_data.get("success"):
                    return job_data
                
                job_id = job_data.get("id")
                
                # Poll for completion
                return self._poll_crawl_job(job_id)
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _poll_crawl_job(self, job_id: str, max_wait: int = 300) -> Dict[str, Any]:
        """Poll crawl job until completion"""
        start_time = time.time()
        
        with httpx.Client(timeout=30) as client:
            while time.time() - start_time < max_wait:
                response = client.get(
                    f"{FIRECRAWL_BASE_URL}/crawl/{job_id}",
                    headers=self.headers
                )
                data = response.json()
                
                status = data.get("status")
                if status == "completed":
                    return data
                elif status == "failed":
                    return {"success": False, "error": data.get("error", "Crawl failed")}
                
                # Wait before polling again
                time.sleep(5)
        
        return {"success": False, "error": "Crawl timeout"}
    
    def scrape_jurisdiction(self, jurisdiction: Dict[str, Any]) -> ScrapeResult:
        """
        Scrape zoning data for a single jurisdiction
        
        Args:
            jurisdiction: Jurisdiction config dict
            
        Returns:
            ScrapeResult with content or error
        """
        jid = jurisdiction["id"]
        name = jurisdiction["name"]
        url = jurisdiction.get("zoning_article_url") or jurisdiction.get("municode_url")
        
        print(f"[{jid}] Scraping {name}: {url}")
        
        # Try elaws first if available (cleaner HTML)
        if jurisdiction.get("elaws_url"):
            result = self.scrape_url(jurisdiction["elaws_url"])
            if result.get("success"):
                return ScrapeResult(
                    jurisdiction_id=jid,
                    jurisdiction_name=name,
                    url=jurisdiction["elaws_url"],
                    success=True,
                    content=result.get("data", {}).get("html"),
                    markdown=result.get("data", {}).get("markdown"),
                    scraped_at=datetime.utcnow().isoformat()
                )
        
        # Fall back to Municode
        result = self.scrape_url(url, wait_for_selector=".chunk-content")
        
        if result.get("success"):
            return ScrapeResult(
                jurisdiction_id=jid,
                jurisdiction_name=name,
                url=url,
                success=True,
                content=result.get("data", {}).get("html"),
                markdown=result.get("data", {}).get("markdown"),
                scraped_at=datetime.utcnow().isoformat()
            )
        else:
            return ScrapeResult(
                jurisdiction_id=jid,
                jurisdiction_name=name,
                url=url,
                success=False,
                error=result.get("error", "Unknown error")
            )
    
    def scrape_all_jurisdictions(self, jurisdictions: List[Dict[str, Any]], 
                                  skip_complete: bool = True) -> List[ScrapeResult]:
        """
        Scrape all jurisdictions with rate limiting
        
        Args:
            jurisdictions: List of jurisdiction configs
            skip_complete: Skip jurisdictions marked as complete
            
        Returns:
            List of ScrapeResults
        """
        results = []
        
        # Sort by priority
        sorted_jurisdictions = sorted(jurisdictions, key=lambda x: x.get("priority", 99))
        
        for i, jurisdiction in enumerate(sorted_jurisdictions):
            # Skip complete jurisdictions
            if skip_complete and jurisdiction.get("status") == "complete":
                print(f"[{jurisdiction['id']}] Skipping {jurisdiction['name']} (already complete)")
                continue
            
            # Scrape
            result = self.scrape_jurisdiction(jurisdiction)
            results.append(result)
            
            if result.success:
                print(f"[{jurisdiction['id']}] ✅ Success: {len(result.markdown or '')} chars")
            else:
                print(f"[{jurisdiction['id']}] ❌ Failed: {result.error}")
            
            # Rate limit delay (except for last item)
            if i < len(sorted_jurisdictions) - 1:
                time.sleep(self.rate_limit_delay)
        
        return results


def load_config(config_path: str = "config/jurisdictions.json") -> Dict[str, Any]:
    """Load pipeline configuration"""
    with open(config_path, "r") as f:
        return json.load(f)


def save_scrape_results(results: List[ScrapeResult], output_dir: str = "data/scraped"):
    """Save scrape results to files"""
    os.makedirs(output_dir, exist_ok=True)
    
    for result in results:
        if result.success and result.markdown:
            filename = f"{result.jurisdiction_id:02d}_{result.jurisdiction_name.lower().replace(' ', '_')}.md"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, "w") as f:
                f.write(f"# {result.jurisdiction_name} Zoning Ordinance\n\n")
                f.write(f"Source: {result.url}\n")
                f.write(f"Scraped: {result.scraped_at}\n\n")
                f.write("---\n\n")
                f.write(result.markdown)
            
            print(f"Saved: {filepath}")


if __name__ == "__main__":
    # Load config
    config = load_config()
    
    # Initialize scraper
    scraper = MunicodeScraper()
    
    # Scrape all jurisdictions
    results = scraper.scrape_all_jurisdictions(config["jurisdictions"])
    
    # Save results
    save_scrape_results(results)
    
    # Summary
    success_count = sum(1 for r in results if r.success)
    print(f"\n{'='*50}")
    print(f"SCRAPING COMPLETE: {success_count}/{len(results)} successful")
