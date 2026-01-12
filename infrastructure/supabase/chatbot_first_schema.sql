-- ZONEWISE CHATBOT-FIRST SUPABASE SCHEMA
-- AI Chatbot/NLP is THE CORE, data supports it
-- Created: January 12, 2026

-- ========================================
-- CORE: CHATBOT CONVERSATIONS
-- ========================================

-- Conversations table (PRIMARY)
CREATE TABLE IF NOT EXISTS chatbot_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id),
    session_id TEXT NOT NULL,
    started_at TIMESTAMP DEFAULT NOW(),
    last_message_at TIMESTAMP DEFAULT NOW(),
    message_count INTEGER DEFAULT 0,
    conversation_status TEXT DEFAULT 'active', -- 'active', 'completed', 'abandoned'
    user_satisfaction INTEGER, -- 1-5 rating
    created_at TIMESTAMP DEFAULT NOW()
);

-- Messages table (conversation content)
CREATE TABLE IF NOT EXISTS chatbot_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES chatbot_conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL, -- 'user' or 'assistant'
    content TEXT NOT NULL,
    intent TEXT, -- classified intent ('feasibility', 'calculation', etc.)
    entities JSONB, -- extracted entities (address, zoning, use, location)
    context JSONB, -- conversation context at this message
    response_time_ms INTEGER, -- AI response time
    confidence_score DECIMAL(3,2), -- 0.00-1.00
    thumbs_up BOOLEAN, -- user feedback
    thumbs_down BOOLEAN,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_chatbot_messages_conversation ON chatbot_messages(conversation_id);
CREATE INDEX idx_chatbot_messages_created ON chatbot_messages(created_at DESC);

-- Intent classification tracking
CREATE TABLE IF NOT EXISTS chatbot_intents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    intent_type TEXT NOT NULL, -- 'feasibility', 'calculation', 'comparison', 'process', 'research', 'definition'
    user_query TEXT NOT NULL,
    classified_intent TEXT NOT NULL,
    confidence DECIMAL(3,2),
    correct_classification BOOLEAN, -- verified by human review
    message_id UUID REFERENCES chatbot_messages(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_chatbot_intents_type ON chatbot_intents(intent_type);

-- Entity extraction tracking
CREATE TABLE IF NOT EXISTS chatbot_entities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id UUID REFERENCES chatbot_messages(id),
    entity_type TEXT NOT NULL, -- 'address', 'zoning', 'use_type', 'location'
    entity_value TEXT NOT NULL,
    confidence DECIMAL(3,2),
    correct_extraction BOOLEAN,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Chatbot learning and improvement
CREATE TABLE IF NOT EXISTS chatbot_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id UUID REFERENCES chatbot_messages(id),
    conversation_id UUID REFERENCES chatbot_conversations(id),
    feedback_type TEXT NOT NULL, -- 'thumbs_up', 'thumbs_down', 'report', 'suggestion'
    feedback_text TEXT,
    user_id UUID REFERENCES auth.users(id),
    reviewed BOOLEAN DEFAULT FALSE,
    action_taken TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_chatbot_feedback_reviewed ON chatbot_feedback(reviewed);

-- ========================================
-- SUPPORT: ZONING DATA (serves chatbot)
-- ========================================

-- Jurisdictions
CREATE TABLE IF NOT EXISTS jurisdictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    county TEXT NOT NULL DEFAULT 'Brevard',
    state TEXT NOT NULL DEFAULT 'FL',
    data_completeness DECIMAL(5,2), -- 0-100%
    last_updated TIMESTAMP,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Zoning districts
CREATE TABLE IF NOT EXISTS zoning_districts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    jurisdiction_id UUID REFERENCES jurisdictions(id),
    code TEXT NOT NULL, -- 'R-1', 'C-2', etc.
    name TEXT NOT NULL,
    description TEXT, -- for chatbot to explain
    ordinance_section TEXT,
    geometry GEOMETRY(MULTIPOLYGON, 4326), -- PostGIS
    created_at TIMESTAMP DEFAULT NOW()
);

-- Allowed uses
CREATE TABLE IF NOT EXISTS allowed_uses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    zoning_district_id UUID REFERENCES zoning_districts(id),
    use_name TEXT NOT NULL,
    use_type TEXT NOT NULL, -- 'by-right', 'conditional', 'prohibited'
    conditions TEXT[], -- chatbot explains these
    ordinance_section TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Dimensional standards
