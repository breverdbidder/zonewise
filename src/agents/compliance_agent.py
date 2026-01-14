"""
ZoneWise Compliance Agent
Analyzes property compliance with local zoning ordinances
"""

import os
import httpx
from typing import Dict, Any, List, Optional
from supabase import create_client, Client

# Environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
BCPAO_API_BASE = "https://www.bcpao.us/api/v1/search"

# Initialize Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def get_property_data(address: str) -> Optional[Dict[str, Any]]:
    """
    Fetch property data from BCPAO API
    
    Args:
        address: Full property address
        
    Returns:
        Property data dict or None
    """
    try:
        params = {
            "siteAddress": address,
            "limit": 1
        }
        response = httpx.get(BCPAO_API_BASE, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if data and len(data) > 0:
            return data[0]
        return None
    except Exception as e:
        print(f"Error fetching property data: {e}")
        return None


def map_use_code_to_zoning(use_code: str, city: str) -> Optional[str]:
    """
    Map BCPAO USE_CODE to zoning district
    
    Args:
        use_code: Property use code from BCPAO
        city: City name
        
    Returns:
        Zoning district code or None
    """
    # Common mappings (expand as needed)
    residential_codes = ["0000", "0001", "0100", "0200"]
    commercial_codes = ["1700", "1800", "1900"]
    
    if use_code in residential_codes:
        if city.upper() in ["INDIAN HARBOUR BEACH", "SATELLITE BEACH"]:
            return "R-1"
        elif city.upper() == "MELBOURNE":
            return "RS-1"
    elif use_code in commercial_codes:
        return "C-1"
    
    return None


def get_zoning_requirements(jurisdiction: str, district: str) -> Optional[Dict[str, Any]]:
    """
    Fetch zoning requirements from Supabase
    
    Args:
        jurisdiction: City/county name
        district: Zoning district code
        
    Returns:
        Requirements dict or None
    """
    try:
        response = supabase.table("zoning_requirements") \
            .select("*") \
            .eq("jurisdiction", jurisdiction.upper()) \
            .eq("district", district) \
            .execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error fetching zoning requirements: {e}")
        return None


def analyze_compliance(address: str) -> Dict[str, Any]:
    """
    Analyze property compliance with zoning ordinances
    
    Args:
        address: Full property address
        
    Returns:
        Compliance analysis dict
    """
    result = {
        "address": address,
        "status": "MANUAL_REVIEW",
        "confidence": 0,
        "violations": [],
        "recommendations": [],
        "property_data": None,
        "zoning_data": None
    }
    
    # Step 1: Fetch property data from BCPAO
    property_data = get_property_data(address)
    if not property_data:
        result["violations"].append({
            "type": "DATA_UNAVAILABLE",
            "message": "Could not fetch property data from BCPAO"
        })
        return result
    
    result["property_data"] = {
        "parcel_id": property_data.get("parcelNo"),
        "owner": property_data.get("ownerName"),
        "city": property_data.get("propCity"),
        "lot_size": property_data.get("lotSize"),
        "building_area": property_data.get("bldgArea"),
        "use_code": property_data.get("dORUseCode"),
        "year_built": property_data.get("yearBuilt")
    }
    
    # Step 2: Map USE_CODE to zoning district
    city = property_data.get("propCity", "")
    use_code = property_data.get("dORUseCode", "")
    zoning_district = map_use_code_to_zoning(use_code, city)
    
    if not zoning_district:
        result["violations"].append({
            "type": "ZONING_UNKNOWN",
            "message": f"Could not determine zoning district for USE_CODE {use_code}"
        })
        return result
    
    # Step 3: Fetch zoning requirements
    jurisdiction = city.upper()
    requirements = get_zoning_requirements(jurisdiction, zoning_district)
    
    if not requirements:
        result["violations"].append({
            "type": "REQUIREMENTS_UNAVAILABLE",
            "message": f"No zoning requirements found for {jurisdiction} {zoning_district}"
        })
        result["recommendations"].append(
            "Manually review zoning ordinance for dimensional requirements"
        )
        return result
    
    result["zoning_data"] = requirements
    
    # Step 4: Check compliance (dimensional requirements)
    lot_size = property_data.get("lotSize")
    building_area = property_data.get("bldgArea")
    
    violations = []
    
    # Lot size check
    if lot_size and requirements.get("min_lot_size"):
        min_lot = requirements["min_lot_size"]
        if lot_size < min_lot:
            violations.append({
                "type": "LOT_SIZE",
                "message": f"Lot size {lot_size} sq ft < minimum {min_lot} sq ft",
                "severity": "HIGH"
            })
    
    # Coverage check (if available)
    if lot_size and building_area and requirements.get("max_coverage"):
        coverage = (building_area / lot_size) * 100
        max_coverage = requirements["max_coverage"]
        if coverage > max_coverage:
            violations.append({
                "type": "LOT_COVERAGE",
                "message": f"Coverage {coverage:.1f}% > maximum {max_coverage}%",
                "severity": "MEDIUM"
            })
    
    # Step 5: Determine status
    if len(violations) == 0:
        result["status"] = "COMPLIANT"
        result["confidence"] = 95
    elif any(v["severity"] == "HIGH" for v in violations):
        result["status"] = "NON_COMPLIANT"
        result["confidence"] = 85
        result["violations"] = violations
        result["recommendations"].append(
            "Consult with local planning department for variance or rezoning"
        )
    else:
        result["status"] = "MANUAL_REVIEW"
        result["confidence"] = 70
        result["violations"] = violations
        result["recommendations"].append(
            "Minor violations detected - professional review recommended"
        )
    
    return result


if __name__ == "__main__":
    # Test addresses
    test_addresses = [
        "798 Ocean Dr, Satellite Beach, FL",
        "790 Hibiscus Dr, Satellite Beach, FL",
        "100 Dale Ave, Melbourne, FL"
    ]
    
    for addr in test_addresses:
        print(f"\n{'='*60}")
        print(f"Analyzing: {addr}")
        print(f"{'='*60}")
        
        result = analyze_compliance(addr)
        
        print(f"Status: {result['status']} ({result['confidence']}% confidence)")
        print(f"Parcel: {result['property_data'].get('parcel_id') if result['property_data'] else 'N/A'}")
        
        if result['violations']:
            print(f"\nViolations: {len(result['violations'])}")
            for v in result['violations']:
                print(f"  - [{v.get('severity', 'INFO')}] {v['message']}")
        
        if result['recommendations']:
            print(f"\nRecommendations:")
            for r in result['recommendations']:
                print(f"  - {r}")
