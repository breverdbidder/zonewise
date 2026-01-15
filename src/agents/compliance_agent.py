"""
ZoneWise Compliance Agent
Analyzes property compliance with local zoning ordinances
"""

import os
import re
import httpx
import warnings
warnings.filterwarnings("ignore", message="Unverified HTTPS request")
from typing import Dict, Any, List, Optional

# Environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
BCPAO_API_BASE = "https://www.bcpao.us/api/v1/search"

# BCPAO requires User-Agent header (403 without it)
BCPAO_HEADERS = {
    "User-Agent": "ZoneWise/1.0 (Property Analysis; contact@zonewise.io)",
    "Accept": "application/json"
}

# Address normalization patterns for BCPAO compatibility
ADDRESS_ABBREVIATIONS = {
    r'\bstreet\b': 'ST',
    r'\bavenue\b': 'AVE',
    r'\bdrive\b': 'DR',
    r'\bboulevard\b': 'BLVD',
    r'\bcircle\b': 'CIR',
    r'\bcourt\b': 'CT',
    r'\blane\b': 'LN',
    r'\broad\b': 'RD',
    r'\bplace\b': 'PL',
    r'\bterrace\b': 'TER',
    r'\bway\b': 'WAY',
    r'\bnorth\b': 'N',
    r'\bsouth\b': 'S',
    r'\beast\b': 'E',
    r'\bwest\b': 'W',
    r'\bnortheast\b': 'NE',
    r'\bnorthwest\b': 'NW',
    r'\bsoutheast\b': 'SE',
    r'\bsouthwest\b': 'SW',
}

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


def normalize_address(address: str) -> str:
    """
    Normalize address to BCPAO-compatible format
    
    Args:
        address: Raw address input
        
    Returns:
        Normalized address with standard abbreviations
    """
    normalized = address.upper()
    
    for pattern, replacement in ADDRESS_ABBREVIATIONS.items():
        normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
    
    # Remove extra spaces
    normalized = ' '.join(normalized.split())
    
    return normalized


def get_property_data(address: str) -> Optional[Dict[str, Any]]:
    """
    Fetch property data from BCPAO API
    
    Args:
        address: Full property address (will extract and normalize street portion)
        
    Returns:
        Property data dict or None
    """
    try:
        # Extract street address (before city)
        street_address = address.split(',')[0].strip() if ',' in address else address
        
        # Normalize for BCPAO compatibility (Street -> ST, Avenue -> AVE, etc.)
        normalized = normalize_address(street_address)
        
        params = {"address": normalized}
        
        response = httpx.get(
            BCPAO_API_BASE, 
            params=params,
            headers=BCPAO_HEADERS,
            timeout=30,
            verify=False
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


def map_land_use_to_zoning(land_use_code: str, city: str = "") -> Optional[str]:
    """
    Map BCPAO land use description to zoning district
    
    Args:
        land_use_code: Land use description from BCPAO
        city: City name for city-specific mappings
        
    Returns:
        Zoning district code or None
    """
    if not land_use_code:
        return None
    
    land_use_lower = land_use_code.lower().strip()
    city_upper = city.upper() if city else ""
    
    # Single-family residential
    if "single family" in land_use_lower:
        return "R-1"
    
    # Multi-family / Mixed-use (important for Satellite Beach RM-3)
    if "multi-family" in land_use_lower or "multifamily" in land_use_lower:
        # Satellite Beach uses RM-3 for multi-family
        if "SATELLITE" in city_upper:
            return "RM-3"
        return "R-3"
    
    # Vacant multi-family platted land
    if "vacant" in land_use_lower and "multi-family" in land_use_lower:
        if "SATELLITE" in city_upper:
            return "RM-3"
        return "R-3"
    
    # General vacant residential
    if "vacant" in land_use_lower and "residential" in land_use_lower:
        if "multi" in land_use_lower or "platted" in land_use_lower:
            if "SATELLITE" in city_upper:
                return "RM-3"
            return "R-2"
        return "R-1"
    
    # Other residential
    if "duplex" in land_use_lower or "triplex" in land_use_lower:
        return "R-2"
    elif "mobile" in land_use_lower or "manufactured" in land_use_lower:
        return "R-3"
    elif "condo" in land_use_lower or "apartment" in land_use_lower:
        return "R-3"
    
    # Commercial mappings
    elif "commercial" in land_use_lower or "retail" in land_use_lower or "store" in land_use_lower:
        return "C-1"
    elif "office" in land_use_lower or "professional" in land_use_lower:
        return "C-2"
    
    # Industrial mappings
    elif "industrial" in land_use_lower or "warehouse" in land_use_lower:
        return "I-1"
    
    # Vacant/agricultural
    elif "vacant" in land_use_lower or "agricultural" in land_use_lower:
        return "AG"
    
    return None


def get_jurisdiction_id(city_name: str) -> Optional[int]:
    """
    Get jurisdiction ID from city name
    
    Args:
        city_name: City name from BCPAO (e.g., "SATELLITE BEACH", "MELBOURNE")
        
    Returns:
        Jurisdiction ID or None
    """
    supabase = get_supabase()
    if not supabase:
        return None
    
    try:
        city_normalized = city_name.upper().strip()
        
        # Try exact match first
        response = supabase.table("jurisdictions") \
            .select("id, name") \
            .ilike("name", city_normalized) \
            .limit(1) \
            .execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]["id"]
        
        # Try partial match (e.g., "SATELLITE BEACH" -> "Satellite Beach")
        for word in city_normalized.split():
            if word in ["BEACH", "BAY", "WEST", "EAST", "NORTH", "SOUTH"]:
                continue  # Skip common suffixes/prefixes
            response = supabase.table("jurisdictions") \
                .select("id, name") \
                .ilike("name", f"%{word}%") \
                .limit(1) \
                .execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]["id"]
        
        return None
    except Exception as e:
        print(f"Error fetching jurisdiction: {e}")
        return None


