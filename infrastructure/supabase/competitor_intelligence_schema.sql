-- ZoneWise Competitor Intelligence Database Schema
-- Supabase PostgreSQL Schema for storing competitor clones and analyses
-- Created: January 12, 2026

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ========================================
-- COMPETITOR CLONES TABLE
-- ========================================
CREATE TABLE IF NOT EXISTS competitor_clones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    competitor_name TEXT NOT NULL,
    website_url TEXT,
    clone_date TIMESTAMP NOT NULL DEFAULT NOW(),
    pages_count INTEGER,
    total_size_mb DECIMAL(10,2),
    confidence_scores JSONB, -- {"part_1": 70, "part_2": 60, "part_3": 20, "part_4": 65, "part_5": 30}
    storage_path TEXT, -- Path in Supabase Storage: competitor-clones/gridics/snapshots/2026-01-12/
    metadata JSONB, -- Additional metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ========================================
-- COMPETITOR ANALYSES TABLE
-- ========================================
CREATE TABLE IF NOT EXISTS competitor_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clone_id UUID REFERENCES competitor_clones(id) ON DELETE CASCADE,
    analysis_type TEXT NOT NULL, -- 'reverse_engineering', 'product_requirements', 'technical_specs', 'strategic_analysis', 'traffic_intelligence'
    confidence_score INTEGER CHECK (confidence_score >= 0 AND confidence_score <= 100),
    findings JSONB, -- Structured findings from analysis
    recommendations TEXT[], -- Array of actionable recommendations
    file_path TEXT, -- Path to detailed analysis document in Supabase Storage
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_competitor_analyses_type ON competitor_analyses(analysis_type);
CREATE INDEX IF NOT EXISTS idx_competitor_analyses_clone ON competitor_analyses(clone_id);

-- ========================================
-- DESIGN SYSTEMS EXTRACTED TABLE
-- ========================================
CREATE TABLE IF NOT EXISTS design_systems_extracted (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clone_id UUID REFERENCES competitor_clones(id) ON DELETE CASCADE,
    competitor_name TEXT NOT NULL,
    color_palette JSONB, -- {"primary": "#XXX", "secondary": "#YYY", "accent": "#ZZZ"}
    typography JSONB, -- {"primary_font": "Inter", "sizes": {"h1": 48, "h2": 36}}
    spacing_system JSONB, -- {"base": 4, "scale": [4, 8, 16, 24, 32, 48, 64]}
    components JSONB, -- {"buttons": {...}, "forms": {...}, "cards": {...}}
    layout_patterns JSONB,
    responsive_breakpoints JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ========================================
-- SEO ANALYSES TABLE
-- ========================================
CREATE TABLE IF NOT EXISTS seo_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clone_id UUID REFERENCES competitor_clones(id) ON DELETE CASCADE,
    competitor_name TEXT NOT NULL,
    analyzed_date TIMESTAMP DEFAULT NOW(),
    keywords JSONB, -- [{"keyword": "zoning", "volume": 1000, "difficulty": 45, "rank": null}]
    meta_tags JSONB, -- {"title": "...", "description": "...", "og_tags": {...}}
    lighthouse_scores JSONB, -- {"performance": 85, "seo": 92, "accessibility": 88, "best_practices": 90}
    content_analysis JSONB, -- {"word_count": 500, "readability": "good", "keyword_density": 2.5}
    technical_seo JSONB, -- {"page_speed": 2.5, "mobile_friendly": true, "https": true}
    recommendations TEXT[],
    created_at TIMESTAMP DEFAULT NOW()
);

