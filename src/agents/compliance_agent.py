"""
ZoneWise Compliance Agent
Analyzes property compliance with local zoning ordinances
"""

import os
import httpx
import warnings
warnings.filterwarnings("ignore", message="Unverified HTTPS request")
from typing import Dict, Any, List, Optional

# Environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
BCPAO_API_BASE = "https://www.bcpao.us/api/v1/search"

# Lazy Supabase initialization
_supabase_client = None

def get_supabase():
    """Lazy initialization of Supabase client"""
    global _supabase_client
    if _supabase_client is None:
        if SUPABASE_URL and SUPABASE_SERVICE_KEY:
            from supabase import create_client
            _supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    return _supabase_client


def get_property_data(address: str) -> Optional[Dict[str, Any]]:
    """
    Fetch property data from BCPAO API
    
    Args:
        address: Full property address (will extract street portion)
        
    Returns:
        Property data dict or None
    """
    try:
        # Extract just the street address (first part before city)
        # BCPAO works best with just street address
        street_address = address.split(',')[0].strip() if ',' in address else address
        
        params = {"address": street_address}
        
        # Use verify=False as workaround for Render's TLS issues
        response = httpx.get(
            BCPAO_API_BASE, 
            params=params, 
            timeout=30,
            verify=False  # Workaround for certificate issues
        )
        response.raise_for_status()
        data = response.json()
        
        if data and len(data) > 0:
            return data[0]
        return None
    except httpx.TimeoutException:
        print(f"Timeout fetching property data for: {address}")
        return None
    except httpx.RequestError as e:
        print(f"Request error fetching property data: {e}")
        return None
    except Exception as e:
        print(f"Error fetching property data: {type(e).__name__}: {e}")
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
        return "R-1"  # Residential
    elif use_code in commercial_codes:
        return "C-1"  # Commercial
    return None


def get_zoning_rules(zoning_district: str, jurisdiction: str) -> Optional[Dict[str, Any]]:
    """
    Get zoning rules from Supabase
    
    Args:
        zoning_district: Zoning district code
        jurisdiction: City/county name
        
    Returns:
        Zoning rules dict or None
    """
    supabase = get_supabase()
    if not supabase:
        return None
        
    try:
        response = supabase.table("zoning_districts") \
            .select("*") \
            .eq("district_code", zoning_district) \
            .eq("jurisdiction", jurisdiction) \
            .single() \
            .execute()
        
        return response.data
    except Exception as e:
        print(f"Error fetching zoning rules: {e}")
        return None


def check_violations(property_data: Dict[str, Any], zoning_rules: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Check property against zoning rules for violations
    
    Args:
        property_data: Property info from BCPAO
        zoning_rules: Zoning rules from database
        
    Returns:
        List of violation dicts
    """
    violations = []
    
    if not zoning_rules:
        return violations
    
    # Lot size check
    lot_size = property_data.get("lotSize", 0)
    min_lot = zoning_rules.get("min_lot_size", 0)
    if lot_size < min_lot:
        violations.append({
            "type": "LOT_SIZE",
            "message": f"Lot size ({lot_size} sq ft) below minimum ({min_lot} sq ft)",
            "severity": "major"
        })
    
    # Building coverage check
    building_area = property_data.get("buildingArea", 0)
    max_coverage = zoning_rules.get("max_coverage", 100)
    if lot_size > 0:
        coverage = (building_area / lot_size) * 100
        if coverage > max_coverage:
            violations.append({
                "type": "COVERAGE",
                "message": f"Building coverage ({coverage:.1f}%) exceeds maximum ({max_coverage}%)",
                "severity": "major"
            })
    
    return violations


def analyze_compliance(address: str) -> Dict[str, Any]:
    """
    Main analysis function - analyzes property compliance
    
    Args:
        address: Full property address
        
    Returns:
        Analysis result dict
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
    
    # Step 1: Get property data from BCPAO
    property_data = get_property_data(address)
    if not property_data:
        result["violations"].append({
            "type": "DATA_ERROR",
            "message": "Could not fetch property data from BCPAO",
            "severity": "info"
        })
        result["recommendations"].append("Verify address and try again")
        return result
    
    # Extract relevant property info
    result["property_data"] = {
        "parcel_id": property_data.get("parcel"),
        "owner": property_data.get("owner"),
        "city": property_data.get("city"),
        "lot_size": property_data.get("lotSize"),
        "building_area": property_data.get("buildingArea"),
        "use_code": property_data.get("useCode"),
        "year_built": property_data.get("yearBuilt")
    }
    
    city = property_data.get("city", "")
    use_code = property_data.get("useCode", "")
    
    # Step 2: Map to zoning district
    zoning_district = map_use_code_to_zoning(use_code, city)
    if not zoning_district:
        result["status"] = "MANUAL_REVIEW"
        result["confidence"] = 30
        result["recommendations"].append("Unable to determine zoning district - manual review required")
        return result
    
    # Step 3: Get zoning rules
    zoning_rules = get_zoning_rules(zoning_district, city)
    result["zoning_data"] = zoning_rules
    
    # Step 4: Check for violations
    violations = check_violations(property_data, zoning_rules)
    result["violations"] = violations
    
    # Step 5: Determine status
    if len(violations) == 0:
        result["status"] = "COMPLIANT"
        result["confidence"] = 85
    elif any(v.get("severity") == "major" for v in violations):
        result["status"] = "NON_COMPLIANT"
        result["confidence"] = 75
        result["recommendations"].append("Address zoning violations before proceeding")
    else:
        result["status"] = "MANUAL_REVIEW"
        result["confidence"] = 60
        result["recommendations"].append("Minor issues found - recommend professional review")
    
    return result
