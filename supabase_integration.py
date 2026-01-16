#!/usr/bin/env python3
"""
ZoneWise Supabase Integration
=============================

Store extracted zoning data in Supabase for persistence and change detection.
"""

import httpx
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import asdict
import os

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")


class ZoneWiseSupabase:
    """Supabase client for ZoneWise data"""
    
    def __init__(self, url: str = SUPABASE_URL, key: str = SUPABASE_KEY):
        self.url = url
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        self.client = httpx.Client(headers=self.headers, timeout=30)
    
    def upsert_districts(self, districts: List[Dict]) -> Dict[str, Any]:
        """Upsert zoning districts to Supabase"""
        if not districts:
            return {"status": "empty", "count": 0}
        
        # Prepare data for upsert
        records = []
        for d in districts:
            record = {
                "jurisdiction": d.get("jurisdiction"),
                "district_code": d.get("district_code"),
                "district_name": d.get("district_name"),
                "district_type": d.get("district_type"),
                "source_url": d.get("source_url"),
                "source_section": d.get("source_section"),
                "source_platform": d.get("source_platform"),
                "content_hash": d.get("content_hash"),
                "last_extracted": d.get("last_extracted"),
                # Dimensional standards
                "min_lot_area_sqft": d.get("min_lot_area_sqft"),
                "min_lot_width_ft": d.get("min_lot_width_ft"),
                "min_lot_depth_ft": d.get("min_lot_depth_ft"),
                "max_lot_coverage_pct": d.get("max_lot_coverage_pct"),
                "min_living_area_sqft": d.get("min_living_area_sqft"),
                "max_height_ft": d.get("max_height_ft"),
                "max_stories": d.get("max_stories"),
                "front_setback_ft": d.get("front_setback_ft"),
                "side_interior_setback_ft": d.get("side_interior_setback_ft"),
                "side_corner_setback_ft": d.get("side_corner_setback_ft"),
                "rear_setback_ft": d.get("rear_setback_ft"),
                "rear_alley_setback_ft": d.get("rear_alley_setback_ft"),
                "water_setback_ft": d.get("water_setback_ft"),
                "max_density_units_acre": d.get("max_density_units_acre"),
                "floor_area_ratio": d.get("floor_area_ratio"),
                "verified": d.get("verified", False),
                "notes": d.get("notes"),
            }
            records.append(record)
        
        try:
            resp = self.client.post(
                f"{self.url}/rest/v1/zonewise_districts",
                json=records,
                params={
                    "on_conflict": "jurisdiction,district_code"
                }
            )
            resp.raise_for_status()
            return {"status": "success", "count": len(records)}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def get_content_hashes(self) -> Dict[str, str]:
        """Get content hashes for all jurisdictions for change detection"""
        try:
            resp = self.client.get(
                f"{self.url}/rest/v1/zonewise_districts",
                params={
                    "select": "jurisdiction,content_hash",
                    "order": "last_extracted.desc"
                }
            )
            resp.raise_for_status()
            data = resp.json()
            
            # Return latest hash per jurisdiction
            hashes = {}
            for row in data:
                if row["jurisdiction"] not in hashes:
                    hashes[row["jurisdiction"]] = row["content_hash"]
            
            return hashes
        except Exception as e:
            print(f"Error getting hashes: {e}")
            return {}
    
    def log_extraction_run(self, results: Dict[str, int]) -> None:
        """Log an extraction run to insights table"""
        try:
            self.client.post(
                f"{self.url}/rest/v1/zonewise_extraction_log",
                json={
                    "run_timestamp": datetime.now().isoformat(),
                    "jurisdictions_processed": len(results),
                    "total_districts": sum(results.values()),
                    "results": results,
                }
            )
        except Exception as e:
            print(f"Error logging run: {e}")
    
    def close(self):
        self.client.close()


# SQL Schema for Supabase
ZONEWISE_SCHEMA = """
-- ZoneWise Zoning Districts Table
CREATE TABLE IF NOT EXISTS zonewise_districts (
    id BIGSERIAL PRIMARY KEY,
    jurisdiction TEXT NOT NULL,
    district_code TEXT NOT NULL,
    district_name TEXT,
    district_type TEXT,  -- residential, commercial, industrial, mixed
    
    -- Source info
    source_url TEXT,
    source_section TEXT,
    source_platform TEXT,  -- municode, elaws, american_legal
    content_hash TEXT,
    last_extracted TIMESTAMPTZ DEFAULT NOW(),
    
    -- Dimensional standards
    min_lot_area_sqft INTEGER,
    min_lot_width_ft INTEGER,
    min_lot_depth_ft INTEGER,
    max_lot_coverage_pct NUMERIC(5,2),
    min_living_area_sqft INTEGER,
    max_height_ft INTEGER,
    max_stories INTEGER,
    
    -- Setbacks
    front_setback_ft INTEGER,
    side_interior_setback_ft INTEGER,
    side_corner_setback_ft INTEGER,
    rear_setback_ft INTEGER,
    rear_alley_setback_ft INTEGER,
    water_setback_ft INTEGER,
    
    -- Additional
    max_density_units_acre NUMERIC(6,2),
    floor_area_ratio NUMERIC(4,2),
    parking_spaces_per_unit NUMERIC(4,2),
    open_space_pct NUMERIC(5,2),
    
    -- Metadata
    verified BOOLEAN DEFAULT FALSE,
    verification_date TIMESTAMPTZ,
    notes TEXT,
    
    -- Constraints
    UNIQUE(jurisdiction, district_code),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for common queries
CREATE INDEX IF NOT EXISTS idx_zonewise_jurisdiction ON zonewise_districts(jurisdiction);
CREATE INDEX IF NOT EXISTS idx_zonewise_district_type ON zonewise_districts(district_type);
CREATE INDEX IF NOT EXISTS idx_zonewise_content_hash ON zonewise_districts(content_hash);

-- Extraction log table
CREATE TABLE IF NOT EXISTS zonewise_extraction_log (
    id BIGSERIAL PRIMARY KEY,
    run_timestamp TIMESTAMPTZ DEFAULT NOW(),
    jurisdictions_processed INTEGER,
    total_districts INTEGER,
    results JSONB,
    changes_detected BOOLEAN DEFAULT FALSE
);

-- Enable RLS
ALTER TABLE zonewise_districts ENABLE ROW LEVEL SECURITY;
ALTER TABLE zonewise_extraction_log ENABLE ROW LEVEL SECURITY;

-- Policies (allow all for service role)
CREATE POLICY "Service role full access" ON zonewise_districts
    FOR ALL USING (true);
CREATE POLICY "Service role full access" ON zonewise_extraction_log
    FOR ALL USING (true);
"""

if __name__ == "__main__":
    print("ZoneWise Supabase Schema:")
    print("="*60)
    print(ZONEWISE_SCHEMA)
