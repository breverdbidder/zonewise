"""
ZoneWise Zoning Crew - CrewAI Orchestration
Coordinates compliance analysis agents for zoning verification
"""

import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

# Import our compliance agent
from src.agents.compliance_agent import (
    get_property_data,
    get_zoning_rules,
    analyze_compliance,
    map_land_use_to_zoning
)


class ComplianceStatus(Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    NEEDS_VARIANCE = "needs_variance"
    UNKNOWN = "unknown"
    ERROR = "error"


@dataclass
class ComplianceReport:
    """Structured compliance analysis report"""
    address: str
    jurisdiction: str
    zoning_district: str
    proposed_use: str
    status: ComplianceStatus
    findings: List[Dict[str, Any]]
    recommendations: List[str]
    property_data: Optional[Dict[str, Any]] = None
    zoning_rules: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class ZoningResearchAgent:
    """Agent that researches zoning rules for a jurisdiction"""
    
    def __init__(self):
        self.name = "Zoning Research Agent"
        self.role = "Research zoning ordinances and district rules"
    
    def execute(self, jurisdiction: str, district: str) -> Dict[str, Any]:
        """
        Research zoning rules for a district
        
        Args:
            jurisdiction: City/county name
            district: Zoning district code (e.g., R-1, C-1)
            
        Returns:
            Zoning rules dict
        """
        rules = get_zoning_rules(jurisdiction, district)
        return {
            "agent": self.name,
            "jurisdiction": jurisdiction,
            "district": district,
            "rules": rules,
            "success": rules is not None
        }


class PropertyAnalysisAgent:
    """Agent that analyzes property data from BCPAO"""
    
    def __init__(self):
        self.name = "Property Analysis Agent"
        self.role = "Fetch and analyze property records"
    
    def execute(self, address: str) -> Dict[str, Any]:
        """
        Analyze property at given address
        
        Args:
            address: Full property address
            
        Returns:
            Property analysis dict
        """
        property_data = get_property_data(address)
        
        if not property_data:
            return {
                "agent": self.name,
                "address": address,
                "success": False,
                "error": "Property not found in BCPAO"
            }
        
        # Extract key fields
        analysis = {
            "agent": self.name,
            "address": address,
            "success": True,
            "account": property_data.get("account"),
            "owner": property_data.get("owner"),
            "land_use": property_data.get("landUseDescription"),
            "zoning_from_bcpao": property_data.get("zoning"),
            "city": property_data.get("city"),
            "acreage": property_data.get("acreage"),
            "year_built": property_data.get("yearBuilt"),
            "just_value": property_data.get("justValue"),
            "raw_data": property_data
        }
        
        return analysis


class ComplianceCheckAgent:
    """Agent that performs compliance analysis"""
    
    def __init__(self):
        self.name = "Compliance Check Agent"
        self.role = "Analyze zoning compliance for proposed use"
    
    def execute(
        self, 
        property_data: Dict[str, Any],
        zoning_rules: Dict[str, Any],
        proposed_use: str
    ) -> Dict[str, Any]:
        """
        Check if proposed use complies with zoning rules
        
        Args:
            property_data: Property analysis from PropertyAnalysisAgent
            zoning_rules: Rules from ZoningResearchAgent
            proposed_use: What the user wants to do
            
        Returns:
            Compliance analysis dict
        """
        result = analyze_compliance(
            property_data.get("raw_data", {}),
            zoning_rules.get("rules", {}),
            proposed_use
        )
        
        return {
            "agent": self.name,
            "proposed_use": proposed_use,
            "result": result
        }


class ZoningCrew:
    """
    CrewAI-style orchestration for zoning compliance analysis
    
    Coordinates multiple agents to perform comprehensive compliance checks:
    1. Property Analysis Agent - Fetches property data
    2. Zoning Research Agent - Gets applicable zoning rules
    3. Compliance Check Agent - Analyzes compliance
    """
    
    def __init__(self):
        self.property_agent = PropertyAnalysisAgent()
        self.zoning_agent = ZoningResearchAgent()
        self.compliance_agent = ComplianceCheckAgent()
    
    def analyze(
        self,
        address: str,
        proposed_use: str,
        jurisdiction: Optional[str] = None,
        zoning_district: Optional[str] = None
    ) -> ComplianceReport:
        """
        Run full compliance analysis workflow
        
        Args:
            address: Property address to analyze
            proposed_use: Proposed use (e.g., "single family home", "retail store")
            jurisdiction: Override jurisdiction (auto-detected if not provided)
            zoning_district: Override zoning district (auto-detected if not provided)
            
        Returns:
            ComplianceReport with full analysis
        """
        findings = []
        recommendations = []
        
        # Step 1: Property Analysis
        print(f"🏠 {self.property_agent.name}: Analyzing {address}...")
        property_result = self.property_agent.execute(address)
        findings.append({"step": "property_analysis", "result": property_result})
        
        if not property_result.get("success"):
            return ComplianceReport(
                address=address,
                jurisdiction=jurisdiction or "Unknown",
                zoning_district=zoning_district or "Unknown",
                proposed_use=proposed_use,
                status=ComplianceStatus.ERROR,
                findings=findings,
                recommendations=["Verify address and try again"],
                error_message=property_result.get("error", "Property lookup failed")
            )
        
        # Auto-detect jurisdiction and zoning if not provided
        detected_jurisdiction = jurisdiction or property_result.get("city", "Unknown")
        detected_zoning = zoning_district or property_result.get("zoning_from_bcpao")
        
        # If BCPAO doesn't have zoning, try to map from land use
        if not detected_zoning:
            land_use = property_result.get("land_use", "")
            detected_zoning = map_land_use_to_zoning(land_use, detected_jurisdiction)
            if detected_zoning:
                findings.append({
                    "step": "zoning_inference",
                    "note": f"Inferred zoning {detected_zoning} from land use: {land_use}"
                })
        
        if not detected_zoning:
            detected_zoning = "Unknown"
            recommendations.append("Manual zoning verification required - not found in BCPAO")
        
        # Step 2: Zoning Research
        print(f"📋 {self.zoning_agent.name}: Researching {detected_jurisdiction} {detected_zoning}...")
        zoning_result = self.zoning_agent.execute(detected_jurisdiction, detected_zoning)
        findings.append({"step": "zoning_research", "result": zoning_result})
        
        if not zoning_result.get("success"):
            recommendations.append(f"Zoning rules for {detected_jurisdiction} {detected_zoning} not in database")
        
        # Step 3: Compliance Check
        print(f"✅ {self.compliance_agent.name}: Checking compliance for '{proposed_use}'...")
        compliance_result = self.compliance_agent.execute(
            property_result,
            zoning_result,
            proposed_use
        )
        findings.append({"step": "compliance_check", "result": compliance_result})
        
        # Determine final status
        analysis = compliance_result.get("result", {})
        if analysis.get("compliant"):
            status = ComplianceStatus.COMPLIANT
        elif analysis.get("needs_variance"):
            status = ComplianceStatus.NEEDS_VARIANCE
            recommendations.extend(analysis.get("variance_items", []))
        elif analysis.get("issues"):
            status = ComplianceStatus.NON_COMPLIANT
            recommendations.append("Review zoning ordinance for permitted uses")
        else:
            status = ComplianceStatus.UNKNOWN
            recommendations.append("Manual review recommended")
        
        return ComplianceReport(
            address=address,
            jurisdiction=detected_jurisdiction,
            zoning_district=detected_zoning,
            proposed_use=proposed_use,
            status=status,
            findings=findings,
            recommendations=recommendations,
            property_data=property_result,
            zoning_rules=zoning_result.get("rules")
        )
    
    def quick_check(self, address: str, proposed_use: str) -> Dict[str, Any]:
        """
        Quick compliance check returning simple dict
        
        Args:
            address: Property address
            proposed_use: What user wants to do
            
        Returns:
            Simple dict with status and key info
        """
        report = self.analyze(address, proposed_use)
        
        return {
            "address": report.address,
            "jurisdiction": report.jurisdiction,
            "zoning": report.zoning_district,
            "proposed_use": report.proposed_use,
            "status": report.status.value,
            "compliant": report.status == ComplianceStatus.COMPLIANT,
            "recommendations": report.recommendations,
            "error": report.error_message
        }


# Singleton instance
_crew = None

def get_crew() -> ZoningCrew:
    """Get or create ZoningCrew singleton"""
    global _crew
    if _crew is None:
        _crew = ZoningCrew()
    return _crew


def run_compliance_check(address: str, proposed_use: str) -> Dict[str, Any]:
    """
    Convenience function to run compliance check
    
    Args:
        address: Property address
        proposed_use: Proposed use
        
    Returns:
        Compliance result dict
    """
    crew = get_crew()
    return crew.quick_check(address, proposed_use)


# CLI for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python zoning_crew.py <address> <proposed_use>")
        print("Example: python zoning_crew.py '123 Main St, Indian Harbour Beach' 'single family home'")
        sys.exit(1)
    
    address = sys.argv[1]
    proposed_use = sys.argv[2]
    
    print(f"\n{'='*60}")
    print(f"ZONEWISE COMPLIANCE ANALYSIS")
    print(f"{'='*60}")
    print(f"Address: {address}")
    print(f"Proposed Use: {proposed_use}")
    print(f"{'='*60}\n")
    
    result = run_compliance_check(address, proposed_use)
    
    print(f"\n{'='*60}")
    print(f"RESULT: {result['status'].upper()}")
    print(f"{'='*60}")
    print(f"Jurisdiction: {result['jurisdiction']}")
    print(f"Zoning: {result['zoning']}")
    print(f"Compliant: {result['compliant']}")
    if result['recommendations']:
        print(f"\nRecommendations:")
        for rec in result['recommendations']:
            print(f"  • {rec}")
    if result['error']:
        print(f"\nError: {result['error']}")
