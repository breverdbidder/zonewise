# GitHub Repository Analysis: Real Estate LLM Platform

**Date:** January 24-25, 2026  
**Purpose:** Evaluate repositories for building Claude AI-style interface  
**Decision:** Open-claude as frontend foundation

---

## Requirements

### Must Have
- Split-screen UI (chat left, artifacts right)
- NLP chatbot capabilities
- Streaming responses
- Document/report generation
- Map visualization

### Stack Alignment
- GitHub (version control)
- Supabase (database + auth)
- Cloudflare (hosting)
- Render.com (compute at scale)
- LiteLLM (LLM routing)
- LangGraph (agent orchestration)

---

## Repository Rankings

### Tier 1: CRITICAL (Ranks 1-5)

| Rank | Repository | Stars | Stack Fit | UI Match | Decision |
|------|------------|-------|-----------|----------|----------|
| **1** | **Damienchakma/Open-claude** | New | 85% | **100%** | ✅ **SELECTED** |
| 2 | mckaywrigley/chatbot-ui | 28K | 95% | 60% | Backup option |
| 3 | makerkit/next-supabase-saas-kit | 500+ | 90% | 40% | SaaS features only |
| 4 | supabase-community/chatgpt-your-files | 2K | 100% | 50% | RAG reference |
| 5 | cloudflare/agents-starter | 1K | 80% | 30% | Edge functions ref |

### Tier 2: Infrastructure (Ranks 6-10)

| Rank | Repository | Stars | Purpose | Use |
|------|------------|-------|---------|-----|
| 6 | BerriAI/litellm | 15K | LLM routing | ✅ Already in stack |
| 7 | fastapi/full-stack-fastapi-template | 27K | Backend patterns | Reference only |
| 8 | langfuse/langfuse | 6K | Observability | GAP - add later |
| 9 | Unstructured-IO/unstructured | 9K | Doc processing | GAP - add later |
| 10 | wassim249/fastapi-langgraph | 500+ | Agent patterns | Reference only |

### Tier 3: Reference (Ranks 11-14)

| Rank | Repository | Stars | Notes |
|------|------------|-------|-------|
| 11 | pengxiaoo/llama-index-fastapi | 200+ | RAG patterns |
| 12 | QuivrHQ/quivr | 36K | Too complex |
| 13 | electron-react-boilerplate | 23K | Desktop - not needed |
| 14 | WrathChaos/react-native-typescript | 2K | Mobile - defer |

### Tier 4: Skip (Ranks 15-18)

| Rank | Repository | Stars | Why Skip |
|------|------------|-------|----------|
| 15 | borys25ol/fastapi-react-kubernetes | 500+ | K8s overkill |
| 16 | Harmeet10000/langchain-fastapi | 100+ | Outdated patterns |
| 17 | alan345/Fullstack-SaaS-Boilerplate | 1K | Not AI-focused |
| 18 | Significant-Gravitas/AutoGPT | 170K | Overly complex |

---

## Detailed Analysis: Top 3

### #1: Damienchakma/Open-claude ✅ SELECTED

**URL:** https://github.com/Damienchakma/Open-claude

**Why Selected:**
- **ArtifactPanel.jsx** - EXACT split-screen we need
- **ThinkingDisplay.jsx** - AI reasoning transparency
- **ModeSwitcher.jsx** - Chat/Build/Code modes
- **CitationDisplay.jsx** - Source document linking

**Key Components:**
```
src/
├── components/
│   ├── ArtifactPanel.jsx      ✅ Ready to use
│   ├── ChatMode.jsx           ✅ Ready to use
│   ├── ThinkingDisplay.jsx    ✅ Ready to use
│   ├── ModeSwitcher.jsx       ✅ Ready to use
│   ├── CitationDisplay.jsx    ✅ Ready to use
│   └── StreamingMessage.jsx   ✅ Ready to use
├── lib/
│   ├── llm-factory.js         ⚠️ Replace with LiteLLM
│   └── storage.js             ⚠️ Replace with Supabase
└── hooks/
    ├── useChat.js             ✅ Modify for our API
    └── useArtifacts.js        ✅ Add report types
```

**Integration Effort:** 2-3 weeks
1. Add Supabase (auth, database, pgvector) - 1 week
2. Replace LLM factory with LiteLLM - 2 days
3. Add LangGraph agent workflows - 1 week
4. Customize ArtifactPanel for real estate - 3 days

**Stack Alignment:**
| Component | Open-claude | Our Need | Effort |
|-----------|-------------|----------|--------|
| Framework | React + Vite | ✅ Same | None |
| Styling | TailwindCSS | ✅ Same | None |
| Database | None | Supabase | Add |
| Auth | None | Supabase Auth | Add |
| LLM | Custom factory | LiteLLM | Replace |
| Agents | Basic | LangGraph | Add |

### #2: mckaywrigley/chatbot-ui (Backup)

**URL:** https://github.com/mckaywrigley/chatbot-ui

**Strengths:**
- 28K stars - massive community
- Native Supabase integration
- Multi-model support
- Production-grade

**Critical Gap:** ❌ NO ARTIFACTS PANEL

