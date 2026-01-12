# ZoneWise
## Florida's Expert Zoning Intelligence Platform

![ZoneWise Logo](docs/brand/logo-placeholder.png)

**Tagline:** "Wise about zoning"  
**Launch:** Q1 2026 (Brevard County, Florida)  
**Status:** 🏗️ In Development  
**Website:** zonewise.io (pending)

---

## 🎯 What is ZoneWise?

**ZoneWise** is Florida's expert zoning intelligence platform providing instant, accurate zoning data for real estate professionals and government planners.

### Key Features
- ⚡ **Instant Zoning Lookup** - Know zoning for any property in seconds
- 📊 **Development Calculator** - Calculate max buildable SF and units
- 📄 **Professional Reports** - Generate polished PDF reports
- ✅ **Compliance Checking** - Verify setbacks, heights, parking requirements
- 🔌 **API Access** - Integrate zoning data into your workflows
- 🗺️ **Map Visualization** - Interactive parcel maps with zoning overlays

### Why ZoneWise?
- 🎯 **Local Expertise** - 100% complete Brevard County coverage (not one of thousands)
- 📈 **Transparent** - Public pricing, clear coverage maps, published accuracy
- 🚀 **Developer-Friendly** - Self-service tiers, instant access, no sales calls
- 🤖 **Modern Technology** - API-first, cloud-native, proven AI
- 📍 **Florida Specialist** - Deep local knowledge, expanding county-by-county

---

## 📊 Repository Structure

```
zonewise/
├── frontend/              # React frontend (Vite + Tailwind)
│   ├── src/
│   │   ├── components/   # Reusable UI components
│   │   ├── pages/        # Page components
│   │   ├── hooks/        # Custom React hooks
│   │   ├── utils/        # Utility functions
│   │   └── styles/       # Global styles, theme
│   ├── public/           # Static assets
│   └── package.json
├── backend/              # Python FastAPI backend
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── models/      # Data models
│   │   ├── services/    # Business logic
│   │   └── utils/       # Utilities
│   ├── tests/           # Backend tests
│   └── requirements.txt
├── data/                # Data pipelines & scraping
│   ├── scrapers/        # Firecrawl ordinance scrapers
│   ├── processors/      # Data processing scripts
│   ├── validators/      # Data quality checks
│   └── migrations/      # Supabase migrations
├── docs/                # Documentation
│   ├── api/            # API documentation
│   ├── brand/          # Brand guidelines
│   ├── setup/          # Setup instructions
│   └── guides/         # User guides
├── infrastructure/      # Deployment & DevOps
│   ├── github-actions/ # CI/CD workflows
│   ├── cloudflare/     # Cloudflare Pages config
│   ├── supabase/       # Supabase schema & functions
│   └── monitoring/     # Observability configs
├── scripts/            # Utility scripts
└── .github/            # GitHub specific files
    ├── workflows/      # GitHub Actions
    └── ISSUE_TEMPLATE/ # Issue templates
```

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ (frontend)
- Python 3.11+ (backend)
- Supabase account (database)
- Firecrawl API key (data scraping)

### Local Development Setup

**1. Clone repository:**
```bash
git clone https://github.com/breverdbidder/zonewise.git
cd zonewise
```

**2. Setup frontend:**
```bash
cd frontend
npm install
cp .env.example .env
# Edit .env with your Supabase credentials
npm run dev
# Frontend runs at http://localhost:5173
```

