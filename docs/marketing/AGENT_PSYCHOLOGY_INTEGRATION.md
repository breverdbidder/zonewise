# ZoneWise: AI Agent Psychology Integration

> **Version:** 1.0 | **Last Updated:** January 18, 2026  
> **Frameworks Combined:** SaaStr 20-Agent Model + Tony Robbins Six Needs  
> **Purpose:** Make AI agents emotionally intelligent in targeting and messaging

---

## Executive Summary

The 16-agent ZoneWise marketing stack becomes 10x more effective when each agent understands the psychological drivers of target users. This document maps the **Robbins Six Human Needs Framework** to specific agent behaviors, message templates, and conversion triggers.

```
┌─────────────────────────────────────────────────────────────────┐
│           PSYCHOLOGY-DRIVEN AGENT ARCHITECTURE                  │
│                                                                 │
│   USER PSYCHOLOGY          →          AGENT BEHAVIOR            │
│                                                                 │
│   CERTAINTY (Fear)         →     S1: SDR leads with risk        │
│   SIGNIFICANCE (Ego)       →     C1: Content builds authority   │
│   CONNECTION (Trust)       →     S2: BDR emphasizes credibility │
│   GROWTH (Ambition)        →     C3: SEO targets expansion      │
│   CONTRIBUTION (Purpose)   →     C2: Social shares success      │
│                                                                 │
│   Result: Messages that resonate, not just reach                │
└─────────────────────────────────────────────────────────────────┘
```

---

## Part 1: User Persona Psychology Mapping

### Persona A: Real Estate Developer

| Need | Intensity | Trigger Phrases | Pain Points |
|------|-----------|-----------------|-------------|
| **CERTAINTY** | ⭐⭐⭐⭐⭐ | "Will this get approved?" | Variance rejections, project delays |
| **SIGNIFICANCE** | ⭐⭐⭐⭐ | "I need to look competent" | Being surprised by code violations |
| **GROWTH** | ⭐⭐⭐ | "More projects, faster" | Bottlenecked by zoning research |
| **CONTRIBUTION** | ⭐⭐ | "Building for the community" | Secondary motivation |

**Agent Instruction:** Lead with CERTAINTY messaging. Open with risk/cost of getting zoning wrong. Follow with SIGNIFICANCE (be the prepared developer).

---

### Persona B: Land Use Attorney

| Need | Intensity | Trigger Phrases | Pain Points |
|------|-----------|-----------------|-------------|
| **SIGNIFICANCE** | ⭐⭐⭐⭐⭐ | "I'm the expert my clients rely on" | AI threatening expertise value |
| **CERTAINTY** | ⭐⭐⭐⭐ | "I need accurate data to advise" | Incomplete/outdated ordinances |
| **GROWTH** | ⭐⭐⭐ | "Expand practice, more clients" | Time spent on research vs. billing |
| **CONNECTION** | ⭐⭐⭐ | "Trusted advisor relationship" | Clients questioning fees |

**Agent Instruction:** Lead with IDENTITY PRESERVATION. Position ZoneWise as tool that amplifies (not replaces) expertise. Emphasize "AI-augmented attorney" narrative.

---

### Persona C: Architect/Designer

| Need | Intensity | Trigger Phrases | Pain Points |
|------|-----------|-----------------|-------------|
| **CERTAINTY** | ⭐⭐⭐⭐ | "Will my design comply?" | Redesign costs after zoning review |
| **GROWTH** | ⭐⭐⭐⭐ | "Take on more complex projects" | Unfamiliar jurisdictions |
| **SIGNIFICANCE** | ⭐⭐⭐ | "Creative professional" | Don't want to be seen as "just looking up codes" |
| **VARIETY** | ⭐⭐⭐ | "Different project types" | Residential vs. commercial confusion |

**Agent Instruction:** Lead with GROWTH + CERTAINTY. Position as enabling more ambitious designs with confidence.

---

### Persona D: Real Estate Investor (BidDeed.AI Crossover)

| Need | Intensity | Trigger Phrases | Pain Points |
|------|-----------|-----------------|-------------|
| **CERTAINTY** | ⭐⭐⭐⭐⭐ | "Can I develop this lot?" | Buying land without knowing buildability |
| **VARIETY** | ⭐⭐⭐⭐ | "More deal flow" | Limited to familiar zoning areas |
| **SIGNIFICANCE** | ⭐⭐⭐ | "Smartest investor in the room" | Competing with institutional buyers |
| **GROWTH** | ⭐⭐⭐ | "Scale my portfolio" | Geographic constraints |

