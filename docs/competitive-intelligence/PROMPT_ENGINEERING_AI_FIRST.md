# ZoneWise Prompt Engineering Framework - AI-First Foundation
## Complete System for Building AI-Powered Conversational Zoning Intelligence

**Product:** ZoneWise  
**Foundation:** AI Chatbot/NLP as THE CORE  
**Created:** January 12, 2026 (Updated from original)

---

## 🎯 FOUNDATIONAL PRINCIPLE

**BEFORE using ANY prompt in this framework, remember:**

```
AI Chatbot/NLP = THE CORE (Layer 1)
ML/AI Capabilities = INTELLIGENCE (Layer 2)
Real Data Integration = KNOWLEDGE (Layer 3)

The AI chatbot IS THE PRODUCT.
Everything else SUPPORTS the chatbot.
```

**This means:**
- Every prompt must consider: "How does this enable/improve the chatbot?"
- Every feature must ask: "Does this support conversational AI?"
- Every decision must align: "Chatbot first, data second"

---

## 📊 UPDATED PROMPT STRUCTURE

### **11 Enhanced Prompts (AI-First Lens)**

**Core Prompts (1-4): Build the Chatbot**
1. **AI Chatbot Core Development** - NLP, intent, context (NEW - PRIORITY 1)
2. Conversational UX Design - Chat-first interface design
3. Knowledge Base & RAG - Data integration for chatbot
4. Conversation Analytics - Chatbot metrics and learning

**Competitive Intelligence (5-8): Understand Market**
5. Initial Website Clone - Full competitor capture
6. AI Capabilities Analysis - Chatbot comparison
7. Feature Extraction - What serves their chatbot?
8. Strategic Analysis - How do we differentiate with AI?

**Supporting Systems (9-11): Complete Product**
9. Traditional Search (Fallback) - When chatbot can't help
10. Maps & Visualization - Chatbot-accessible features
11. Continuous Monitoring - Track competitive chatbot moves

---

## 🤖 PROMPT 1: AI CHATBOT CORE DEVELOPMENT (NEW - HIGHEST PRIORITY)

**Purpose:** Build the natural language processing and conversational AI that IS ZoneWise

**Use When:** Starting AI chatbot development, improving NLP, enhancing conversations

**Prompt:**

