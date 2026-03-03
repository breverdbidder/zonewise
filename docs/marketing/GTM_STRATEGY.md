# ZoneWise.AI — GTM Playbook v2.0
**Version:** 2.0 | **Date:** March 3, 2026 | **Status:** PRODUCTION  
**Based on:** PRD V5 + PRS V5 + Sprint 7 (March 1, 2026) + CoStar Architecture Model  
**Maintainer:** Claude AI Architect (Everest Capital USA)

> **"Distressed Assets Decoded. For Everyone. Everywhere."**

---

## ⚠️ CRITICAL RULES — READ FIRST

1. **ZoneWise is NOT a foreclosure data tool.** It is Florida's first agentic AI zoning intelligence platform that integrates auction intelligence as one capability layer.
2. **ALWAYS cover BOTH auction types together** — foreclosure sales AND tax deed sales. Never reference one without the other.
3. **Agentic AI Ecosystem, NOT SaaS** — 10-15× valuation multiple vs 3-5× SaaS. We sell work performed by AI agents, not software licenses.
4. **CoStar Group architecture model** — decided Feb 26, 2026. BidDeed.AI is permanently separate, consumed as external API only. Never merge.

---

## 1. WHAT ZONEWISE.AI ACTUALLY IS

### The Platform
ZoneWise.AI unifies **5 AI agent capabilities** into a single intelligence platform:

| Capability | Agent | Covers |
|---|---|---|
| **ZoneAnalyze** | Zoning Intelligence | Real-time compliance · setbacks · permitted uses · overlays · 5,321 FL districts |
| **DiscoverWise** | Auction Discovery | Foreclosure sales + tax deed sales · 67 FL counties · daily AgentQL scrape |
| **LienWise** | Lien Discovery | AcclaimWeb + RealTDM auto-search · surviving liens in foreclosure · tax cert chains in tax deed |
| **CMAWise** | Market Intelligence | HBU analysis · comps · ARV · demographics · 52 market KPIs |
| **TitleWise** | Title Intelligence | Chain of title · deed verification · HOA status · easements — both auction types |

### Current State (Sprint 7 Complete — March 1, 2026)
- **303** foreclosure + tax deed auctions live across 9 counties
- **10.8M** FL parcels (FDOT) · **5,321** zoning districts · **1,100** jurisdictions
- **67** county skill files deployed · County Research Agent active
- Auction dashboard live on zonewise.ai · Mapbox integration verified
- Brevard pilot: 16 municipalities + 16 CDPs + 351,423 parcels with geometry

### The Two Auction Types — Always Together

**Foreclosure Sales:**
- Court-ordered · judgment-based · in-person at courthouse (Titusville 11AM) + online
- Bid/Judgment ratio drives BID (≥75%) / REVIEW (60–74%) / SKIP (<60%)
- Max Bid = (ARV × 70%) − Repairs − $10K − MIN($25K, 15% ARV)
- LienWise detects surviving senior mortgages automatically (critical for HOA-plaintiff cases)

**Tax Deed Sales:**
- County-administered · delinquent tax cert redemption · online via RealForeclose (brevard.realforeclose.com)
- Tax deed wipes most junior liens · but cert chain analysis is critical
- ZoneWise RealTDM integration auto-maps all outstanding tax certificates
- Often lower competition · higher % of vacant/distressed properties

---

## 2. MARKET & COMPETITIVE POSITIONING

### The Real Competitor Set

| Competitor | Category | Fatal Weakness |
|---|---|---|
| **PropertyOnion** | Auction data (both types) | ZERO zoning · ZERO ML · ZERO lien automation · web-only |
| **Zoneomics** | Zoning data SaaS | No auction data · no ML · stale data · no FL-specific depth |
| **Gridics** | Site feasibility | No auction data · no lien analysis · $10K+/yr pricing |
| **TestFit** | Development feasibility | No API (confirmed) · relies on Zoneomics · no auction intel |
| **CoStar / LoopNet** | Commercial RE data | $500-2K/mo · no AI-native · no MCP · no auction data |
| **Zoning Consultants** | Human expertise | 100× slower · 50× more expensive · not scalable |
| **Generic AI (ChatGPT)** | General AI | 60% zoning accuracy · no real-time ordinance data · no auction pipeline |

### ZoneWise Position
- Only platform combining: **Zoning Intelligence + Auction Intelligence (both types) + ML Predictions + Lien Discovery + HBU Analysis**
- **298 KPIs** vs PropertyOnion 96 · Gridics 74 · Zoneomics 66
- **MCP-native distribution** — inside Claude Desktop + Cursor · zero competitor has this
- **10.8M FL parcels** — data moat built, not buyable

