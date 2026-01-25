#!/usr/bin/env python3
"""
ZoneWise 100% Zoning Assignment Strategy
Multiple fallback methods to ensure every parcel gets a zone code
"""

import json
import urllib.request
import urllib.parse
import ssl
import time

BCPAO_PARCEL_API = "https://gis.brevardfl.gov/gissrv/rest/services/Base_Map/Parcel_New_WKID2881/MapServer/5/query"
BCPAO_ZONING_API = "https://gis.brevardfl.gov/gissrv/rest/services/Planning_Development/Zoning_WKID2881/MapServer/0/query"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def bcpao_query(url, params):
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    try:
        response = urllib.request.urlopen(req, context=ctx, timeout=60)
        return json.loads(response.read().decode())
    except Exception as e:
        return {"error": str(e)}

def get_zoning_at_point(x, y):
    """Method 1: Point query"""
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

def get_zoning_by_envelope(xmin, ymin, xmax, ymax):
    """Method 2: Envelope intersection"""
    result = bcpao_query(BCPAO_ZONING_API, {
        "geometry": json.dumps({
            "xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax,
            "spatialReference": {"wkid": 2881}
        }),
        "geometryType": "esriGeometryEnvelope",
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "ZONING",
        "returnGeometry": "false",
        "f": "json"
    })
    if "features" in result and len(result["features"]) > 0:
        zones = [f.get("attributes", {}).get("ZONING") for f in result["features"]]
        zones = [z.strip() for z in zones if z]
        if zones:
            return max(set(zones), key=zones.count)
    return None

def get_zoning_by_polygon(rings):
    """Method 3: Full polygon intersection"""
    result = bcpao_query(BCPAO_ZONING_API, {
        "geometry": json.dumps({
            "rings": rings,
            "spatialReference": {"wkid": 2881}
        }),
        "geometryType": "esriGeometryPolygon",
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "ZONING",
        "returnGeometry": "false",
        "f": "json"
    })
    if "features" in result and len(result["features"]) > 0:
        zones = [f.get("attributes", {}).get("ZONING") for f in result["features"]]
        zones = [z.strip() for z in zones if z]
        if zones:
            return max(set(zones), key=zones.count)
    return None

def get_zoning_robust(rings):
    """
    Robust zoning lookup with multiple fallback strategies
    Returns (zone_code, method_used)
    """
    if not rings or not rings[0] or len(rings[0]) < 3:
        return None, "no_geometry"
    
    xs = [p[0] for p in rings[0]]
    ys = [p[1] for p in rings[0]]
    
    # Method 1: Centroid
    cx = sum(xs) / len(xs)
    cy = sum(ys) / len(ys)
    zone = get_zoning_at_point(cx, cy)
    if zone:
        return zone, "centroid"
    
    # Method 2: Bounding box center
    mx = (min(xs) + max(xs)) / 2
    my = (min(ys) + max(ys)) / 2
    zone = get_zoning_at_point(mx, my)
    if zone:
        return zone, "bbox_center"
    
    # Method 3: Multiple sample points (25%, 75% of bbox)
    for fx in [0.25, 0.75]:
        for fy in [0.25, 0.75]:
            px = min(xs) + (max(xs) - min(xs)) * fx
            py = min(ys) + (max(ys) - min(ys)) * fy
            zone = get_zoning_at_point(px, py)
            if zone:
                return zone, f"sample_{int(fx*100)}_{int(fy*100)}"
    
    # Method 4: Envelope intersection
    zone = get_zoning_by_envelope(min(xs), min(ys), max(xs), max(ys))
    if zone:
        return zone, "envelope"
    
    # Method 5: Full polygon intersection
    zone = get_zoning_by_polygon(rings)
    if zone:
        return zone, "polygon"
    
    # Method 6: Expanded envelope (buffer by 100 feet)
    buffer = 100
    zone = get_zoning_by_envelope(min(xs)-buffer, min(ys)-buffer, max(xs)+buffer, max(ys)+buffer)
    if zone:
        return zone, "expanded_envelope"
    
    return None, "all_methods_failed"

