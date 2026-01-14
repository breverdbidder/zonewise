"""
ZoneWise Ordinance Parser
Parses scraped Municode content into structured zoning data using Gemini 2.5 Flash (FREE)

Usage:
    from ordinance_parser import parse_ordinance
    districts = parse_ordinance(content, 'indian_harbour_beach')
"""

import re
import json
import os
from typing import Dict, Any, List, Optional
import httpx

# Gemini API configuration (FREE tier)
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GEMINI_MODEL = "gemini-2.0-flash"  # FREE tier model


def extract_districts_regex(content: str) -> List[Dict[str, Any]]:
    """
    Extract zoning districts using regex patterns (fast, free fallback)
    
    Args:
        content: Raw ordinance markdown content
        
    Returns:
        List of district dictionaries with basic info
    """
    districts = []
    
    # Common district patterns
    district_patterns = [
        # R-1, R-1A, R-1AA, etc.
        (r'\b(R-\d+[A-Z]*)\b', 'Residential'),
        # C-1, C-2, C-P
        (r'\b(C-\d+|C-[A-Z]+)\b', 'Commercial'),
        # B-1, B-2
        (r'\b(B-\d+)\b', 'Commercial'),
        # M-1, M-2, I-1, I-2
        (r'\b([MI]-\d+)\b', 'Industrial'),
        # P-1, P-2
        (r'\b(P-\d+)\b', 'Institutional'),
        # PUD, MU, MXD
        (r'\b(PUD|MU|MXD)\b', 'Mixed-Use'),
    ]
    
    found_codes = set()
    
    for pattern, category in district_patterns:
        matches = re.findall(pattern, content)
        for code in matches:
            if code not in found_codes:
                found_codes.add(code)
                districts.append({
                    'district_code': code,
                    'category': category,
                    'source': 'regex'
                })
    
    return districts


def extract_setbacks_regex(content: str) -> Dict[str, List[int]]:
    """
    Extract setback values using regex
    
    Args:
        content: Raw ordinance content
        
    Returns:
        Dict with setback types and found values
    """
    setbacks = {
        'front': [],
        'rear': [],
        'side': [],
        'corner': []
    }
    
    patterns = {
        'front': r'front\s*(?:yard|setback)?[:\s]*(\d+)\s*(?:feet|ft)',
        'rear': r'rear\s*(?:yard|setback)?[:\s]*(\d+)\s*(?:feet|ft)',
        'side': r'side\s*(?:yard|setback)?[:\s]*(\d+)\s*(?:feet|ft)',
        'corner': r'corner\s*(?:side)?[:\s]*(\d+)\s*(?:feet|ft)'
    }
    
    for setback_type, pattern in patterns.items():
        matches = re.findall(pattern, content, re.IGNORECASE)
        setbacks[setback_type] = sorted(set(int(m) for m in matches))
    
    return setbacks


def extract_dimensions_regex(content: str) -> Dict[str, Any]:
    """
    Extract dimensional requirements using regex
    
    Args:
        content: Raw ordinance content
        
    Returns:
        Dict with dimensional values
    """
    dimensions = {}
    
    patterns = {
        'min_lot_width': r'minimum\s*lot\s*width[:\s-]*(\d+)\s*(?:feet|ft)',
        'min_lot_depth': r'minimum\s*lot\s*depth[:\s-]*(\d+)\s*(?:feet|ft)',
        'min_lot_area': r'minimum\s*lot\s*(?:area|size)[:\s-]*(\d+(?:,\d+)?)\s*(?:square\s*feet|sq\.?\s*ft|sqft)',
        'max_height': r'maximum\s*(?:building\s*)?height[:\s-]*(\d+)\s*(?:feet|ft)',
        'max_living_area': r'maximum\s*living\s*area[:\s-]*(\d+(?:,\d+)?)\s*(?:square\s*feet|sq\.?\s*ft)',
        'min_living_area': r'minimum\s*(?:living|floor)\s*area[:\s-]*(\d+(?:,\d+)?)\s*(?:square\s*feet|sq\.?\s*ft)'
    }
    
    for dim_type, pattern in patterns.items():
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            # Clean and convert
            values = [int(m.replace(',', '')) for m in matches]
            dimensions[dim_type] = sorted(set(values))
    
    return dimensions