**3. Setup backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Supabase and Firecrawl credentials
uvicorn app.main:app --reload
# Backend runs at http://localhost:8000
```

**4. Setup Supabase:**
- See [docs/setup/SUPABASE_SETUP.md](docs/setup/SUPABASE_SETUP.md)
- Run migrations: `supabase db push`

**5. Run data pipeline:**
```bash
cd data
python scrapers/brevard_scraper.py
```

---

## 💰 Pricing

### Individual / Business Tiers
- **Free:** 5 searches/month - No credit card required
- **Basic:** $49/month - 50 searches, basic reports
- **Pro:** $199/month - Unlimited searches, development calculator, professional reports
- **Enterprise:** $999/month - API access, bulk analysis, white-label

### Government Tier
- **Municipal Portal:** $2,500-5,000/year - Public-facing portal, unlimited staff access

See [docs/PRICING.md](docs/PRICING.md) for details.

---

## 🛠️ Technology Stack

### Frontend
- **Framework:** React 18 with Vite
- **Styling:** Tailwind CSS 3.x
- **Maps:** Mapbox GL JS
- **State:** Zustand
- **Forms:** React Hook Form + Zod
- **HTTP:** Axios
- **Deployment:** Cloudflare Pages

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **Database:** Supabase (PostgreSQL 15 + PostGIS)
- **Auth:** Supabase Auth
- **Storage:** Supabase Storage
- **ORM:** SQLAlchemy
- **Validation:** Pydantic
- **Testing:** Pytest
- **Deployment:** Render.com

### Data Pipeline
- **Scraping:** Firecrawl API ($5,988/year)
- **Orchestration:** LangGraph
- **AI/ML:** ForecastEngine™ pattern
- **Smart Router:** Gemini 2.5 Flash (90% FREE tier)
- **Automation:** GitHub Actions

### Infrastructure
- **Version Control:** GitHub
- **CI/CD:** GitHub Actions
- **Frontend Hosting:** Cloudflare Pages
- **Backend Hosting:** Render.com
- **Database:** Supabase (managed PostgreSQL + PostGIS)
- **Monitoring:** Supabase built-in + Sentry (errors)

---

## 📋 Development Workflow

### Branch Strategy (GitHub Flow)
- `main` - Production-ready code
- `develop` - Development branch
- `feature/*` - Feature branches
- `hotfix/*` - Urgent fixes

### Commit Convention
```
type(scope): subject

feat(scraper): add Melbourne ordinance scraper
fix(api): correct parcel search query
docs(readme): update setup instructions
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Pull Request Process
1. Create feature branch from `develop`
2. Implement changes with tests
3. Run linters and tests locally
4. Open PR to `develop` with description
5. CI/CD runs automated tests
6. Code review and approval
7. Merge to `develop`
8. Deploy to staging for testing
9. Merge `develop` → `main` for production

---

## 🔐 Environment Variables

### Frontend (.env)
```bash
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
VITE_MAPBOX_TOKEN=your-mapbox-token
VITE_API_BASE_URL=http://localhost:8000
```

### Backend (.env)
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
FIRECRAWL_API_KEY=your-firecrawl-key
ENVIRONMENT=development
DATABASE_URL=postgresql://postgres:password@localhost:5432/zonewise
```

See [docs/setup/ENVIRONMENT_VARIABLES.md](docs/setup/ENVIRONMENT_VARIABLES.md) for full list.

---

## 🧪 Testing

### Frontend Tests
```bash
cd frontend
npm run test           # Run all tests
npm run test:watch     # Watch mode
npm run test:coverage  # Coverage report
```

### Backend Tests
```bash
cd backend
pytest                 # Run all tests
pytest --cov           # Coverage report
pytest -v              # Verbose output
```

### End-to-End Tests
```bash
npm run test:e2e       # Playwright E2E tests
```

---

## 🚀 Deployment

### Automatic Deployment (CI/CD)
- **Frontend:** Auto-deploys to Cloudflare Pages on push to `main`
- **Backend:** Auto-deploys to Render.com on push to `main`
- **Database:** Migrations run automatically via GitHub Actions

### Manual Deployment
See [docs/deployment/DEPLOYMENT.md](docs/deployment/DEPLOYMENT.md)

---

## 📊 Project Status

### Current Phase: Development (Pre-Launch)

**Q1 2026 Milestones:**
- [x] Product name finalized (ZoneWise)
- [x] Brand guide created
- [x] Competitive intelligence complete (Gridics)
- [ ] Domain registered (zonewise.io)
- [ ] Trademark filed
- [ ] Logo designed
- [ ] Data scraping (17 Brevard jurisdictions) - In Progress
- [ ] Frontend development - Starting
- [ ] Backend API development - Starting
- [ ] Beta testing (3-5 developers) - Planned Feb/Mar
- [ ] Public launch - March 31, 2026

**Progress Tracking:** [GitHub Projects Board](../../projects)

---

## 👥 Team & Contributors

**Company:** Everest Capital USA  
**Founder:** Ariel Shapira (Solo Founder)  
**AI Architect:** Claude (Anthropic)  
**Agentic Engineer:** Claude Code  
**Orchestration:** LangGraph

### Contributing
We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Code of Conduct
Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

---

## 📚 Documentation

- **[API Documentation](docs/api/)** - API endpoints and usage
- **[Brand Guide](docs/brand/BRAND_GUIDE.md)** - Visual identity and messaging
- **[Setup Guide](docs/setup/SETUP.md)** - Local development setup
- **[Deployment Guide](docs/deployment/DEPLOYMENT.md)** - Production deployment
- **[Architecture](docs/ARCHITECTURE.md)** - System architecture overview
- **[Contributing](CONTRIBUTING.md)** - Contribution guidelines

---

## 🔗 Related Projects

### Everest Capital USA Product Ecosystem

**[BidDeed.AI](https://github.com/breverdbidder/brevard-bidder-scraper)** - Florida Foreclosure Intelligence
- Status: Operational (V13.4.0)
- Coverage: 67 Florida counties
- Integration: Foreclosure reports + zoning intelligence (Q3 2026)

**[SPD Site Plan Development](https://github.com/breverdbidder/spd-site-plan-dev)** - Agentic Site Plan Generation
- Status: In Development
- Launch: Q2 2026
- Integration: Uses ZoneWise API for Stage 3 (Zoning Compliance)

**[Competitive Intelligence](https://github.com/breverdbidder/competitive-intelligence)** - Systematic Competitor Analysis
- Gridics analysis complete
- Framework for future competitor research

---

## 📧 Contact & Support

**Website:** zonewise.io (pending)  
**Email:** hello@zonewise.io (pending domain)  
**Support:** support@zonewise.io  
**Developers:** api@zonewise.io  
**Government:** gov@zonewise.io

**Social Media:**
- Twitter: [@zonewise](https://twitter.com/zonewise) (pending)
- LinkedIn: [/company/zonewise](https://linkedin.com/company/zonewise) (pending)

---

## 📄 License

**Proprietary** - © 2026 Everest Capital USA. All rights reserved.

This repository contains proprietary software developed by Everest Capital USA. Unauthorized copying, distribution, or modification is prohibited.

---

## 🙏 Acknowledgments

- **Gridics** - Competitive intelligence informed our product strategy
- **Anthropic** - Claude AI and Claude Code for development
- **Supabase** - Database, auth, and storage infrastructure
- **Firecrawl** - Ordinance scraping capabilities

---

## 🎯 Vision

**Mission:** Make zoning intelligence accessible to every Florida real estate professional.

**Q1 2026:** Brevard County mastery (17 jurisdictions, 100% coverage)  
**Q2-Q3 2026:** Regional expansion (Orange, Seminole counties)  
**Q4 2026:** Statewide Florida (67 counties)  
**2027+:** National expansion (expert platform, local knowledge)

---

**ZoneWise - Wise about zoning**  
**Launching Q1 2026 | Brevard County, Florida**  
**Everest Capital USA**

*Built with ❤️ in Florida*
