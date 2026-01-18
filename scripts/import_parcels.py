#!/usr/bin/env python3
"""Import Brevard County Parcels"""
import httpx
import os
import sys
import time

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GIS_URL = "https://services7.arcgis.com/BDKC97XHbtyzbfkd/ArcGIS/rest/services/Brevard_County_Parcels/FeatureServer/0/query"
ZONING_URL = "https://gis.brevardfl.gov/gissrv/rest/services/Planning_Development/Zoning_WKID2881/MapServer/0/query"

def main():
    max_parcels = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
    client = httpx.Client(timeout=60, verify=False)
    
    print(f"Importing up to {max_parcels:,} parcels...")
    
    total = 0
    offset = 0
    batch_size = 500
    
    while total < max_parcels:
        # Fetch from GIS
        resp = client.get(GIS_URL, params={
            "where": "1=1",
            "outFields": "TaxAcct,Name,Acres,Township,Range,Section,SubMoniker,SubBlock,Lot",
            "returnGeometry": "true",
            "outSR": "3857",
            "resultOffset": offset,
            "resultRecordCount": batch_size,
            "f": "json"
        })
        
        data = resp.json()
        features = data.get("features", [])
        if not features:
            break
        
        parcels = []
        for f in features:
            attrs = f.get("attributes", {})
            account = str(attrs.get("TaxAcct", ""))
            if not account or account == "None":
                continue
            
            geom = f.get("geometry", {})
            cx = cy = None
            if geom and "rings" in geom and geom["rings"]:
                ring = geom["rings"][0]
                if ring:
                    cx = sum(p[0] for p in ring) / len(ring)
                    cy = sum(p[1] for p in ring) / len(ring)
            
            parcels.append({
                "account": account,
                "parcel_id": attrs.get("Name", ""),
                "acres": attrs.get("Acres"),
                "township": attrs.get("Township", ""),
                "range": attrs.get("Range", ""),
                "section": attrs.get("Section", ""),
                "subdivision": attrs.get("SubMoniker", ""),
                "block": attrs.get("SubBlock", ""),
                "lot": str(attrs.get("Lot", ""))[:50],
                "centroid_x": cx,
                "centroid_y": cy
            })
        
        if parcels:
            resp = client.post(
                f"{SUPABASE_URL}/rest/v1/parcels",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "resolution=merge-duplicates"
                },
                json=parcels
            )
            if resp.status_code in [200, 201]:
                total += len(parcels)
                print(f"  Imported: {total:,}")
        
        offset += batch_size
        time.sleep(0.3)
    
    print(f"\nComplete: {total:,} parcels imported")

if __name__ == "__main__":
    main()