async def parse_with_gemini(
    content: str,
    jurisdiction_name: str,
    max_tokens: int = 2000
) -> Optional[Dict[str, Any]]:
    """
    Use Gemini 2.5 Flash (FREE) to parse ordinance content
    
    Args:
        content: Raw ordinance content (truncated for token limits)
        jurisdiction_name: Name of jurisdiction for context
        max_tokens: Max response tokens
        
    Returns:
        Parsed district data or None if API fails
    """
    if not GEMINI_API_KEY:
        print("⚠️ No Gemini API key - using regex fallback")
        return None
    
    # Truncate content to ~8K chars for free tier limits
    truncated = content[:8000]
    
    prompt = f"""Extract zoning district information from this {jurisdiction_name} ordinance.

Return JSON with this structure:
{{
    "districts": [
        {{
            "code": "R-1",
            "name": "Single-Family Residential",
            "category": "Residential",
            "allowed_uses": ["single-family dwellings", "accessory structures"],
            "dimensional_requirements": {{
                "min_lot_width_ft": 100,
                "min_lot_depth_ft": 120,
                "max_height_ft": 35,
                "setbacks": {{
                    "front_ft": 25,
                    "rear_ft": 20,
                    "side_ft": 10
                }}
            }}
        }}
    ]
}}

Only include districts explicitly mentioned. Use null for unknown values.

ORDINANCE CONTENT:
{truncated}

Return ONLY valid JSON, no explanation."""

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": max_tokens
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                text = data['candidates'][0]['content']['parts'][0]['text']
                
                # Clean JSON from markdown fences
                text = re.sub(r'```json\s*', '', text)
                text = re.sub(r'```\s*', '', text)
                
                return json.loads(text)
            else:
                print(f"⚠️ Gemini API error: {response.status_code}")
                return None
                
    except Exception as e:
        print(f"⚠️ Gemini parsing failed: {e}")
        return None


def parse_ordinance(
    content: str,
    jurisdiction_id: str,
    jurisdiction_name: Optional[str] = None,
    use_llm: bool = False
) -> Dict[str, Any]:
    """
    Parse ordinance content into structured zoning data
    
    Args:
        content: Raw ordinance markdown content
        jurisdiction_id: Jurisdiction identifier
        jurisdiction_name: Full jurisdiction name
        use_llm: Whether to use Gemini LLM (requires API key)
        
    Returns:
        Dict with parsed zoning districts and metadata
    """
    if jurisdiction_name is None:
        jurisdiction_name = jurisdiction_id.replace('_', ' ').title()
    
    result = {
        'jurisdiction_id': jurisdiction_id,
        'jurisdiction_name': jurisdiction_name,
        'districts': [],
        'setbacks': {},
        'dimensions': {},
        'parse_method': 'regex',
        'confidence': 0.0
    }
    
    # Always run regex extraction (fast, free)
    regex_districts = extract_districts_regex(content)
    regex_setbacks = extract_setbacks_regex(content)
    regex_dimensions = extract_dimensions_regex(content)
    
    result['districts'] = regex_districts
    result['setbacks'] = regex_setbacks
    result['dimensions'] = regex_dimensions
    
    # Calculate confidence based on data found
    confidence = 0.0
    if regex_districts:
        confidence += 0.3
    if any(regex_setbacks.values()):
        confidence += 0.3
    if regex_dimensions:
        confidence += 0.2
    if len(content) > 50000:  # Good amount of content
        confidence += 0.2
    
    result['confidence'] = min(confidence, 1.0)
    
    # Optionally enhance with LLM
    if use_llm and GEMINI_API_KEY:
        import asyncio
        llm_result = asyncio.run(parse_with_gemini(content, jurisdiction_name))
        
        if llm_result and llm_result.get('districts'):
            result['districts'] = llm_result['districts']
            result['parse_method'] = 'gemini_llm'
            result['confidence'] = min(result['confidence'] + 0.3, 1.0)
    
    return result


def enrich_district_data(
    district: Dict[str, Any],
    content: str
) -> Dict[str, Any]:
    """
    Enrich a district with additional data found in content
    
    Args:
        district: Basic district dict
        content: Full ordinance content
        
    Returns:
        Enriched district dict
    """
    code = district.get('district_code', district.get('code', ''))
    
    # Find section mentioning this district
    pattern = rf'(?:Sec(?:tion)?\.?\s*\d+[^.]*{code}[^.]*\.)(.*?)(?=Sec(?:tion)?\.|\Z)'
    match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
    
    if match:
        section_content = match.group(1)[:2000]
        
        # Extract uses
        use_patterns = [
            r'(?:permitted|allowed|principal)\s*uses?[:\s]*(.*?)(?:\n|$)',
            r'uses?\s*(?:permitted|allowed)[:\s]*(.*?)(?:\n|$)'
        ]
        
        for pattern in use_patterns:
            use_match = re.search(pattern, section_content, re.IGNORECASE)
            if use_match:
                uses_text = use_match.group(1)
                # Split by common delimiters
                uses = re.split(r'[,;]|\band\b', uses_text)
                uses = [u.strip() for u in uses if u.strip() and len(u.strip()) > 3]
                if uses:
                    district['allowed_uses'] = uses[:10]
                break
    
    return district


# CLI interface
if __name__ == '__main__':
    import sys
    
    # Test with sample content
    sample_content = """
    Article XII - Schedule of District Regulations
    
    Sec. 1. R-1 Single-Family Residential District
    Minimum lot width: 100 feet
    Maximum height: 35 feet
    Front yard setback: 25 feet
    Rear yard: 20 feet
    Side yard: 10 feet
    
    Sec. 2. R-2 Multiple-Family Residential
    Minimum lot width: 100 feet
    Maximum height: 35 feet
    
    Sec. 3. C-1 Commercial
    Minimum lot size: 9,000 square feet
    """
    
    result = parse_ordinance(sample_content, 'test_jurisdiction')
    print(json.dumps(result, indent=2))
