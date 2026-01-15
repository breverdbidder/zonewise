"""
ZoneWise Supabase Ingestion
Batch insert parsed zoning districts into Supabase
"""

import os
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")


class SupabaseIngestor:
    """Batch ingest zoning districts into Supabase"""
    
    def __init__(self, url: str = None, key: str = None):
        self.url = url or SUPABASE_URL
        self.key = key or SUPABASE_SERVICE_KEY
        
        if not self.key:
            raise ValueError("SUPABASE_SERVICE_KEY environment variable not set")
        
        # Initialize Supabase client
        from supabase import create_client
        self.client = create_client(self.url, self.key)
        self.table = "zoning_districts"
    
    def clear_jurisdiction(self, jurisdiction_id: int) -> bool:
        """
        Clear existing districts for a jurisdiction
        
        Args:
            jurisdiction_id: ID of jurisdiction to clear
            
        Returns:
            True if successful
        """
        try:
            self.client.table(self.table) \
                .delete() \
                .eq("jurisdiction_id", jurisdiction_id) \
                .execute()
            print(f"Cleared existing districts for jurisdiction {jurisdiction_id}")
            return True
        except Exception as e:
            print(f"Error clearing jurisdiction {jurisdiction_id}: {e}")
            return False
    
    def insert_district(self, district: Dict[str, Any]) -> bool:
        """
        Insert a single district
        
        Args:
            district: District data dict
            
        Returns:
            True if successful
        """
        # Prepare record for Supabase
        record = {
            "jurisdiction_id": district["jurisdiction_id"],
            "code": district["code"],
            "name": district["name"],
            "category": district["category"],
            "description": district.get("description", ""),
            "ordinance_section": district.get("ordinance_section"),
            "effective_date": district.get("effective_date", "2024-01-01"),
        }
        
        # Add optional numeric fields if present
        for field in ["min_lot_size", "max_height", "max_lot_coverage", 
                      "front_setback", "side_setback", "rear_setback"]:
            if district.get(field):
                record[field] = district[field]
        
        try:
            self.client.table(self.table) \
                .insert(record) \
                .execute()
            return True
        except Exception as e:
            print(f"Error inserting {district['code']}: {e}")
            return False
    
    def insert_batch(self, districts: List[Dict[str, Any]], 
                     clear_first: bool = True) -> Dict[str, int]:
        """
        Batch insert districts
        
        Args:
            districts: List of district dicts
            clear_first: Clear existing data for affected jurisdictions first
            
        Returns:
            Dict with success/failure counts
        """
        results = {"success": 0, "failed": 0, "skipped": 0}
        
        # Group by jurisdiction
        by_jurisdiction = {}
        for d in districts:
            jid = d["jurisdiction_id"]
            if jid not in by_jurisdiction:
                by_jurisdiction[jid] = []
            by_jurisdiction[jid].append(d)
        
        print(f"Processing {len(districts)} districts across {len(by_jurisdiction)} jurisdictions")
        
        for jid, jur_districts in sorted(by_jurisdiction.items()):
            print(f"\n[{jid}] Processing {len(jur_districts)} districts...")
            
            # Clear existing data if requested
            if clear_first:
                if not self.clear_jurisdiction(jid):
                    print(f"[{jid}] Failed to clear - skipping jurisdiction")
                    results["skipped"] += len(jur_districts)
                    continue
            
            # Insert each district
            for district in jur_districts:
                if self.insert_district(district):
                    results["success"] += 1
                    print(f"  ✅ {district['code']}: {district['name']}")
                else:
                    results["failed"] += 1
                    print(f"  ❌ {district['code']}: Failed to insert")
        
        return results
    
    def verify_counts(self) -> Dict[int, int]:
        """Get district counts per jurisdiction"""
        try:
            response = self.client.table(self.table) \
                .select("jurisdiction_id") \
                .execute()
            
            from collections import Counter
            counts = Counter(r["jurisdiction_id"] for r in response.data)
            return dict(counts)
        except Exception as e:
            print(f"Error verifying counts: {e}")
            return {}


def ingest_from_file(filepath: str, clear_first: bool = True) -> Dict[str, int]:
    """
    Ingest districts from a JSON file
    
    Args:
        filepath: Path to JSON file with district data
        clear_first: Clear existing data first
        
    Returns:
        Results dict
    """
    # Load districts
    with open(filepath, "r") as f:
        districts = json.load(f)
    
    print(f"Loaded {len(districts)} districts from {filepath}")
    
    # Initialize ingestor
    ingestor = SupabaseIngestor()
    
    # Insert
    results = ingestor.insert_batch(districts, clear_first=clear_first)
    
    # Verify
    print("\nVerifying counts...")
    counts = ingestor.verify_counts()
    
    print("\nDistricts per jurisdiction:")
    for jid, count in sorted(counts.items()):
        print(f"  {jid}: {count} districts")
    
    return results


def ingest_from_dict(districts: List[Dict[str, Any]], 
                     clear_first: bool = True) -> Dict[str, int]:
    """
    Ingest districts from a list of dicts
    
    Args:
        districts: List of district dicts
        clear_first: Clear existing data first
        
    Returns:
        Results dict
    """
    ingestor = SupabaseIngestor()
    return ingestor.insert_batch(districts, clear_first=clear_first)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = "data/parsed/all_districts.json"
    
    results = ingest_from_file(filepath)
    
    print(f"\n{'='*50}")
    print(f"INGESTION COMPLETE")
    print(f"  Success: {results['success']}")
    print(f"  Failed:  {results['failed']}")
    print(f"  Skipped: {results['skipped']}")
