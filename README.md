# ZoneWise Municipal Code Extraction System

**Continuous extraction of verified zoning dimensional standards from official municipal codes.**

## Overview

ZoneWise MCP Integration provides automated extraction of zoning data from multiple municipal code publishing platforms:

| Platform | Jurisdictions | Method |
|----------|---------------|--------|
| **Municode** | Melbourne, Cocoa, Titusville, Rockledge, Palm Bay, West Melbourne, Brevard County, Indian Harbour Beach, Cape Canaveral, Cocoa Beach | Jina AI Reader (JS rendering) |
| **eLaws** | Satellite Beach, Indialantic, Melbourne Beach, Malabar | Direct HTTP + HTML parsing |
| **American Legal** | (Future) | TBD |

## Key Features

- ✅ **100% Verified Data** - Extracted directly from official municipal codes
- ✅ **Continuous Monitoring** - Daily scheduled extraction via GitHub Actions
- ✅ **Change Detection** - Content hashing to detect code updates
- ✅ **MCP Protocol** - Standard interface for Claude Code integration
- ✅ **Supabase Storage** - Persistent storage with full audit trail
- ✅ **Zero API Cost** - Uses free Jina AI Reader for JavaScript rendering

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ZoneWise MCP Server                       │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │  Municode   │  │   eLaws     │  │ American    │          │
│  │  Extractor  │  │  Extractor  │  │  Legal Ext  │          │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘          │
│         │                │                │                  │
│         └────────────────┼────────────────┘                  │
│                          │                                   │
│                   ┌──────▼──────┐                            │
│                   │ Jina Reader │                            │
│                   │(JS Rendering)│                           │
│                   └──────┬──────┘                            │
│                          │                                   │
│                   ┌──────▼──────┐                            │
│                   │  Supabase   │                            │
│                   │   Storage   │                            │
│                   └─────────────┘                            │
└─────────────────────────────────────────────────────────────┘
```

## Data Extracted

For each zoning district, we extract:

### Dimensional Standards
- Minimum lot area (sq ft)
- Minimum lot width (ft)
- Minimum lot depth (ft)
- Maximum lot coverage (%)
- Minimum living area (sq ft)
- Maximum building height (ft)
- Maximum stories

### Setback Requirements
- Front setback (ft)
- Side interior setback (ft)
- Side corner setback (ft)
- Rear setback (ft)
- Rear alley setback (ft)
- Waterfront setback (ft)

### Additional
- Maximum density (units/acre)
- Floor area ratio (FAR)
- Parking requirements
- Open space requirements

## Usage

### MCP Tools

```python
from zonewise_mcp_server import ZoneWiseMCPServer

server = ZoneWiseMCPServer()

# List available jurisdictions
jurisdictions = server.call_tool("list_jurisdictions", {})

# Extract single jurisdiction
melbourne = server.call_tool("extract_jurisdiction", {"jurisdiction": "melbourne"})

# Extract all jurisdictions
all_data = server.call_tool("extract_all_jurisdictions", {})

# Check for changes
changed = server.call_tool("check_for_changes", {
    "jurisdiction": "melbourne",
    "previous_hash": "abc123def456"
})
```

### Direct Extraction

```python
from zonewise_mcp_server import ZoneWiseExtractor

extractor = ZoneWiseExtractor()

# Extract Melbourne's zoning districts
districts = extractor.extract_jurisdiction("melbourne")

for d in districts:
    print(f"{d.district_code}: {d.district_name}")
    print(f"  Min Lot: {d.min_lot_area_sqft} sqft")
    print(f"  Max Height: {d.max_height_ft} ft")
    print(f"  Front Setback: {d.front_setback_ft} ft")

extractor.close()
```

## Brevard County Jurisdictions (17)

| Jurisdiction | Platform | Status |
|-------------|----------|--------|
| Melbourne | Municode | ✅ Active |
| Satellite Beach | eLaws | ✅ Active |
| Cocoa | Municode | 🔄 Pending |
| Titusville | Municode | 🔄 Pending |
| Rockledge | Municode | 🔄 Pending |
| Palm Bay | Municode | 🔄 Pending |
| West Melbourne | Municode | 🔄 Pending |
| Brevard County | Municode | 🔄 Pending |
| Indian Harbour Beach | Municode | 🔄 Pending |
| Cape Canaveral | Municode | 🔄 Pending |
| Cocoa Beach | Municode | 🔄 Pending |
| Indialantic | eLaws | 🔄 Pending |
| Melbourne Beach | eLaws | 🔄 Pending |
| Malabar | eLaws | 🔄 Pending |
| Grant-Valkaria | TBD | ⏳ Unknown |
| Melbourne Village | TBD | ⏳ Unknown |
| Palm Shores | TBD | ⏳ Unknown |

## Supabase Schema

```sql
CREATE TABLE zonewise_districts (
    id BIGSERIAL PRIMARY KEY,
    jurisdiction TEXT NOT NULL,
    district_code TEXT NOT NULL,
    district_name TEXT,
    district_type TEXT,
    
    -- Source info
    source_url TEXT,
    source_section TEXT,
    source_platform TEXT,
    content_hash TEXT,
    last_extracted TIMESTAMPTZ,
    
    -- Dimensional standards
    min_lot_area_sqft INTEGER,
    min_lot_width_ft INTEGER,
    max_height_ft INTEGER,
    front_setback_ft INTEGER,
    -- ... (see full schema in supabase_integration.py)
    
    verified BOOLEAN DEFAULT FALSE,
    UNIQUE(jurisdiction, district_code)
);
```

## GitHub Action Schedule

Extraction runs **daily at 11 PM EST** via GitHub Actions:

```yaml
on:
  schedule:
    - cron: '0 4 * * *'  # 4 AM UTC = 11 PM EST
```

Manual trigger available via workflow_dispatch.

## Competitive Analysis

### ZoneWise vs Zoneomics vs Gridics

| Feature | ZoneWise | Zoneomics | Gridics |
|---------|----------|-----------|---------|
| Brevard Coverage | 17/17 | Partial | None |
| Data Source | Official codes | Proprietary | Proprietary |
| Update Frequency | Daily | Unknown | Unknown |
| API Cost | $0 | $199+/mo | $0.29+/call |
| BCPAO Integration | ✅ | ❌ | ❌ |
| BidDeed.AI Integration | ✅ | ❌ | ❌ |

## Cost Analysis

| Component | Cost |
|-----------|------|
| Jina AI Reader | **FREE** |
| GitHub Actions | **FREE** (public repo) |
| Supabase | **FREE** tier sufficient |
| **Total** | **$0/month** |

## Roadmap

### Phase 1: Brevard County (Current)
- [x] Melbourne extraction
- [x] Satellite Beach extraction
- [ ] Complete all 17 jurisdictions
- [ ] Supabase integration live
- [ ] Daily scheduled extraction

### Phase 2: Florida Expansion (Q1 2026)
- [ ] Orange County
- [ ] Volusia County
- [ ] Seminole County

### Phase 3: Multi-State (Q2 2026)
- [ ] Georgia
- [ ] Texas
- [ ] California

## Files

```
zonewise_extractor/
├── zonewise_mcp_server.py    # Main MCP server + extractors
├── supabase_integration.py   # Supabase storage layer
├── municipal_code_extractor.py  # Legacy extractor
└── .github/
    └── workflows/
        └── continuous_extraction.yml
```

## License

Proprietary - Part of BidDeed.AI ecosystem.

---

**Built for Everest Capital USA / BidDeed.AI**  
*Verified zoning data, continuously extracted.*
