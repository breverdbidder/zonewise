#!/usr/bin/env python3
"""
ZoneWise CDP Full Import Pipeline
Imports ALL parcels from 4 key CDPs with zoning assignment
Designed for GitHub Actions execution

Target: 80,777 parcels across Mims, Merritt Island, Port St. John, Viera
"""

import json
import urllib.request
import urllib.parse
import ssl
import time
import sys
from typing import Dict, List, Optional
from datetime import datetime

# Config
BCPAO_PARCEL_API = "https://gis.brevardfl.gov/gissrv/rest/services/Base_Map/Parcel_New_WKID2881/MapServer/5/query"
BCPAO_ZONING_API = "https://gis.brevardfl.gov/gissrv/rest/services/Planning_Development/Zoning_WKID2881/MapServer/0/query"
BATCH_SIZE = 500  # Records per API call
RATE_LIMIT_DELAY = 0.05  # 50ms between zoning queries

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# CDP definitions
CDPS = {
    "Mims": {"zips": ["32754"], "jurisdiction_id": 17, "priority": 1},
    "Merritt Island": {"zips": ["32952", "32953", "32954"], "jurisdiction_id": 17, "priority": 2},
    "Port St. John": {"zips": ["32927"], "jurisdiction_id": 17, "priority": 3},
    "Viera": {"zips": ["32940", "32955"], "jurisdiction_id": 17, "priority": 4},
}

def bcpao_query(url: str, params: dict) -> dict:
    """Execute BCPAO API query"""
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("User-Agent", "ZoneWise/1.0")
    try:
        response = urllib.request.urlopen(req, context=ctx, timeout=120)
        return json.loads(response.read().decode())
    except Exception as e:
        return {"error": str(e)}

def get_parcel_count(zip_code: str) -> int:
    """Get count of parcels in ZIP code"""
    result = bcpao_query(BCPAO_PARCEL_API, {
        "where": f"ZIP_CODE='{zip_code}'",
        "returnCountOnly": "true",
        "f": "json"
    })
    return result.get("count", 0)

def get_parcels_batch(zip_code: str, offset: int, limit: int = BATCH_SIZE) -> List[Dict]:
    """Get batch of parcels with geometry"""
    result = bcpao_query(BCPAO_PARCEL_API, {
        "where": f"ZIP_CODE='{zip_code}'",
        "outFields": "PARCEL_ID,STREET_NUMBER,STREET_NAME,STREET_TYPE,CITY,ZIP_CODE,OWNER_NAME1,USE_CODE,USE_CODE_DESCRIPTION,LIV_AREA,ACRES,BLDG_VALUE,LAND_VALUE,HOMESTEAD_VALUE",
        "returnGeometry": "true",
        "geometryPrecision": "2",
        "resultOffset": str(offset),
        "resultRecordCount": str(limit),
        "f": "json"
    })
    
    parcels = []
    if "features" in result:
        for f in result["features"]:
            attrs = f.get("attributes", {})
            geom = f.get("geometry", {})
            
            # Calculate centroid
            rings = geom.get("rings", [[]])
            centroid = None
            if rings and rings[0] and len(rings[0]) > 0:
                xs = [p[0] for p in rings[0]]
                ys = [p[1] for p in rings[0]]
                centroid = (sum(xs) / len(xs), sum(ys) / len(ys))
            
            parcels.append({
                "parcel_id": attrs.get("PARCEL_ID"),
                "address": f"{attrs.get('STREET_NUMBER', '')} {attrs.get('STREET_NAME', '')} {attrs.get('STREET_TYPE', '')}".strip(),
                "city": (attrs.get("CITY") or "").strip(),
                "zip_code": (attrs.get("ZIP_CODE") or "").strip(),
                "owner_name": attrs.get("OWNER_NAME1"),
                "use_code": attrs.get("USE_CODE"),
                "use_description": (attrs.get("USE_CODE_DESCRIPTION") or "").strip(),
                "living_area_sf": attrs.get("LIV_AREA"),
                "acres": attrs.get("ACRES"),
                "bldg_value": attrs.get("BLDG_VALUE"),
                "land_value": attrs.get("LAND_VALUE"),
                "homestead_value": attrs.get("HOMESTEAD_VALUE"),
                "centroid_x": centroid[0] if centroid else None,
                "centroid_y": centroid[1] if centroid else None,
            })
    
    return parcels

def get_zoning_at_point(x: float, y: float) -> Optional[str]:
    """Query zoning layer at point"""
    result = bcpao_query(BCPAO_ZONING_API, {
        "geometry": json.dumps({"x": x, "y": y, "spatialReference": {"wkid": 2881}}),
        "geometryType": "esriGeometryPoint",
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "ZONING",
        "returnGeometry": "false",
        "f": "json"
    })
    
    if "features" in result and len(result["features"]) > 0:
        zone = result["features"][0].get("attributes", {}).get("ZONING")
        return zone.strip() if zone else None
    return None

