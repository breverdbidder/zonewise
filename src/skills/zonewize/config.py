"""
zonewize/config.py
Configuration for all 17 Brevard County jurisdictions.

Each jurisdiction has:
- Ordinance URLs (Municode or government site)
- Contact information
- Parser version (for handling different formats)
- Zoning districts
"""

JURISDICTION_CONFIGS = {
    "indian_harbour_beach": {
        "full_name": "Indian Harbour Beach",
        "abbreviation": "IHB",
        "ordinance_url": "https://library.municode.com/fl/indian_harbour_beach/codes/code_of_ordinances",
        "zoning_map_url": "https://ihb.maps.arcgis.com/apps/webappviewer/index.html",
        "contact_email": "planning@ihb-fl.gov",
        "contact_phone": "(321) 773-2200",
        "office_hours": "Monday-Friday 8:00 AM - 4:30 PM",
        "zoning_districts": ["R-1", "R-2", "R-3", "C-1", "C-2", "I-1"],
        "parser_version": "municode_v2"
    },
    
    "melbourne": {
        "full_name": "City of Melbourne",
        "abbreviation": "MEL",
        "ordinance_url": "https://library.municode.com/fl/melbourne/codes/code_of_ordinances",
        "zoning_map_url": "https://melbourne.maps.arcgis.com/apps/webappviewer/",
        "contact_email": "planning@melbourneflorida.org",
        "contact_phone": "(321) 608-7500",
        "office_hours": "Monday-Friday 8:00 AM - 5:00 PM",
        "zoning_districts": ["RS-1", "RS-2", "RM", "CN", "CG", "CB", "IN", "IL"],
        "parser_version": "municode_v2"
    },
    
    "palm_bay": {
        "full_name": "City of Palm Bay",
        "abbreviation": "PB",
        "ordinance_url": "https://library.municode.com/fl/palm_bay/codes/code_of_ordinances",
        "zoning_map_url": "https://www.palmbayflorida.org/our-city/departments/planning-zoning",
        "contact_email": "planning@palmbayflorida.org",
        "contact_phone": "(321) 952-3410",
        "office_hours": "Monday-Friday 8:00 AM - 5:00 PM",
        "zoning_districts": ["RES-1", "RES-2", "RES-3", "COM", "IND", "PUD"],
        "parser_version": "municode_v2"
    },
    
    "cocoa": {
        "full_name": "City of Cocoa",
        "abbreviation": "COC",
        "ordinance_url": "https://library.municode.com/fl/cocoa/codes/code_of_ordinances",
        "zoning_map_url": "https://www.cocoafl.org/departments/growth-management",
        "contact_email": "planning@cocoafl.org",
        "contact_phone": "(321) 433-8600",
        "office_hours": "Monday-Friday 8:00 AM - 5:00 PM",
        "zoning_districts": ["R-1", "R-2", "R-3", "C-1", "C-2", "M-1"],
        "parser_version": "municode_v2"
    },
    
    "cocoa_beach": {
        "full_name": "City of Cocoa Beach",
        "abbreviation": "CB",
        "ordinance_url": "https://library.municode.com/fl/cocoa_beach/codes/code_of_ordinances",
        "zoning_map_url": "https://www.cityofcocoabeach.com/planning-zoning",
        "contact_email": "planning@cityofcocoabeach.com",
        "contact_phone": "(321) 868-3258",
        "office_hours": "Monday-Friday 8:00 AM - 5:00 PM",
        "zoning_districts": ["R-1", "R-2", "R-3", "C-1", "C-2", "C-3"],
        "parser_version": "municode_v2"
    },
    
    "rockledge": {
        "full_name": "City of Rockledge",
        "abbreviation": "ROC",
        "ordinance_url": "https://library.municode.com/fl/rockledge/codes/code_of_ordinances",
        "zoning_map_url": "https://www.cityofrockledge.org/planning",
        "contact_email": "planning@cityofrockledge.org",
        "contact_phone": "(321) 690-3978",
        "office_hours": "Monday-Friday 8:00 AM - 5:00 PM",
        "zoning_districts": ["R-1", "R-2", "R-3", "C-1", "C-2", "I-1"],
        "parser_version": "municode_v2"
    },
    
    "titusville": {
        "full_name": "City of Titusville",
        "abbreviation": "TIT",
        "ordinance_url": "https://library.municode.com/fl/titusville/codes/code_of_ordinances",
        "zoning_map_url": "https://www.titusville.com/planning-zoning",
        "contact_email": "planning@titusville.com",
        "contact_phone": "(321) 567-3774",
        "office_hours": "Monday-Friday 8:00 AM - 5:00 PM",
        "zoning_districts": ["R-1", "R-2", "R-3", "C-1", "C-2", "I-1", "I-2"],
        "parser_version": "municode_v2"
    },
    
    "satellite_beach": {
        "full_name": "City of Satellite Beach",
        "abbreviation": "SAT",
        "ordinance_url": "https://library.municode.com/fl/satellite_beach/codes/code_of_ordinances",
        "zoning_map_url": "https://www.satellitebeach.org/planning",
        "contact_email": "planning@satellitebeach.org",
        "contact_phone": "(321) 773-4407",
        "office_hours": "Monday-Friday 8:00 AM - 5:00 PM",
        "zoning_districts": ["R-1", "R-2", "C-1", "C-2"],
        "parser_version": "municode_v2"
    },
    
    "west_melbourne": {
        "full_name": "City of West Melbourne",
        "abbreviation": "WM",
        "ordinance_url": "https://library.municode.com/fl/west_melbourne/codes/code_of_ordinances",
        "zoning_map_url": "https://www.westmelbourne.org/planning",
        "contact_email": "planning@westmelbourne.org",
        "contact_phone": "(321) 837-7774",
        "office_hours": "Monday-Friday 8:00 AM - 5:00 PM",
        "zoning_districts": ["R-1", "R-2", "C-1", "C-2", "I-1"],
        "parser_version": "municode_v2"
    },
    
    "cape_canaveral": {
        "full_name": "City of Cape Canaveral",
        "abbreviation": "CC",
        "ordinance_url": "https://library.municode.com/fl/cape_canaveral/codes/code_of_ordinances",
        "zoning_map_url": "https://www.cityofcapecanaveral.org/planning",
        "contact_email": "planning@cityofcapecanaveral.org",
        "contact_phone": "(321) 868-1220",
        "office_hours": "Monday-Friday 8:00 AM - 5:00 PM",
        "zoning_districts": ["R-1", "R-2", "C-1", "C-2"],
        "parser_version": "municode_v2"
    },
    
    "malabar": {
        "full_name": "Town of Malabar",
        "abbreviation": "MAL",
        "ordinance_url": "https://library.municode.com/fl/malabar/codes/code_of_ordinances",
        "zoning_map_url": "https://www.malabarflorida.org/planning",
        "contact_email": "planning@malabarflorida.org",
        "contact_phone": "(321) 727-7764",
        "office_hours": "Monday-Friday 9:00 AM - 5:00 PM",
        "zoning_districts": ["RR", "R-1", "C-1"],
        "parser_version": "municode_v2"
    },
    
    "grant_valkaria": {
        "full_name": "Town of Grant-Valkaria",
        "abbreviation": "GV",
        "ordinance_url": "https://library.municode.com/fl/grant-valkaria/codes/code_of_ordinances",
        "zoning_map_url": "https://www.grantfl.us/planning",
        "contact_email": "planning@grantfl.us",
        "contact_phone": "(321) 723-8696",
        "office_hours": "Monday-Friday 9:00 AM - 5:00 PM",
        "zoning_districts": ["RR", "R-1", "C-1"],
        "parser_version": "municode_v2"
    },
    
    "indialantic": {
        "full_name": "Town of Indialantic",
        "abbreviation": "IND",
        "ordinance_url": "https://library.municode.com/fl/indialantic/codes/code_of_ordinances",
        "zoning_map_url": "https://www.indialantic.com/planning",
        "contact_email": "planning@indialantic.com",
        "contact_phone": "(321) 723-2242",
        "office_hours": "Monday-Friday 8:00 AM - 5:00 PM",
        "zoning_districts": ["R-1", "R-2", "C-1", "C-2"],
        "parser_version": "municode_v2"
    },
    
    "melbourne_beach": {
        "full_name": "Town of Melbourne Beach",
        "abbreviation": "MB",
        "ordinance_url": "https://library.municode.com/fl/melbourne_beach/codes/code_of_ordinances",
        "zoning_map_url": "https://www.melbournebeachfl.org/planning",
        "contact_email": "planning@melbournebeachfl.org",
        "contact_phone": "(321) 724-5860",
        "office_hours": "Monday-Friday 8:00 AM - 4:30 PM",
        "zoning_districts": ["R-1", "R-2", "C-1"],
        "parser_version": "municode_v2"
    },
    
    "melbourne_village": {
        "full_name": "Town of Melbourne Village",
        "abbreviation": "MV",
        "ordinance_url": "https://library.municode.com/fl/melbourne_village/codes/code_of_ordinances",
        "zoning_map_url": "https://www.melbournevillage-fl.gov/planning",
        "contact_email": "planning@melbournevillage-fl.gov",
        "contact_phone": "(321) 723-5462",
        "office_hours": "Monday-Friday 9:00 AM - 4:00 PM",
        "zoning_districts": ["R-1"],
        "parser_version": "municode_v2"
    },
    
    "palm_shores": {
        "full_name": "Town of Palm Shores",
        "abbreviation": "PS",
        "ordinance_url": "https://library.municode.com/fl/palm_shores/codes/code_of_ordinances",
        "zoning_map_url": "https://www.palmshores.com/planning",
        "contact_email": "planning@palmshores.com",
        "contact_phone": "(321) 984-4420",
        "office_hours": "Monday-Friday 9:00 AM - 4:00 PM",
        "zoning_districts": ["R-1", "R-2"],
        "parser_version": "municode_v2"
    },
    
    "brevard_county_unincorporated": {
        "full_name": "Brevard County (Unincorporated Areas)",
        "abbreviation": "BC",
        "ordinance_url": "https://library.municode.com/fl/brevard_county/codes/code_of_ordinances",
        "zoning_map_url": "https://www.brevardfl.gov/PlanningAndDevelopment/Zoning",
        "contact_email": "planning@brevardfl.gov",
        "contact_phone": "(321) 633-2069",
        "office_hours": "Monday-Friday 8:00 AM - 5:00 PM",
        "zoning_districts": ["RU-1", "RU-2", "RR-1", "R-1", "R-2", "C-1", "C-2", "I-1", "I-2"],
        "parser_version": "municode_v2"
    }
}


# Helper function to get jurisdiction by various identifiers
def get_jurisdiction_config(identifier: str) -> dict:
    """
    Get jurisdiction config by name, abbreviation, or fuzzy match.
    
    Args:
        identifier: Jurisdiction name, abbreviation, or partial match
    
    Returns:
        Jurisdiction config dict
    
    Raises:
        KeyError: If jurisdiction not found
    """
    identifier_lower = identifier.lower().replace(' ', '_')
    
    # Direct match
    if identifier_lower in JURISDICTION_CONFIGS:
        return JURISDICTION_CONFIGS[identifier_lower]
    
    # Try abbreviation match
    for key, config in JURISDICTION_CONFIGS.items():
        if config['abbreviation'].lower() == identifier.upper():
            return config
    
    # Try full name match
    for key, config in JURISDICTION_CONFIGS.items():
        if config['full_name'].lower() == identifier.lower():
            return config
    
    raise KeyError(f"Jurisdiction not found: {identifier}")


# List of all supported jurisdictions
SUPPORTED_JURISDICTIONS = list(JURISDICTION_CONFIGS.keys())
