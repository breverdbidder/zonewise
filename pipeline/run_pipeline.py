#!/usr/bin/env python3
"""
ZoneWise Municode Pipeline
Main orchestrator for scraping, parsing, and ingesting zoning data

Usage:
    python run_pipeline.py                    # Run full pipeline
    python run_pipeline.py --scrape-only      # Only scrape
    python run_pipeline.py --parse-only       # Only parse (requires scraped data)
    python run_pipeline.py --ingest-only      # Only ingest (requires parsed data)
    python run_pipeline.py --jurisdiction 2   # Process single jurisdiction (Palm Bay)
    python run_pipeline.py --test             # Test mode with Palm Bay only

Environment Variables:
    FIRECRAWL_API_KEY     - Firecrawl API key for scraping
    SUPABASE_URL          - Supabase project URL
    SUPABASE_SERVICE_KEY  - Supabase service role key
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from municode_scraper import MunicodeScraper, ScrapeResult, save_scrape_results
from zoning_parser import ZoningParser, ZoningDistrict, parse_all_scraped_files
from supabase_ingest import SupabaseIngestor, ingest_from_dict


class ZoneWisePipeline:
    """Main pipeline orchestrator"""
    
    def __init__(self, config_path: str = "config/jurisdictions.json"):
        self.config_path = config_path
        self.config = self._load_config()
        
        # Output directories
        self.scraped_dir = Path("data/scraped")
        self.parsed_dir = Path("data/parsed")
        self.logs_dir = Path("logs")
        
        # Create directories
        for d in [self.scraped_dir, self.parsed_dir, self.logs_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        # Pipeline state
        self.scrape_results: List[ScrapeResult] = []
        self.parsed_districts: List[Dict] = []
        self.ingest_results: Dict[str, int] = {}
    
    def _load_config(self) -> Dict[str, Any]:
        """Load pipeline configuration"""
        with open(self.config_path, "r") as f:
            return json.load(f)
    
    def _save_config(self):
        """Save updated configuration"""
        with open(self.config_path, "w") as f:
            json.dump(self.config, f, indent=2)
    
    def _log(self, message: str, level: str = "INFO"):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def get_jurisdictions(self, jurisdiction_id: Optional[int] = None,
                          skip_complete: bool = True) -> List[Dict]:
        """Get jurisdictions to process"""
        jurisdictions = self.config["jurisdictions"]
        
        if jurisdiction_id:
            jurisdictions = [j for j in jurisdictions if j["id"] == jurisdiction_id]
        
        if skip_complete:
            jurisdictions = [j for j in jurisdictions if j.get("status") != "complete"]
        
        return sorted(jurisdictions, key=lambda x: x.get("priority", 99))
    
    def run_scrape(self, jurisdictions: List[Dict]) -> List[ScrapeResult]:
        """Run scraping phase"""
        self._log(f"Starting scrape for {len(jurisdictions)} jurisdictions")
        
        # Check for Firecrawl API key
        if not os.getenv("FIRECRAWL_API_KEY"):
            self._log("FIRECRAWL_API_KEY not set - using fallback scraper", "WARN")
            return self._run_fallback_scrape(jurisdictions)
        
        scraper = MunicodeScraper()
        results = scraper.scrape_all_jurisdictions(jurisdictions, skip_complete=False)
        
        # Save results
        save_scrape_results(results, str(self.scraped_dir))
        
        self.scrape_results = results
        return results
    
    def _run_fallback_scrape(self, jurisdictions: List[Dict]) -> List[ScrapeResult]:
        """Fallback scraper using httpx directly (no Firecrawl)"""
        import httpx
        import time
        
        results = []
        
        for j in jurisdictions:
            url = j.get("elaws_url") or j.get("zoning_article_url")
            self._log(f"Scraping {j['name']}: {url}")
            
            try:
                with httpx.Client(timeout=60, follow_redirects=True) as client:
                    response = client.get(url, headers={
                        "User-Agent": "ZoneWise/1.0 (Property Zoning Analysis)"
                    })
                    response.raise_for_status()
                    
                    result = ScrapeResult(
                        jurisdiction_id=j["id"],
                        jurisdiction_name=j["name"],
                        url=url,
                        success=True,
                        content=response.text,
                        markdown=response.text,  # Raw HTML as markdown for parsing
                        scraped_at=datetime.utcnow().isoformat()
                    )
                    
                    # Save to file
                    filename = f"{j['id']:02d}_{j['name'].lower().replace(' ', '_')}.md"
                    filepath = self.scraped_dir / filename
                    with open(filepath, "w") as f:
                        f.write(f"# {j['name']} Zoning Ordinance\n\n")
                        f.write(f"Source: {url}\n\n---\n\n")
                        f.write(response.text)
                    
                    self._log(f"  ✅ Saved {len(response.text)} chars")
                    
            except Exception as e:
                result = ScrapeResult(
                    jurisdiction_id=j["id"],
                    jurisdiction_name=j["name"],
                    url=url,
                    success=False,
                    error=str(e)
                )
                self._log(f"  ❌ Failed: {e}", "ERROR")
            
            results.append(result)
            time.sleep(2)  # Rate limit
        
        self.scrape_results = results
        return results
    
    def run_parse(self, jurisdictions: Optional[List[Dict]] = None) -> List[Dict]:
        """Run parsing phase"""
        parser = ZoningParser()
        all_districts = []
        
        # Get list of scraped files
        scraped_files = list(self.scraped_dir.glob("*.md"))
        self._log(f"Parsing {len(scraped_files)} scraped files")
        
        for filepath in sorted(scraped_files):
            # Extract jurisdiction ID from filename
            filename = filepath.stem
            parts = filename.split("_", 1)
            
            try:
                jid = int(parts[0])
                jname = parts[1].replace("_", " ").title() if len(parts) > 1 else "Unknown"
            except ValueError:
                continue
            
            # Skip if jurisdiction not in filter list
            if jurisdictions and not any(j["id"] == jid for j in jurisdictions):
                continue
            
            self._log(f"Parsing {jname} ({jid})")
            
            # Parse file
            districts = parser.parse_file(str(filepath), jid, jname)
            
            # Convert to dicts
            from dataclasses import asdict
            for d in districts:
                district_dict = asdict(d)
                district_dict = {k: v for k, v in district_dict.items() if v is not None}
                all_districts.append(district_dict)
        
        # Save parsed data
        output_file = self.parsed_dir / "all_districts.json"
        with open(output_file, "w") as f:
            json.dump(all_districts, f, indent=2)
        
        self._log(f"Parsed {len(all_districts)} districts total")
        self.parsed_districts = all_districts
        return all_districts
    
    def run_ingest(self, districts: Optional[List[Dict]] = None,
                   clear_first: bool = True) -> Dict[str, int]:
        """Run ingestion phase"""
        if districts is None:
            # Load from file
            parsed_file = self.parsed_dir / "all_districts.json"
            if not parsed_file.exists():
                self._log("No parsed data found - run parse first", "ERROR")
                return {"success": 0, "failed": 0, "skipped": 0}
            
            with open(parsed_file, "r") as f:
                districts = json.load(f)
        
        self._log(f"Ingesting {len(districts)} districts")
        
        try:
            ingestor = SupabaseIngestor()
            results = ingestor.insert_batch(districts, clear_first=clear_first)
            
            # Update config status for successful jurisdictions
            if results["success"] > 0:
                success_jids = set(d["jurisdiction_id"] for d in districts)
                for j in self.config["jurisdictions"]:
                    if j["id"] in success_jids:
                        j["status"] = "complete"
                self._save_config()
            
            self.ingest_results = results
            return results
            
        except Exception as e:
            self._log(f"Ingestion failed: {e}", "ERROR")
            return {"success": 0, "failed": len(districts), "skipped": 0}
    
    def run_full_pipeline(self, jurisdiction_id: Optional[int] = None,
                          skip_complete: bool = True) -> Dict[str, Any]:
        """Run full pipeline: scrape -> parse -> ingest"""
        start_time = datetime.now()
        
        self._log("="*60)
        self._log("ZONEWISE MUNICODE PIPELINE")
        self._log("="*60)
        
        # Get jurisdictions to process
        jurisdictions = self.get_jurisdictions(jurisdiction_id, skip_complete)
        
        if not jurisdictions:
            self._log("No jurisdictions to process")
            return {"status": "skipped", "reason": "No pending jurisdictions"}
        
        self._log(f"Processing {len(jurisdictions)} jurisdictions:")
        for j in jurisdictions:
            self._log(f"  - [{j['id']}] {j['name']} (priority {j.get('priority', 99)})")
        
        # Phase 1: Scrape
        self._log("\n" + "="*60)
        self._log("PHASE 1: SCRAPING")
        self._log("="*60)
        scrape_results = self.run_scrape(jurisdictions)
        scrape_success = sum(1 for r in scrape_results if r.success)
        self._log(f"Scraping complete: {scrape_success}/{len(scrape_results)} successful")
        
        # Phase 2: Parse
        self._log("\n" + "="*60)
        self._log("PHASE 2: PARSING")
        self._log("="*60)
        parsed_districts = self.run_parse(jurisdictions)
        self._log(f"Parsing complete: {len(parsed_districts)} districts extracted")
        
        # Phase 3: Ingest
        self._log("\n" + "="*60)
        self._log("PHASE 3: INGESTION")
        self._log("="*60)
        ingest_results = self.run_ingest(parsed_districts)
        
        # Summary
        duration = (datetime.now() - start_time).total_seconds()
        
        self._log("\n" + "="*60)
        self._log("PIPELINE COMPLETE")
        self._log("="*60)
        self._log(f"Duration: {duration:.1f} seconds")
        self._log(f"Scraped:  {scrape_success}/{len(jurisdictions)} jurisdictions")
        self._log(f"Parsed:   {len(parsed_districts)} districts")
        self._log(f"Ingested: {ingest_results.get('success', 0)} success, "
                 f"{ingest_results.get('failed', 0)} failed")
        
        return {
            "status": "complete",
            "duration_seconds": duration,
            "scrape_results": {
                "total": len(scrape_results),
                "success": scrape_success
            },
            "parse_results": {
                "districts": len(parsed_districts)
            },
            "ingest_results": ingest_results
        }


def main():
    parser = argparse.ArgumentParser(description="ZoneWise Municode Pipeline")
    parser.add_argument("--scrape-only", action="store_true", help="Only run scraping")
    parser.add_argument("--parse-only", action="store_true", help="Only run parsing")
    parser.add_argument("--ingest-only", action="store_true", help="Only run ingestion")
    parser.add_argument("--jurisdiction", "-j", type=int, help="Process single jurisdiction by ID")
    parser.add_argument("--all", action="store_true", help="Process all jurisdictions including complete")
    parser.add_argument("--test", action="store_true", help="Test mode with Palm Bay only")
    parser.add_argument("--config", default="config/jurisdictions.json", help="Config file path")
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = ZoneWisePipeline(args.config)
    
    # Test mode
    if args.test:
        args.jurisdiction = 2  # Palm Bay
    
    # Get jurisdictions
    skip_complete = not args.all
    jurisdictions = pipeline.get_jurisdictions(args.jurisdiction, skip_complete)
    
    # Run appropriate phase(s)
    if args.scrape_only:
        pipeline.run_scrape(jurisdictions)
    elif args.parse_only:
        pipeline.run_parse(jurisdictions)
    elif args.ingest_only:
        pipeline.run_ingest()
    else:
        # Full pipeline
        results = pipeline.run_full_pipeline(args.jurisdiction, skip_complete)
        
        # Save results log
        log_file = pipeline.logs_dir / f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_file, "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults saved to: {log_file}")


if __name__ == "__main__":
    main()
