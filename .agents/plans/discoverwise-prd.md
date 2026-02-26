# DiscoverWise — BidDeed.AI × ZoneWise.AI Integration PRD
**Version:** 1.0 | **Date:** 2026-02-26 | **Status:** Awaiting Claude Code Audit

## Core Strategic Question
Should BidDeed.AI's pipeline run inside ZoneWise as a feature (Option A — Shared Supabase),
or should BidDeed.AI expose an API that ZoneWise consumes (Option B — External API)?

## AI Architect Recommendation: Option B
BidDeed.AI and ZoneWise.AI must remain independently deployable. Option B (External API).

## Phase 1 MANDATORY: Claude Code Audit
Before writing a single line of code, Claude Code must:
1. Read both codebases in full (brevard-bidder-scraper + zonewise-agents)
2. Answer all questions in Section 7 of the DOCX PRD
3. Output findings to `.agents/plans/discoverwise-audit.md`
4. Confirm or revise the Option B recommendation

## Key Constraints (Non-Negotiable)
- BidDeed.AI and ZoneWise.AI must remain independently deployable
- No ML model weights in ZoneWise codebase
- BidDeed DOCX reports keep BidDeed.AI branding only
- HOA lien warning must surface in ZoneWise property drawer
- All services auto-deploy with health checks — zero new manual steps for Ariel

## Implementation Sequence (after audit confirms architecture)
Phase 1: Audit (Day 1) → Phase 2: BidDeed API (Days 2-4) → Phase 3: ZoneWise Consumer (Days 5-7)
→ Phase 4: Map UI (Days 8-10) → Phase 5: NLP + Alerts (Days 11-14)

## Claude Code Entry Point
Run `/prime` in brevard-bidder-scraper then zonewise-agents.
Then: `/plan-feature discoverwise-audit`
Output: `.agents/plans/discoverwise-audit.md`