def get_zoning_rules(zoning_district: str, city_name: str) -> Optional[Dict[str, Any]]:
    """
    Get zoning rules from Supabase using jurisdiction lookup
    
    Args:
        zoning_district: Zoning district code (e.g., "R-1", "RM-3")
        city_name: City name from BCPAO
        
    Returns:
        Zoning rules dict or None
    """
    supabase = get_supabase()
    if not supabase:
        return None
    
    try:
        jurisdiction_id = get_jurisdiction_id(city_name)
        if not jurisdiction_id:
            print(f"Jurisdiction not found for city: {city_name}")
            return None
        
        response = supabase.table("zoning_districts") \
            .select("*") \
            .eq("code", zoning_district) \
            .eq("jurisdiction_id", jurisdiction_id) \
            .limit(1) \
            .execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        
        print(f"Zoning district {zoning_district} not found for jurisdiction_id {jurisdiction_id}")
        return None
    except Exception as e:
        print(f"Error fetching zoning rules: {e}")
        return None


def check_violations(property_data: Dict[str, Any], zoning_rules: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Check property against zoning rules for violations
    """
    violations = []
    
    if not zoning_rules:
        return violations
    
    acreage = property_data.get("acreage", 0) or 0
    lot_size_sqft = int(float(acreage) * 43560)
    
    min_lot = zoning_rules.get("min_lot_size", 0) or 0
    if lot_size_sqft > 0 and min_lot > 0 and lot_size_sqft < min_lot:
        violations.append({
            "type": "LOT_SIZE",
            "message": f"Lot size ({lot_size_sqft:,} sq ft) below minimum ({min_lot:,} sq ft)",
            "severity": "major"
        })
    
    building_area = property_data.get("totalBaseArea", 0) or 0
    max_coverage = zoning_rules.get("max_coverage", 100) or 100
    if lot_size_sqft > 0 and building_area > 0:
        coverage = (building_area / lot_size_sqft) * 100
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
    
    # Step 1: Get property data from BCPAO (with address normalization)
    bcpao_data = get_property_data(address)
    if not bcpao_data:
        result["violations"].append({
            "type": "DATA_ERROR",
            "message": "Could not fetch property data from BCPAO",
            "severity": "info"
        })
        result["recommendations"].append("Verify address and try again")
        return result
    
    # Convert acreage to sqft
    acreage = bcpao_data.get("acreage", 0) or 0
    lot_size_sqft = int(float(acreage) * 43560) if acreage else None
    
    # Extract property info
    result["property_data"] = {
        "parcel_id": bcpao_data.get("parcelID"),
        "account": bcpao_data.get("account"),
        "owner": bcpao_data.get("owners"),
        "city": bcpao_data.get("taxingDistrict"),
        "site_address": bcpao_data.get("siteAddress"),
        "lot_size": lot_size_sqft,
        "building_area": bcpao_data.get("totalBaseArea"),
        "use_code": bcpao_data.get("landUseCode", "").strip() if bcpao_data.get("landUseCode") else None,
        "year_built": bcpao_data.get("yearBuilt"),
        "market_value": bcpao_data.get("marketValue"),
        "photo_url": bcpao_data.get("masterPhotoUrl"),
        "subdivision": bcpao_data.get("subdivisionName"),
        "acreage": acreage
    }
    
    city = bcpao_data.get("taxingDistrict", "")
    land_use = bcpao_data.get("landUseCode", "")
    
    # Step 2: Map to zoning district (city-aware for Satellite Beach RM-3)
    zoning_district = map_land_use_to_zoning(land_use, city)
    if not zoning_district:
        result["status"] = "MANUAL_REVIEW"
        result["confidence"] = 30
        result["recommendations"].append(f"Unable to determine zoning district from land use: {land_use.strip() if land_use else 'unknown'}")
        return result
    
    result["property_data"]["inferred_zoning"] = zoning_district
    
    # Step 3: Get zoning rules
    zoning_rules = get_zoning_rules(zoning_district, city)
    result["zoning_data"] = zoning_rules
    
    if not zoning_rules:
        result["status"] = "MANUAL_REVIEW"
        result["confidence"] = 50
        result["recommendations"].append(f"Zoning rules not found for {zoning_district} in {city}")
        return result
    
    # Step 4: Check for violations
    violations = check_violations(bcpao_data, zoning_rules)
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
