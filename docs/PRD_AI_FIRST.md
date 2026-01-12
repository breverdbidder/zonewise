# ZoneWise Product Requirements Document (PRD)
## AI-Powered Conversational Zoning Intelligence Platform

**Product:** ZoneWise  
**Core:** AI Chatbot with Natural Language Processing  
**Launch:** Q1 2026 (March 31, 2026)  
**Market:** Brevard County, Florida  
**Created:** January 12, 2026

---

## 🎯 EXECUTIVE SUMMARY

### **What is ZoneWise?**

**ZoneWise is an AI-powered conversational zoning intelligence platform.**

The AI chatbot with Natural Language Processing (NLP) **IS THE PRODUCT**.
Everything else (data, reports, maps) **SUPPORTS THE CHATBOT**.

### **Core Value Proposition:**

**"Talk to Your AI Zoning Expert"**

Users ask zoning questions in plain English and get instant, accurate answers from an AI that understands natural language.

### **Primary Differentiator:**

- **Gridics (Competitor):** Traditional database with forms and menus
- **ZoneWise (Us):** AI chatbot that understands "Can I build apartments in Melbourne?"

### **Target Market:**

- **Primary:** Small-mid developers (5-50 projects/year in Brevard)
- **Secondary:** Government planners (17 Brevard jurisdictions)
- **Tertiary:** Architects, engineers, realtors, homeowners

### **Business Model:**

- **Free:** 5 chatbot conversations/month (experience the AI)
- **Basic:** $49/month unlimited chatbot conversations
- **Pro:** $199/month advanced AI features
- **Enterprise:** $999/month API access to AI

---

## 1. PRODUCT VISION

### **Mission:**

Make zoning intelligence accessible to everyone through conversational AI.

### **Vision:**

Become the AI assistant that every Florida real estate professional talks to before making development decisions.

### **North Star Metric:**

**Daily Active Chatbot Users (DACU)**
- Q1 2026: 20 DACU
- Q2 2026: 100 DACU
- Q4 2026: 500 DACU

### **Product Positioning:**

**"The AI Zoning Expert for Florida"**

Not: "A zoning database with chatbot"
But: "An AI expert powered by comprehensive data"

---

## 2. USER PERSONAS

### **Primary Persona: Small Developer Dan**

**Profile:**
- Age: 35-50
- Projects: 5-20/year in Brevard County
- Pain: Spends hours researching zoning, often gets it wrong
- Goal: Quick, accurate zoning answers to bid on properties

**Conversation:**
```
Dan: "Can I build a duplex on this lot in Satellite Beach?"
ZoneWise: "I'd be happy to help! What's the address?"
Dan: "123 Ocean Ave"
ZoneWise: "That property is zoned R-1. Duplexes are not allowed 
          by-right in R-1, but you could apply for a conditional 
          use permit. Would you like details on the CUP process?"
```

**Value:** Saves 2-3 hours per property research

### **Secondary Persona: Government Planner Paula**

**Profile:**
- Job: Planning technician at Melbourne City Hall
- Pain: Handles 50-100 zoning inquiries per week
- Goal: Reduce citizen inquiry load, improve service

**Use Case:**
- Embeds ZoneWise AI chatbot on city website
- Citizens ask questions directly to AI
- Paula handles only complex cases (10-15/week instead of 50-100)

**Value:** Reduces workload by 70%

### **Tertiary Persona: First-Time Developer Frank**

**Profile:**
- Age: 25-35
- Experience: Zero development knowledge
- Pain: Intimidated by zoning codes and terminology
- Goal: Learn if real estate development is feasible

**Conversation:**
```
Frank: "I inherited a lot in Melbourne. What can I do with it?"
ZoneWise: "I can help you figure that out! Do you have the address?"
Frank: "456 Palm Bay Road"
ZoneWise: "Your property is zoned R-2, which allows:
          • Single-family homes (by-right)
          • Duplexes (by-right)
          • Small apartments up to 5 units (by-right)
          Would you like me to calculate how much you could build?"
```

**Value:** Zero learning curve, instant education

---

## 3. CORE FEATURES (AI-FIRST)

