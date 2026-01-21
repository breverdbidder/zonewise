# CLAUDE.md - AI Architect Instructions for ZoneWise.ai

## 🎯 Project Overview

ZoneWise.ai is an AI-powered zoning intelligence platform. This document provides context for Claude (AI Architect) and Claude Code (Agentic Engineer) when working on this repository.

## 🏗️ Architecture Principles

### Agentic Development
- **Autonomous execution:** Make decisions and execute without asking permission
- **Minimal human-in-the-loop:** Ariel reviews weekly summaries, not daily tasks
- **Self-documenting:** Update PROJECT_STATE.json after significant changes

### Stack Decisions (LOCKED)
| Component | Choice | Rationale |
|-----------|--------|-----------|
| Framework | Next.js 14 (App Router) | SSR, API routes, Vercel-compatible |
| Database | Supabase | PostgreSQL + Auth + Realtime |
| Styling | Tailwind CSS | Utility-first, shadcn/ui compatible |
| Auth/Billing | Makerkit Pro | Pre-built SaaS boilerplate |
| AI | Claude Sonnet 4.5 | Best reasoning for zoning interpretation |
| Hosting | Cloudflare Pages | Edge performance, free tier |
| Domain | zonewise.ai | Cloudflare Registrar |

## 📋 Development Rules

### DO ✅
- Commit frequently with descriptive messages
- Run tests before pushing
- Update PROJECT_STATE.json with decisions
- Use TypeScript strict mode
- Follow existing code patterns
- Deploy to Cloudflare Pages automatically

### DON'T ❌
- Ask permission for routine tasks
- Create ZIP files or use Google Drive
- Install packages without checking alternatives
- Skip error handling
- Hardcode API keys (use environment variables)

## 🔑 Environment Variables

```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=

# Anthropic
ANTHROPIC_API_KEY=

# Stripe
STRIPE_SECRET_KEY=
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=
STRIPE_WEBHOOK_SECRET=
```

## 📊 Data Model

### Core Tables

```sql
-- Jurisdictions (cities/counties)
CREATE TABLE jurisdictions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  state TEXT DEFAULT 'FL',
  municode_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Zoning Districts
CREATE TABLE zoning_districts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  jurisdiction_id UUID REFERENCES jurisdictions(id),
  code TEXT NOT NULL,           -- e.g., "R-1", "C-2"
  name TEXT NOT NULL,           -- e.g., "Single Family Residential"
  description TEXT,
  allowed_uses JSONB,
  setbacks JSONB,
  height_limits JSONB,
  lot_requirements JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User Queries (for analytics)
CREATE TABLE queries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id),
  question TEXT NOT NULL,
  jurisdiction_id UUID REFERENCES jurisdictions(id),
  district_code TEXT,
  response TEXT,
  tokens_used INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 🚀 Deployment

### Cloudflare Pages
- **Production:** Automatic deploy on `main` branch push
- **Preview:** Automatic deploy on PR creation
- **Build command:** `npm run build`
- **Output directory:** `.next`

### GitHub Actions
- CI runs on every push
- Tests must pass before merge
- Auto-deploy to Cloudflare Pages

## 📁 Key Files

| File | Purpose |
|------|---------|
| `PROJECT_STATE.json` | Current state, recent decisions, blockers |
| `CLAUDE.md` | This file - AI context |
| `docs/PRD.md` | Product requirements document |
| `src/lib/zoning-ai.ts` | Core AI interpretation logic |
| `src/lib/supabase.ts` | Database client |

## 🔄 Workflow

### Claude Code Session Flow
1. Read `PROJECT_STATE.json` for current context
2. Check `docs/` for requirements
3. Implement features/fixes
4. Update `PROJECT_STATE.json`
5. Commit and push
6. Cloudflare auto-deploys

### Escalation Protocol
1. Try to solve autonomously (3 attempts)
2. Log blocker to `PROJECT_STATE.json`
3. Only then surface to Ariel with:
   - Problem description
   - Attempts made
   - Recommended solution

## 📈 Success Metrics

- **Query accuracy:** >95% correct zoning interpretations
- **Response time:** <3 seconds for standard queries
- **Uptime:** 99.9%
- **User satisfaction:** >4.5/5 rating

---

*Last updated: 2026-01-21*
