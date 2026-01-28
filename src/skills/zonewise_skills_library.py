#!/usr/bin/env python3
"""
ZoneWise Browser Automation Skills
===================================

Skills for navigating municipal permit portals across 17 Brevard jurisdictions.

PORTALS COVERED:
- Brevard County (unincorporated)
- Melbourne, Palm Bay, Titusville, Cocoa, Rockledge
- Satellite Beach, Indian Harbour Beach, Indialantic
- Melbourne Beach, Cape Canaveral, Cocoa Beach
- West Melbourne, Malabar, Grant-Valkaria
- Palm Shores, Melbourne Village

USE CASES:
- Permit application status lookup
- Zoning verification
- Development review tracking
- Building permit search
- Site plan approval status

Author: Claude AI Architect + ZoneWise.AI
Team: We are the team of Claude innovators!
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime
import json


@dataclass
class RecordedAction:
    """Single recorded user action"""
    timestamp: str
    action_type: str
    selector: Optional[str]
    value: Optional[str]
    url: Optional[str]
    element_info: Dict[str, Any]
    wait_condition: Optional[str] = None


@dataclass
class ZoneWiseSkill:
    """Skill specifically for zoning/permit workflows"""
    skill_id: str
    name: str
    description: str
    created_at: str
    jurisdiction: str  # brevard_county, melbourne, palm_bay, etc.
    portal_type: str   # citizen_access, tyler_erp, custom
    actions: List[RecordedAction]
    variables: Dict[str, str]
    success_criteria: List[Dict[str, Any]]
    output_fields: List[str]  # What data to extract
    
    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)


# =============================================================================
# BREVARD COUNTY SKILLS (Unincorporated)
# =============================================================================

class BrevardCountyPermitSkills:
    """
    Skills for Brevard County's Citizen Access portal.
    Portal: https://egov.brevardfl.gov/CitizenAccess/
    """
    
    @staticmethod
    def permit_search_by_address() -> ZoneWiseSkill:
        """Search permits by property address"""
        return ZoneWiseSkill(
            skill_id="brevard_permit_addr_001",
            name="Brevard County Permit Search (Address)",
            description="Search building permits by property address",
            created_at=datetime.now().isoformat(),
            jurisdiction="brevard_county",
            portal_type="citizen_access",
            actions=[
                RecordedAction(
                    timestamp="",
                    action_type="navigate",
                    selector=None,
                    value=None,
                    url="https://egov.brevardfl.gov/CitizenAccess/Cap/CapHome.aspx",
                    element_info={"destination": "Permit Home"}
                ),
                RecordedAction(
                    timestamp="",
                    action_type="click",
                    selector="a[href*='Building']",
                    value=None,
                    url=None,
                    element_info={"label": "Building", "role": "link"}
                ),
                RecordedAction(
                    timestamp="",
                    action_type="type",
                    selector="#ctl00_PlaceHolderMain_generalSearchForm_txtGSAddress",
                    value="{{street_address}}",
                    url=None,
                    element_info={"label": "Street Address", "role": "textbox"}
                ),
                RecordedAction(
                    timestamp="",
                    action_type="click",
                    selector="#ctl00_PlaceHolderMain_btnNewSearch",
                    value=None,
                    url=None,
                    element_info={"label": "Search", "role": "button"}
                ),
                RecordedAction(
                    timestamp="",
                    action_type="wait",
                    selector=".ACA_Grid_OverFlow",
                    value=None,
                    url=None,
                    element_info={"wait_for": "Results grid"},
                    wait_condition="visible"
                )
            ],
            variables={"street_address": ""},
            success_criteria=[
                {"type": "element_visible", "selector": ".ACA_Grid_OverFlow"}
            ],
            output_fields=["permit_number", "permit_type", "status", "issue_date", "expiration_date"]
        )
    
    @staticmethod
    def permit_detail_lookup() -> ZoneWiseSkill:
        """Get detailed permit information"""
        return ZoneWiseSkill(
            skill_id="brevard_permit_detail_001",
            name="Brevard County Permit Detail",
            description="Get full permit details including inspections",
            created_at=datetime.now().isoformat(),
            jurisdiction="brevard_county",
            portal_type="citizen_access",
            actions=[
                RecordedAction(
                    timestamp="",
                    action_type="navigate",
                    selector=None,
                    value=None,
                    url="https://egov.brevardfl.gov/CitizenAccess/Cap/CapDetail.aspx?Module=Building&capID1={{cap_id1}}&capID2={{cap_id2}}&capID3={{cap_id3}}",
                    element_info={"destination": "Permit Detail"}
                ),
                RecordedAction(
                    timestamp="",
                    action_type="wait",
                    selector="#ctl00_PlaceHolderMain_PermitDetailList1",
                    value=None,
                    url=None,
                    element_info={"wait_for": "Permit details"},
                    wait_condition="visible"
                )
            ],
            variables={"cap_id1": "", "cap_id2": "", "cap_id3": ""},
            success_criteria=[
                {"type": "element_visible", "selector": ".permit-details"}
            ],
            output_fields=["permit_number", "description", "valuation", "contractor", "inspections"]
        )
    
    @staticmethod
    def zoning_verification() -> ZoneWiseSkill:
        """Verify zoning designation for parcel"""
        return ZoneWiseSkill(
            skill_id="brevard_zoning_001",
            name="Brevard County Zoning Verification",
            description="Verify zoning code and permitted uses",
            created_at=datetime.now().isoformat(),
            jurisdiction="brevard_county",
            portal_type="gis",
            actions=[
                RecordedAction(
                    timestamp="",
                    action_type="navigate",
                    selector=None,
                    value=None,
                    url="https://gis.brevardfl.gov/brevardmaps/",
                    element_info={"destination": "Brevard GIS"}
                ),
                RecordedAction(
                    timestamp="",
                    action_type="type",
                    selector="#searchInput",
                    value="{{parcel_id}}",
                    url=None,
                    element_info={"label": "Search", "role": "textbox"}
                ),
                RecordedAction(
                    timestamp="",
                    action_type="click",
                    selector="#searchButton",
                    value=None,
                    url=None,
                    element_info={"label": "Search", "role": "button"}
                ),
                RecordedAction(
                    timestamp="",
                    action_type="wait",
                    selector=".esri-popup",
                    value=None,
                    url=None,
                    element_info={"wait_for": "Popup"},
                    wait_condition="visible"
                )
            ],
            variables={"parcel_id": ""},
            success_criteria=[
                {"type": "element_visible", "selector": ".esri-popup"}
            ],
            output_fields=["zoning_code", "future_land_use", "overlay_districts"]
        )


# =============================================================================
# MELBOURNE SKILLS
# =============================================================================

class MelbournePermitSkills:
    """
    Skills for City of Melbourne permit portal.
    Portal: Tyler ERP / EnerGov
    """
    
    @staticmethod
    def permit_search() -> ZoneWiseSkill:
        """Search Melbourne building permits"""
        return ZoneWiseSkill(
            skill_id="melbourne_permit_001",
            name="Melbourne Permit Search",
            description="Search City of Melbourne building permits",
            created_at=datetime.now().isoformat(),
            jurisdiction="melbourne",
            portal_type="tyler_erp",
            actions=[
                RecordedAction(
                    timestamp="",
                    action_type="navigate",
                    selector=None,
                    value=None,
                    url="https://aca-prod.accela.com/MELBOURNE/",
                    element_info={"destination": "Melbourne Permits"}
                ),
                RecordedAction(
                    timestamp="",
                    action_type="click",
                    selector="a[href*='Building']",
                    value=None,
                    url=None,
                    element_info={"label": "Building", "role": "link"}
                ),
                RecordedAction(
                    timestamp="",
                    action_type="type",
                    selector="#ctl00_PlaceHolderMain_generalSearchForm_txtGSAddress",
                    value="{{street_address}}",
                    url=None,
                    element_info={"label": "Address", "role": "textbox"}
                ),
                RecordedAction(
                    timestamp="",
                    action_type="click",
                    selector="#ctl00_PlaceHolderMain_btnNewSearch",
                    value=None,
                    url=None,
                    element_info={"label": "Search", "role": "button"}
                )
            ],
            variables={"street_address": ""},
            success_criteria=[
                {"type": "page_loaded", "timeout": 15000}
            ],
            output_fields=["permit_number", "type", "status", "issue_date"]
        )
    
    @staticmethod
    def site_plan_status() -> ZoneWiseSkill:
        """Check site plan review status"""
        return ZoneWiseSkill(
            skill_id="melbourne_siteplan_001",
            name="Melbourne Site Plan Status",
            description="Check status of site plan application",
            created_at=datetime.now().isoformat(),
            jurisdiction="melbourne",
            portal_type="tyler_erp",
            actions=[
                RecordedAction(
                    timestamp="",
                    action_type="navigate",
                    selector=None,
                    value=None,
                    url="https://aca-prod.accela.com/MELBOURNE/Cap/CapHome.aspx?module=Planning",
                    element_info={"destination": "Planning Module"}
                ),
                RecordedAction(
                    timestamp="",
                    action_type="type",
                    selector="#ctl00_PlaceHolderMain_generalSearchForm_txtGSPermitNumber",
                    value="{{application_number}}",
                    url=None,
                    element_info={"label": "Application Number", "role": "textbox"}
                ),
                RecordedAction(
                    timestamp="",
                    action_type="click",
                    selector="#ctl00_PlaceHolderMain_btnNewSearch",
                    value=None,
                    url=None,
                    element_info={"label": "Search", "role": "button"}
                )
            ],
            variables={"application_number": ""},
            success_criteria=[
                {"type": "element_visible", "selector": ".ACA_Grid_OverFlow"}
            ],
            output_fields=["application_number", "project_name", "status", "review_comments"]
        )


# =============================================================================
# PALM BAY SKILLS
# =============================================================================

class PalmBayPermitSkills:
    """
    Skills for City of Palm Bay permit portal.
    Portal: Custom / Tyler ERP
    """
    
    @staticmethod
    def permit_search() -> ZoneWiseSkill:
        """Search Palm Bay building permits"""
        return ZoneWiseSkill(
            skill_id="palmbay_permit_001",
            name="Palm Bay Permit Search",
            description="Search City of Palm Bay building permits",
            created_at=datetime.now().isoformat(),
            jurisdiction="palm_bay",
            portal_type="custom",
            actions=[
                RecordedAction(
                    timestamp="",
                    action_type="navigate",
                    selector=None,
                    value=None,
                    url="https://palmbayflorida.org/departments/growth-management/building/",
                    element_info={"destination": "Palm Bay Building"}
                ),
                RecordedAction(
                    timestamp="",
                    action_type="click",
                    selector="a[href*='permit-search']",
                    value=None,
                    url=None,
                    element_info={"label": "Permit Search", "role": "link"}
                ),
                RecordedAction(
                    timestamp="",
                    action_type="type",
                    selector="#address-input",
                    value="{{street_address}}",
                    url=None,
                    element_info={"label": "Address", "role": "textbox"}
                ),
                RecordedAction(
                    timestamp="",
                    action_type="click",
                    selector="button[type='submit']",
                    value=None,
                    url=None,
                    element_info={"label": "Search", "role": "button"}
                )
            ],
            variables={"street_address": ""},
            success_criteria=[
                {"type": "page_loaded", "timeout": 15000}
            ],
            output_fields=["permit_number", "type", "status", "contractor"]
        )
    
    @staticmethod
    def development_review() -> ZoneWiseSkill:
        """Check development review status"""
        return ZoneWiseSkill(
            skill_id="palmbay_devreview_001",
            name="Palm Bay Development Review",
            description="Check status of development review application",
            created_at=datetime.now().isoformat(),
            jurisdiction="palm_bay",
            portal_type="custom",
            actions=[
                RecordedAction(
                    timestamp="",
                    action_type="navigate",
                    selector=None,
                    value=None,
                    url="https://palmbayflorida.org/departments/growth-management/planning-zoning/",
                    element_info={"destination": "Planning & Zoning"}
                ),
                RecordedAction(
                    timestamp="",
                    action_type="click",
                    selector="a[href*='development-review']",
                    value=None,
                    url=None,
                    element_info={"label": "Development Review", "role": "link"}
                )
            ],
            variables={},
            success_criteria=[
                {"type": "page_loaded", "timeout": 10000}
            ],
            output_fields=["project_name", "status", "next_meeting"]
        )


# =============================================================================
# SATELLITE BEACH SKILLS (Our Home Jurisdiction)
# =============================================================================

class SatelliteBeachPermitSkills:
    """
    Skills for City of Satellite Beach permit portal.
    This is our home jurisdiction - priority support.
    """
    
    @staticmethod
    def permit_search() -> ZoneWiseSkill:
        """Search Satellite Beach permits"""
        return ZoneWiseSkill(
            skill_id="satbeach_permit_001",
            name="Satellite Beach Permit Search",
            description="Search City of Satellite Beach building permits",
            created_at=datetime.now().isoformat(),
            jurisdiction="satellite_beach",
            portal_type="custom",
            actions=[
                RecordedAction(
                    timestamp="",
                    action_type="navigate",
                    selector=None,
                    value=None,
                    url="https://www.satellitebeach.org/departments/building-department",
                    element_info={"destination": "Satellite Beach Building"}
                ),
                RecordedAction(
                    timestamp="",
                    action_type="click",
                    selector="a[href*='permit']",
                    value=None,
                    url=None,
                    element_info={"label": "Permits", "role": "link"}
                )
            ],
            variables={},
            success_criteria=[
                {"type": "page_loaded", "timeout": 10000}
            ],
            output_fields=["permit_info", "contact", "requirements"]
        )
    
    @staticmethod
    def zoning_info() -> ZoneWiseSkill:
        """Get Satellite Beach zoning information"""
        return ZoneWiseSkill(
            skill_id="satbeach_zoning_001",
            name="Satellite Beach Zoning Info",
            description="Get zoning codes and requirements for Satellite Beach",
            created_at=datetime.now().isoformat(),
            jurisdiction="satellite_beach",
            portal_type="municode",
            actions=[
                RecordedAction(
                    timestamp="",
                    action_type="navigate",
                    selector=None,
                    value=None,
                    url="https://library.municode.com/fl/satellite_beach/codes/code_of_ordinances",
                    element_info={"destination": "Satellite Beach Code"}
                ),
                RecordedAction(
                    timestamp="",
                    action_type="click",
                    selector="a[href*='ZONING']",
                    value=None,
                    url=None,
                    element_info={"label": "Zoning", "role": "link"}
                )
            ],
            variables={},
            success_criteria=[
                {"type": "url_contains", "value": "ZONING"}
            ],
            output_fields=["chapter", "sections", "use_table"]
        )


# =============================================================================
# MULTI-JURISDICTION COMBINED SKILLS
# =============================================================================

class MultiJurisdictionSkills:
    """
    Skills that work across multiple jurisdictions or aggregate data.
    """
    
    @staticmethod
    def comprehensive_permit_search() -> ZoneWiseSkill:
        """Search permits across all 17 Brevard jurisdictions"""
        return ZoneWiseSkill(
            skill_id="multi_permit_001",
            name="Multi-Jurisdiction Permit Search",
            description="Search permits across all Brevard jurisdictions",
            created_at=datetime.now().isoformat(),
            jurisdiction="multi",
            portal_type="aggregator",
            actions=[
                # This skill orchestrates calls to individual jurisdiction skills
                RecordedAction(
                    timestamp="",
                    action_type="orchestrate",
                    selector=None,
                    value="parallel",
                    url=None,
                    element_info={
                        "skills": [
                            "brevard_permit_addr_001",
                            "melbourne_permit_001",
                            "palmbay_permit_001",
                            "satbeach_permit_001"
                        ],
                        "merge_strategy": "union"
                    }
                )
            ],
            variables={"street_address": "", "parcel_id": ""},
            success_criteria=[
                {"type": "all_skills_completed", "min_success": 0.5}
            ],
            output_fields=["jurisdiction", "permit_number", "type", "status", "issue_date"]
        )
    
    @staticmethod
    def zoning_comparison() -> ZoneWiseSkill:
        """Compare zoning across jurisdictions for a property"""
        return ZoneWiseSkill(
            skill_id="zoning_compare_001",
            name="Zoning Comparison",
            description="Compare zoning requirements across jurisdictions",
            created_at=datetime.now().isoformat(),
            jurisdiction="multi",
            portal_type="aggregator",
            actions=[
                RecordedAction(
                    timestamp="",
                    action_type="orchestrate",
                    selector=None,
                    value="sequential",
                    url=None,
                    element_info={
                        "skills": [
                            "brevard_zoning_001",
                            "satbeach_zoning_001"
                        ],
                        "compare_fields": ["setbacks", "height", "lot_coverage"]
                    }
                )
            ],
            variables={"parcel_id": ""},
            success_criteria=[
                {"type": "data_extracted", "min_fields": 3}
            ],
            output_fields=["jurisdiction", "zone_code", "setbacks", "height_limit", "lot_coverage", "permitted_uses"]
        )


# =============================================================================
# ZONEWISE SKILLS LIBRARY
# =============================================================================

class ZoneWiseSkillsLibrary:
    """
    Complete ZoneWise skills library for permit portal automation.
    
    17 Brevard Jurisdictions:
    - Brevard County (unincorporated)
    - Melbourne, Palm Bay, Titusville, Cocoa, Rockledge
    - Satellite Beach, Indian Harbour Beach, Indialantic
    - Melbourne Beach, Cape Canaveral, Cocoa Beach
    - West Melbourne, Malabar, Grant-Valkaria
    - Palm Shores, Melbourne Village
    """
    
    def __init__(self):
        self.brevard_county = BrevardCountyPermitSkills()
        self.melbourne = MelbournePermitSkills()
        self.palm_bay = PalmBayPermitSkills()
        self.satellite_beach = SatelliteBeachPermitSkills()
        self.multi = MultiJurisdictionSkills()
    
    def get_all_skills(self) -> Dict[str, ZoneWiseSkill]:
        """Return all ZoneWise skills"""
        return {
            # Brevard County
            "brevard_permit_search": self.brevard_county.permit_search_by_address(),
            "brevard_permit_detail": self.brevard_county.permit_detail_lookup(),
            "brevard_zoning": self.brevard_county.zoning_verification(),
            
            # Melbourne
            "melbourne_permit_search": self.melbourne.permit_search(),
            "melbourne_site_plan": self.melbourne.site_plan_status(),
            
            # Palm Bay
            "palmbay_permit_search": self.palm_bay.permit_search(),
            "palmbay_dev_review": self.palm_bay.development_review(),
            
            # Satellite Beach (Home jurisdiction)
            "satbeach_permit_search": self.satellite_beach.permit_search(),
            "satbeach_zoning": self.satellite_beach.zoning_info(),
            
            # Multi-jurisdiction
            "multi_permit_search": self.multi.comprehensive_permit_search(),
            "zoning_comparison": self.multi.zoning_comparison(),
        }
    
    def get_skills_by_jurisdiction(self, jurisdiction: str) -> Dict[str, ZoneWiseSkill]:
        """Get skills for specific jurisdiction"""
        all_skills = self.get_all_skills()
        return {k: v for k, v in all_skills.items() if v.jurisdiction == jurisdiction}
    
    def export_all_skills(self, output_dir: str = "skills/zonewise/"):
        """Export all skills to JSON files"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        for skill_name, skill in self.get_all_skills().items():
            filepath = os.path.join(output_dir, f"{skill_name}.json")
            with open(filepath, 'w') as f:
                f.write(skill.to_json())
            print(f"✅ Exported: {filepath}")


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    library = ZoneWiseSkillsLibrary()
    
    print("=" * 60)
    print("ZONEWISE SKILLS LIBRARY")
    print("Permit Portal Automation for 17 Brevard Jurisdictions")
    print("=" * 60)
    print()
    
    all_skills = library.get_all_skills()
    
    print(f"Total Skills: {len(all_skills)}")
    print()
    
    # Group by jurisdiction
    jurisdictions = {}
    for name, skill in all_skills.items():
        jur = skill.jurisdiction
        if jur not in jurisdictions:
            jurisdictions[jur] = []
        jurisdictions[jur].append((name, skill))
    
    for jurisdiction, skills in jurisdictions.items():
        print(f"🏛️ {jurisdiction.upper().replace('_', ' ')} ({len(skills)} skills)")
        for name, skill in skills:
            print(f"   - {name}: {skill.description[:50]}...")
        print()
    
    # Export all
    print("Exporting skills to JSON...")
    library.export_all_skills("skills/zonewise/")
    print()
    print("✅ All ZoneWise skills exported!")