### **3.1 AI CHATBOT (THE PRODUCT)**

**Feature: Natural Language Understanding**

**User Story:**
"As a developer, I want to ask zoning questions in plain English so that I don't need to learn complex zoning terminology."

**Requirements:**
- ✅ Accept natural language input (conversational text)
- ✅ Understand 6 core intent types:
  1. Feasibility: "Can I build X?"
  2. Calculation: "How much can I build?"
  3. Comparison: "What's the difference between R-1 and R-1A?"
  4. Process: "How do I get a permit?"
  5. Research: "Show me properties where I can build 4 units"
  6. Definition: "What does FAR mean?"
- ✅ Extract entities: address, zoning code, use type, location
- ✅ Handle misspellings and colloquial language
- ✅ Response time: <2 seconds (p95)

**Technical Implementation:**
- NLP Model: Gemini 2.5 Flash (90% FREE tier)
- Intent Classification: 6-class supervised model
- Entity Extraction: NER (Named Entity Recognition)
- Orchestration: LangGraph

**Success Criteria:**
- Intent classification accuracy: 90%+
- Entity extraction accuracy: 85%+
- User satisfaction: 4.5+/5.0

---

**Feature: Multi-Turn Context Awareness**

**User Story:**
"As a user, I want the AI to remember what I asked previously so I don't have to repeat myself."

**Requirements:**
- ✅ Maintain conversation context (5-10 messages)
- ✅ Reference previous properties/addresses
- ✅ Build on previous answers
- ✅ Ask clarifying questions when needed

**Example:**
```
User: "What's the zoning for 123 Ocean Ave?"
AI: "That's R-1. Would you like to know what you can build there?"
User: "Yes" ← AI remembers address and zoning
AI: "In R-1 at 123 Ocean Ave, you can build..."
```

**Technical Implementation:**
- Conversation state management (Supabase)
- Context window: Last 10 messages
- Entity tracking: Current property, zoning, user intent

**Success Criteria:**
- Context retention: 90%+ accuracy over 5 turns
- User confusion rate: <5% (measured by clarification requests)

---

**Feature: Intelligent Follow-Up Suggestions**

**User Story:**
"As a user, I want the AI to suggest relevant next steps so I know what to do next."