### 4-Layer Moat
1. **DATA** — 10.8M parcels · real ordinance data (not synthetic) · 303+ live auctions both types
2. **INTERPRETATION** — Encodes zoning attorney logic · ML auction predictions · lien priority rules
3. **ACCUMULATION** — Every query improves accuracy · network effects compound
4. **DISTRIBUTION** — MCP-native · first-mover FL zoning AI · inside AI assistants (not a web form)

---

## 3. IDEAL CUSTOMER PROFILES

| ICP | Persona | Use Case | Price Point |
|---|---|---|---|
| **ICP-1 PRIMARY** | Fix & Flip / Foreclosure + Tax Deed Investor | Analyze both auction types pre-bid · LienWise auto-checks · ZoneAnalyze for exit strategy | $99/mo Pro |
| **ICP-1 PRIMARY** | Land Developer | Zoning feasibility · HBU analysis · setbacks + overlays before site acquisition | $299/mo Team |
| **ICP-2** | ADU / Infill Builder | Automated compliance · overlay detection · density bonuses | $99/mo Pro |
| **ICP-2** | Commercial Investor | Use classification pre-acquisition · CMA · both auction types for distressed | $299/mo Team |
| **ICP-3** | Architect / Engineer | Zoning data inside Claude/Cursor via MCP · no context switching | $99/mo Pro |
| **ICP-3** | Title / RE Attorney | Lien priority for both auction types · AcclaimWeb + RealTDM auto-search | $299/mo Team |
| **ICP-4** | AI-Native Developer / PropTech | ZoneWise API embedded in their apps · high LTV · network effects | API $0.50/query |
| **ICP-4** | Municipality / County Planning | Internal compliance · resident-facing tools · bulk data | Custom $999+/mo |

### Where to Find ICP-1 (Both Auction Type Investors)
**Foreclosure buyers:** Court docket watchers · PropertyOnion subscribers (direct competitive switch) · BiggerPockets FL · LinkedIn 'Real Estate Investor' + FL · BidDeed.AI user base  
**Tax deed buyers:** RealForeclose.com active bidders · TaxSaleResources.com · r/taxliens · Ted Thomas YouTube community · FL county tax collector office networks

---

## 4. POSITIONING & MESSAGING

### Positioning Statement
> "Florida's first agentic AI ecosystem for real estate intelligence — analyzing every property across 67 counties against 298 KPIs, covering both foreclosure sales and tax deed sales, powering zoning, lien, title, and auction intelligence through AI — in seconds."

### Per-Persona Headlines

| Persona | Headline |
|---|---|
| Foreclosure + Tax Deed Investor | "Stop guessing at auctions. Know your max bid, surviving liens, and exit zoning — before you raise your paddle." |
| Land Developer | "Zoning feasibility in seconds. Know what you can build before you buy." |
| Architect / Engineer | "ZoneWise lives inside Claude and Cursor. Query zoning data without leaving your design workflow." |
| Title / RE Attorney | "Every lien, every cert, every chain — for both foreclosure and tax deed sales — before your client closes." |
| AI-Native Developer | "Embed FL zoning intelligence in your app. $0.50/query. Real-time. MCP or REST. 10.8M parcels. 67 counties." |

### Agentic AI Ecosystem vs SaaS — Why It Matters
| | Traditional SaaS | ZoneWise Agentic AI |
|---|---|---|
| What is sold | Software license | AI work product |
| Valuation multiple | 3-5× revenue | **10-15× revenue** |
| Value metric | Seat/month | Queries processed · Auctions analyzed |
| Moat | Switching cost | Data + agent quality + MCP lock-in |

---

## 5. GTM CHANNELS — AI-FIRST, ZERO SALES HEADCOUNT

### Channel Allocation
| Channel | % | Mechanism |
|---|---|---|
| **MCP Marketplace** | 40% | Claude Desktop + Cursor registry · Zero-friction install · Default FL zoning tool for AI-native users |
| **Content Flywheel** | 30% | 5-Agent autonomous system · $0 human hours/week · Unique data no competitor can publish |
| **AI Outreach** | 20% | LinkedIn personalized sequences · Email permit applicants · Human only for enterprise |
| **PLG / Scout Pass** | 10% | Free tier (10 queries/mo) · 3 Scout Passes/quarter · trust-based distribution |

### Channel 1: MCP-First (PRIMARY ACQUISITION)
Deploy all 5 tools → Claude Desktop registry → Cursor directory → Beta via BidDeed.AI users → 67 programmatic county SEO pages → Demo video

**Why this works for ZoneWise:** No competitor has MCP distribution. Every AI developer querying FL zoning discovers ZoneWise automatically. Zero CAC.

