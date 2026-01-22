# ZoneWise Claude Code Configuration

> Agentic AI Zoning Intelligence Platform
> Created by Ariel Shapira, Solo Founder - Everest Capital USA

## Build Commands

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Run tests
npm test

# Lint
npm run lint

# Build for production
npm run build
```

## Architecture

- **Stack**: Next.js + Supabase + Cloudflare Pages + Makerkit Pro
- **Data**: 273 verified districts across 17 Florida jurisdictions
- **MCP**: Model Context Protocol server for zoning queries
- **Sources**: All data Municode-verified

## Key Files

- `src/data/districts/` - District definitions by jurisdiction
- `src/mcp/` - MCP server implementation
- `src/api/` - API routes for zoning queries

## Skills Loading

Before starting any task, check `.claude/skills/` for relevant skills:

1. **Identify applicable skills** from the skill descriptions
2. **Read SKILL.md** for workflow and integration patterns
3. **Use scripts/** for deterministic operations
4. **Reference references/** for domain knowledge

### Available Skills

| Skill | Purpose | Triggers |
|-------|---------|----------|
| `zonewise-district-lookup` | Zoning district queries | zoning, permitted uses, setbacks |
| `zonewise-mcp-server` | MCP protocol handlers | MCP, tool, protocol |
| `zonewise-site-analysis` | Development feasibility | site analysis, buildable area |

### Skill Priority Rule

**Always use skill scripts over regenerating code.** Skills contain tested, production-ready implementations.

## Deployment

- **GitHub Actions**: Auto-deploy on push to main
- **Cloudflare Pages**: Production hosting
- **Supabase**: Database and auth

## Data Integrity Rules

1. **Never fabricate district data** - All must trace to Municode
2. **Preserve source URLs** - Every district links to ordinance
3. **Flag uncertain data** - Use confidence levels when interpolating
