# ZoneWise Development Workflow

> **Connecting GitHub ↔ Claude Code ↔ Lovable for Rapid AI-Powered Development**

[![Stack](https://img.shields.io/badge/Stack-GitHub%20%7C%20Supabase%20%7C%20Cloudflare-blue)](https://github.com/breverdbidder/zonewise)
[![Lovable](https://img.shields.io/badge/Frontend-Lovable.dev-purple)](https://lovable.dev)
[![Claude](https://img.shields.io/badge/AI-Claude%20Code-orange)](https://claude.ai)

## 🎯 Overview

ZoneWise uses a **three-way sync workflow** between:
- **GitHub** - Source of truth, version control, CI/CD
- **Claude Code** - AI-powered development (7-hour autonomous sessions)
- **Lovable** - Visual frontend builder with AI assistance

This workflow enables **zero-code handoffs** between visual design and backend development.

---

## 📁 Repository Structure

```
zonewise/
├── .github/
│   └── workflows/
│       ├── deploy.yml           # Cloudflare Pages deployment
│       ├── sync-lovable.yml     # Auto-sync from Lovable
│       └── nightly-scraper.yml  # Daily 11PM EST data refresh
├── docs/
│   ├── ARCHITECTURE.md          # System design & data flow
│   ├── LOVABLE_PROMPTS/         # Prompt engineering templates
│   │   ├── 01_FOUNDATION.md
│   │   ├── 02_DATA_LAYER.md
│   │   ├── 03_UI_COMPONENTS.md
│   │   ├── 04_MAPS_LAYERS.md
│   │   └── 05_DEPLOYMENT.md
│   └── CLAUDE_CONTEXT.md        # Context for Claude Code sessions
├── src/
│   ├── components/              # React components
│   ├── hooks/                   # Custom React hooks
│   ├── pages/                   # Page components
│   ├── lib/                     # Utilities & Supabase client
│   └── types/                   # TypeScript definitions
├── supabase/
│   └── migrations/              # Database schema
├── .lovable/
│   └── context.md               # Lovable project context
├── CLAUDE.md                    # Claude Code instructions
├── PROJECT_STATE.json           # Current development state
└── package.json
```

---

## 🔗 Step 1: Initial GitHub Setup

### Create Repository
```bash
# Option A: Via GitHub CLI
gh repo create breverdbidder/zonewise --public --description "AI-Powered Zoning Intelligence Platform"

# Option B: Via Web
# Go to github.com/new → Name: zonewise → Create
```

### Clone Locally
```bash
git clone https://github.com/breverdbidder/zonewise.git
cd zonewise
```

### Initialize Project
```bash
# Create React + TypeScript + Vite project
npm create vite@latest . -- --template react-ts

# Install dependencies
npm install @supabase/supabase-js mapbox-gl lucide-react
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Initial commit
git add .
git commit -m "Initial project setup"
git push -u origin main
```

---

## 💻 Step 2: Claude Code Integration

### CLAUDE.md Configuration
Create `CLAUDE.md` in repo root:

```markdown
# ZoneWise - Claude Code Context

## Project Overview
ZoneWise is an AI-powered zoning intelligence platform covering 273 districts 
across 17 Florida jurisdictions (100% Municode-verified).

## Tech Stack
- Frontend: React + TypeScript + Vite + Tailwind CSS
- Backend: Supabase (PostgreSQL + Auth + Storage)
- Maps: Mapbox GL JS
- Deployment: Cloudflare Pages
- CI/CD: GitHub Actions

## Development Rules
1. **Autonomous Execution** - Make decisions, don't ask permission
2. **Real Data Only** - Never use placeholder/mock data
3. **Update PROJECT_STATE.json** - After every significant change
4. **Test Before Push** - Run `npm run build` before committing
5. **Minimal Engineering** - Simplest solution that works

## Key Files
- `src/lib/supabase.ts` - Database client
- `src/hooks/useZoningData.ts` - Data fetching
- `PROJECT_STATE.json` - Current state tracking

## Environment Variables
- VITE_SUPABASE_URL
- VITE_SUPABASE_ANON_KEY
- VITE_MAPBOX_TOKEN
```

### PROJECT_STATE.json
```json
{
  "version": "1.0.0",
  "last_updated": "2026-01-20T00:00:00Z",
  "current_phase": "MVP",
  "completed_features": [],
  "in_progress": [],
  "blocked": [],
  "recent_decisions": [],
  "next_actions": [
    "Set up Supabase tables",
    "Create zoning district components",
    "Integrate Mapbox layers"
  ]
}
```

### Claude Code Session Workflow
```bash
# Start autonomous session
claude code --repo breverdbidder/zonewise --hours 7

# Claude Code will:
# 1. Read CLAUDE.md for context
# 2. Check PROJECT_STATE.json for current status
# 3. Execute tasks autonomously
# 4. Commit changes with descriptive messages
# 5. Update PROJECT_STATE.json
# 6. Push to GitHub
```

---

## 🎨 Step 3: Lovable Integration

### Connect Lovable to GitHub

1. **Open Lovable.dev** → Create New Project
2. **Settings** ⚙️ → **GitHub Integration**
3. **Connect to GitHub** → Authorize
4. **Select Repository**: `breverdbidder/zonewise`
5. **Branch**: `main`
6. **Enable Auto-Sync**: ✅

### Lovable Context File
Create `.lovable/context.md`:

```markdown
# ZoneWise Lovable Context

## Design System
- Colors: Navy (#1E3A5F), Teal (#0D9488), White (#FFFFFF)
- Font: Inter (headings), System UI (body)
- Border Radius: 8px (cards), 4px (buttons)
- Shadows: sm for cards, md for modals

## Component Patterns
- Use Tailwind CSS utility classes
- Prefer composition over inheritance
- Keep components under 200 lines
- Extract hooks for data fetching

## Data Integration
- Supabase client: `src/lib/supabase.ts`
- All data fetching via custom hooks
- Never hardcode data in components

## Map Integration
- Mapbox GL JS for all maps
- Layer toggle controls in sidebar
- Responsive: full-width on mobile
```

### Lovable Prompt Templates

#### Prompt 01: Foundation
```
Create a React + TypeScript + Tailwind CSS application for ZoneWise, 
a zoning intelligence platform.

Requirements:
- Responsive layout with sidebar navigation
- Dark/light mode toggle
- Supabase authentication
- Environment variables for API keys

Tech stack:
- Vite for bundling
- React Router for navigation
- Lucide React for icons
- Tailwind CSS for styling

Pages needed:
- Dashboard (/)
- Map View (/map)
- Districts (/districts)
- Settings (/settings)
```

#### Prompt 02: Data Layer
```
Add Supabase integration to ZoneWise.

Create these hooks:
- useZoningDistricts() - Fetch all districts
- useDistrictDetails(id) - Fetch single district
- useJurisdictions() - Fetch jurisdiction list

Supabase tables:
- zoning_districts (id, name, code, jurisdiction_id, regulations)
- jurisdictions (id, name, county, state, municode_verified)
- use_types (id, district_id, use_name, permitted, conditional)

Add loading states, error handling, and TypeScript types.
```

#### Prompt 03: Map Integration
```
Add Mapbox GL JS map to ZoneWise with these features:

1. Base map with district boundaries
2. Color-coded zones by type (residential, commercial, industrial)
3. Click handler showing district details popup
4. Layer toggle controls in sidebar
5. Search by address with geocoding
6. Responsive: full-width on mobile, split-screen on desktop

Use environment variable VITE_MAPBOX_TOKEN for API key.
```

---

## 🔄 Workflow: Three-Way Sync

### From Claude Code → GitHub → Lovable
```bash
# Claude Code makes changes
git add .
git commit -m "feat: Add district filtering"
git push origin main

# Lovable auto-syncs within 2-5 minutes
# Verify in Lovable: Settings → GitHub → Last Sync
```

### From Lovable → GitHub → Claude Code
```bash
# After making changes in Lovable:
# 1. Lovable auto-commits to GitHub
# 2. Pull changes locally:
git pull origin main

# 3. Claude Code picks up changes on next session
```

### Conflict Resolution
```bash
# If conflicts occur:
git pull origin main

# Resolve conflicts in affected files
# Keep Lovable's UI changes, Claude Code's logic

git add .
git commit -m "merge: Resolve Lovable/Claude Code conflicts"
git push origin main
```

---

## 🚀 Deployment

### GitHub Actions → Cloudflare Pages

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Cloudflare Pages

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      
      - name: Install Dependencies
        run: npm ci
      
      - name: Build
        run: npm run build
        env:
          VITE_SUPABASE_URL: ${{ secrets.VITE_SUPABASE_URL }}
          VITE_SUPABASE_ANON_KEY: ${{ secrets.VITE_SUPABASE_ANON_KEY }}
          VITE_MAPBOX_TOKEN: ${{ secrets.VITE_MAPBOX_TOKEN }}
      
      - name: Deploy to Cloudflare Pages
        uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          projectName: zonewise
          directory: dist
```

### Environment Variables

Set in GitHub Secrets (`Settings → Secrets → Actions`):
- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_ANON_KEY`
- `VITE_MAPBOX_TOKEN`
- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`

---

## 📊 Database Schema

### Supabase Tables

```sql
-- Jurisdictions
CREATE TABLE jurisdictions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  county TEXT NOT NULL,
  state TEXT DEFAULT 'FL',
  municode_url TEXT,
  municode_verified BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Zoning Districts
CREATE TABLE zoning_districts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  jurisdiction_id UUID REFERENCES jurisdictions(id),
  code TEXT NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  color TEXT, -- Hex color for map
  regulations JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Use Types
CREATE TABLE use_types (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  district_id UUID REFERENCES zoning_districts(id),
  use_name TEXT NOT NULL,
  category TEXT, -- residential, commercial, industrial
  permitted BOOLEAN DEFAULT false,
  conditional BOOLEAN DEFAULT false,
  notes TEXT
);

-- Indexes
CREATE INDEX idx_districts_jurisdiction ON zoning_districts(jurisdiction_id);
CREATE INDEX idx_use_types_district ON use_types(district_id);
```

---

## 🛠️ Development Commands

```bash
# Local development
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type checking
npm run typecheck

# Linting
npm run lint

# Format code
npm run format
```

---

## 📝 Git Workflow

### Branch Naming
- `feat/` - New features
- `fix/` - Bug fixes
- `refactor/` - Code refactoring
- `docs/` - Documentation updates

### Commit Messages
```
feat: Add district search functionality
fix: Resolve map zoom on mobile
refactor: Extract useMapLayers hook
docs: Update API documentation
```

### Pull Request Template
```markdown
## Summary
Brief description of changes

## Changes
- [ ] Feature 1
- [ ] Feature 2

## Testing
- [ ] Tested locally
- [ ] Build passes
- [ ] No TypeScript errors

## Screenshots
(if applicable)
```

---

## 🔧 Troubleshooting

### Lovable Not Syncing
1. Check GitHub connection in Settings
2. Verify branch is `main`
3. Manual sync: Settings → GitHub → Sync Now

### Claude Code Context Lost
1. Check `CLAUDE.md` exists in repo root
2. Verify `PROJECT_STATE.json` is up to date
3. Add context to conversation: "Read CLAUDE.md first"

### Build Failures
1. Check environment variables in GitHub Secrets
2. Verify all dependencies in `package.json`
3. Run `npm run build` locally to debug

### Map Not Loading
1. Verify `VITE_MAPBOX_TOKEN` is set
2. Check Mapbox token permissions (styles:read, etc.)
3. Inspect browser console for errors

---

## 📚 Resources

- [Lovable Documentation](https://docs.lovable.dev)
- [Claude Code Guide](https://docs.anthropic.com/claude-code)
- [Supabase Docs](https://supabase.com/docs)
- [Mapbox GL JS](https://docs.mapbox.com/mapbox-gl-js)
- [Cloudflare Pages](https://developers.cloudflare.com/pages)

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

**Built with 🤖 by Ariel Shapira & Claude AI**