```
You are the lead AI engineer building ZoneWise, an AI-powered conversational zoning intelligence platform.

CRITICAL FOUNDATION:
The AI chatbot with Natural Language Processing IS THE PRODUCT.
Everything else (database, maps, reports) SUPPORTS THE CHATBOT.

Your mission: Build the best conversational zoning AI in the world.

CHATBOT REQUIREMENTS:

1. NATURAL LANGUAGE UNDERSTANDING (NLP)
   Input: Plain English questions from users
   - "Can I build apartments in Melbourne?"
   - "What's the difference between R-1 and R-1A?"
   - "How much can I build on my 10,000 SF lot?"
   
   Requirements:
   - Accept conversational input (not keywords)
   - Handle misspellings and colloquialisms
   - Understand context from previous messages
   - Detect user intent (6 core types)
   - Extract entities (address, zoning, use, location)
   
   Technology:
   - NLP Model: Gemini 2.5 Flash (90% FREE tier)
   - Backup: Claude Sonnet 4.5 (complex reasoning)
   - Orchestration: LangGraph (agentic workflows)
   - Pattern: ForecastEngine™ (proven 93.7 accuracy)

2. INTENT CLASSIFICATION (6 Core Types)
   
   **Feasibility:** "Can I build X?"
   - User wants to know if something is allowed
   - Response: Yes/No + conditions + next steps
   - Example: "Can I build a duplex?" → "Yes, in R-1A zoning with..."
   
   **Calculation:** "How much can I build?"
   - User wants quantitative analysis
   - Response: Numbers + breakdown + assumptions
   - Example: "Max SF?" → "6,250 SF based on lot size × FAR..."
   
   **Comparison:** "What's the difference between X and Y?"
   - User wants to understand distinctions
   - Response: Side-by-side comparison + recommendation
   - Example: "R-1 vs R-1A?" → "Table showing key differences..."
   
   **Process:** "How do I get a permit/variance?"
   - User needs procedural guidance
   - Response: Step-by-step + contacts + timeline
   - Example: "Variance process?" → "1. Submit application 2..."
   
   **Research:** "Find properties where I can build X"
   - User wants to discover options
   - Response: List of matches + map + details
   - Example: "4-unit properties?" → "Found 12 parcels in..."
   
   **Definition:** "What does X mean?"
   - User needs education
   - Response: Clear explanation + example + context
   - Example: "What's FAR?" → "Floor Area Ratio is..."

3. ENTITY EXTRACTION
   
   Extract from user input:
   - **Address:** "123 Ocean Ave" → Geocode and lookup
   - **Zoning:** "R-1" or "residential" → Normalize to code
   - **Use Type:** "apartments" → Map to allowed_uses
   - **Location:** "Melbourne" → Filter to jurisdiction
   - **Quantity:** "10,000 SF" → Use in calculations
   
   Technology:
   - Named Entity Recognition (NER)
   - Regex patterns for addresses
   - Fuzzy matching for locations
   - Confidence scoring (0.0-1.0)

4. MULTI-TURN CONTEXT MANAGEMENT
   
   Maintain conversation state:
   ```python
   conversation_context = {
       "session_id": "session_123",
       "current_property": {
           "address": "123 Ocean Ave, Satellite Beach",
           "parcel_id": "25-37-123-456",
           "zoning": "R-1",
           "lot_size": 7500
       },
       "conversation_history": [
           {"role": "user", "content": "What's the zoning?"},
           {"role": "assistant", "content": "R-1 Single-Family"},
           {"role": "user", "content": "Can I add a garage apartment?"}
       ],
       "user_intent": "feasibility",
       "entities": {
           "use_type": "ADU",
           "property": "123 Ocean Ave"
       }
   }
   ```
   
   Context Rules:
   - Remember last 10 messages
   - Track current property throughout conversation
   - Reference previous entities without re-asking
   - Build on prior answers ("As I mentioned...")
   - Ask clarifying questions when context unclear

5. RAG KNOWLEDGE RETRIEVAL
   
   Retrieve relevant zoning data for responses:
   
   ```python
   def retrieve_knowledge(user_query, conversation_context):
       # Step 1: Extract search terms from query
       search_terms = extract_key_terms(user_query)
       
       # Step 2: Semantic search on ordinance content
       ordinances = supabase.rpc('search_ordinances_semantic', {
           'query_embedding': embed(user_query),
           'similarity_threshold': 0.7,
           'limit': 5
       })
       
       # Step 3: Structured data lookup
       if conversation_context['current_property']:
           zoning_data = supabase.table('zoning_districts').select('*').eq(
               'code', conversation_context['current_property']['zoning']
           ).single()
       
       # Step 4: Combine and rank by relevance
       knowledge = {
           'ordinances': ordinances,
           'zoning_data': zoning_data,
           'confidence': calculate_confidence(ordinances)
       }
       
       return knowledge
   ```

6. RESPONSE GENERATION
   
   Generate natural language responses:
   
   **Principles:**
   - Conversational tone (friendly, helpful)
   - Clear and concise (no jargon unless explained)
   - Actionable (include next steps)
   - Accurate (cite sources when needed)
   - Honest (admit uncertainty, don't guess)
   
   **Structure:**
   1. Direct answer first
   2. Supporting details
   3. Explanation if needed
   4. Suggested next steps
   5. Offer further help
   
   **Example:**
   ```
   User: "Can I build apartments in Melbourne?"
   
   BAD Response:
   "The zoning code for the City of Melbourne allows multifamily 
   residential development in certain designated districts subject 
   to compliance with dimensional standards..."
   
   GOOD Response:
   "Yes, apartments are allowed in Melbourne! They're permitted 
   in R-2, R-3, and certain commercial zones.
   
   To give you specific details, I'd need to know your property 
   address. Do you have a specific location in mind?"
   ```

7. FOLLOW-UP SUGGESTIONS
   
   After each response, suggest 3-5 relevant actions:
   
   ```python
   def generate_suggestions(intent, context, zoning_data):
       suggestions = []
       
       if intent == "feasibility":
           if context['current_property']:
               suggestions = [
                   "Calculate maximum buildable SF",
                   "View parking requirements",
                   "Generate development report (PDF)",
                   "Show property on map"
               ]
           else:
               suggestions = [
                   "Provide property address for analysis",
                   "Browse properties by zoning type",
                   "Learn about zoning districts"
               ]
       
       elif intent == "calculation":
           suggestions = [
               "View setback diagram",
               "Check height restrictions",
               "Calculate parking spaces needed",
               "Generate detailed report"
           ]
       
       return suggestions[:5]  # Max 5 suggestions
   ```

8. EDUCATIONAL MODE
   
   Detect when user needs education:
   
   **Triggers:**
   - User asks "What does X mean?"
   - User seems confused (clarification questions)
   - User is first-time developer (inferred from conversation)
   - Technical term used that may be unfamiliar
   
   **Response Style:**
   - Define term simply
   - Provide real-world example
   - Use analogy if helpful
   - Offer to explain more ("Want details?")
   - Link to source ordinance
   
   **Example:**
   ```
   User: "What's FAR?"
   
   ZoneWise: "FAR stands for Floor Area Ratio. It's the ratio 
   of a building's total floor area to the lot size.
   
   Simple example:
   • Your lot: 10,000 SF
   • FAR allowed: 0.5
   • Maximum building: 10,000 × 0.5 = 5,000 SF total
   
   This could be 5,000 SF single-story OR 2,500 SF two-story.
   
   Want me to calculate FAR for a specific property?"
   ```

9. ERROR HANDLING & GRACEFUL DEGRADATION
   
   **When chatbot can't answer:**
   
   ```python
   if confidence < 0.7:
       response = (
           "I'm not 100% certain about this answer. "
           "Would you like me to:\n"
           "• Search our database directly\n"
           "• Connect you with a human expert\n"
           "• Provide general guidance with disclaimer"
       )
   
   if no_relevant_data_found:
       response = (
           "I don't have specific information about that in my "
           "knowledge base. However, I can:\n"
           "• Search Brevard County planning departments\n"
           "• Suggest similar questions I can answer\n"
           "• Escalate to human support"
       )
   
   if technical_error:
       response = (
           "I'm experiencing a technical issue. Let me try "
           "a different approach...\n"
           "[Fallback to simpler method]"
       )
   ```

10. CONTINUOUS LEARNING
    
    **Feedback Loop:**
    
    Every conversation teaches the chatbot:
    
    ```python
    # After each message
    supabase.table('chatbot_messages').insert({
        'conversation_id': conversation_id,
        'role': 'assistant',
        'content': response,
        'intent': classified_intent,
        'entities': extracted_entities,
        'confidence_score': confidence,
        'response_time_ms': response_time
    })
    
    # User feedback
    if thumbs_up:
        # Reinforce this pattern
        update_model_weights(positive_feedback)
    
    if thumbs_down:
        # Learn what went wrong
        supabase.table('chatbot_feedback').insert({
            'message_id': message_id,
            'feedback_type': 'thumbs_down',
            'feedback_text': user_comment
        })
        # Queue for human review and model improvement
    ```

11. PERFORMANCE TARGETS
    
    **Quality:**
    - Intent classification accuracy: 90%+
    - Entity extraction accuracy: 85%+
    - Answer accuracy: 95%+
    - User satisfaction: 4.5+/5.0
    
    **Speed:**
    - Response time: <2 seconds (p95)
    - NLP processing: <500ms
    - Knowledge retrieval: <500ms
    - Response generation: <1s
    
    **Engagement:**
    - Multi-turn conversations: 80%+ (>1 exchange)
    - Average messages per conversation: 5-10
    - Thumbs up rate: 80%+
    - Return user rate: 40%+ weekly

OUTPUT DELIVERABLES:
1. chatbot_core_implementation.py (LangGraph + FastAPI)
2. nlu_models.py (intent classification, entity extraction)
3. rag_retrieval.py (knowledge base queries)
4. response_generator.py (natural language generation)
5. conversation_manager.py (context and state)
6. educational_content.py (explanations and examples)
7. chatbot_test_suite.py (100+ test conversations)
8. performance_monitoring.py (metrics and analytics)

SUCCESS CRITERIA:
✅ Users prefer chatbot over traditional search (80%+ usage)
✅ Chatbot accurately answers 95%+ of zoning questions
✅ Response time consistently <2 seconds
✅ User satisfaction 4.5+/5.0
✅ Users describe it as "like talking to an expert"
```