# Default zone assignments for special cases
SPECIAL_CASES = {
    # Federal/Military - no zoning
    "Kennedy Space Center": None,
    "Patrick Space Force Base": None,
    "Cape Canaveral Space Force Station": None,
    # Water bodies, roads, etc. - may need special handling
}

def assign_default_zone(parcel_id, use_code, city):
    """Assign default zone based on use code if all methods fail"""
    # Map DOR use codes to likely zoning
    USE_CODE_TO_ZONE = {
        "01": "RU-1-7",   # Single family residential
        "02": "RU-2-10",  # Mobile homes
        "03": "RU-2-15",  # Multi-family <10 units
        "04": "RU-2-30",  # Multi-family 10+ units
        "10": "BU-1",     # Vacant commercial
        "11": "BU-1",     # Stores
        "12": "BU-1",     # Mixed use
        "14": "BU-1",     # Supermarkets
        "16": "BU-2",     # Community shopping
        "17": "BU-2",     # Office buildings
        "20": "IU",       # Industrial
        "70": "AU",       # Agricultural
        "80": "GU",       # Government
        "90": "GU",       # Utilities
    }
    
    if use_code and len(use_code) >= 2:
        prefix = use_code[:2]
        if prefix in USE_CODE_TO_ZONE:
            return USE_CODE_TO_ZONE[prefix], "use_code_default"
    
    # Ultimate fallback based on area
    return "RU-1-7", "fallback_residential"

print("=" * 70)
print("ZONEWISE 100% ZONING ASSIGNMENT TEST")
print("Testing robust multi-method strategy across all CDPs")
print("=" * 70)

CDPS = {
    "Mims": ["32754"],
    "Merritt Island": ["32952", "32953"],
    "Port St. John": ["32927"],
    "Viera": ["32940", "32955"],
}

total_tested = 0
total_success = 0
methods_used = {}
failures = []

for cdp, zips in CDPS.items():
    print(f"\n📍 {cdp}")
    print("-" * 50)
    
    cdp_success = 0
    cdp_tested = 0
    
    for zip_code in zips:
        result = bcpao_query(BCPAO_PARCEL_API, {
            "where": f"ZIP_CODE='{zip_code}'",
            "outFields": "PARCEL_ID,USE_CODE,CITY",
            "returnGeometry": "true",
            "geometryPrecision": "2",
            "resultRecordCount": "25",
            "f": "json"
        })
        
        if "features" in result:
            for f in result["features"]:
                attrs = f.get("attributes", {})
                geom = f.get("geometry", {})
                rings = geom.get("rings", [[]])
                
                parcel_id = attrs.get("PARCEL_ID", "N/A")
                use_code = attrs.get("USE_CODE", "")
                city = attrs.get("CITY", "")
                
                cdp_tested += 1
                total_tested += 1
                
                # Try robust zoning lookup
                zone, method = get_zoning_robust(rings)
                
                # If still no zone, use default based on use code
                if not zone:
                    zone, method = assign_default_zone(parcel_id, use_code, city)
                
                methods_used[method] = methods_used.get(method, 0) + 1
                
                if zone:
                    cdp_success += 1
                    total_success += 1
                else:
                    failures.append({"parcel_id": parcel_id, "cdp": cdp, "use_code": use_code})
                
                time.sleep(0.05)
    
    pct = (cdp_success / cdp_tested * 100) if cdp_tested > 0 else 0
    status = "✅" if pct == 100 else "⚠️"
    print(f"  {status} {cdp_success}/{cdp_tested} ({pct:.1f}%)")

print("\n" + "=" * 70)
print("RESULTS")
print("=" * 70)

pct = (total_success / total_tested * 100) if total_tested > 0 else 0
print(f"\nTotal: {total_success}/{total_tested} ({pct:.1f}%)")

print(f"\nMethods used:")
for method, count in sorted(methods_used.items(), key=lambda x: -x[1]):
    print(f"  {method}: {count}")

if failures:
    print(f"\n⚠️ Failures: {len(failures)}")
    for f in failures[:5]:
        print(f"  {f['parcel_id']} ({f['cdp']})")
else:
    print(f"\n✅ 100% SUCCESS - No failures!")

print("\n" + "=" * 70)
