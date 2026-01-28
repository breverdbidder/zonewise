# ZoneWise Verification Agent

AI-powered agent for verifying zoning district completeness using **Vercel AI SDK + Firecrawl + Claude**.

## Overview

This agent autonomously:
1. Fetches existing districts from ZoneWise Supabase
2. Searches for official municipal zoning codes (Municode, eLaws, etc.)
3. Scrapes the complete district list from official sources
4. Compares and reports any missing districts
5. Provides confidence ratings and source citations

## Quick Start

```bash
# Install dependencies
npm install

# Set environment variables (or use defaults in code)
export ANTHROPIC_API_KEY="your-key"
export FIRECRAWL_API_KEY="your-firecrawl-api-key"

# Verify a single jurisdiction
npm run verify:rockledge

# Or specify any jurisdiction
node zonewise-verify-agent.js "Melbourne" 1
node zonewise-verify-agent.js "Palm Bay" 2
node zonewise-verify-agent.js "Cocoa Beach" 7

# Batch verify all Brevard County jurisdictions
npm run verify:all
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ZONEWISE VERIFY AGENT                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Claude     │    │  Firecrawl   │    │   Supabase   │  │
│  │  Sonnet 4.5  │◄──►│   Search &   │◄──►│   ZoneWise   │  │
│  │              │    │   Scrape     │    │   Database   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                    │          │
│         ▼                   ▼                    ▼          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              VERCEL AI SDK ORCHESTRATION              │  │
│  │  • Tool calling loop (max 15 steps)                   │  │
│  │  • Automatic context management                       │  │
│  │  • Structured output generation                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Tools Available to Agent

| Tool | Description |
|------|-------------|
| `scrape_page` | Scrape any URL with Firecrawl (handles JS rendering) |
| `search_web` | Search for zoning information |
| `get_existing_districts` | Query ZoneWise Supabase for current data |
| `report_missing_districts` | Structured reporting of gaps |

## Brevard County Jurisdiction IDs

| ID | Jurisdiction | Status |
|----|--------------|--------|
| 1 | Melbourne | ✅ Loaded |
| 2 | Palm Bay | ✅ Loaded |
| 3 | Indian Harbour Beach | ✅ Loaded |
| 4 | Titusville | ✅ Loaded |
| 5 | Cocoa | ✅ Loaded |
| 6 | Satellite Beach | ✅ Loaded |
| 7 | Cocoa Beach | ✅ Loaded |
| 8 | Rockledge | ✅ 14 districts |
| 9 | West Melbourne | ✅ Loaded |
| 10 | Cape Canaveral | ✅ Loaded |
| 11 | Indialantic | ✅ Loaded |
| 12 | Melbourne Beach | ✅ Loaded |
| 13 | Unincorporated Brevard | ✅ Loaded |
| 14 | Malabar | ✅ Loaded |
| 15 | Grant-Valkaria | ✅ Loaded |
| 16 | Palm Shores | ✅ Loaded |
| 17 | Melbourne Village | ✅ Loaded |

## Example Output

```
═══════════════════════════════════════════════════════════════════════
🏛️  ZONEWISE VERIFICATION AGENT
   Jurisdiction: Rockledge (ID: 8)
═══════════════════════════════════════════════════════════════════════

   📋 Fetching existing districts for jurisdiction 8
   🔎 Searching: Rockledge Florida zoning districts land development code
   🔍 Scraping: https://library.municode.com/fl/rockledge/codes/land_development_regulations_

──────────────────────────────────────────────────────────────────────
📊 VERIFICATION REPORT
──────────────────────────────────────────────────────────────────────

## Summary
- **Official districts found**: 16
- **ZoneWise districts**: 14
- **Missing**: 2

## Missing Districts
| Code | Name | Source |
|------|------|--------|
| PS | Public Service | Municode §62.100 |
| CON | Conservation | Municode §62.110 |

## Confidence: HIGH
All sources verified against official Municode publication.

## Recommended Action
Add PS and CON districts to ZoneWise for Rockledge (jurisdiction_id=8)

🔧 Tool calls: 4
```

## Extending to Other Counties

To use for counties outside Brevard:

1. Add jurisdiction to Supabase `jurisdictions` table
2. Run agent with jurisdiction name and ID
3. Agent will auto-discover zoning code platform

```javascript
import { verifyJurisdiction } from './zonewise-verify-agent.js';

// Verify Orange County jurisdiction
await verifyJurisdiction('Orlando', 101);
```

## Cost Optimization

- Uses Claude Sonnet 4.5 (not Opus) for cost efficiency
- Firecrawl: ~500 credits/jurisdiction
- Typical verification: 3-8 tool calls
- Batch mode includes rate limiting

## Integration with ZoneWise Pipeline

This agent is part of the broader ZoneWise MCP ecosystem:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Verify    │────►│   Scrape    │────►│    Load     │
│   Agent     │     │   Agent     │     │   Agent     │
│  (this)     │     │ (Firecrawl) │     │ (Supabase)  │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       └───────────────────┴───────────────────┘
                           │
                    ┌──────▼──────┐
                    │   ZoneWise  │
                    │   MCP API   │
                    └─────────────┘
```

## Troubleshooting

**SSL Errors**: Run in Claude Code (Node environment bypasses Python SSL issues)

**Municode Blocked**: Agent will automatically try eLaws and other sources

**Rate Limits**: Batch mode includes 2-second delays between jurisdictions

---

Built for BidDeed.AI / ZoneWise.AI 2026
