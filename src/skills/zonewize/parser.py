"""
zonewize/parser.py
Ordinance parsing and rule extraction.

Responsibilities:
- Parse HTML ordinance content
- Extract zoning districts, allowed uses, dimensional requirements
- Use Gemini 2.5 Flash (FREE tier) for LLM-assisted parsing
"""

from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import re


def parse_ordinance(
    ordinance_html: str,
    jurisdiction: str
) -> Dict[str, any]:
    """
    Parse ordinance HTML to extract zoning rules.
    
    Uses a combination of:
    1. BeautifulSoup for HTML parsing
    2. Regex for pattern matching
    3. Gemini 2.5 Flash (FREE tier) for ambiguous sections
    
    Args:
        ordinance_html: Raw HTML content from ordinance page
        jurisdiction: Jurisdiction identifier (affects parsing strategy)
    
    Returns:
        Dict with extracted zoning rules:
        - zoning_districts (list): All zoning districts in jurisdiction
        - allowed_uses (dict): {district: [uses]} mapping
        - setbacks (dict): {district: {front, side, rear}} setback requirements
        - height_limits (dict): {district: height_ft}
        - lot_requirements (dict): {district: {min_size, min_width}}
        - sections_referenced (list): Ordinance sections used
        - has_ambiguous_language (bool): Whether ordinance has unclear sections
    """
    soup = BeautifulSoup(ordinance_html, 'html.parser')
    
    # Initialize result structure
    result = {
        'zoning_districts': [],
        'allowed_uses': {},
        'setbacks': {},
        'height_limits': {},
        'lot_requirements': {},
        'sections_referenced': [],
        'has_ambiguous_language': False,
        'use_section': None,
        'setback_section': None,
        'height_section': None,
        'lot_section': None
    }
    
    # Parse based on jurisdiction (different sites have different structures)
    if 'municode' in jurisdiction or 'municode.com' in ordinance_html.lower():
        result = _parse_municode_ordinance(soup, jurisdiction)
    else:
        result = _parse_generic_ordinance(soup, jurisdiction)
    
    return result


def _parse_municode_ordinance(soup: BeautifulSoup, jurisdiction: str) -> Dict:
    """Parse Municode.com formatted ordinances."""
    result = {
        'zoning_districts': [],
        'allowed_uses': {},
        'setbacks': {},
        'height_limits': {},
        'lot_requirements': {},
        'sections_referenced': [],
        'has_ambiguous_language': False
    }
    
    # Municode typically uses specific class names and structure
    # Look for section titles containing "zoning", "district", "permitted uses"
    
    # Extract zoning districts
    # Common patterns: "R-1", "RS-1", "C-1", "I-1", etc.
    district_pattern = re.compile(r'\b([A-Z]{1,2}-\d{1,2}|[A-Z]{2,3})\b')
    
    text_content = soup.get_text()
    districts = list(set(district_pattern.findall(text_content)))
    
    # Filter out false positives (dates, etc.)
    districts = [d for d in districts if len(d) <= 4 and not d.isdigit()]
    
    result['zoning_districts'] = sorted(districts)
    
    # Extract allowed uses (simplified mock)
    # In production, use Gemini 2.5 Flash to extract from tables
    for district in result['zoning_districts']:
        if 'R' in district:  # Residential
            result['allowed_uses'][district] = [
                'single_family_residence',
                'home_occupation',
                'accessory_building'
            ]
        elif 'C' in district:  # Commercial
            result['allowed_uses'][district] = [
                'retail_store',
                'restaurant',
                'office',
                'service_business'
            ]
        elif 'I' in district:  # Industrial
            result['allowed_uses'][district] = [
                'warehouse',
                'manufacturing',
                'distribution'
            ]
    
    # Extract setbacks (simplified)
    # Look for patterns like "25 feet", "25'", etc.
    setback_pattern = re.compile(r'(\d+)\s*(?:feet|ft|\')')
    setbacks_text = text_content.lower()
    
    for district in result['zoning_districts']:
        result['setbacks'][district] = {
            'front': 25,  # Default values (in production, extract from ordinance)
            'side': 10,
            'rear': 20
        }
    
    # Extract height limits
    for district in result['zoning_districts']:
        if 'R' in district:
            result['height_limits'][district] = 35  # Typical residential
        elif 'C' in district:
            result['height_limits'][district] = 45  # Typical commercial
        elif 'I' in district:
            result['height_limits'][district] = 50  # Typical industrial
    
    # Extract lot requirements
    for district in result['zoning_districts']:
        if 'R-1' in district:
            result['lot_requirements'][district] = {
                'min_size': 7200,  # sqft
                'min_width': 60    # feet
            }
        elif 'R-2' in district:
            result['lot_requirements'][district] = {
                'min_size': 5000,
                'min_width': 50
            }
    
    # Check for ambiguous language
    ambiguous_phrases = [
        'may be permitted',
        'at the discretion of',
        'as determined by',
        'subject to approval'
    ]
    
    text_lower = text_content.lower()
    result['has_ambiguous_language'] = any(
        phrase in text_lower for phrase in ambiguous_phrases
    )
    
    return result


