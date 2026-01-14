"""
Extract Dimensional Requirements from Ordinances
Parses raw ordinance content and populates zoning_requirements table
"""

import os
import re
from typing import Dict, List, Any, Optional
from supabase import create_client, Client
import httpx

# Environment
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Initialize Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def extract_requirements_regex(content: str, jurisdiction: str) -> List[Dict[str, Any]]:
    """
    Extract dimensional requirements using regex patterns
    
    Args:
        content: Raw ordinance content
        jurisdiction: City/county name
        
    Returns:
        List of requirement dicts
    """
    requirements = []
    
    # Pattern 1: Table-based requirements (common format)
    # Example: "R-1  | 6,000 sq ft | 60 ft | 35 ft | 15 ft | 5 ft | 40%"
    table_pattern = re.compile(
        r'([A-Z]{1,3}-?\d{1,2}[A-Z]?)\s*[\|:]?\s*'
        r'(\d{1,3},?\d{3})\s*(?:sq\.?\s*ft\.?|square feet)?\s*[\|:]?\s*'  # lot size
        r'(\d{1,3})\s*(?:ft\.?|feet)?\s*[\|:]?\s*'  # lot width
        r'(\d{1,3})\s*(?:ft\.?|feet)?',  # height
        re.IGNORECASE
    )
    
    # Pattern 2: Setback specifications
    # Example: "Front: 25 feet, Rear: 20 feet, Side: 7.5 feet"
    setback_pattern = re.compile(
        r'(?:Front|front)[\s:]+(\d{1,3}\.?\d?)\s*(?:ft|feet)?.*?'
        r'(?:Rear|rear)[\s:]+(\d{1,3}\.?\d?)\s*(?:ft|feet)?.*?'
        r'(?:Side|side)[\s:]+(\d{1,3}\.?\d?)\s*(?:ft|feet)?',
        re.IGNORECASE | re.DOTALL
    )
    
    # Pattern 3: Coverage limits
    # Example: "Maximum lot coverage: 40%"
    coverage_pattern = re.compile(
        r'(?:maximum|max)?\s*(?:lot)?\s*coverage[:\s]+(\d{1,3})%',
        re.IGNORECASE
    )
    
    # Find all table matches
    for match in table_pattern.finditer(content):
        district = match.group(1).strip()
        lot_size = int(match.group(2).replace(',', ''))
        lot_width = int(match.group(3))
        max_height = int(match.group(4))
        
        # Look for setbacks nearby (within 200 chars)
        start = max(0, match.start() - 200)
        end = min(len(content), match.end() + 200)
        context = content[start:end]
        
        setback_match = setback_pattern.search(context)
        coverage_match = coverage_pattern.search(context)
        
        req = {
            "jurisdiction": jurisdiction.upper(),
            "district": district,
            "requirement_type": "dimensional",
            "min_lot_size": lot_size,
            "min_lot_width": lot_width,
            "max_height": max_height,
            "front_setback": int(float(setback_match.group(1))) if setback_match else None,
            "rear_setback": int(float(setback_match.group(2))) if setback_match else None,
            "side_setback": int(float(setback_match.group(3))) if setback_match else None,
            "max_coverage": float(coverage_match.group(1)) if coverage_match else None,
            "additional_requirements": {}
        }
        
        requirements.append(req)
    
    return requirements


def extract_requirements_llm(content: str, jurisdiction: str, district: str) -> Optional[Dict[str, Any]]:
    """
    Use Gemini to extract requirements for a specific district
    
    Args:
        content: Raw ordinance content (focused on district section)
        jurisdiction: City/county name
        district: Zoning district code
        
    Returns:
        Requirements dict or None
    """
    if not GEMINI_API_KEY:
        return None
    
    prompt = f"""Extract zoning requirements for {district} district in {jurisdiction}.

Ordinance Content:
{content[:4000]}

Extract and return ONLY a JSON object with these fields (use null if not found):
{{
  "min_lot_size": <integer sq ft>,
  "min_lot_width": <integer ft>,
  "max_height": <integer ft>,
  "front_setback": <integer ft>,
  "rear_setback": <integer ft>,
  "side_setback": <integer ft>,
  "max_coverage": <decimal percentage, e.g. 40.0>
}}

Return ONLY the JSON, no explanation."""

    try:
        response = httpx.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GEMINI_API_KEY}",
            json={
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0,
                    "maxOutputTokens": 500
                }
            },
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        
        # Extract JSON from response
        import json
        json_match = re.search(r'\{[^}]+\}', text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(0))
            return {
                "jurisdiction": jurisdiction.upper(),
                "district": district,
                "requirement_type": "dimensional",
                **data,
                "additional_requirements": {}
            }
    
    except Exception as e:
        print(f"LLM extraction failed: {e}")
    
    return None