---

## 🎨 PROMPT 2: CONVERSATIONAL UX DESIGN (UPDATED)

**Purpose:** Design chat-first user interface and conversation flows

**Original Focus:** General UX and information architecture
**AI-First Update:** Prioritize conversational interface design

**Prompt:**

```
You are a conversation designer for ZoneWise, an AI-powered conversational zoning platform.

CORE PRINCIPLE:
Chat interface is THE PRIMARY user experience, not a feature.
Traditional forms/search are FALLBACK only.

DESIGN REQUIREMENTS:

1. HOMEPAGE: CHAT-FIRST
   
   Hero Section:
   ┌────────────────────────────────────────┐
   │  ZONEWISE                              │
   │  Your AI Zoning Expert                 │
   │                                        │
   │  ┌──────────────────────────────────┐ │
   │  │  💬 Ask me anything about        │ │
   │  │     Brevard County zoning        │ │
   │  │                                   │ │
   │  │  Try:                             │ │
   │  │  • Can I build apartments in      │ │
   │  │    Melbourne?                     │ │
   │  │  • What's R-1 zoning?            │ │
   │  │  • How much can I build?         │ │
   │  │                                   │ │
   │  │  [Type your question here...]     │ │
   │  │  🎤 [Voice] 💬 [Send]            │ │
   │  └──────────────────────────────────┘ │
   │                                        │
   │  🎯 No zoning knowledge required       │
   │  ⚡ Instant accurate answers           │
   │  🤖 Powered by AI                     │
   └────────────────────────────────────────┘
   
   NOT:
   ❌ Search bar as hero
   ❌ "Search our database" headline
   ❌ Forms-first design

2. CONVERSATION FLOW DESIGN
   
   Principles:
   - Start with open-ended prompt
   - Ask clarifying questions naturally
   - Build context over multiple turns
   - Suggest next steps proactively
   - Make it feel like talking to expert
   
   Example Flow:
   
   Welcome Message:
   "Hi! I'm ZoneWise AI, your zoning expert for Brevard County. 
   What would you like to know?"
   
   User: "Can I build apartments?"
   
   Chatbot: "Apartments are allowed in several Brevard zones. 
   Do you have a specific property in mind? If so, I can give 
   you exact details."
   
   User: "Yes, 456 Palm Bay Road in Melbourne"
   
   Chatbot: "Perfect! Let me look that up...
   
   📍 456 Palm Bay Rd, Melbourne, FL
   🏘️ Zoning: R-2 (Medium Density Residential)
   📏 Lot Size: 12,500 SF
   
   ✅ Good news! Apartments (up to 5 units) are allowed by-right.
   
   Would you like me to:
   • Calculate maximum buildable SF
   • Show parking requirements  
   • Generate development report
   • View comparable properties"

3. MOBILE CHAT OPTIMIZATION
   
   - Full-screen chat interface
   - Thumb-friendly message input
   - Voice input prominent (future)
   - Swipe gestures for navigation
   - Quick reply buttons for suggestions
   - Typing indicator during AI processing
   - Message bubbles (user vs AI)

4. ACCESSIBILITY
   
   - ARIA labels for screen readers
   - Keyboard navigation (Tab, Enter)
   - High contrast mode
   - Text sizing options
   - Voice input/output (future)

OUTPUT:
1. Homepage_Chat_First.figma (mockups)
2. Conversation_Flows.pdf (10+ example interactions)
3. Mobile_Chat_Designs.figma (iOS + Android)
4. Accessibility_Checklist.md (WCAG 2.1 AA compliance)
```

---

[Continue with remaining prompts updated for AI-first...]

