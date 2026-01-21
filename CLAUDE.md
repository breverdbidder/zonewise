# ZoneWise - Claude Code Context

> AI Architect Instructions for Autonomous Development

## 🎯 Project Overview

**ZoneWise** is an AI-powered zoning intelligence platform providing:
- 273 REAL zoning districts (100% Municode-verified)
- 17 Florida jurisdictions
- MCP server integration for LLM access
- SaaS platform via Makerkit Pro

**GTM Target:** Q1 2026

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React + TypeScript + Vite + Tailwind CSS |
| Backend | Supabase (PostgreSQL + Auth + Edge Functions) |
| Maps | Mapbox GL JS |
| AI | Claude API (via Smart Router) |
| Deployment | Cloudflare Pages |
| CI/CD | GitHub Actions |
| Framework | Makerkit Pro ($299) |

## 📁 Key Files

```
zonewise/
├── CLAUDE.md              ← YOU ARE HERE
├── PROJECT_STATE.json     ← Current state (UPDATE THIS)
├── src/
│   ├── lib/supabase.ts    ← Database client
│   ├── hooks/             ← Data fetching hooks
│   ├── components/        ← UI components
│   └── pages/             ← Route pages
├── supabase/
│   └── migrations/        ← Database schema
└── .github/workflows/     ← CI/CD pipelines
```

## ⚡ Development Rules

### ALWAYS Do:
1. **Read PROJECT_STATE.json first** - Know current status before coding
2. **Update PROJECT_STATE.json** - After every significant change
3. **Use real data only** - Never mock/placeholder data
4. **Run `npm run build`** - Before committing
5. **Commit frequently** - Small, descriptive commits
6. **Push to GitHub** - Auto-deploys via Cloudflare

### NEVER Do:
1. ❌ Ask permission - Execute and report results
2. ❌ Use placeholder data - Always real Supabase queries
3. ❌ Leave console.logs - Clean code only
4. ❌ Skip TypeScript types - Full type safety required
5. ❌ Create ZIP files - GitHub is source of truth
6. ❌ Use Google Drive - Everything in repo

## 🗄️ Database Schema

### Tables
```sql
-- Core tables
jurisdictions       -- 17 FL jurisdictions
zoning_districts    -- 273 districts
use_types          -- Permitted/conditional uses
regulations        -- Setbacks, heights, FAR

-- Analytics
user_searches      -- Search history
saved_properties   -- User favorites
```

### Key Queries
```typescript
// Get all districts for a jurisdiction
const { data } = await supabase
  .from('zoning_districts')
  .select('*, jurisdictions(*)')
  .eq('jurisdiction_id', jurisdictionId);

// Search by use type
const { data } = await supabase
  .from('use_types')
  .select('*, zoning_districts(*)')
  .ilike('use_name', `%${search}%`);
```

## 🔑 Environment Variables

```env
VITE_SUPABASE_URL=https://mocerqjnksmhcjzxrewo.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...
VITE_MAPBOX_TOKEN=pk.eyJ...
```

## 📊 Current State

Check `PROJECT_STATE.json` for:
- `current_phase` - Where we are
- `completed_features` - What's done
- `in_progress` - Active work
- `blocked` - Issues needing resolution
- `next_actions` - Priority queue

## 🚀 Deployment

```bash
# Local dev
npm run dev

# Build & deploy (auto via GitHub Actions)
git push origin main
```

**Live URLs:**
- Production: https://zonewise.pages.dev
- Preview: https://{branch}.zonewise.pages.dev

## 🔄 Workflow Integration

### With Lovable
- Lovable syncs from `main` branch
- UI changes in Lovable auto-push to GitHub
- Pull before starting Claude Code session

### With GitHub Actions
- Push to `main` → Auto-deploy to Cloudflare
- All secrets in GitHub Settings

## 📋 Task Execution Pattern

```markdown
1. Read PROJECT_STATE.json
2. Identify highest priority task
3. Implement solution
4. Test locally (npm run build)
5. Commit with descriptive message
6. Update PROJECT_STATE.json
7. Push to GitHub
8. Repeat
```

## 🎨 Design System

| Element | Value |
|---------|-------|
| Primary | #1E3A5F (Navy) |
| Accent | #0D9488 (Teal) |
| Background | #FFFFFF |
| Text | #1F2937 |
| Border Radius | 8px |
| Font | Inter |

## 📞 Escalation

Only escalate to Ariel if:
- Spend > $10 required
- Production data deletion needed
- Schema breaking changes
- Security/auth changes

**Format:** `BLOCKED: [issue]. Tried: [attempts]. Recommend: [solution].`

---

**Last Updated:** 2026-01-20
**AI Architect:** Claude (Sonnet 4.5)
**Product Owner:** Ariel Shapira
---

## Supabase MCP Integration

### Configuration
This repo uses Supabase MCP for direct database operations during Claude Code sessions.
- **Package**: @supabase/mcp-server
- **Token**: SUPABASE_MCP_TOKEN (GitHub Secret)
- **Project**: mocerqjnksmhcjzxrewo.supabase.co

### MCP Operation Rules

#### ✅ AUTONOMOUS (No Approval)
- CREATE TABLE, ALTER TABLE ADD COLUMN
- CREATE INDEX, CREATE VIEW
- SELECT (any query)
- INSERT (any amount)
- UPDATE/DELETE ≤100 rows

#### ⚠️ REQUIRES CONFIRMATION  
- UPDATE/DELETE >100 rows
- Schema changes to core tables
- New foreign key constraints

#### 🚫 NEVER WITHOUT EXPLICIT APPROVAL
- DROP TABLE
- TRUNCATE
- ALTER TABLE DROP COLUMN
- DELETE/UPDATE without WHERE clause

### Audit Logging
Log all schema changes and bulk operations to `activities` table:
```sql
INSERT INTO activities (activity_type, description, metadata, created_at)
VALUES ('mcp_operation', 'description', '{"operation": "..."}', NOW());
```
