#!/bin/bash
# Install BidDeed data sources into CraftAgents (zonewise-desktop)
# Run from zonewise-desktop repo root
# Usage: bash scripts/install-biddeed-sources.sh

WS_DIR="${HOME}/.craft-agent/workspaces"

# Find the active workspace
WS_ID=$(ls "$WS_DIR" 2>/dev/null | head -1)
if [ -z "$WS_ID" ]; then
  echo "No CraftAgents workspace found at $WS_DIR"
  echo "Open CraftAgents desktop app first to create a workspace"
  exit 1
fi

SOURCES_DIR="$WS_DIR/$WS_ID/sources"
echo "Installing BidDeed sources into workspace: $WS_ID"

# ── 1. BidDeed External API ──────────────────────────────────────────────────

mkdir -p "$SOURCES_DIR/biddeed-api"

cat > "$SOURCES_DIR/biddeed-api/config.json" << 'EOF'
{
  "id": "biddeed_api_001",
  "name": "BidDeed.AI API",
  "slug": "biddeed-api",
  "enabled": true,
  "provider": "biddeed",
  "type": "api",
  "icon": "🏛️",
  "tagline": "BidDeed.AI auction intelligence — foreclosures, tax deeds, ML scores, max bid",
  "api": {
    "baseUrl": "https://biddeed-api.onrender.com/",
    "authType": "bearer",
    "testEndpoint": {
      "method": "GET",
      "path": "api/v1/health"
    }
  },
  "isAuthenticated": false,
  "connectionStatus": "needs_auth",
  "createdAt": 1740614400000
}
EOF

cat > "$SOURCES_DIR/biddeed-api/guide.md" << 'EOF'
# BidDeed.AI API

BidDeed.AI's external API for the Ariel Shapira investment workflow. Provides
auction data, ML-scored recommendations, and DOCX reports for ZoneWise integration.

## Authentication
Bearer token (BIDDEED_API_KEY from GitHub Secrets / .env)

## Endpoints

### GET /api/v1/health
Pipeline health check. No auth required.
Returns: status, last_run_at, auctions_last_24h, error_count_24h

### GET /api/v1/auctions
Paginated auction list with filters.
Params: county, auction_type, recommendation (BID|REVIEW|SKIP), date_from, date_to
Example: "Show me all BID-rated foreclosures in Brevard this week"

### GET /api/v1/auctions/{case_number}
Full property detail: lien stack, HOA warning, max bid, ARV, BCPAO photo.
Example: "Get full details for case 2026-CA-001234"

### GET /api/v1/auctions/county/{county}
All active auctions for a county (for map overlay).
Example: "Load all Orange County auctions for the map"

### GET /api/v1/auctions/{case_number}/report
DOCX report download URL (generates on demand if missing).
Example: "Download the report for case 2026-CA-001234"

### POST /api/v1/pipeline/trigger
Trigger the nightly scraper for a specific county.
Example: "Trigger a scrape for Hillsborough County"

## Key Rules
- HOA plaintiff = senior mortgage survives. Always surface this warning.
- max_bid = (ARV×70%) - repairs - $10K - MIN($25K, 15%×ARV)
- BID ≥75% bid/judgment ratio | REVIEW 60-74% | SKIP <60%
EOF

cat > "$SOURCES_DIR/biddeed-api/permissions.json" << 'EOF'
{
  "allowedApiEndpoints": [
    { "method": "GET", "path": ".*", "comment": "All GET operations are read-only" },
    { "method": "POST", "path": "api/v1/pipeline/trigger", "comment": "Pipeline trigger — Ariel only" }
  ]
}
EOF

echo "✅ biddeed-api source installed"

# ── 2. Supabase Direct ───────────────────────────────────────────────────────

mkdir -p "$SOURCES_DIR/supabase-biddeed"

cat > "$SOURCES_DIR/supabase-biddeed/config.json" << 'EOF'
{
  "id": "supabase_biddeed_001",
  "name": "Supabase — BidDeed + ZoneWise",
  "slug": "supabase-biddeed",
  "enabled": true,
  "provider": "supabase",
  "type": "api",
  "icon": "🗄️",
  "tagline": "Direct Supabase access — auctions, insights, capability registry, ZoneWise data",
  "api": {
    "baseUrl": "https://mocerqjnksmhcjzxrewo.supabase.co/rest/v1/",
    "authType": "header",
    "headerNames": ["apikey", "Authorization"],
    "testEndpoint": {
      "method": "GET",
      "path": "capabilities?select=slug,status&limit=5"
    }
  },
  "isAuthenticated": false,
  "connectionStatus": "needs_auth",
  "createdAt": 1740614400000
}
EOF

cat > "$SOURCES_DIR/supabase-biddeed/guide.md" << 'EOF'
# Supabase — Everest Capital Shared Database

Single Supabase instance for BidDeed.AI and ZoneWise.AI.
URL: mocerqjnksmhcjzxrewo.supabase.co