**Requirements:**
- ✅ After answering, suggest 3-5 follow-up actions
- ✅ Context-appropriate (based on user's question)
- ✅ Actionable (can be completed via chatbot)
- ✅ Examples:
  - "Calculate maximum buildable SF"
  - "View comparable properties on map"
  - "Generate PDF report"
  - "Check parking requirements"

**Technical Implementation:**
- Rule-based suggestion engine
- Intent → Suggested actions mapping
- Priority ranking (most relevant first)

**Success Criteria:**
- Click-through rate on suggestions: 40%+
- User session length increase: 20%+

---

**Feature: Educational Explanations**

**User Story:**
"As a first-time developer, I want the AI to explain zoning concepts so I can learn while I get answers."

**Requirements:**
- ✅ Detect unfamiliar terms (FAR, CUP, setback, etc.)
- ✅ Provide brief explanations in conversation
- ✅ Offer deeper explanations ("Tell me more")
- ✅ Use examples and analogies
- ✅ Link to ordinance sources

**Example:**
```
User: "What's FAR?"
AI: "FAR stands for Floor Area Ratio. It's the ratio of a 
     building's total floor area to the lot size.
     
     Example: On a 10,000 SF lot with FAR = 0.5:
     Maximum building = 10,000 × 0.5 = 5,000 SF total
     
     Would you like me to calculate FAR for a specific property?"
```

**Technical Implementation:**
- Glossary database (100+ zoning terms)
- Dynamic explanation generation
- Real-world examples

**Success Criteria:**
- User comprehension: 85%+ (survey)
- Repeat question rate: <10%

---

### **3.2 DATA INTEGRATION (SUPPORTS CHATBOT)**

**Feature: Brevard County Zoning Data**

**User Story:**
"As a user, I want accurate Brevard County zoning data so the AI gives me correct answers."

**Requirements:**
- ✅ 17 Brevard jurisdictions covered (100%)
- ✅ Data completeness: 95%+ per jurisdiction
- ✅ Updated: Daily at 11 PM EST
- ✅ Sources: American Legal, Municode, BCPAO
- ✅ Includes:
  - Zoning districts (R-1, C-2, etc.)
  - Allowed uses (by-right, conditional, prohibited)
  - Dimensional standards (setbacks, height, FAR)
  - Parking requirements
  - Parcel boundaries (PostGIS)

**Technical Implementation:**
- Firecrawl scrapers (automated)
- Supabase storage (PostgreSQL + PostGIS)
- Data validation pipeline
- Version control (track changes)

**Success Criteria:**
- Data accuracy: 95%+ (manual verification)
- Coverage: 100% of Brevard County
- Freshness: Updated within 24 hours of ordinance changes

---

**Feature: RAG Knowledge Retrieval**

**User Story:**
"As the AI, I want to retrieve relevant zoning data quickly so I can answer user questions accurately."

**Requirements:**
- ✅ Semantic search on ordinance content
- ✅ Vector embeddings for similarity matching
- ✅ Response time: <500ms for data retrieval
- ✅ Ranked results (most relevant first)
- ✅ Source attribution (cite ordinance sections)

**Technical Implementation:**
- Ordinance embeddings (OpenAI text-embedding-3)
- Supabase pgvector extension
- Similarity threshold: 0.7+
- Cache frequent queries

**Success Criteria:**
- Retrieval precision: 90%+ (correct info in top 3 results)
- Retrieval speed: <500ms (p95)

---

### **3.3 SUPPORTING FEATURES (COMPLEMENT CHATBOT)**

**Feature: PDF Report Generation**

**User Story:**
"As a developer, I want to generate a PDF report from my chatbot conversation so I can share it with my team."

**Requirements:**
- ✅ Generate from chatbot conversation
- ✅ Includes: Property details, zoning analysis, development potential
- ✅ Professional formatting (ZoneWise branding)
- ✅ One-click generation from chat
- ✅ Email delivery option

**Technical Implementation:**
- Report template (docx)
- python-docx library
- Convert to PDF (pandoc or wkhtmltopdf)
- Supabase Storage

**Success Criteria:**
- Generation time: <10 seconds
- User satisfaction: 4.5+/5.0 (report quality)

---

**Feature: Map Visualization (Optional)**

**User Story:**
"As a user, I want to see properties on a map so I can understand spatial relationships."

**Requirements:**
- ✅ Mapbox GL JS integration
- ✅ Parcel boundaries (PostGIS)
- ✅ Zoning district overlays
- ✅ Click parcel → Chatbot lookup
- ✅ Accessible from chatbot ("Show me on map")

**Technical Implementation:**
- Mapbox GL JS
- Supabase PostGIS queries
- GeoJSON rendering

**Success Criteria:**
- Map load time: <3 seconds
- Usage: 20% of users interact with map

---

**Feature: Traditional Search (Fallback)**

**User Story:**
"As a power user, I want a traditional search interface so I can quickly look up properties I already know."

**Requirements:**
- ✅ Address/parcel ID search
- ✅ Filters (city, zoning type, use)
- ✅ Results table
- ✅ Secondary to chatbot (not default)

**Technical Implementation:**
- React form component
- Supabase full-text search
- Typeahead suggestions

**Success Criteria:**
- Usage: <30% of interactions (chatbot is primary)

---

## 4. USER EXPERIENCE (CHATBOT-FIRST)

### **4.1 Homepage Design**

**Layout:**
```
┌────────────────────────────────────────────┐
│  ZONEWISE - Your AI Zoning Expert         │
├────────────────────────────────────────────┤
│                                            │
│   ┌──────────────────────────────────┐   │
│   │  💬 Chat with ZoneWise AI        │   │
│   │                                   │   │
│   │  Try asking:                      │   │
│   │  • Can I build apartments in      │   │
│   │    Melbourne?                     │   │
│   │  • What's R-1 zoning?            │   │
│   │  • How much can I build on my    │   │
│   │    lot?                           │   │
│   │                                   │   │
│   │  [Type your question here...]     │   │
│   │  [🎤 Voice input]  [Send]        │   │
│   └──────────────────────────────────┘   │
│                                            │
│   🎯 No zoning knowledge required         │
│   ⚡ Instant accurate answers             │
│   🤖 Powered by advanced AI               │
│   📍 100% Brevard County coverage         │
│                                            │
│   [Try Free - 5 Conversations] [Sign Up]  │
└────────────────────────────────────────────┘
```

**NOT:**
- Search form as hero
- "Search database" CTA
- Traditional navigation first

---

### **4.2 Conversation Flow**

**Example Interaction:**

```
┌─────────────────────────────────────┐
│ Welcome! I'm ZoneWise AI.           │
│ Ask me any zoning question about    │
│ Brevard County properties.          │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ User: Can I build apartments in     │
│       Melbourne?                     │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ ZoneWise: Apartments are allowed in │
│ certain Melbourne zoning districts. │
│ Do you have a specific property     │
│ address?                             │
│                                      │
│ [Yes, I have an address]            │
│ [No, just exploring]                │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ User: Yes, 456 Palm Bay Road        │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ ZoneWise: Found it!                 │
│                                      │
│ 📍 456 Palm Bay Rd, Melbourne, FL   │
│ 🏘️ Zoning: R-2 (Medium Density)     │
│ 📏 Lot Size: 12,500 SF              │
│                                      │
│ ✅ Good news! Apartments (up to 5   │
│    units) are allowed by-right in   │
│    R-2 zoning.                       │
│                                      │
│ Would you like me to:                │
│ • Calculate max buildable SF        │
│ • Show parking requirements         │
│ • Generate development report       │
│ • View on map                       │
└─────────────────────────────────────┘

[Conversation continues...]
```

---

### **4.3 Mobile Experience**

**Requirements:**
- ✅ Chat-optimized for thumb typing
- ✅ Voice input prominent (future Phase 3)
- ✅ Full-screen chat interface
- ✅ Swipe to access history/settings
- ✅ Offline: "Chatbot requires internet"

---

## 5. TECHNICAL ARCHITECTURE

### **5.1 System Architecture**

```
┌─────────────────────────────────────────────────┐
│              USER (Web/Mobile)                   │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│  FRONTEND: React + Vite + Tailwind              │
│  - Chat UI (primary)                            │
│  - Map (optional)                               │
│  - Forms (fallback)                             │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│  BACKEND: Python FastAPI                        │
│  - LangGraph orchestration                      │
│  - Intent classification                        │
│  - Entity extraction                            │
│  - Response generation                          │
│  - RAG knowledge retrieval                      │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│  AI/ML LAYER                                    │
│  - Gemini 2.5 Flash (NLP, 90% FREE)            │
│  - Claude Sonnet 4.5 (complex reasoning)        │
│  - ForecastEngine™ (ML orchestration)           │
│  - Smart Router (cost optimization)             │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│  DATA LAYER: Supabase                           │
│  - PostgreSQL + PostGIS                         │
│  - Conversations (primary)                      │
│  - Zoning data (support)                        │
│  - Embeddings (RAG)                             │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│  DATA SOURCES                                   │
│  - Firecrawl (ordinance scraping)              │
│  - BCPAO (property data)                        │
│  - American Legal / Municode                    │
└─────────────────────────────────────────────────┘
```

---

### **5.2 AI/ML Pipeline**

**Request Flow:**

1. **User Input** → Natural language message
2. **Intent Classification** → Identify question type (feasibility, calculation, etc.)
3. **Entity Extraction** → Extract address, zoning, use type
4. **Context Retrieval** → Load conversation history
5. **Knowledge Retrieval** → RAG query to Supabase (semantic search)
6. **Response Generation** → LLM generates natural language answer
7. **Suggestion Generation** → Rule-based follow-up suggestions
8. **Response Delivery** → Send to user (<2s total)
9. **Feedback Loop** → Store conversation, learn from feedback

---

### **5.3 Technology Stack**

**Frontend:**
- React 18 (component library)
- Vite (build tool, 5x faster than Webpack)
- Tailwind CSS (styling)
- Mapbox GL JS (maps)
- Zustand (state management)
- Axios (HTTP client)

**Backend:**
- Python 3.11+
- FastAPI (async web framework)
- LangGraph (agentic orchestration)
- Pydantic (validation)
- httpx (async HTTP)

**AI/ML:**
- Gemini 2.5 Flash (primary NLP, 90% FREE tier)
- Claude Sonnet 4.5 (backup, complex reasoning)
- OpenAI text-embedding-3 (embeddings for RAG)
- ForecastEngine™ pattern (ML orchestration)

**Database:**
- Supabase (managed PostgreSQL)
- PostGIS (spatial data)
- pgvector (embeddings)
- Supabase Auth (authentication)
- Supabase Storage (PDFs, reports)

**Infrastructure:**
- GitHub (version control)
- GitHub Actions (CI/CD)
- Cloudflare Pages (frontend hosting)
- Render.com (backend hosting)
- Sentry (error tracking)

---

## 6. DEVELOPMENT ROADMAP

### **Phase 1: MVP (Q1 2026 - Launch March 31)**

**Weeks 1-4: AI Chatbot Core**
- [ ] LangGraph orchestration setup
- [ ] Gemini 2.5 Flash integration
- [ ] Intent classification (6 types)
- [ ] Entity extraction
- [ ] Basic conversation flow
- [ ] Context management (multi-turn)

**Weeks 5-6: Data Integration**
- [ ] Supabase connection
- [ ] Brevard zoning data (17 jurisdictions)
- [ ] RAG knowledge retrieval
- [ ] Response generation

**Weeks 7-8: Conversation Design**
- [ ] Friendly, helpful tone
- [ ] Clarification questions
- [ ] Follow-up suggestions
- [ ] Educational explanations
- [ ] Error handling

**Weeks 9-10: Testing**
- [ ] 100+ NL query tests
- [ ] Multi-turn conversations
- [ ] Beta testing (5 developers)

**Weeks 11-12: Polish & Launch**
- [ ] UI/UX refinement
- [ ] Performance (<2s response)
- [ ] Mobile optimization
- [ ] Public launch

**Launch Metrics:**
- 20 paying customers
- 4.5+/5.0 satisfaction
- 95%+ answer accuracy
- <2s response time

---

### **Phase 2: Enhanced AI (Q2 2026)**

- 📊 Development calculator (via chat)
- 📄 PDF report generation (from chat)
- 🗺️ Map integration ("Show me on map")
- 💬 Improved suggestions (ML-powered)
- 📚 Expanded knowledge base

---

### **Phase 3: Advanced Features (Q3 2026)**

- 🎤 Voice input (speak questions)
- 📸 Photo upload ("What's zoning here?")
- 🔔 Zoning change alerts
- 🤝 Team collaboration (share chats)
- 📊 Analytics dashboard

---

### **Phase 4: API & Scale (Q4 2026)**

- 🔌 Public API (chatbot integration)
- 🔄 Bulk analysis via chat
- 🧠 Predictive suggestions
- 📞 Escalation to human expert
- 🌐 Multilingual (Spanish)

---

## 7. SUCCESS METRICS

### **Primary (Chatbot-Centric):**

**Engagement:**
- Daily Active Chatbot Users (DACU): 20 → 100 → 500
- Average messages per conversation: 5-10
- Multi-turn rate: 80%+ (more than 1 exchange)
- Return user rate: 40%+ weekly

**Quality:**
- Answer accuracy: 95%+
- User satisfaction: 4.5+/5.0
- Response time: <2s (p95)
- Clarification rate: <15%

**Business:**
- MRR: $5-10K (Q1) → $90-150K (Q4)
- Free → Paid conversion: 20%+
- Customer retention: 80%+ monthly
- API adoption: 5 enterprises by Q4

### **Secondary (Supporting):**

- Data completeness: 95%+ Brevard
- Map usage: 20% of users
- Traditional search: <30% of interactions
- PDF downloads: 40% of conversations

---

## 8. COMPETITIVE ADVANTAGE

**ZoneWise vs Gridics:**

| Category | Gridics | ZoneWise | Winner |
|----------|---------|----------|--------|
| **Interface** | Forms | AI Chat | **ZoneWise** |
| **Input** | Keywords | Natural Language | **ZoneWise** |
| **Learning Curve** | Steep | Zero | **ZoneWise** |
| **Context** | None | Multi-turn | **ZoneWise** |
| **Education** | Limited | Built-in | **ZoneWise** |
| Coverage | Vague 1000s | 100% Brevard | **ZoneWise** |
| Pricing | Hidden | Public $49-999 | **ZoneWise** |
| Self-Service | No | Yes | **ZoneWise** |
| Data Accuracy | Unverified | 95%+ published | **ZoneWise** |
| Technology | WordPress | AI-powered | **ZoneWise** |

**Result: ZoneWise wins 10/10 categories**

---

## 9. GO-TO-MARKET STRATEGY

### **Launch Messaging:**

**Headline:** "Talk to Your AI Zoning Expert"

**Subheadline:** "Get instant, accurate zoning answers in plain English. No zoning knowledge required."

**Demo:** Video showing:
1. User asks: "Can I build apartments in Melbourne?"
2. AI responds with comprehensive answer
3. Suggests next steps
4. Generates PDF report

### **Channels:**

**Phase 1 (Q1): Direct Outreach**
- LinkedIn (50 Brevard developers)
- Email (warm intros)
- Government presentations (17 planning depts)

**Phase 2 (Q2): Content Marketing**
- SEO: "Melbourne zoning", "Satellite Beach development"
- Blog: "Complete Brevard County Zoning Guide"
- Free tool: Development calculator

**Phase 3 (Q3): Partnerships**
- Brevard BIA
- Space Coast Builders
- Attorney referrals

**Phase 4 (Q4): Paid Acquisition**
- Google Ads: "Brevard County zoning"
- LinkedIn Ads: Target developers
- <$100 CAC target

---

## 10. RISKS & MITIGATION

### **Risk: AI gives wrong answer**

**Impact:** High (loss of trust)
**Probability:** Medium
**Mitigation:**
- 95%+ data accuracy validation
- Confidence threshold (don't answer if <70%)
- Escalation to human for complex cases
- Feedback loop (thumbs up/down)
- Disclaimer: "Verify with local authorities"

### **Risk: Users prefer traditional search**

**Impact:** High (invalidates hypothesis)
**Probability:** Low
**Mitigation:**
- Beta test chatbot vs forms (A/B test)
- Gather user feedback early
- Keep forms as fallback option
- Measure: chatbot usage >70% target

### **Risk: Response time too slow**

**Impact:** Medium (poor UX)
**Probability:** Low
**Mitigation:**
- Target <2s (p95)
- Use Gemini 2.5 Flash (fast)
- Cache common queries
- Optimize RAG retrieval (<500ms)
- Monitor latency continuously

---

## 11. LAUNCH CHECKLIST

### **Technical:**
- [ ] AI chatbot fully functional
- [ ] 95%+ data accuracy verified
- [ ] Response time <2s (p95)
- [ ] Mobile optimized
- [ ] Error handling robust
- [ ] Analytics tracking live

### **Content:**
- [ ] 100+ zoning terms in glossary
- [ ] Example conversations written
- [ ] Help documentation
- [ ] FAQ page
- [ ] Terms of Service
- [ ] Privacy Policy

### **Marketing:**
- [ ] Homepage (chat-first design)
- [ ] Demo video recorded
- [ ] LinkedIn posts scheduled
- [ ] Email list ready (100 contacts)
- [ ] Government presentations prepared

### **Business:**
- [ ] Pricing live ($49-999)
- [ ] Stripe payment integration
- [ ] Free tier limits (5 chats)
- [ ] Customer support ready
- [ ] Feedback mechanisms

---

## ✅ APPROVAL

**Product Owner:** Ariel Shapira  
**AI Architect:** Claude (Anthropic)  
**Date:** January 12, 2026  
**Status:** Approved for Development

---

**ZoneWise: AI-First. Chatbot-Core. Data-Supported.**

**Launch: Q1 2026 | Brevard County, Florida**
