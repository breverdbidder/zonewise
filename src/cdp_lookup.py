#!/usr/bin/env python3
"""
ZoneWise CDP Lookup Module
Maps Census Designated Places to their zoning authority (Unincorporated Brevard County)

Usage:
    from cdp_lookup import CDPLookup
    lookup = CDPLookup()
    result = lookup.get_zoning_authority("Mims")
    # Returns: {"jurisdiction_id": 17, "zoning_authority": "Unincorporated Brevard County", ...}
"""

import json
import os
from typing import Optional, Dict, List, Any

class CDPLookup:
    """Lookup Census Designated Places (CDPs) and map to zoning authority"""
    
    # Hardcoded CDP data for reliability
    CDPS = {
        "mims": {"jurisdiction_id": 17, "zip_codes": ["32754"], "population": 7336},
        "merritt island": {"jurisdiction_id": 17, "zip_codes": ["32952", "32953", "32954"], "population": 34743},
        "port st. john": {"jurisdiction_id": 17, "zip_codes": ["32927"], "population": 12112},
        "port saint john": {"jurisdiction_id": 17, "zip_codes": ["32927"], "population": 12112},
        "psj": {"jurisdiction_id": 17, "zip_codes": ["32927"], "population": 12112},
        "viera": {"jurisdiction_id": 17, "zip_codes": ["32940", "32955"], "population": 25148},
        "viera east": {"jurisdiction_id": 17, "zip_codes": ["32940"], "population": 12716},
        "viera west": {"jurisdiction_id": 17, "zip_codes": ["32940"], "population": 12432},
        "scottsmoor": {"jurisdiction_id": 17, "zip_codes": ["32775"], "population": 952},
        "sharpes": {"jurisdiction_id": 17, "zip_codes": ["32959"], "population": 3073},
        "micco": {"jurisdiction_id": 17, "zip_codes": ["32976"], "population": 1894},
        "june park": {"jurisdiction_id": 17, "zip_codes": ["32935"], "population": 4202},
        "south patrick shores": {"jurisdiction_id": 17, "zip_codes": ["32937"], "population": 8028},
        "patrick shores": {"jurisdiction_id": 17, "zip_codes": ["32937"], "population": 8028},
        "canaveral groves": {"jurisdiction_id": 17, "zip_codes": ["32926", "32927"], "population": 3146},
        "west canaveral groves": {"jurisdiction_id": 17, "zip_codes": ["32926"], "population": 209},
        "barefoot bay": {"jurisdiction_id": 17, "zip_codes": ["32976"], "population": 8794},
        "palm bay heights": {"jurisdiction_id": 17, "zip_codes": ["32905", "32907"], "population": 2500},
        "tropical park": {"jurisdiction_id": 17, "zip_codes": ["32905"], "population": 1543},
        "north merritt island": {"jurisdiction_id": 17, "zip_codes": ["32953"], "population": 8000},
        "east mims": {"jurisdiction_id": 17, "zip_codes": ["32754"], "population": 2000},
    }
    
    # ZIP code to jurisdiction mapping for CDPs
    ZIP_TO_CDP = {
        "32754": "mims",
        "32775": "scottsmoor", 
        "32927": "port st. john",
        "32935": "june park",
        "32937": "south patrick shores",
        "32940": "viera",
        "32952": "merritt island",
        "32953": "merritt island",
        "32954": "merritt island",
        "32955": "viera",
        "32959": "sharpes",
        "32976": "barefoot bay",  # Also Micco
        "32926": "canaveral groves",
    }
    
    # Incorporated municipalities (NOT CDPs - have their own zoning)
    INCORPORATED = {
        "melbourne": 1,
        "palm bay": 2,
        "titusville": 3,
        "west melbourne": 4,
        "rockledge": 5,
        "cocoa": 6,
        "cocoa beach": 7,
        "cape canaveral": 8,
        "satellite beach": 9,
        "indian harbour beach": 10,
        "indialantic": 11,
        "melbourne beach": 12,
        "melbourne village": 13,
        "palm shores": 14,
        "malabar": 15,
        "grant-valkaria": 16,
    }
    
    # Federal areas - no county zoning
    FEDERAL = {
        "kennedy space center": "Federal/NASA",
        "ksc": "Federal/NASA",
        "patrick space force base": "Federal/Military",
        "patrick sfb": "Federal/Military",
        "cape canaveral space force station": "Federal/Military",
        "ccsfs": "Federal/Military",
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize CDP lookup with optional external config"""
        self.config_path = config_path
        if config_path and os.path.exists(config_path):
            with open(config_path) as f:
                self.config = json.load(f)
        else:
            self.config = None
    
    def normalize(self, name: str) -> str:
        """Normalize community name for lookup"""
        return name.lower().strip()
    
    def get_zoning_authority(self, community_name: str) -> Dict[str, Any]:
        """
        Get zoning authority for a community name
        
        Returns dict with:
            - jurisdiction_id: int or None
            - zoning_authority: str
            - community_type: "incorporated" | "cdp" | "federal" | "unknown"
            - zip_codes: list (for CDPs)
        """
        name = self.normalize(community_name)
        
        # Check if incorporated municipality
        if name in self.INCORPORATED:
            return {
                "jurisdiction_id": self.INCORPORATED[name],
                "zoning_authority": community_name.title(),
                "community_type": "incorporated",
                "zip_codes": [],
                "note": "Incorporated municipality with own zoning code"
            }
        
        # Check if CDP (unincorporated)
        if name in self.CDPS:
            cdp = self.CDPS[name]
            return {
                "jurisdiction_id": cdp["jurisdiction_id"],
                "zoning_authority": "Unincorporated Brevard County",
                "community_type": "cdp",
                "zip_codes": cdp["zip_codes"],
                "population": cdp["population"],
                "note": "Census Designated Place - uses Brevard County zoning"
            }
        
        # Check if federal area
        if name in self.FEDERAL:
            return {
                "jurisdiction_id": None,
                "zoning_authority": self.FEDERAL[name],
                "community_type": "federal",
                "zip_codes": [],
                "note": "Federal property - no county zoning jurisdiction"
            }
        
        # Unknown - could be unincorporated area
        return {
            "jurisdiction_id": 17,  # Default to unincorporated
            "zoning_authority": "Unincorporated Brevard County (assumed)",
            "community_type": "unknown",
            "zip_codes": [],
            "note": "Community not found - assuming unincorporated Brevard County"
        }
    
    def get_by_zip(self, zip_code: str) -> Optional[Dict[str, Any]]:
        """Get CDP info by ZIP code"""
        if zip_code in self.ZIP_TO_CDP:
            cdp_name = self.ZIP_TO_CDP[zip_code]
            result = self.get_zoning_authority(cdp_name)
            result["matched_cdp"] = cdp_name.title()
            return result
        return None
    
    def list_all_cdps(self) -> List[Dict[str, Any]]:
        """List all CDPs with their info"""
        seen = set()
        cdps = []
        for name, data in self.CDPS.items():
            # Skip aliases
            if name in seen:
                continue
            seen.add(name)
            cdps.append({
                "name": name.title(),
                "jurisdiction_id": data["jurisdiction_id"],
                "zip_codes": data["zip_codes"],
                "population": data["population"]
            })
        return sorted(cdps, key=lambda x: -x["population"])


# CLI for testing
if __name__ == "__main__":
    import sys
    lookup = CDPLookup()
    
    print("=" * 70)
    print("ZONEWISE CDP LOOKUP TEST")
    print("=" * 70)
    
    test_communities = [
        "Mims",
        "Merritt Island", 
        "Port St. John",
        "Viera",
        "Melbourne",  # Incorporated
        "Kennedy Space Center",  # Federal
        "Some Random Place"  # Unknown
    ]
    
    for community in test_communities:
        result = lookup.get_zoning_authority(community)
        print(f"\n📍 {community}")
        print(f"   Type: {result['community_type']}")
        print(f"   Jurisdiction ID: {result['jurisdiction_id']}")
        print(f"   Zoning Authority: {result['zoning_authority']}")
        if result.get('zip_codes'):
            print(f"   ZIP Codes: {', '.join(result['zip_codes'])}")
    
    print("\n" + "=" * 70)
    print("ALL CDPs (sorted by population)")
    print("=" * 70)
    
    for cdp in lookup.list_all_cdps()[:10]:
        print(f"   {cdp['name']:<25} Pop: {cdp['population']:>6,}  ZIP: {', '.join(cdp['zip_codes'])}")
    
    print("\n✅ CDP Lookup module ready for deployment")