**Agent Instruction:** Cross-sell opportunity. Lead with CERTAINTY (don't buy unbuildable land). Follow with VARIETY (expand to new areas with confidence).

---

## Part 2: Agent-by-Agent Psychology Training

### SALES AGENTS

#### Agent S1: Warm Outbound SDR

**Primary Need Targeted:** CERTAINTY + SIGNIFICANCE

**Message Templates by Need:**

```
CERTAINTY Template (Fear-Based):
Subject: [FirstName], the $47K mistake most {role}s make in {city}

Hey [FirstName],

Quick question: before your last project in [City], did you verify 
the setback requirements for [their zoning district]?

I ask because we just helped a [similar role] discover their 
planned addition violated the [specific code] — BEFORE they 
submitted plans. Saved them $47K in redesign and a 6-month delay.

Would it be helpful if I showed you what ZoneWise found for 
[their recent permit address]?

— ZoneWise AI SDR
```

```
SIGNIFICANCE Template (Ego-Based):
Subject: [FirstName], be the developer who never gets surprised

Hey [FirstName],

The best developers I work with share one trait: they verify 
zoning compliance BEFORE their architect draws a single line.

When you're evaluating [their recent acquisition], wouldn't 
it be valuable to know exactly what's permitted — and what 
variance you'd need — in 30 seconds instead of 3 hours?

That's what ZoneWise does. Want to see your [property address] 
analyzed?

— ZoneWise AI SDR
```

**Sequence Logic:**
- Permit applicants → CERTAINTY first (fear of rejection)
- Experienced developers → SIGNIFICANCE first (competitive edge)
- Attorneys → IDENTITY PRESERVATION (see special template below)

---

#### Agent S2: Inbound Website BDR (Chatbot)

**Primary Need Targeted:** CERTAINTY + CONNECTION

**Conversation Flows by Detected Need:**

```python
CHATBOT_PSYCHOLOGY_TRIGGERS = {
    "certainty_signals": [
        "accurate", "reliable", "sure", "guarantee", 
        "compliant", "approved", "rejected", "mistake"
    ],
    "significance_signals": [
        "expert", "professional", "better than", 
        "competitive", "ahead", "first"
    ],
    "growth_signals": [
        "scale", "expand", "more projects", "faster",
        "multiple", "portfolio"
    ],
    "connection_signals": [
        "trust", "recommend", "reviews", "who uses",
        "testimonials", "proven"
    ]
}

# Response adaptation
if detected_need == "certainty":
    response = emphasize_accuracy_stats + cite_sources
elif detected_need == "significance":
    response = emphasize_edge_over_competitors
elif detected_need == "growth":
    response = emphasize_time_savings + scale_benefits
elif detected_need == "connection":
    response = share_testimonials + user_count
```

---

#### Agent S3: Lead Qualification

**Primary Need Targeted:** ALL (discovery phase)

**Qualification Questions Mapped to Needs:**

| Question | Need Detected | Scoring |
|----------|---------------|---------|
| "How do you currently verify zoning?" | CERTAINTY | Manual = high score |
| "How many projects per year?" | GROWTH | >5 = high score |
| "What's your biggest frustration with zoning research?" | SIGNIFICANCE | "Takes too long" = high score |
| "Who else on your team would use this?" | CONNECTION | Team = higher tier |

---

### CONTENT AGENTS

#### Agent C1: Content Generation

**Primary Need Targeted:** SIGNIFICANCE + CERTAINTY

**Content Types by Need:**

| Need | Content Type | Example Titles |
|------|-------------|----------------|
| CERTAINTY | Checklists, Guides | "Complete Brevard County Setback Requirements by District" |
| SIGNIFICANCE | Expert Insights | "5 Zoning Loopholes Only Experienced Developers Know" |
| GROWTH | Case Studies | "How [Developer] Expanded from 3 to 12 Projects/Year" |
| CONNECTION | Community Content | "What 47 Brevard Developers Say About Variance Approvals" |
| CONTRIBUTION | Impact Stories | "Building Workforce Housing: Zoning Strategies That Work" |

**Editorial Calendar Integration:**

```
Week 1: CERTAINTY content (technical, reference)
Week 2: SIGNIFICANCE content (insider knowledge)
Week 3: GROWTH content (expansion stories)
Week 4: CONNECTION content (community, testimonials)

Rotate monthly. Track engagement by need type to optimize.
```

---

#### Agent C2: Social Distribution

**Platform Psychology Mapping:**

| Platform | Primary Need | Content Style |
|----------|--------------|---------------|
| LinkedIn | SIGNIFICANCE | Authority, expertise, professional wins |
| Twitter/X | VARIETY | Quick tips, controversy, engagement |
| YouTube | GROWTH | Tutorials, how-tos, deep dives |
| Email | CERTAINTY | Reliable updates, reference material |

**LinkedIn Post Template (SIGNIFICANCE):**

```
🏗️ The difference between developers who get approved first-time 
and those who don't?

It's not experience. It's not connections.

It's verification BEFORE submission.

I just watched a $2.4M project get delayed 8 months because 
no one checked if the lot line setback was 10' or 15'.

The answer was in the Melbourne zoning code. Section 4.2.3.

ZoneWise would have found it in 4 seconds.

#RealEstateDevelopment #Zoning #BrevardCounty
```

---

#### Agent C3: SEO Content

**Keyword Strategy by Need:**

| Need | Search Intent | Target Keywords |
|------|--------------|-----------------|
| CERTAINTY | Verification | "melbourne florida setback requirements", "brevard county zoning map" |
| SIGNIFICANCE | Expertise | "zoning expert florida", "land use attorney brevard" |
| GROWTH | Expansion | "multi-family zoning florida", "commercial zoning melbourne" |
| CONNECTION | Social Proof | "zonewise reviews", "best zoning tool florida" |

---

### SUPPORT AGENT

#### Agent SU1: MCP Support (Accuracy Feedback)

**Primary Need:** CERTAINTY (core product promise)

**Error Handling Psychology:**

```python
ERROR_RESPONSES = {
    "data_missing": {
        "certainty_message": """
        I don't have complete data for {district} yet. 
        
        Rather than guess (which would be inaccurate), I'm flagging 
        this for our data team. We'll have verified information 
        within 48 hours.
        
        For immediate needs, here's the direct link to {jurisdiction}'s 
        official ordinance: {url}
        
        Accuracy > Speed. Always.
        """,
    },
    "conflicting_data": {
        "certainty_message": """
        I found conflicting information for {query}:
        - Source A ({date}): {value_a}
        - Source B ({date}): {value_b}
        
        The most recently published source is {recommendation}.
        
        However, I recommend confirming directly with {jurisdiction} 
        planning department at {phone} given this discrepancy.
        
        I've flagged this for resolution.
        """
    }
}
```

---

### OPERATIONS AGENTS

#### Agent O1: Competitive Intelligence

**Monitor competitors through SIGNIFICANCE lens:**

```python
COMPETITIVE_TRACKING = {
    "gridics": {
        "weakness": "No AI interface",
        "zonewise_counter": "SIGNIFICANCE: 'Be the AI-augmented expert'",
        "trigger": "When prospect mentions Gridics"
    },
    "municode": {
        "weakness": "Raw ordinance text, no interpretation",
        "zonewise_counter": "CERTAINTY: 'We tell you what it means'",
        "trigger": "When prospect mentions reading ordinances"
    },
    "planning_dept": {
        "weakness": "Slow response, office hours only",
        "zonewise_counter": "VARIETY: '24/7, any question, instant'",
        "trigger": "When prospect mentions calling the city"
    }
}
```

---

## Part 3: Identity Preservation Messaging (Critical)

### The AI Anxiety Response

**User Fear:** "AI will replace me"  
**Agent Response Protocol:** NEVER position ZoneWise as replacement

**Banned Phrases:**
- "Replaces the need for..."
- "No more expensive consultants..."
- "Do it yourself without..."
- "AI does it better than..."

**Required Phrases:**
- "Amplifies your expertise..."
- "Frees you for higher-value work..."
- "Makes you the AI-augmented professional..."
- "Your judgment + our data = unbeatable..."

**Template for Attorneys (High Identity Sensitivity):**

```
Subject: [FirstName], your clients need AI-augmented counsel

Hi [FirstName],

A quick observation: the attorneys winning the biggest land use 
cases in Brevard aren't fighting AI. They're wielding it.

ZoneWise doesn't replace your judgment—it arms it with instant, 
verified zoning data that would take your paralegal hours to compile.

Your clients pay for your analysis and strategy. 
They shouldn't pay for your research time.

Would you like to see how [recent case/property] looks through 
ZoneWise's compliance check?

— ZoneWise
```

---

## Part 4: Conversion Triggers by Need

### When to Push for Conversion

| Detected Need | Trigger Event | CTA |
|--------------|---------------|-----|
| CERTAINTY | User checks 3+ properties | "Lock in accuracy with Pro tier" |
| SIGNIFICANCE | User shares report externally | "Add your firm's branding with Enterprise" |
| GROWTH | User asks about other counties | "Unlock all 67 FL counties" |
| CONNECTION | User asks for references | "Join 200+ Brevard professionals" |
| CONTRIBUTION | User mentions affordable housing | "Partner discount for community projects" |

---

## Part 5: Agent Training Data Requirements

### Psychology-Aware Training Sets

Each agent needs training data tagged with psychological context:

```json
{
  "training_examples": [
    {
      "input": "How accurate is your data?",
      "need_detected": "certainty",
      "ideal_response": "Our data is sourced directly from published municipal ordinances and cross-verified against BCPAO records. We cite every source. When we're uncertain, we say so—and point you to the official document. Accuracy is our core promise.",
      "tone": "confident, specific, transparent"
    },
    {
      "input": "Why should I use this instead of just calling the planning department?",
      "need_detected": "significance",
      "ideal_response": "You absolutely should build relationships with planning staff—that's irreplaceable. ZoneWise handles the baseline lookup so when you DO call, you're asking informed questions, not basic ones. It positions you as the prepared professional.",
      "tone": "collaborative, elevating, non-threatening"
    }
  ]
}
```

---

## Part 6: Metrics Dashboard (Need-Based)

### Track Conversion by Psychological Trigger

| Metric | Purpose | Target |
|--------|---------|--------|
| CERTAINTY conversion rate | % who convert after accuracy messaging | 12% |
| SIGNIFICANCE conversion rate | % who convert after authority messaging | 8% |
| IDENTITY messaging response | % positive response to "amplifies expertise" | 15% |
| Fear-based open rate | Email opens with risk/loss subject lines | 35% |
| Ego-based open rate | Email opens with competitive edge subject lines | 28% |

### A/B Test Framework

```
Test: CERTAINTY vs SIGNIFICANCE lead message

Group A: "Avoid costly zoning mistakes" (CERTAINTY/fear)
Group B: "Be the most prepared professional" (SIGNIFICANCE/ego)

Measure: Response rate, conversion rate, LTV

Hypothesis: CERTAINTY leads win for investors, 
SIGNIFICANCE leads win for attorneys
```

---

## Part 7: Implementation Checklist

### Week 1: Foundation
- [ ] Tag existing content by primary need addressed
- [ ] Create persona-need mapping in Supabase
- [ ] Train S1 SDR on CERTAINTY + SIGNIFICANCE templates
- [ ] Configure chatbot triggers for need detection

### Week 2: Content Alignment
- [ ] Audit editorial calendar for need coverage
- [ ] Create content templates for each need type
- [ ] Build LinkedIn post library (5 per need)
- [ ] Design email sequences by persona-need

### Week 3: Agent Training
- [ ] Load psychology-aware training data to all agents
- [ ] Test identity preservation messaging
- [ ] Implement A/B testing framework
- [ ] Set up need-based conversion tracking

### Week 4: Optimization
- [ ] Analyze which needs drive highest conversion
- [ ] Adjust agent prioritization based on data
- [ ] Refine persona-need intensity scores
- [ ] Document learnings for next iteration

---

## Conclusion

The 16-agent ZoneWise stack becomes dramatically more effective when each agent understands not just WHAT users do, but WHY they do it.

**Key Insight:** Most competitors market features. ZoneWise markets to psychological needs. That's the difference between "95% accurate data" and "Never be surprised by zoning again."

**The Formula:**
```
Agent Reach (SaaStr model) × Psychological Resonance (Robbins model) 
= 10x Conversion Lift
```

---

*Psychology Integration Framework v1.0*  
*Claude AI Architect | January 18, 2026*  
*"Messages that resonate, not just reach."*
