# ZoneWise V3 - Claude Code Instructions

## Project Overview

**ZoneWise V3** is an AI-powered split-screen zoning intelligence platform combining:
- **Frontend**: Next.js 15 + ShadCNBlocks Premium + Mapbox GL JS
- **Backend**: FastAPI + LangGraph multi-agent system
- **Database**: Supabase PostgreSQL + PostGIS
- **Deployment**: Cloudflare Pages (frontend) + Render.com (backend)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND (Next.js 15 + ShadCNBlocks)                       │
│  ├── Split-Screen Layout (60% Map / 40% Chat)               │
│  ├── MapPanel (Mapbox GL choropleth)                        │
│  ├── ChatPanel (NLP interface)                              │
│  └── Bidirectional sync via Zustand                         │
└─────────────────────────────────────────────────────────────┘
                         ↓ REST + WebSocket
┌─────────────────────────────────────────────────────────────┐
│  BACKEND (FastAPI + LangGraph)                              │
│  ├── Coordinator Agent (task decomposition)                 │
│  ├── Zoning Agent (zone lookup, rules)                      │
│  ├── CMA Agent (comparable analysis)                        │
│  ├── HBU Agent (highest & best use)                         │
│  ├── ML Agent (XGBoost predictions)                         │
│  └── Reporter Agent (response synthesis)                    │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  DATABASE (Supabase PostgreSQL + PostGIS)                   │
│  ├── fl_parcels (10M+ Florida parcels)                      │
│  ├── fl_zoning_districts (GIS polygons)                     │
│  ├── chatbot_conversations, chatbot_messages                │
│  └── deployments (CI/CD tracking)                           │
└─────────────────────────────────────────────────────────────┘
```

## Zero-Human-In-The-Loop Rules

### Execute Autonomously (No Permission Needed)

- Bug fixes and error resolution
- Code refactoring and optimization
- GitHub Actions workflow updates
- Documentation updates
- Test creation and execution
- Dependency updates
- Performance improvements
- Database queries (read operations)
- Report generation
- Git commits and pushes
- Cloudflare Pages deployments
- Supabase inserts/updates

### Require Approval

- Spend >$10 (new API subscriptions)
- Schema changes to production tables
- Deleting production data
- Security/authentication changes
- API key rotations
- New third-party service integrations

## Repository Structure

```
zonewise-v3/
├── .github/
│   └── workflows/
│       └── deploy.yml          # CI/CD pipeline
├── frontend/
│   ├── app/                    # Next.js App Router
│   ├── components/
│   │   ├── map/               # MapPanel, controls
│   │   ├── chat/              # ChatPanel, messages
│   │   ├── ui/                # ShadCNBlocks components
│   │   └── shared/            # SplitScreen, layout
│   ├── hooks/                 # Custom React hooks
│   ├── stores/                # Zustand state
│   ├── lib/                   # Utilities
│   └── package.json
├── backend/
│   ├── agents/
│   │   ├── orchestrator.py    # Main coordinator
│   │   ├── zoning_agent.py    # Zone lookup
│   │   ├── cma_agent.py       # Comparables
│   │   ├── hbu_agent.py       # Highest & best use
│   │   ├── ml_agent.py        # XGBoost predictions
│   │   └── reporter_agent.py  # Response synthesis
│   ├── api/                   # API routes
│   ├── services/
│   │   ├── llm_router.py      # Smart LLM routing
│   │   └── supabase_client.py # Database client
│   ├── models/                # Pydantic models
│   ├── main.py                # FastAPI app
│   └── requirements.txt
├── infrastructure/
│   ├── supabase/
│   │   └── schema.sql         # Database schema
│   └── render/
│       └── render.yaml        # Render config
├── docs/
│   ├── PRD_V3.md             # Product requirements
│   └── PRS_V3.md             # Technical specs
└── CLAUDE.md                  # This file
```

## Development Commands

### Frontend
```bash
cd frontend
npm install
npm run dev          # Development server
npm run build        # Production build
npm run lint         # ESLint
npm run type-check   # TypeScript check
```

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload    # Development server
pytest tests/ -v             # Run tests
ruff check .                 # Linting
```

## Environment Variables

### Frontend (.env.local)
```
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
NEXT_PUBLIC_MAPBOX_TOKEN=
NEXT_PUBLIC_API_URL=
NEXT_PUBLIC_WS_URL=
```

### Backend (.env)
```
SUPABASE_URL=
SUPABASE_KEY=
GEMINI_API_KEY=
ANTHROPIC_API_KEY=
MODEL_DIR=models
ENV=development
```

## Key Implementation Details

### LLM Router Tiers
- **FREE (90%)**: Gemini 2.5 Flash - intent classification, simple queries
- **ULTRA_CHEAP (5%)**: DeepSeek V3.2 - medium complexity
- **STANDARD (4%)**: Claude Sonnet 4.5 - HBU analysis, synthesis
- **PREMIUM (1%)**: Claude Opus 4.5 - complex reasoning

### Map-Chat Synchronization
1. Map → Chat: Parcel click triggers `setSelectedParcel()` → chat auto-populates context
2. Chat → Map: AI response includes `map_actions` → frontend calls `setMapHighlights()`

### Agent Workflow
1. Coordinator receives query + context
2. Classifies intent, extracts entities
3. Routes to appropriate agents (parallel execution)
4. Reporter synthesizes results
5. Returns response with map actions + suggestions

## Current Sprint Tasks

### Week 1-2: Foundation
- [x] Project structure
- [x] GitHub Actions CI/CD
- [x] Backend agent scaffolding
- [ ] Frontend ShadCNBlocks setup
- [ ] Mapbox integration
- [ ] WebSocket connection

### Week 3-4: Core Features
- [ ] Zoning agent database queries
- [ ] CMA agent comparables
- [ ] HBU scoring algorithm
- [ ] ML model integration
- [ ] Chat-map synchronization

### Week 5-6: Polish
- [ ] Error handling
- [ ] Loading states
- [ ] Mobile responsive
- [ ] Performance optimization

### Week 7-8: Launch
- [ ] Beta testing
- [ ] Documentation
- [ ] Monitoring setup
- [ ] Public launch

## Testing Strategy

- **Unit tests**: pytest for backend, Vitest for frontend
- **Integration tests**: API endpoint tests
- **E2E tests**: Playwright for critical flows
- **Coverage target**: 70% minimum

## Deployment

### Automatic (on push to main)
1. GitHub Actions runs lint + tests
2. Frontend builds and deploys to Cloudflare Pages
3. Backend triggers Render deploy webhook
4. Health checks verify deployment
5. Logs to Supabase deployments table

### Manual (workflow_dispatch)
```bash
gh workflow run deploy.yml --ref main
```

## Contacts

- **Product Owner**: Ariel Shapira
- **AI Architect**: Claude (Opus/Sonnet)
- **Engineer**: Claude Code

## Remember

1. **NEVER** ask permission for routine tasks
2. **ALWAYS** run tests before pushing
3. **ALWAYS** update this file when architecture changes
4. **ALWAYS** commit frequently with descriptive messages
5. **ALWAYS** use the LLM router for cost optimization
6. Target: 90% FREE tier LLM usage
