---
name: zonewise-district-lookup
description: Looks up zoning district information for Florida properties across 17 jurisdictions and 273 Municode-verified districts. Use when determining permitted uses, setbacks, density limits, height restrictions, or zoning compliance. Returns regulatory requirements from verified municipal codes. Triggers on: zoning lookup, permitted uses, setback requirements, land use, district regulations, development feasibility, zoning code, what can I build.
---

# ZoneWise District Lookup

## Overview

273 verified zoning districts across 17 Florida jurisdictions, all sourced directly from Municode ordinances. No assumptions or interpolations.

## Quick Lookup

```python
from scripts.lookup_district import lookup_district

result = lookup_district(
    jurisdiction="melbourne",
    district_code="R-1A"
)
# Returns: {'permitted_uses': [...], 'setbacks': {...}, 'density': {...}}
```

## Jurisdiction Coverage

| Jurisdiction | Districts | Municode Verified |
|--------------|-----------|-------------------|
| Brevard County (Unincorp) | 28 | ✅ |
| Melbourne | 24 | ✅ |
| Palm Bay | 22 | ✅ |
| Titusville | 18 | ✅ |
| Cocoa | 16 | ✅ |
| Rockledge | 14 | ✅ |
| Satellite Beach | 12 | ✅ |
| Indian Harbour Beach | 10 | ✅ |
| Melbourne Beach | 8 | ✅ |
| Indialantic | 8 | ✅ |
| Cape Canaveral | 12 | ✅ |
| Cocoa Beach | 14 | ✅ |
| West Melbourne | 16 | ✅ |
| Merritt Island (Unincorp) | 18 | ✅ |
| Mims (Unincorp) | 12 | ✅ |
| Palm Shores | 6 | ✅ |
| Grant-Valkaria | 15 | ✅ |

**Total: 273 districts**

## Data Structure

Each district contains:

```json
{
  "jurisdiction": "melbourne",
  "district_code": "R-1A",
  "district_name": "Single-Family Residential",
  "category": "residential",
  "permitted_uses": {
    "by_right": ["single-family dwelling", "home occupation (limited)"],
    "conditional": ["accessory dwelling unit", "day care (family)"],
    "prohibited": ["commercial", "industrial", "multi-family"]
  },
  "dimensional_standards": {
    "min_lot_size_sf": 7500,
    "min_lot_width_ft": 60,
    "max_lot_coverage_pct": 40,
    "max_building_height_ft": 35,
    "setbacks": {
      "front_ft": 25,
      "side_ft": 7.5,
      "rear_ft": 20,
      "corner_side_ft": 15
    }
  },
  "density": {
    "max_units_per_acre": 4.5,
    "far": null
  },
  "parking": {
    "residential_spaces_per_unit": 2
  },
  "municode_url": "https://library.municode.com/fl/melbourne/codes/code_of_ordinances?nodeId=..."
}
```

## Workflow

### 1. Identify Jurisdiction
Use parcel address or coordinates to determine governing jurisdiction.

```python
from scripts.identify_jurisdiction import get_jurisdiction

jurisdiction = get_jurisdiction(
    address="123 Main St, Melbourne, FL 32901"
)
# Returns: "melbourne"
```

### 2. Get District Code
From BCPAO parcel data or user input.

### 3. Lookup District
```python
district = lookup_district(jurisdiction, district_code)
```

### 4. Answer User Query
Map user question to relevant district attributes:
- "What can I build?" → `permitted_uses.by_right`
- "Setback requirements?" → `dimensional_standards.setbacks`
- "Maximum height?" → `dimensional_standards.max_building_height_ft`
- "Can I build an ADU?" → Check `permitted_uses.conditional`

## MCP Tool Integration

ZoneWise exposes these MCP tools:

| Tool | Description |
|------|-------------|
| `zonewise_lookup` | Full district lookup |
| `zonewise_permitted_uses` | Just permitted uses |
| `zonewise_setbacks` | Just setback requirements |
| `zonewise_density` | Density and FAR info |
| `zonewise_jurisdiction` | Identify jurisdiction from address |

## Error Handling

### Unknown District
```python
if not district:
    return {
        "error": "district_not_found",
        "message": f"District '{district_code}' not found in {jurisdiction}",
        "suggestion": "Verify district code with BCPAO or contact jurisdiction"
    }
```

### Unincorporated Areas
Properties in unincorporated Brevard County use county zoning, not municipal codes.

```python
def is_unincorporated(address: str) -> bool:
    """Check if address is in unincorporated area."""
    # Logic based on municipal boundaries
    pass
```

## Data Sources

All district data sourced from:
1. **Municode** - Primary source for ordinance text
2. **BCPAO** - Parcel zoning district assignments
3. **Municipal websites** - Supplementary documentation

**Last verified:** January 2026

## Limitations

- Data reflects current ordinances; pending amendments not included
- Overlay districts may add additional requirements
- Special exceptions require case-by-case research
- PUD (Planned Unit Development) districts have custom rules per development agreement

## See Also

- `references/jurisdiction_mapping.md` - Full jurisdiction boundary definitions
- `references/district_codes.md` - Complete list of all 273 districts
- `references/municode_sources.md` - Direct links to source ordinances