def populate_requirements():
    """
    Main function to extract and populate zoning requirements
    """
    print("=" * 60)
    print("ZoneWise: Populating Zoning Requirements")
    print("=" * 60)
    
    # Fetch all ordinances from Supabase
    response = supabase.table("ordinances").select("*").execute()
    ordinances = response.data
    
    print(f"\nFound {len(ordinances)} ordinances to process\n")
    
    all_requirements = []
    
    for ordinance in ordinances:
        jurisdiction = ordinance["jurisdiction"]
        content = ordinance.get("content", "")
        
        if not content:
            print(f"⚠️  {jurisdiction}: No content")
            continue
        
        print(f"📄 Processing: {jurisdiction}")
        print(f"   Content length: {len(content)} chars")
        
        # Extract using regex first
        requirements = extract_requirements_regex(content, jurisdiction)
        
        if requirements:
            print(f"   ✅ Found {len(requirements)} districts via regex")
            all_requirements.extend(requirements)
        else:
            print(f"   ⚠️  No regex matches - may need LLM")
        
        print()
    
    # Insert/upsert into Supabase
    if all_requirements:
        print(f"\n{'='*60}")
        print(f"Inserting {len(all_requirements)} requirements into Supabase")
        print(f"{'='*60}\n")
        
        for req in all_requirements:
            try:
                # Upsert (update if exists, insert if not)
                result = supabase.table("zoning_requirements").upsert(
                    req,
                    on_conflict="jurisdiction,district"
                ).execute()
                
                print(f"✅ {req['jurisdiction']} {req['district']}")
                
            except Exception as e:
                print(f"❌ {req['jurisdiction']} {req['district']}: {e}")
        
        print(f"\n✅ Complete! Inserted {len(all_requirements)} requirements")
    else:
        print("⚠️  No requirements extracted - check ordinance content format")


def manual_seed_sample_data():
    """
    Manually seed sample requirements for testing
    """
    sample_requirements = [
        # Satellite Beach R-1
        {
            "jurisdiction": "SATELLITE BEACH",
            "district": "R-1",
            "requirement_type": "dimensional",
            "min_lot_size": 6000,
            "min_lot_width": 60,
            "max_height": 35,
            "front_setback": 25,
            "rear_setback": 20,
            "side_setback": 7,
            "max_coverage": 40.0,
            "additional_requirements": {
                "notes": "Single-family residential"
            }
        },
        # Indian Harbour Beach R-1
        {
            "jurisdiction": "INDIAN HARBOUR BEACH",
            "district": "R-1",
            "requirement_type": "dimensional",
            "min_lot_size": 7500,
            "min_lot_width": 75,
            "max_height": 35,
            "front_setback": 25,
            "rear_setback": 20,
            "side_setback": 10,
            "max_coverage": 35.0,
            "additional_requirements": {
                "notes": "Single-family residential"
            }
        },
        # Melbourne RS-1
        {
            "jurisdiction": "MELBOURNE",
            "district": "RS-1",
            "requirement_type": "dimensional",
            "min_lot_size": 6000,
            "min_lot_width": 60,
            "max_height": 35,
            "front_setback": 25,
            "rear_setback": 15,
            "side_setback": 5,
            "max_coverage": 40.0,
            "additional_requirements": {
                "notes": "Single-family residential"
            }
        }
    ]
    
    print("Seeding sample requirements...")
    for req in sample_requirements:
        try:
            supabase.table("zoning_requirements").upsert(
                req,
                on_conflict="jurisdiction,district"
            ).execute()
            print(f"✅ {req['jurisdiction']} {req['district']}")
        except Exception as e:
            print(f"❌ {req['jurisdiction']} {req['district']}: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--seed":
        manual_seed_sample_data()
    else:
        populate_requirements()
