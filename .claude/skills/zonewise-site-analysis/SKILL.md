---
name: zonewise-site-analysis
description: Performs comprehensive site analysis for development feasibility in Florida. Calculates buildable area considering setbacks, FAR, lot coverage, and height limits. Identifies constraints including flood zones, wetlands, and easements. Determines approval pathway (by-right vs variance). Generates professional site analysis reports. Triggers on: site analysis, buildable area, FAR calculation, development feasibility, setback analysis, lot coverage, site constraints.
---

# ZoneWise Site Analysis

## Overview

Comprehensive development feasibility analysis combining zoning regulations, parcel geometry, and environmental constraints.

## Quick Start

```python
from scripts.analyze_site import analyze_site

result = analyze_site(
    parcel_id="12345678",
    proposed_use="single_family",
    jurisdiction="melbourne"
)
# Returns: feasibility analysis with buildable area, constraints, approval path
```

## Analysis Components

### 1. Parcel Geometry
```python
from scripts.get_parcel_geometry import get_parcel

parcel = get_parcel(parcel_id="12345678")
# Returns:
# {
#   "lot_area_sf": 10000,
#   "lot_width_ft": 80,
#   "lot_depth_ft": 125,
#   "frontage_ft": 80,
#   "shape": "rectangular",
#   "corner_lot": False
# }
```

### 2. Setback Calculation
```python
from scripts.calculate_setbacks import calculate_buildable_envelope

envelope = calculate_buildable_envelope(
    lot_width=80,
    lot_depth=125,
    setbacks={
        "front": 25,
        "rear": 20,
        "side": 7.5
    },
    corner_lot=False
)
# Returns:
# {
#   "buildable_width_ft": 65,
#   "buildable_depth_ft": 80,
#   "buildable_area_sf": 5200
# }
```

### 3. FAR & Coverage Analysis
```python
from scripts.calculate_density import calculate_max_building

max_building = calculate_max_building(
    lot_area_sf=10000,
    far=0.5,
    lot_coverage_pct=40,
    max_height_ft=35
)
# Returns:
# {
#   "max_building_sf": 5000,  # FAR limit
#   "max_footprint_sf": 4000,  # Coverage limit
#   "max_stories": 2,  # Based on height
#   "limiting_factor": "lot_coverage"
# }
```

### 4. Density Calculation
```python
from scripts.calculate_density import calculate_max_units

units = calculate_max_units(
    lot_area_sf=43560,  # 1 acre
    max_units_per_acre=12,
    min_lot_area_per_unit=3500
)
# Returns:
# {
#   "max_units": 12,
#   "by_density": 12,
#   "by_lot_area": 12,
#   "limiting_factor": "density"
# }
```

### 5. Constraint Detection
```python
from scripts.detect_constraints import check_constraints

constraints = check_constraints(parcel_id="12345678")
# Returns:
# {
#   "flood_zone": {"zone": "AE", "bfe": 12},
#   "wetlands": {"present": True, "buffer_ft": 25},
#   "easements": [{"type": "utility", "width_ft": 10}],
#   "historic": False,
#   "coastal": {"cccl": False, "coastal_zone": True}
# }
```

## Full Site Analysis

```python
def analyze_site(
    parcel_id: str,
    proposed_use: str,
    jurisdiction: str,
    proposed_units: int = None
) -> dict:
    """
    Complete site feasibility analysis.
    
    Returns comprehensive analysis including:
    - Zoning compliance
    - Buildable envelope
    - Maximum development potential
    - Constraints and limitations
    - Approval pathway recommendation
    """
    
    # Get parcel data
    parcel = get_parcel(parcel_id)
    
    # Get zoning district
    district = lookup_district(jurisdiction, parcel["zoning"])
    
    # Check use compatibility
    use_status = check_use_allowed(district, proposed_use)
    
    # Calculate buildable envelope
    envelope = calculate_buildable_envelope(
        parcel["lot_width"],
        parcel["lot_depth"],
        district["setbacks"],
        parcel["corner_lot"]
    )
    
    # Calculate max building
    max_building = calculate_max_building(
        parcel["lot_area_sf"],
        district["far"],
        district["lot_coverage_pct"],
        district["max_height_ft"]
    )
    
    # Check constraints
    constraints = check_constraints(parcel_id)
    
    # Adjust for constraints
    adjusted = apply_constraint_adjustments(
        envelope, max_building, constraints
    )
    
    # Determine approval pathway
    pathway = determine_approval_pathway(
        use_status, proposed_units, district, constraints
    )
    
    return {
        "parcel_id": parcel_id,
        "jurisdiction": jurisdiction,
        "district": parcel["zoning"],
        "proposed_use": proposed_use,
        "use_status": use_status,
        "parcel": parcel,
        "buildable_envelope": envelope,
        "max_development": adjusted,
        "constraints": constraints,
        "approval_pathway": pathway,
        "feasibility_score": calculate_feasibility_score(...)
    }
```