CREATE TABLE IF NOT EXISTS dimensional_standards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    zoning_district_id UUID REFERENCES zoning_districts(id),
    min_lot_size INTEGER, -- SF
    setback_front DECIMAL(10,2), -- feet
    setback_side DECIMAL(10,2),
    setback_rear DECIMAL(10,2),
    max_height DECIMAL(10,2),
    max_lot_coverage DECIMAL(5,2), -- percentage
    max_far DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Parcels (for specific property queries)
CREATE TABLE IF NOT EXISTS parcels (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    jurisdiction_id UUID REFERENCES jurisdictions(id),
    parcel_id TEXT NOT NULL,
    address TEXT, -- indexed for chatbot lookups
    zoning_district_id UUID REFERENCES zoning_districts(id),
    geometry GEOMETRY(POLYGON, 4326),
    owner_name TEXT,
    square_footage INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(jurisdiction_id, parcel_id)
);

CREATE INDEX idx_parcels_address ON parcels USING GIN(to_tsvector('english', address));

-- ========================================
-- CHATBOT KNOWLEDGE BASE (RAG)
-- ========================================

-- Ordinance content for RAG retrieval
CREATE TABLE IF NOT EXISTS ordinance_content (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    jurisdiction_id UUID REFERENCES jurisdictions(id),
    section_number TEXT NOT NULL,
    section_title TEXT,
    content TEXT NOT NULL, -- full text for semantic search
    content_vector VECTOR(1536), -- embeddings for RAG
    metadata JSONB, -- {page, source, date, etc.}
    created_at TIMESTAMP DEFAULT NOW()
);

-- Chatbot knowledge embeddings
CREATE TABLE IF NOT EXISTS chatbot_knowledge_base (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_type TEXT NOT NULL, -- 'ordinance', 'faq', 'definition'
    question TEXT, -- common user question
    answer TEXT, -- curated answer
    source_reference TEXT,
    embedding VECTOR(1536), -- for similarity search
    usage_count INTEGER DEFAULT 0,
    last_used TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ========================================
-- ANALYTICS (chatbot-centric)
-- ========================================

-- Daily chatbot metrics
CREATE TABLE IF NOT EXISTS chatbot_daily_metrics (
    date DATE PRIMARY KEY,
    total_conversations INTEGER DEFAULT 0,
    total_messages INTEGER DEFAULT 0,
    avg_messages_per_conversation DECIMAL(5,2),
    avg_response_time_ms INTEGER,
    thumbs_up_count INTEGER DEFAULT 0,
    thumbs_down_count INTEGER DEFAULT 0,
    satisfaction_score DECIMAL(3,2), -- 0.00-1.00
    unique_users INTEGER DEFAULT 0,
    returning_users INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Chatbot performance tracking
CREATE TABLE IF NOT EXISTS chatbot_performance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name TEXT NOT NULL,
    metric_value DECIMAL(10,2),
    metric_unit TEXT, -- 'ms', 'percentage', 'count'
    timestamp TIMESTAMP DEFAULT NOW(),
    notes TEXT
);

-- ========================================
-- USER ACCOUNTS (support chatbot usage)
-- ========================================

CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id),
    subscription_tier TEXT DEFAULT 'free', -- free (5 chats), basic, pro, enterprise
    chatbot_usage_limit INTEGER DEFAULT 5, -- conversations per month
    chatbot_usage_count INTEGER DEFAULT 0, -- current month usage
    usage_reset_date DATE,
    api_key UUID DEFAULT uuid_generate_v4(), -- for API chatbot access
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ========================================
-- VIEWS FOR CHATBOT ANALYTICS
-- ========================================

-- Active conversations
CREATE OR REPLACE VIEW active_chatbot_conversations AS
SELECT 
    c.id,
    c.user_id,
    c.started_at,
    c.message_count,
    COUNT(m.id) FILTER (WHERE m.role = 'user') as user_message_count,
    COUNT(m.id) FILTER (WHERE m.role = 'assistant') as ai_message_count,
    MAX(m.created_at) as last_message_at
FROM chatbot_conversations c
LEFT JOIN chatbot_messages m ON c.id = m.conversation_id
WHERE c.conversation_status = 'active'
GROUP BY c.id, c.user_id, c.started_at, c.message_count;

-- Chatbot satisfaction summary
CREATE OR REPLACE VIEW chatbot_satisfaction_summary AS
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_rated_messages,
    COUNT(*) FILTER (WHERE thumbs_up = true) as thumbs_up_count,
    COUNT(*) FILTER (WHERE thumbs_down = true) as thumbs_down_count,
    ROUND(COUNT(*) FILTER (WHERE thumbs_up = true)::DECIMAL / NULLIF(COUNT(*), 0) * 100, 2) as satisfaction_percentage