Would need to build split-screen UI from scratch (1.5-2 weeks extra work).

**When to Use:** Only if Open-claude proves unmaintainable.

### #3: makerkit/next-supabase-saas-kit

**URL:** https://makerkit.dev

**Strengths:**
- ZoneWise already approved ($299)
- Full SaaS features (auth, Stripe, multi-tenant)
- AI Chatbot Plugin available
- Long-term support

**Critical Gap:** ❌ NO SPLIT-SCREEN ARTIFACTS

**Decision:** Use for ZoneWise marketing site + billing portal, NOT for AI app interface.

---

## Stack Comparison: Manus AI vs Our Approach

Manus AI recommended enterprise stack (FastAPI + Kubernetes + Milvus). Here's how our serverless approach compares:

| Layer | Manus AI | Our Implementation | Verdict |
|-------|----------|-------------------|---------|
| Database | PostgreSQL + Milvus + MongoDB + Redis | Supabase (PostgreSQL + pgvector) | ✅ Simpler |
| LLM Routing | LiteLLM proxy | LiteLLM + Smart Router | ✅ Same |
| Backend | FastAPI + Docker + Kubernetes | GitHub Actions + Cloudflare Workers | ✅ Serverless |
| Agents | LangGraph + LlamaIndex | LangGraph + GitHub Actions | ✅ Aligned |
| Frontend | React + React Native + Electron | Open-claude (React) | ✅ Focused |
| Observability | Langfuse/LangSmith | Basic logging | ❌ GAP |
| Doc Processing | Unstructured.io + PyMuPDF | pdfplumber only | ❌ GAP |

**Identified Gaps to Address Later:**
1. **Langfuse** - Add for LLM observability in Week 7-8
2. **Unstructured.io** - Add for Municode PDF processing

---

## Hybrid Architecture Decision

**Final Decision:** Combine Open-claude UI + Supabase backend

```
FROM Open-claude:
✅ ArtifactPanel.jsx (split-screen UI)
✅ ThinkingDisplay (AI reasoning)
✅ ModeSwitcher (expandable modes)
✅ StreamingMessage (real-time)
✅ CitationDisplay (sources)

FROM Supabase:
✅ Auth (user management)
✅ Database (PostgreSQL)
✅ pgvector (embeddings)
✅ Storage (PDFs, images)
✅ Realtime (streaming updates)
✅ Edge Functions (API)

OUR ADDITIONS:
✅ LiteLLM (multi-provider routing)
✅ LangGraph (agent orchestration)
✅ Modal.com (parallel compute)
✅ Real estate components (ZoningReport, ParcelMap, etc.)
```

---

## Implementation Priority

### Phase 1: Data (Weeks 1-8)
NO UI WORK. Focus entirely on:
- Brevard 100% zone coverage
- Modal.com deployment
- 67 county pipeline

### Phase 2: UI (Weeks 9-12)
ONLY THEN start UI:
1. Fork Open-claude
2. Add Supabase
3. Add LiteLLM + LangGraph
4. Build real estate artifacts
5. Launch MVP

---

## Appendix: All Evaluated Repositories

| # | Repository | URL | Stars | Evaluated |
|---|------------|-----|-------|-----------|
| 1 | Open-claude | github.com/Damienchakma/Open-claude | New | ✅ |
| 2 | chatbot-ui | github.com/mckaywrigley/chatbot-ui | 28K | ✅ |
| 3 | makerkit | makerkit.dev | 500+ | ✅ |
| 4 | chatgpt-your-files | github.com/supabase-community/chatgpt-your-files | 2K | ✅ |
| 5 | agents-starter | github.com/cloudflare/agents-starter | 1K | ✅ |
| 6 | litellm | github.com/BerriAI/litellm | 15K | ✅ |
| 7 | full-stack-fastapi | github.com/fastapi/full-stack-fastapi-template | 27K | ✅ |
| 8 | langfuse | github.com/langfuse/langfuse | 6K | ✅ |
| 9 | unstructured | github.com/Unstructured-IO/unstructured | 9K | ✅ |
| 10 | fastapi-langgraph | github.com/wassim249/fastapi-langgraph-agent | 500+ | ✅ |
| 11 | llama-index-fastapi | github.com/pengxiaoo/llama-index-fastapi | 200+ | ✅ |
| 12 | quivr | github.com/QuivrHQ/quivr | 36K | ✅ |
| 13 | electron-react | github.com/electron-react-boilerplate | 23K | ✅ |
| 14 | react-native-ts | github.com/WrathChaos/react-native-typescript | 2K | ✅ |
| 15 | fastapi-react-k8s | github.com/borys25ol/fastapi-react-kubernetes | 500+ | ✅ |
| 16 | langchain-fastapi | github.com/Harmeet10000/langchain-fastapi | 100+ | ✅ |
| 17 | fullstack-saas | github.com/alan345/Fullstack-SaaS-Boilerplate | 1K | ✅ |
| 18 | AutoGPT | github.com/Significant-Gravitas/AutoGPT | 170K | ✅ |

---

*This analysis informed the architecture decision documented in ARCHITECTURE_DECISION_2026-01-25.md*
