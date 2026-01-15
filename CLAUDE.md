# ZoneWise - AI Architect Instructions

## Project Identity
- **Product:** ZoneWise - Agentic AI Zoning Compliance Platform
- **Owner:** Ariel Shapira (Solo Founder)
- **Repo:** github.com/breverdbidder/zonewise
- **Stack:** FastAPI + Supabase + Cloudflare + Render + CrewAI/LangGraph

## Current State (Jan 14, 2026)
- ✅ 4 jurisdictions scraped (IHB, Melbourne, Satellite Beach, Brevard County)
- ✅ 37 zoning districts in Supabase
- ✅ 417,540 chars of ordinance content
- 🔄 Next: Build Compliance Agent with real data

## Architecture
```
User Query → FastAPI → CrewAI Agents → Supabase (zoning_districts) → Response
                              ↓
                    Gemini 2.5 Flash (Smart Router)
```

## Key Files
- `src/ingestion/firecrawl_scraper.py` - 17 jurisdiction configs
- `src/ingestion/ordinance_parser.py` - Regex + Gemini LLM parsing
- `zonewise_api.py` - FastAPI entry point
- `pipeline/` - Agent orchestration

## Supabase Tables
- `jurisdictions` - 17 Brevard municipalities
- `zoning_districts` - 37 districts with dimensional data
- `compliance_queries` - User query logs
- `zonewise_dev_sessions` - Development checkpoints

## AI Architect Rules
1. **Zero user actions** - Deploy autonomously via GitHub API
2. **Checkpoint at 75%** - Save progress to Supabase before context limit
3. **Smart Router** - Use Gemini 2.5 Flash (FREE) for 90% of calls
4. **No permission needed** - Execute and report results

## Quick Commands
```bash
# Deploy to GitHub (use GITHUB_TOKEN env var)
curl -X PUT "https://api.github.com/repos/breverdbidder/zonewise/contents/{path}" \
  -H "Authorization: token $GITHUB_TOKEN" \
  -d '{"message":"...","content":"base64..."}'

# Query Supabase (use SUPABASE_SERVICE_KEY env var)
curl "https://mocerqjnksmhcjzxrewo.supabase.co/rest/v1/{table}" \
  -H "apikey: $SUPABASE_SERVICE_KEY"
```

## Priority Tasks
1. Build CrewAI Compliance Agent
2. Test with 3 properties (one per jurisdiction)
3. Deploy to Render.com
4. Scale to 67 FL counties

## Session Checkpointing
When context reaches 75% (150K tokens):
1. Save to `zonewise_dev_sessions` table
2. Include: task, progress, next_steps, code_snippets
3. In new chat: "resume zonewise" → loads checkpoint