FROM chatbot_messages
WHERE thumbs_up IS NOT NULL OR thumbs_down IS NOT NULL
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Intent distribution
CREATE OR REPLACE VIEW chatbot_intent_distribution AS
SELECT 
    intent_type,
    COUNT(*) as count,
    ROUND(COUNT(*)::DECIMAL / (SELECT COUNT(*) FROM chatbot_intents) * 100, 2) as percentage,
    AVG(confidence) as avg_confidence
FROM chatbot_intents
GROUP BY intent_type
ORDER BY count DESC;

-- Top unanswered questions (for improvement)
CREATE OR REPLACE VIEW chatbot_improvement_opportunities AS
SELECT 
    m.content as user_question,
    COUNT(*) as frequency,
    AVG(m.confidence_score) as avg_confidence,
    COUNT(*) FILTER (WHERE m.thumbs_down = true) as thumbs_down_count
FROM chatbot_messages m
WHERE m.role = 'user'
AND (m.confidence_score < 0.7 OR m.thumbs_down = true)
GROUP BY m.content
ORDER BY frequency DESC, thumbs_down_count DESC
LIMIT 50;

-- ========================================
-- FUNCTIONS
-- ========================================

-- Function: Get chatbot response time p95
CREATE OR REPLACE FUNCTION get_chatbot_response_time_p95()
RETURNS INTEGER AS $$
    SELECT PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms)::INTEGER
    FROM chatbot_messages
    WHERE role = 'assistant'
    AND response_time_ms IS NOT NULL;
$$ LANGUAGE SQL;

-- Function: Calculate chatbot satisfaction rate
CREATE OR REPLACE FUNCTION get_chatbot_satisfaction_rate()
RETURNS DECIMAL AS $$
    SELECT ROUND(
        COUNT(*) FILTER (WHERE thumbs_up = true)::DECIMAL / 
        NULLIF(COUNT(*) FILTER (WHERE thumbs_up IS NOT NULL OR thumbs_down IS NOT NULL), 0) * 100,
        2
    )
    FROM chatbot_messages;
$$ LANGUAGE SQL;

-- ========================================
-- COMMENTS
-- ========================================

COMMENT ON TABLE chatbot_conversations IS 'PRIMARY: User conversations with AI chatbot (THE CORE)';
COMMENT ON TABLE chatbot_messages IS 'All messages in chatbot conversations (user and AI)';
COMMENT ON TABLE chatbot_intents IS 'Intent classification tracking for ML improvement';
COMMENT ON TABLE chatbot_entities IS 'Entity extraction tracking for NLP improvement';
COMMENT ON TABLE chatbot_feedback IS 'User feedback for continuous chatbot learning';
COMMENT ON TABLE chatbot_knowledge_base IS 'RAG knowledge base for chatbot responses';
COMMENT ON TABLE ordinance_content IS 'Full ordinance text for semantic search';
COMMENT ON TABLE jurisdictions IS 'SUPPORT: Brevard County jurisdictions (serves chatbot)';
COMMENT ON TABLE zoning_districts IS 'SUPPORT: Zoning codes (serves chatbot knowledge)';
COMMENT ON TABLE allowed_uses IS 'SUPPORT: Permitted uses (serves chatbot answers)';
COMMENT ON TABLE parcels IS 'SUPPORT: Property data (serves chatbot lookups)';

-- ========================================
-- INITIAL DATA
-- ========================================

-- Insert core intent types
INSERT INTO chatbot_intents (intent_type, user_query, classified_intent, confidence, correct_classification) VALUES
('feasibility', 'Can I build apartments in Melbourne?', 'feasibility', 0.95, true),
('calculation', 'How much can I build on my lot?', 'calculation', 0.92, true),
('comparison', 'What is the difference between R-1 and R-1A?', 'comparison', 0.88, true),
('process', 'How do I get a variance?', 'process', 0.90, true),
('research', 'Show me all properties where I can build 4 units', 'research', 0.87, true),
('definition', 'What does FAR mean?', 'definition', 0.93, true)
ON CONFLICT DO NOTHING;

-- ========================================
-- SCHEMA COMPLETE
-- ========================================
SELECT 'ZoneWise Chatbot-First Schema Created Successfully - AI is THE CORE' AS status;