## Auth Headers
- apikey: SUPABASE_SERVICE_ROLE_KEY
- Authorization: Bearer SUPABASE_SERVICE_ROLE_KEY

## Key Tables

### BidDeed tables
- multi_county_auctions — active auction listings (67 counties)
- historical_auctions — past auctions + ML scores
- insights — all pipeline logs and errors

### ZoneWise tables  
- districts — 5,321 zoning districts
- jurisdictions — 1,100 Florida jurisdictions
- mcp_requests — MCP server request logs

### Shared tables
- capabilities — capability registry (DiscoverWise, LienWise, etc.)
- data_sources — registered data sources (RealForeclose, BCPAO, etc.)
- master_index — cross-repo file index (single source of truth)
- claude_context_checkpoints — context boot checkpoints

## Common Queries
- "What BID auctions are in Brevard tonight?"
  → GET multi_county_auctions?county=eq.Brevard&recommendation=eq.BID&auction_date=gte.[today]
  
- "Show capability registry status"
  → GET capabilities?select=slug,name,status&order=sort_order

- "Last 10 pipeline errors"
  → GET insights?status=eq.ERROR&order=created_at.desc&limit=10

- "Active zoning districts in Orange County"
  → GET districts?county=eq.Orange&select=name,code,permitted_uses
EOF

cat > "$SOURCES_DIR/supabase-biddeed/permissions.json" << 'EOF'
{
  "allowedApiEndpoints": [
    { "method": "GET", "path": ".*", "comment": "All SELECT operations" },
    { "method": "POST", "path": "insights", "comment": "Log to insights table" },
    { "method": "PATCH", "path": "capabilities", "comment": "Update capability status" }
  ]
}
EOF

echo "✅ supabase-biddeed source installed"

# ── 3. GitHub — breverdbidder ────────────────────────────────────────────────

mkdir -p "$SOURCES_DIR/github-everest"

cat > "$SOURCES_DIR/github-everest/config.json" << 'EOF'
{
  "id": "github_everest_001",
  "name": "GitHub — breverdbidder",
  "slug": "github-everest",
  "enabled": true,
  "provider": "github",
  "type": "mcp",
  "icon": "🐙",
  "tagline": "All Everest Capital repos — BidDeed, ZoneWise, skills, tools",
  "mcp": {
    "url": "https://api.githubcopilot.com/mcp/",
    "authType": "bearer"
  },
  "isAuthenticated": false,
  "connectionStatus": "needs_auth",
  "createdAt": 1740614400000
}
EOF

cat > "$SOURCES_DIR/github-everest/guide.md" << 'EOF'
# GitHub — breverdbidder

All repos for Ariel Shapira's Everest Capital USA / BidDeed.AI / ZoneWise.AI stack.

## Auth
Bearer token: use GITHUB_PAT from env (ghp_ij7Lpk9Nv8... — repo+workflow scope)

## Key Repos
- breverdbidder/brevard-bidder-scraper — BidDeed.AI pipeline (Python)
- breverdbidder/zonewise — ZoneWise monorepo (TypeScript)
- breverdbidder/zonewise-agents — FastAPI agents (Python)
- breverdbidder/zonewise-web — Marketing site (Next.js)
- breverdbidder/zonewise-desktop — CraftAgents fork (Electron)
- breverdbidder/ssot-task-manager — Shared task queue (SSOT)

## Workflow
- Primary CI/CD: GitHub Actions (auto-deploy on push to main)
- Skills sync: .github/workflows/sync-claude-skills.yml
- Nightly pipeline: .github/workflows/nightly-auction-scrape.yml

## Common Tasks
- "What's the status of the last workflow run?"
- "Open issues in zonewise-agents?"
- "Show recent commits to brevard-bidder-scraper"
- "Trigger the nightly scrape workflow"
EOF

cat > "$SOURCES_DIR/github-everest/permissions.json" << 'EOF'
{
  "allowedMcpPatterns": [
    { "pattern": "list", "comment": "List repos, issues, PRs, workflows" },
    { "pattern": "get", "comment": "Get specific items" },
    { "pattern": "search", "comment": "Search across repos" },
    { "pattern": "create_issue", "comment": "Create GitHub issues (Traycer workflow)" },
    { "pattern": "create_pull_request", "comment": "Create PRs for skill syncs" }
  ]
}
EOF

echo "✅ github-everest source installed"

echo ""
echo "══════════════════════════════════════════"
echo "BidDeed sources installed into CraftAgents"
echo "Workspace: $WS_ID"
echo ""
echo "Next steps:"
echo "1. Open CraftAgents desktop app"
echo "2. Go to Sources panel"
echo "3. Authenticate each source:"
echo "   - biddeed-api: Enter BIDDEED_API_KEY"
echo "   - supabase-biddeed: Enter apikey + Bearer SUPABASE_SERVICE_ROLE_KEY"
echo "   - github-everest: Enter GITHUB_PAT"
echo "══════════════════════════════════════════"