## Approval Pathway Logic

```python
def determine_approval_pathway(
    use_status: str,
    proposed_units: int,
    district: dict,
    constraints: dict
) -> dict:
    """Determine required approval process."""
    
    if use_status == "prohibited":
        return {
            "pathway": "not_feasible",
            "reason": "Use not permitted in this district",
            "alternative": "Rezone or find different site"
        }
    
    if use_status == "by_right":
        if not constraints_require_review(constraints):
            return {
                "pathway": "by_right",
                "process": "Building permit only",
                "timeline_days": 30,
                "risk": "low"
            }
    
    if use_status == "conditional":
        return {
            "pathway": "special_exception",
            "process": "Planning board hearing required",
            "timeline_days": 90,
            "risk": "medium",
            "requirements": get_special_exception_requirements(district)
        }
    
    # Variance needed
    return {
        "pathway": "variance",
        "process": "Board of Adjustment hearing",
        "timeline_days": 120,
        "risk": "high",
        "hardship_required": True
    }
```

## Feasibility Score

```python
def calculate_feasibility_score(analysis: dict) -> dict:
    """Calculate 0-100 feasibility score."""
    
    score = 100
    factors = []
    
    # Use status
    if analysis["use_status"] == "prohibited":
        return {"score": 0, "factors": ["Use not permitted"]}
    elif analysis["use_status"] == "conditional":
        score -= 20
        factors.append("Conditional use requires approval (-20)")
    
    # Constraints
    if analysis["constraints"]["flood_zone"]["zone"] in ["AE", "VE"]:
        score -= 15
        factors.append("High-risk flood zone (-15)")
    
    if analysis["constraints"]["wetlands"]["present"]:
        score -= 25
        factors.append("Wetlands present (-25)")
    
    # Buildable area ratio
    buildable_ratio = (
        analysis["buildable_envelope"]["buildable_area_sf"] / 
        analysis["parcel"]["lot_area_sf"]
    )
    if buildable_ratio < 0.3:
        score -= 20
        factors.append("Limited buildable area (-20)")
    
    return {
        "score": max(0, score),
        "rating": get_rating(score),
        "factors": factors
    }

def get_rating(score: int) -> str:
    if score >= 80: return "Excellent"
    if score >= 60: return "Good"
    if score >= 40: return "Fair"
    if score >= 20: return "Poor"
    return "Not Feasible"
```

## Report Generation

```python
from scripts.generate_site_report import generate_report

report_path = generate_report(
    analysis=site_analysis,
    output_format="docx",
    include_maps=True
)
```

### Report Sections
1. Executive Summary
2. Property Information
3. Zoning Analysis
4. Development Potential
5. Constraints Map
6. Approval Pathway
7. Recommendations
8. Appendix (Municode references)

## Data Sources

| Data | Source |
|------|--------|
| Parcel geometry | BCPAO GIS |
| Zoning district | ZoneWise DB |
| Flood zones | FEMA NFHL |
| Wetlands | NWI / SJRWMD |
| Easements | BCPAO recorded plats |

## Integration

- **District Lookup**: Get zoning regulations
- **MCP Server**: Expose via `zonewise_site_analysis` tool
- **BidDeed.AI**: Evaluate foreclosure properties for development

## Limitations

- Analysis based on available data; site survey recommended
- Does not account for pending ordinance changes
- PUD districts require individual agreement review
- Coastal construction requires additional review