-- ========================================
-- FEATURE COMPARISONS TABLE
-- ========================================
CREATE TABLE IF NOT EXISTS feature_comparisons (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    feature_category TEXT NOT NULL, -- 'search', 'reports', 'maps', 'calculator', 'authentication'
    feature_name TEXT NOT NULL,
    gridics_has BOOLEAN DEFAULT FALSE,
    zonewise_has BOOLEAN DEFAULT FALSE,
    gridics_quality TEXT CHECK (gridics_quality IN ('poor', 'good', 'excellent', 'unknown')),
    zonewise_quality TEXT CHECK (zonewise_quality IN ('poor', 'good', 'excellent', 'unknown')),
    competitive_advantage TEXT CHECK (competitive_advantage IN ('gridics', 'zonewise', 'neutral')),
    priority TEXT CHECK (priority IN ('critical', 'high', 'medium', 'low')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for feature category queries
CREATE INDEX IF NOT EXISTS idx_feature_comparisons_category ON feature_comparisons(feature_category);

-- ========================================
-- MONITORING SNAPSHOTS TABLE
-- ========================================
CREATE TABLE IF NOT EXISTS monitoring_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    competitor_name TEXT NOT NULL,
    snapshot_date TIMESTAMP NOT NULL DEFAULT NOW(),
    snapshot_type TEXT DEFAULT 'weekly', -- 'daily', 'weekly', 'monthly', 'on_demand'
    pages_captured JSONB, -- {"homepage": "hash123", "solutions": "hash456"}
    changes_from_previous JSONB, -- [{"page": "homepage", "change": "New hero image", "significance": "medium"}]
    priority TEXT CHECK (priority IN ('critical', 'high', 'medium', 'low')),
    action_required BOOLEAN DEFAULT FALSE,
    response_action TEXT,
    response_completed BOOLEAN DEFAULT FALSE,
    response_date TIMESTAMP,
    storage_path TEXT, -- Path to snapshot in Supabase Storage
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index for monitoring queries
CREATE INDEX IF NOT EXISTS idx_monitoring_snapshots_date ON monitoring_snapshots(snapshot_date DESC);
CREATE INDEX IF NOT EXISTS idx_monitoring_snapshots_name ON monitoring_snapshots(competitor_name);

-- ========================================
-- COMPETITIVE ALERTS TABLE
-- ========================================
CREATE TABLE IF NOT EXISTS competitive_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    competitor_name TEXT NOT NULL,
    alert_type TEXT NOT NULL, -- 'feature_launch', 'pricing_change', 'design_update', 'marketing_campaign', 'coverage_expansion'
    alert_description TEXT NOT NULL,
    severity TEXT CHECK (severity IN ('critical', 'high', 'medium', 'low')),
    detected_date TIMESTAMP DEFAULT NOW(),
    recommended_action TEXT,
    action_taken TEXT,
    action_completed BOOLEAN DEFAULT FALSE,
    action_date TIMESTAMP,
    created_by TEXT DEFAULT 'system', -- 'system' or 'manual'
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index for alerts
CREATE INDEX IF NOT EXISTS idx_competitive_alerts_severity ON competitive_alerts(severity);
CREATE INDEX IF NOT EXISTS idx_competitive_alerts_completed ON competitive_alerts(action_completed);

-- ========================================
-- PRICING INTELLIGENCE TABLE
-- ========================================
CREATE TABLE IF NOT EXISTS pricing_intelligence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    competitor_name TEXT NOT NULL,
    captured_date TIMESTAMP DEFAULT NOW(),
    pricing_visible BOOLEAN DEFAULT FALSE,
    pricing_tiers JSONB, -- [{"name": "Basic", "price": 49, "features": [...]}]
    pricing_model TEXT, -- 'subscription', 'usage_based', 'freemium', 'enterprise_only'
    free_tier_available BOOLEAN DEFAULT FALSE,
    trial_period_days INTEGER,
    payment_terms TEXT, -- 'monthly', 'annual', 'both'
    discounts JSONB, -- {"annual": "20%", "volume": "custom"}
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ========================================
-- ZONEWISE ENHANCEMENTS TRACKING TABLE
-- ========================================
CREATE TABLE IF NOT EXISTS zonewise_enhancements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    enhancement_type TEXT NOT NULL, -- 'feature', 'design', 'messaging', 'pricing', 'ux'
    based_on_competitor TEXT, -- 'gridics' or other
    description TEXT NOT NULL,
    rationale TEXT, -- Why this enhancement was chosen
    implementation_status TEXT CHECK (implementation_status IN ('planned', 'in_progress', 'completed', 'deferred', 'rejected')),
    priority TEXT CHECK (priority IN ('critical', 'high', 'medium', 'low')),
    target_quarter TEXT, -- 'Q1 2026', 'Q2 2026', etc.
    github_issue_url TEXT,
    completed_date TIMESTAMP,
    impact_notes TEXT, -- Actual impact after implementation
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for enhancements
CREATE INDEX IF NOT EXISTS idx_zonewise_enhancements_status ON zonewise_enhancements(implementation_status);
CREATE INDEX IF NOT EXISTS idx_zonewise_enhancements_priority ON zonewise_enhancements(priority);

-- ========================================
-- VIEWS FOR EASY QUERYING
-- ========================================

-- View: Latest competitor snapshot
CREATE OR REPLACE VIEW latest_competitor_snapshot AS
SELECT DISTINCT ON (competitor_name) *
FROM monitoring_snapshots
ORDER BY competitor_name, snapshot_date DESC;

-- View: Pending competitive alerts
CREATE OR REPLACE VIEW pending_competitive_alerts AS
SELECT *
FROM competitive_alerts
WHERE action_completed = FALSE
ORDER BY severity DESC, detected_date ASC;

-- View: Feature advantage summary
CREATE OR REPLACE VIEW feature_advantage_summary AS
SELECT 
    feature_category,
    COUNT(*) FILTER (WHERE competitive_advantage = 'zonewise') AS zonewise_advantages,
    COUNT(*) FILTER (WHERE competitive_advantage = 'gridics') AS gridics_advantages,
    COUNT(*) FILTER (WHERE competitive_advantage = 'neutral') AS neutral_features,
    COUNT(*) AS total_features
FROM feature_comparisons
GROUP BY feature_category;

-- View: Competitor clone summary
CREATE OR REPLACE VIEW competitor_clone_summary AS
SELECT 
    c.competitor_name,
    c.clone_date,
    c.pages_count,
    c.total_size_mb,
    c.confidence_scores,
    COUNT(a.id) AS analysis_count,
    MAX(a.created_at) AS latest_analysis_date
FROM competitor_clones c
LEFT JOIN competitor_analyses a ON c.id = a.clone_id
GROUP BY c.id, c.competitor_name, c.clone_date, c.pages_count, c.total_size_mb, c.confidence_scores;

-- ========================================
-- FUNCTIONS
-- ========================================

-- Function: Calculate average confidence score for a clone
CREATE OR REPLACE FUNCTION calculate_avg_confidence(clone_uuid UUID)
RETURNS DECIMAL AS $$
    SELECT AVG(confidence_score)::DECIMAL(5,2)
    FROM competitor_analyses
    WHERE clone_id = clone_uuid;
$$ LANGUAGE SQL;

-- Function: Get competitive advantage count
CREATE OR REPLACE FUNCTION get_advantage_count(advantage_type TEXT)
RETURNS INTEGER AS $$
    SELECT COUNT(*)::INTEGER
    FROM feature_comparisons
    WHERE competitive_advantage = advantage_type;
$$ LANGUAGE SQL;

-- ========================================
-- INITIAL DATA POPULATION
-- ========================================

-- Insert Gridics clone record
INSERT INTO competitor_clones (
    competitor_name,
    website_url,
    clone_date,
    pages_count,
    confidence_scores,
    storage_path
) VALUES (
    'Gridics',
    'https://gridics.com',
    '2026-01-12 00:00:00',
    13,
    '{"part_1": 70, "part_2": 60, "part_3": 20, "part_4": 65, "part_5": 30}'::JSONB,
    'competitor-clones/gridics/snapshots/2026-01-12/'
) ON CONFLICT DO NOTHING;

-- Insert initial feature comparisons (examples)
INSERT INTO feature_comparisons (feature_category, feature_name, gridics_has, zonewise_has, competitive_advantage, priority, notes) VALUES
('search', 'Address Search', TRUE, TRUE, 'neutral', 'critical', 'Both platforms have basic address search'),
('search', 'Natural Language Search', FALSE, TRUE, 'zonewise', 'high', 'ZoneWise allows "Can I build apartments in Melbourne?"'),
('reports', 'PDF Reports', TRUE, TRUE, 'neutral', 'critical', 'Both generate PDF reports'),
('reports', 'Development Calculator', FALSE, TRUE, 'zonewise', 'high', 'ZoneWise calculates max buildable SF and units'),
('maps', 'Interactive Map', TRUE, TRUE, 'neutral', 'high', 'Both have map visualization'),
('maps', 'PostGIS Spatial Queries', FALSE, TRUE, 'zonewise', 'medium', 'ZoneWise uses PostGIS for advanced spatial analysis'),
('pricing', 'Public Pricing', FALSE, TRUE, 'zonewise', 'critical', 'Gridics hides pricing, ZoneWise shows $49-999/month'),
('pricing', 'Free Tier', FALSE, TRUE, 'zonewise', 'high', 'ZoneWise offers 5 free searches/month'),
('data', 'Coverage Transparency', FALSE, TRUE, 'zonewise', 'critical', 'ZoneWise publishes 95%+ accuracy, Gridics does not'),
('data', 'Local Expertise', FALSE, TRUE, 'zonewise', 'critical', '100% Brevard coverage vs one of thousands')
ON CONFLICT DO NOTHING;

-- ========================================
-- COMMENTS
-- ========================================
COMMENT ON TABLE competitor_clones IS 'Master table storing metadata about competitor website clones';
COMMENT ON TABLE competitor_analyses IS 'Detailed analyses (5-part framework) for each competitor clone';
COMMENT ON TABLE design_systems_extracted IS 'Extracted design systems from competitor clones';
COMMENT ON TABLE seo_analyses IS 'SEO and content strategy analyses';
COMMENT ON TABLE feature_comparisons IS 'Feature-by-feature comparison matrix';
COMMENT ON TABLE monitoring_snapshots IS 'Weekly/monthly snapshots for change detection';
COMMENT ON TABLE competitive_alerts IS 'Actionable alerts triggered by competitive intelligence';
COMMENT ON TABLE pricing_intelligence IS 'Pricing strategy and monetization tracking';
COMMENT ON TABLE zonewise_enhancements IS 'Track improvements inspired by competitive intelligence';

-- ========================================
-- PERMISSIONS
-- ========================================
-- Grant appropriate permissions (adjust based on your Supabase roles)
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO authenticated;
-- GRANT INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO authenticated;

-- ========================================
-- SCHEMA COMPLETE
-- ========================================
SELECT 'ZoneWise Competitor Intelligence Schema Created Successfully' AS status;