def process_cdp(cdp_name: str, max_parcels: int = None) -> Dict:
    """Process a CDP - import all parcels with zoning"""
    info = CDPS.get(cdp_name, {})
    zips = info.get("zips", [])
    
    print(f"\n{'='*60}")
    print(f"📍 {cdp_name}")
    print(f"{'='*60}")
    
    results = {
        "cdp": cdp_name,
        "jurisdiction_id": info.get("jurisdiction_id", 17),
        "zips": zips,
        "total_expected": 0,
        "imported": 0,
        "with_zoning": 0,
        "zoning_codes": {},
        "parcels": []
    }
    
    for zip_code in zips:
        count = get_parcel_count(zip_code)
        results["total_expected"] += count
        print(f"\n  ZIP {zip_code}: {count:,} parcels")
        
        # Limit if specified
        target = min(count, max_parcels) if max_parcels else count
        
        offset = 0
        while offset < target:
            batch = get_parcels_batch(zip_code, offset, BATCH_SIZE)
            if not batch:
                break
            
            for parcel in batch:
                # Add CDP info
                parcel["cdp_name"] = cdp_name
                parcel["jurisdiction_id"] = info.get("jurisdiction_id", 17)
                
                # Get zoning via spatial query
                if parcel["centroid_x"] and parcel["centroid_y"]:
                    zone_code = get_zoning_at_point(parcel["centroid_x"], parcel["centroid_y"])
                    parcel["zone_code"] = zone_code
                    
                    if zone_code:
                        results["with_zoning"] += 1
                        results["zoning_codes"][zone_code] = results["zoning_codes"].get(zone_code, 0) + 1
                    
                    time.sleep(RATE_LIMIT_DELAY)
                
                results["parcels"].append(parcel)
                results["imported"] += 1
            
            offset += len(batch)
            pct = (results["imported"] / target) * 100
            print(f"    Progress: {results['imported']:,}/{target:,} ({pct:.1f}%)", end='\r')
        
        print(f"    Completed: {results['imported']:,} parcels, {results['with_zoning']:,} with zoning")
    
    return results

def main():
    # Parse args
    max_per_cdp = int(sys.argv[1]) if len(sys.argv) > 1 else 100  # Default to 100 for testing
    
    print("=" * 60)
    print("ZONEWISE CDP FULL IMPORT PIPELINE")
    print(f"Mode: {'FULL' if max_per_cdp > 10000 else f'SAMPLE ({max_per_cdp} per CDP)'}")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 60)
    
    all_results = {}
    all_parcels = []
    
    for cdp_name in CDPS.keys():
        results = process_cdp(cdp_name, max_parcels=max_per_cdp)
        all_results[cdp_name] = {
            "total_expected": results["total_expected"],
            "imported": results["imported"],
            "with_zoning": results["with_zoning"],
            "zoning_codes": results["zoning_codes"]
        }
        all_parcels.extend(results["parcels"])
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    total_expected = sum(r["total_expected"] for r in all_results.values())
    total_imported = sum(r["imported"] for r in all_results.values())
    total_with_zone = sum(r["with_zoning"] for r in all_results.values())
    
    print(f"\n{'CDP':<20} {'Expected':>10} {'Imported':>10} {'With Zone':>10} {'%':>8}")
    print("-" * 60)
    for cdp, data in all_results.items():
        pct = (data["with_zoning"] / data["imported"] * 100) if data["imported"] > 0 else 0
        print(f"{cdp:<20} {data['total_expected']:>10,} {data['imported']:>10,} {data['with_zoning']:>10,} {pct:>7.1f}%")
    print("-" * 60)
    pct = (total_with_zone / total_imported * 100) if total_imported > 0 else 0
    print(f"{'TOTAL':<20} {total_expected:>10,} {total_imported:>10,} {total_with_zone:>10,} {pct:>7.1f}%")
    
    # Aggregate zoning codes
    all_zones = {}
    for data in all_results.values():
        for zone, count in data["zoning_codes"].items():
            all_zones[zone] = all_zones.get(zone, 0) + count
    
    print(f"\nZoning Codes Found: {len(all_zones)}")
    for zone, count in sorted(all_zones.items(), key=lambda x: -x[1])[:10]:
        print(f"  {zone:<15} {count:>6,} parcels")
    
    # Save results
    output = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "mode": "full" if max_per_cdp > 10000 else "sample",
            "max_per_cdp": max_per_cdp,
            "total_imported": total_imported,
            "total_with_zoning": total_with_zone,
            "success_rate": pct
        },
        "cdp_summary": all_results,
        "zoning_codes": all_zones,
        "parcels": all_parcels
    }
    
    with open("/home/claude/cdp_parcels_import.json", "w") as f:
        json.dump(output, f)
    
    print(f"\n✅ Saved {total_imported:,} parcels to cdp_parcels_import.json")
    print(f"Completed: {datetime.now().isoformat()}")
    
    return output

if __name__ == "__main__":
    main()