### Channel 2: Content Flywheel — 5 Agents
The `FL Zoning + Auction Intelligence Weekly` is the core content asset:
- **Published:** Every Monday · Auto-generated from ZoneWise pipeline
- **Always covers:** Both foreclosure sales AND tax deed sales statewide
- **Content:** Top auctions analyzed · BID flags · bid/judgment ratios · opening bids for tax deeds · county spotlight · 1 unique insight from 10.8M property dataset
- **Distribution:** LinkedIn newsletter + email list + blog on zonewise.ai

ZoneWise generates content nobody else can publish — real FL auction data (both types) + zoning intelligence combined.

### Channel 3: AI LinkedIn Outreach Sequence
| Step | Timing | Message |
|---|---|---|
| Connect | Day 0 | "[Name] — saw you invest in FL auctions. Building AI tool covering both foreclosure sales and tax deed sales statewide. Would love your take as someone active in [County]." |
| Value | Day 3 | "Ran [County] through ZoneWise — [X] foreclosure + [Y] tax deed auctions analyzed, [Z] flagged BID. Happy to send the full report with zoning exits." |
| Demo | Day 7 | "Happy to run any parcel: LienWise (surviving liens), ZoneAnalyze (zoning exit), CMAWise (ARV), max bid formula. Reply with a parcel ID." |
| Close | Day 14 | "Full access $99/mo for your county — covers both foreclosure and tax deed sales, all 298 KPIs. 14-day trial. Next [County] auction is [date]." |

### Channel 4: Scout Pass (Referral — Already Designed)
- **3 passes/quarter** per paid user · expires 30 days
- **Recipient gets:** 14-day full access to referrer's counties (both auction types)
- **Referrer earns:** +7 days per accepted invite · All 3 = +21 days free
- **Card required** before trial activates — filters to high-intent users
- **Leaderboard:** Top 3 referrers/quarter earn free month
- API: `POST /api/v1/referral/passes/generate` · `GET /api/v1/referral/scout/{code}`

---

## 6. PRICING

### Tiers
| Tier | Price | Queries | Key Feature |
|---|---|---|---|
| **Free** | $0/mo | 10/month | Brevard only · all 5 MCP tools · foreclosure + tax deed |
| **Pro** | $99/mo | 100/month | All active counties · both auction types · full 298 KPI report + DOCX |
| **Team** | $299/mo | 500/month | 5 seats · API access (100/day) · bulk export |
| **Enterprise** | Custom | Unlimited | Unlimited seats · full API · white-label · SOC 2 |
| **API-only** | $0.50/query | Pay-as-go | Volume: 10K+ → $0.40 · 50K+ → $0.30 |

### Economics
- **COGS per query:** ~$0.03 (90% Gemini FREE tier via Smart Router)
- **Pro gross margin:** 97% · **Team:** 95% · **API:** 94%
- **Monthly fixed costs:** ~$70/mo (Render $25 + Supabase $25 + Cloudflare $20)
- **Break-even:** 1 Pro subscriber OR 140 API queries

### Pricing Anchor (Always Lead With)
> "Zoning consultants charge $150-500/hr. ZoneWise: 100 compliance checks + both auction types for $99/mo."

---

## 7. 90-DAY EXECUTION TIMELINE

### Phase 1: MCP Launch + Beta (Days 1–30)
| Day | Action | Owner | Metric |
|---|---|---|---|
| 5 | Deploy 5 MCP tools to Render · verify <100ms | Claude Code | Health check green |
| 7 | Submit Claude Desktop + Cursor MCP registries | Ariel (10 min) | Listing live |
| 7 | Invite 5-10 BidDeed.AI users as beta (warm leads) | Ariel (15 min) | 5+ installs |
| 10 | Launch FL Zoning + Auction Weekly newsletter — first issue | Claude Code + Ariel approval | 50+ subscribers |
| 10 | HubSpot CRM · email capture · 4-email welcome sequence | Claude Code | Form live |
| 14 | 67 programmatic county pages (foreclosure + tax deed data) | Claude Code | 67 pages indexed |
| 14 | MCP demo video: analyze any FL auction property in 30 sec | Ariel (30 min) | Video live |
| **30** | **GATE: 50 email subscribers** | All channels | HubSpot |

### Phase 2: Activation + First Revenue (Days 31–60)
| Day | Action | Owner | Metric |
|---|---|---|---|
| 35 | Stripe live · Pro $99 + Team $299 · 14-day trial (card required) | Claude Code | Checkout live |
| 36 | Monetization email to 50 beta users · county data teaser | Claude Code | 3+ demo requests |
| 40 | Scout Pass system deployed (fully designed, needs code) | Claude Code | Pass tracking live |
| 45 | 5 demo calls with ICP-1 investors (both auction type buyers) | Ariel | 5 calls logged |
| 45 | First 3 paying customers | Sales + product | $297 MRR |
| 45 | Phase 1 counties: Hillsborough + Palm Beach + Pinellas | Claude Code | 3 counties scraping |
| **60** | **GATE: 10 paying customers · $990 MRR** | All channels | Stripe |