def _parse_generic_ordinance(soup: BeautifulSoup, jurisdiction: str) -> Dict:
    """Parse generic ordinance format (fallback method)."""
    # Simplified generic parser
    # In production, use Gemini 2.5 Flash for custom formats
    
    return {
        'zoning_districts': ['R-1', 'C-1', 'I-1'],  # Default districts
        'allowed_uses': {
            'R-1': ['single_family_residence', 'home_occupation'],
            'C-1': ['retail_store', 'office'],
            'I-1': ['warehouse', 'manufacturing']
        },
        'setbacks': {
            'R-1': {'front': 25, 'side': 10, 'rear': 20},
            'C-1': {'front': 20, 'side': 5, 'rear': 15},
            'I-1': {'front': 30, 'side': 15, 'rear': 20}
        },
        'height_limits': {
            'R-1': 35,
            'C-1': 45,
            'I-1': 50
        },
        'lot_requirements': {
            'R-1': {'min_size': 7200, 'min_width': 60}
        },
        'sections_referenced': [],
        'has_ambiguous_language': False
    }


def extract_zoning_rules(
    ordinance_data: Dict,
    property_zoning_district: str
) -> Dict[str, any]:
    """
    Extract specific rules for a property's zoning district.
    
    Args:
        ordinance_data: Full parsed ordinance data
        property_zoning_district: The specific district to extract rules for
    
    Returns:
        Dict with rules specific to the property's district
    """
    return {
        'allowed_uses': ordinance_data['allowed_uses'].get(
            property_zoning_district, []
        ),
        'setbacks': ordinance_data['setbacks'].get(
            property_zoning_district, {}
        ),
        'height_limit': ordinance_data['height_limits'].get(
            property_zoning_district
        ),
        'lot_requirements': ordinance_data['lot_requirements'].get(
            property_zoning_district, {}
        )
    }


def _use_gemini_for_parsing(text: str, instruction: str) -> Dict:
    """
    Use Gemini 2.5 Flash (FREE tier) for complex parsing.
    
    This is a placeholder for the actual Gemini API integration.
    In production, this would call Gemini to extract structured data
    from ambiguous ordinance sections.
    
    Args:
        text: Ordinance text to parse
        instruction: What to extract (e.g., "Extract allowed uses for R-1")
    
    Returns:
        Structured data extracted by Gemini
    """
    # Placeholder - in production, call Gemini 2.5 Flash API
    # Cost: $0.00 (FREE tier)
    
    # Example call:
    # response = gemini_client.generate_content(
    #     model="gemini-2.5-flash",
    #     prompt=f"{instruction}\n\nText:\n{text}",
    #     max_tokens=500
    # )
    # return parse_gemini_response(response)
    
    return {}
