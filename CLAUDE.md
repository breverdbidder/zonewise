# ZoneWise - AI Architect Instructions

## Project Identity
- **Product:** ZoneWise - Agentic AI Zoning Compliance Platform
- **Status:** FIRST GTM PRODUCT (Q1 2026 Launch)
- **Owner:** Ariel Shapira (Solo Founder, Everest Capital USA)
- **Repo:** github.com/breverdbidder/zonewise
- **Stack:** FastAPI + Supabase + Render + MCP

## Current State (Jan 18, 2026)
- ✅ 17 jurisdictions configured
- ✅ 189 zoning districts in Supabase (TEMPLATE DATA - needs real extraction)
- ✅ MCP Server skeleton deployed (`src/mcp/zonewise_mcp_server.py`)
- ✅ Extraction script ready (`scripts/extract_real_data.py`)
- 🔴 CRITICAL: Replace synthetic data with real ordinance values
- 🔄 Next: Extract real data → Test MCP tools → Beta launch

## MCP Architecture (NEW)
```
User Query → AI Assistant (Claude/Cursor) → MCP Client
                                               ↓
                                    ZoneWise MCP Server (Render)
                                               ↓
                                    Supabase (zoning_districts)
                                               ↓
                                         Response
```

### MCP Tools Exposed
| Tool | Description | Parameters |
|------|-------------|------------|
| `lookup_zoning` | Get dimensional standards | jurisdiction, district_code |
| `check_compliance` | Verify structure meets requirements | jurisdiction, district, setbacks, height, lot_size |
| `list_districts` | Get all districts for a jurisdiction | jurisdiction |
| `list_jurisdictions` | Get all Brevard County jurisdictions | none |
| `search_ordinance` | Search ordinance text | jurisdiction, query |

## Data Sources
| Platform | Jurisdictions | Method |
|----------|---------------|--------|
| Municode | Melbourne, IHB, Titusville, Cocoa, Cocoa Beach, Rockledge, West Melbourne, Cape Canaveral, Brevard County | Jina Reader + regex |
| eLaws | Satellite Beach, Indialantic, Melbourne Beach, Malabar | Direct HTTP + BeautifulSoup |
| American Legal | Palm Bay | Jina Reader + custom parser |
| PDF | Grant-Valkaria, Melbourne Village, Palm Shores | Firecrawl + pdfplumber |

## Key Files
- `src/mcp/zonewise_mcp_server.py` - MCP server (5 tools)
- `scripts/extract_real_data.py` - Real data extraction pipeline
- `src/ingestion/firecrawl_scraper.py` - 17 jurisdiction configs
- `src/ingestion/ordinance_parser.py` - Regex + Gemini parsing

## Supabase Tables
- `jurisdictions` - 17 Brevard municipalities
- `zoning_districts` - 189 districts with dimensional data
- `compliance_queries` - User query logs
- `zonewise_dev_sessions` - Development checkpoints

## AI Architect Rules
1. **Zero user actions** - Deploy autonomously via GitHub API
2. **Checkpoint at 75%** - Save progress to Supabase before context limit
3. **Smart Router** - Use Gemini 2.5 Flash (FREE) for 90% of calls
4. **No permission needed** - Execute and report results
5. **Real data priority** - Synthetic data must be replaced before launch

## Quick Commands
```bash
# Deploy to GitHub
curl -X PUT "https://api.github.com/repos/breverdbidder/zonewise/contents/{path}" \
  -H "Authorization: token $GITHUB_TOKEN" \
  -d '{"message":"...","content":"base64..."}'

# Query Supabase
curl "https://mocerqjnksmhcjzxrewo.supabase.co/rest/v1/{table}" \
  -H "apikey: $SUPABASE_SERVICE_KEY"

# Extract real data (single jurisdiction)
python scripts/extract_real_data.py --jurisdiction melbourne

# Extract all jurisdictions
python scripts/extract_real_data.py --all
```

## MVP Timeline (5 weeks)
| Week | Milestone | Deliverables |
|------|-----------|--------------|
| 1 | Data Extraction | 189 districts with real ordinance data |
| 2 | MCP Server | 5 tools deployed to Render.com |
| 3 | Integration Testing | Claude Desktop + Cursor verified |
| 4 | Documentation | README, API docs, example queries |
| 5 | Beta Launch | 10 beta users, feedback collection |

## Success Metrics
- Data Accuracy: 95%+ (spot-check 20 districts)
- MCP Response Time: <2 seconds
- Beta User Satisfaction: 8+/10 NPS
- Revenue Pipeline: $5K MRR potential

## Session Checkpointing
When context reaches 75% (150K tokens):
1. Save to `zonewise_dev_sessions` table
2. Include: task, progress, next_steps, code_snippets
3. In new chat: "resume zonewise" → loads checkpoint