### Phase 3: Scale to $7,500 MRR (Days 61–90)
| Day | Action | Owner | Metric |
|---|---|---|---|
| 65 | API product launch · $0.50/query · PropTech devs | Claude Code | API docs live |
| 70 | All 10 Tier 1 counties · both auction types daily | Claude Code | 500+ auctions/day |
| 72 | Press pitch: BiggerPockets · Connected Investors · FL RE Investor Mag | Claude AI drafts · Ariel sends | 1+ feature |
| 75 | Speaking slot: FL RE Investor meetup / Space Coast HBCA | Ariel | Live demo |
| 85 | 5 design partner builders · testimonials | Ariel | 3+ written |
| **90** | **GATE: 50 subscribers · $7,500 MRR** | All channels | Stripe |

---

## 8. SUCCESS METRICS

| Metric | Day 30 | Day 60 | Day 90 |
|---|---|---|---|
| MCP installs | 25 | 75 | 150+ |
| Email subscribers | 50 | 150 | 250 |
| Foreclosure + tax deed auctions/week | 303 (live) | 600+ | 1,000+ |
| Paying customers | 0 | 10 | 50 |
| MRR | $0 | $990 | $7,500 |
| Trial → Paid conversion | — | >35% | >40% |
| Monthly churn | — | <5% | <5% |
| **Queries/user/week (North Star)** | — | 3+ | **5+ = PMF** |

---

## 9. ARIEL'S 20-MIN DAILY ROUTINE

| Time | Minutes | Action |
|---|---|---|
| Morning | 5 | Check PROJECT_STATE.json + Supabase daily_metrics. Green = proceed. |
| Morning | 10 | LinkedIn: 5 connection requests to ICP-1 investors. Approve 1 newsletter draft (30 sec). Reply to demo requests. |
| Evening | 5 | HubSpot: new signups? Stripe: new trials? Only escalate if churn >3 this week. |

**Claude Code handles autonomously (zero Ariel input):**
Weekly newsletter generation + send · MCP tool responses · Supabase metrics logging · Scout Pass credit application · HubSpot email sequences · Daily foreclosure + tax deed scrape · Programmatic SEO updates · LinkedIn post drafts

---

## 10. RISK REGISTER

| Risk | Level | Mitigation |
|---|---|---|
| Scraper blocking (RealForeclose, court dockets, Municode) | MED | AgentQL anti-detection · BECA Scraper V2 12 regex patterns · IP rotation via Modal.com |
| Data accuracy below 95% MEP threshold | HIGH | Weekly scrape · 7-day TTL cache · user correction feedback loop · GitHub Actions daily validation |
| MCP adoption slower than expected | MED | REST API + web interface as parallel distribution · never bet exclusively on MCP |
| PropertyOnion launches FL zoning | LOW | 18+ month rebuild for them · 298 KPIs vs their 96 · MCP they won't adopt · 10.8M parcel data moat |
| Ariel ADHD context-switch (highest GTM risk) | HIGH | System designed for 3 hrs/week. Claude Code overnight. Sunday-only review. No daily check-ins. |
| Wrong ICP — MCP-only pre-traction | MED | ICP-1 investor direct LinkedIn outreach runs parallel · never rely on MCP exclusively pre-traction |

---

## 11. TECH STACK

| Function | Tool | Repo / Service |
|---|---|---|
| Marketing Site | Next.js · Vercel | `zonewise-web` → zonewise.ai |
| MCP Distribution | FastAPI · Render | `zonewise-agents` → zonewise-agents.onrender.com |
| Data Pipeline | AgentQL · Modal.com | `zonewise-modal` |
| Database | Supabase PostgreSQL | mocerqjnksmhcjzxrewo.supabase.co |
| CRM + Email | HubSpot Free | HubSpot portal |
| Payments | Stripe | Pro $99 · Team $299 · API metered |
| Content AI | Claude Sonnet 4.5 | Claude Max plan |
| Desktop App | CraftAgents v0.4.0 fork | `zonewise-desktop` → zonewise.app |
| Scheduling | Calendly Free | Demo calls |

---

*ZoneWise.AI GTM Playbook v2.0 · March 3, 2026 · Claude AI Architect (Everest Capital USA)*  
*Built on PRD V5 + PRS V5 + Sprint 7 + CoStar Architecture Model*  
*CONFIDENTIAL*
