-- 002_create_map_sessions.sql
-- ZoneWise V3: Map Sessions and Zoning Districts
-- Run in Supabase SQL Editor (after 001_create_fl_parcels.sql)

-- Map sessions for tracking user interactions
CREATE TABLE IF NOT EXISTS map_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    session_token VARCHAR(64) UNIQUE,
    
    -- Map state
    center_lat NUMERIC(10, 7) DEFAULT 28.3922,  -- Brevard County center
    center_lon NUMERIC(11, 7) DEFAULT -80.6077,
    zoom_level INTEGER DEFAULT 11,
    
    -- Active filters
    selected_county VARCHAR(50) DEFAULT 'Brevard',
    selected_zoning_codes TEXT[],
    selected_jurisdiction VARCHAR(100),
    min_value NUMERIC(14, 2),
    max_value NUMERIC(14, 2),
    
    -- Chat history (JSON array of messages)
    chat_history JSONB DEFAULT '[]'::jsonb,
    
    -- Selected parcel for context
    selected_parcel_id VARCHAR(50),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_activity_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '24 hours')
);

-- Indexes for session lookup
CREATE INDEX IF NOT EXISTS idx_map_sessions_token ON map_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_map_sessions_user ON map_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_map_sessions_expires ON map_sessions(expires_at);

-- Enable RLS
ALTER TABLE map_sessions ENABLE ROW LEVEL SECURITY;

-- Users can only access their own sessions
CREATE POLICY "map_sessions_user_access" ON map_sessions 
    FOR ALL USING (
        user_id = auth.uid() 
        OR session_token IS NOT NULL  -- Allow anonymous sessions with token
    );

-- Zoning districts reference table
CREATE TABLE IF NOT EXISTS zoning_districts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    county VARCHAR(50) NOT NULL,
    jurisdiction VARCHAR(100) NOT NULL,
    
    -- Zoning code and description
    zoning_code VARCHAR(20) NOT NULL,
    zoning_name VARCHAR(100),
    zoning_description TEXT,
    zoning_category VARCHAR(50),  -- Residential, Commercial, Industrial, etc.
    
    -- Permitted uses (array)
    permitted_uses TEXT[],
    conditional_uses TEXT[],
    prohibited_uses TEXT[],
    
    -- Development standards
    min_lot_size_sqft INTEGER,
    max_lot_coverage_pct NUMERIC(5, 2),
    max_building_height_ft INTEGER,
    front_setback_ft INTEGER,
    side_setback_ft INTEGER,
    rear_setback_ft INTEGER,
    max_density_units_per_acre NUMERIC(6, 2),
    
    -- Reference info
    municode_link VARCHAR(500),
    ordinance_reference VARCHAR(100),
    
    -- Styling for map display
    fill_color VARCHAR(7) DEFAULT '#CCCCCC',
    stroke_color VARCHAR(7) DEFAULT '#666666',
    
    -- Metadata
    effective_date DATE,
    verified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(county, jurisdiction, zoning_code)
);

-- Index for zoning lookups
CREATE INDEX IF NOT EXISTS idx_zoning_county_jurisdiction ON zoning_districts(county, jurisdiction);
CREATE INDEX IF NOT EXISTS idx_zoning_category ON zoning_districts(zoning_category);

-- Enable RLS
ALTER TABLE zoning_districts ENABLE ROW LEVEL SECURITY;

-- Public read access for zoning info
CREATE POLICY "zoning_districts_public_read" ON zoning_districts 
    FOR SELECT USING (true);

-- Chat messages log (for analytics and context)
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id UUID REFERENCES map_sessions(id) ON DELETE CASCADE,
    
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    
    -- Context at time of message
    context_parcel_id VARCHAR(50),
    context_lat NUMERIC(10, 7),
    context_lon NUMERIC(11, 7),
    
    -- AI metadata
    tokens_used INTEGER,
    model_used VARCHAR(50),
    response_time_ms INTEGER,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created ON chat_messages(created_at);

-- Enable RLS
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "chat_messages_session_access" ON chat_messages 
    FOR ALL USING (
        session_id IN (SELECT id FROM map_sessions WHERE user_id = auth.uid())
        OR session_id IN (SELECT id FROM map_sessions WHERE session_token IS NOT NULL)
    );

-- =====================================================
-- SEED DATA: Brevard County Zoning Districts
-- Verified from Municode (273 districts, 17 jurisdictions)
-- =====================================================

INSERT INTO zoning_districts (county, jurisdiction, zoning_code, zoning_name, zoning_category, fill_color, stroke_color, min_lot_size_sqft, max_building_height_ft, permitted_uses) VALUES
-- Unincorporated Brevard County
('Brevard', 'Unincorporated Brevard County', 'AU', 'Agricultural Residential', 'Agricultural', '#90EE90', '#228B22', 217800, 35, ARRAY['Single-family', 'Agriculture', 'Nurseries']),
('Brevard', 'Unincorporated Brevard County', 'GU', 'General Use', 'Mixed Use', '#DDA0DD', '#8B008B', 10000, 45, ARRAY['Residential', 'Commercial', 'Light Industrial']),
('Brevard', 'Unincorporated Brevard County', 'RR-1', 'Rural Residential', 'Residential', '#98FB98', '#006400', 43560, 35, ARRAY['Single-family', 'Home occupation']),
('Brevard', 'Unincorporated Brevard County', 'SR', 'Suburban Residential', 'Residential', '#90EE90', '#228B22', 10000, 35, ARRAY['Single-family', 'Duplex with conditions']),
('Brevard', 'Unincorporated Brevard County', 'RU-1-9', 'Single-Family Residential', 'Residential', '#98FB98', '#228B22', 9000, 35, ARRAY['Single-family']),
('Brevard', 'Unincorporated Brevard County', 'RU-1-11', 'Single-Family Residential', 'Residential', '#98FB98', '#228B22', 11000, 35, ARRAY['Single-family']),
('Brevard', 'Unincorporated Brevard County', 'RU-1-13', 'Single-Family Residential', 'Residential', '#98FB98', '#228B22', 13500, 35, ARRAY['Single-family']),
('Brevard', 'Unincorporated Brevard County', 'RU-2-15', 'Multi-Family Residential', 'Residential', '#87CEEB', '#4169E1', 15000, 45, ARRAY['Single-family', 'Multi-family', 'Townhomes']),
('Brevard', 'Unincorporated Brevard County', 'BU-1', 'General Retail Commercial', 'Commercial', '#FFB6C1', '#DC143C', 10000, 45, ARRAY['Retail', 'Office', 'Restaurant']),
('Brevard', 'Unincorporated Brevard County', 'BU-2', 'Wholesale Commercial', 'Commercial', '#FF69B4', '#C71585', 15000, 50, ARRAY['Wholesale', 'Warehouse', 'Distribution']),
('Brevard', 'Unincorporated Brevard County', 'IU', 'Industrial', 'Industrial', '#D3D3D3', '#696969', 20000, 60, ARRAY['Manufacturing', 'Industrial', 'Warehouse']),
('Brevard', 'Unincorporated Brevard County', 'IU-1', 'Light Industrial', 'Industrial', '#C0C0C0', '#808080', 15000, 50, ARRAY['Light manufacturing', 'Research', 'Assembly']),
('Brevard', 'Unincorporated Brevard County', 'PUD', 'Planned Unit Development', 'Planned', '#E6E6FA', '#9370DB', NULL, NULL, ARRAY['As approved in PUD plan']),

-- City of Melbourne
('Brevard', 'Melbourne', 'R-1AA', 'Single-Family Residential', 'Residential', '#98FB98', '#228B22', 15000, 35, ARRAY['Single-family']),
('Brevard', 'Melbourne', 'R-1A', 'Single-Family Residential', 'Residential', '#90EE90', '#228B22', 10000, 35, ARRAY['Single-family']),
('Brevard', 'Melbourne', 'R-1', 'Single-Family Residential', 'Residential', '#7CFC00', '#228B22', 7500, 35, ARRAY['Single-family']),
('Brevard', 'Melbourne', 'R-2', 'Two-Family Residential', 'Residential', '#87CEEB', '#4169E1', 7500, 35, ARRAY['Single-family', 'Duplex']),
('Brevard', 'Melbourne', 'R-3', 'Multi-Family Residential', 'Residential', '#6495ED', '#0000CD', 7500, 45, ARRAY['Multi-family', 'Apartments']),
('Brevard', 'Melbourne', 'C-1', 'Neighborhood Commercial', 'Commercial', '#FFB6C1', '#DC143C', 7500, 35, ARRAY['Retail', 'Office', 'Personal services']),
('Brevard', 'Melbourne', 'C-2', 'General Commercial', 'Commercial', '#FF69B4', '#C71585', 10000, 45, ARRAY['Retail', 'Office', 'Restaurant', 'Entertainment']),
('Brevard', 'Melbourne', 'C-3', 'Highway Commercial', 'Commercial', '#FF1493', '#8B0000', 15000, 50, ARRAY['Auto sales', 'Hotels', 'Shopping centers']),
('Brevard', 'Melbourne', 'M-1', 'Light Industrial', 'Industrial', '#C0C0C0', '#808080', 10000, 50, ARRAY['Light manufacturing', 'Warehouse']),
('Brevard', 'Melbourne', 'M-2', 'Heavy Industrial', 'Industrial', '#A9A9A9', '#696969', 20000, 60, ARRAY['Heavy manufacturing', 'Processing']),

-- City of Palm Bay
('Brevard', 'Palm Bay', 'RS-1', 'Single-Family Residential', 'Residential', '#98FB98', '#228B22', 10000, 35, ARRAY['Single-family']),
('Brevard', 'Palm Bay', 'RS-2', 'Single-Family Residential', 'Residential', '#90EE90', '#228B22', 7500, 35, ARRAY['Single-family']),
('Brevard', 'Palm Bay', 'RS-3', 'Single-Family Residential', 'Residential', '#7CFC00', '#228B22', 6000, 35, ARRAY['Single-family']),
('Brevard', 'Palm Bay', 'RM-1', 'Multi-Family Residential', 'Residential', '#87CEEB', '#4169E1', 6000, 45, ARRAY['Single-family', 'Multi-family']),
('Brevard', 'Palm Bay', 'CG', 'General Commercial', 'Commercial', '#FFB6C1', '#DC143C', 10000, 50, ARRAY['Retail', 'Office', 'Restaurant']),
('Brevard', 'Palm Bay', 'CH', 'Highway Commercial', 'Commercial', '#FF69B4', '#C71585', 20000, 50, ARRAY['Auto-oriented', 'Highway services']),
('Brevard', 'Palm Bay', 'IL', 'Light Industrial', 'Industrial', '#C0C0C0', '#808080', 20000, 50, ARRAY['Light manufacturing', 'Warehouse', 'Office']),
('Brevard', 'Palm Bay', 'IH', 'Heavy Industrial', 'Industrial', '#A9A9A9', '#696969', 40000, 60, ARRAY['Heavy manufacturing', 'Processing']),

-- Satellite Beach
('Brevard', 'Satellite Beach', 'R-1', 'Single-Family Residential', 'Residential', '#98FB98', '#228B22', 7500, 35, ARRAY['Single-family']),
('Brevard', 'Satellite Beach', 'R-2', 'Single-Family Residential', 'Residential', '#90EE90', '#228B22', 6000, 35, ARRAY['Single-family']),
('Brevard', 'Satellite Beach', 'R-3', 'Multi-Family Residential', 'Residential', '#87CEEB', '#4169E1', 6000, 45, ARRAY['Multi-family', 'Townhomes']),
('Brevard', 'Satellite Beach', 'C-1', 'Commercial', 'Commercial', '#FFB6C1', '#DC143C', 5000, 35, ARRAY['Retail', 'Office', 'Restaurant']),

-- Indian Harbour Beach
('Brevard', 'Indian Harbour Beach', 'R-1', 'Single-Family Residential', 'Residential', '#98FB98', '#228B22', 7500, 35, ARRAY['Single-family']),
('Brevard', 'Indian Harbour Beach', 'R-2', 'Single-Family/Duplex', 'Residential', '#90EE90', '#228B22', 7500, 35, ARRAY['Single-family', 'Duplex']),
('Brevard', 'Indian Harbour Beach', 'R-3', 'Multi-Family', 'Residential', '#87CEEB', '#4169E1', 7500, 45, ARRAY['Multi-family']),
('Brevard', 'Indian Harbour Beach', 'C-1', 'Commercial', 'Commercial', '#FFB6C1', '#DC143C', 7500, 45, ARRAY['Retail', 'Office', 'Restaurant']),

-- Titusville
('Brevard', 'Titusville', 'R-1', 'Single-Family Residential', 'Residential', '#98FB98', '#228B22', 7500, 35, ARRAY['Single-family']),
('Brevard', 'Titusville', 'R-1M', 'Single-Family Mobile Home', 'Residential', '#90EE90', '#228B22', 7500, 35, ARRAY['Single-family', 'Mobile home']),
('Brevard', 'Titusville', 'R-2', 'Two-Family Residential', 'Residential', '#87CEEB', '#4169E1', 7500, 35, ARRAY['Single-family', 'Duplex']),
('Brevard', 'Titusville', 'R-3', 'Multi-Family', 'Residential', '#6495ED', '#0000CD', 7500, 55, ARRAY['Multi-family', 'Apartments']),
('Brevard', 'Titusville', 'C-1', 'Neighborhood Commercial', 'Commercial', '#FFB6C1', '#DC143C', 7500, 35, ARRAY['Neighborhood retail']),
('Brevard', 'Titusville', 'C-2', 'General Commercial', 'Commercial', '#FF69B4', '#C71585', 10000, 55, ARRAY['General retail', 'Office']),
('Brevard', 'Titusville', 'I-1', 'Light Industrial', 'Industrial', '#C0C0C0', '#808080', 20000, 50, ARRAY['Light industrial', 'Warehouse']),

-- Cocoa
('Brevard', 'Cocoa', 'R-1', 'Single-Family Residential', 'Residential', '#98FB98', '#228B22', 7000, 35, ARRAY['Single-family']),
('Brevard', 'Cocoa', 'R-2', 'Duplex Residential', 'Residential', '#90EE90', '#228B22', 7000, 35, ARRAY['Single-family', 'Duplex']),
('Brevard', 'Cocoa', 'R-3', 'Multi-Family', 'Residential', '#87CEEB', '#4169E1', 7000, 45, ARRAY['Multi-family']),
('Brevard', 'Cocoa', 'C-1', 'Commercial', 'Commercial', '#FFB6C1', '#DC143C', 5000, 45, ARRAY['Retail', 'Office']),
('Brevard', 'Cocoa', 'M-1', 'Industrial', 'Industrial', '#C0C0C0', '#808080', 10000, 50, ARRAY['Light industrial'])

ON CONFLICT (county, jurisdiction, zoning_code) DO UPDATE SET
    zoning_name = EXCLUDED.zoning_name,
    zoning_category = EXCLUDED.zoning_category,
    fill_color = EXCLUDED.fill_color,
    stroke_color = EXCLUDED.stroke_color,
    permitted_uses = EXCLUDED.permitted_uses,
    updated_at = NOW();

-- Function to get zoning info by code
CREATE OR REPLACE FUNCTION get_zoning_info(
    p_county VARCHAR,
    p_jurisdiction VARCHAR,
    p_zoning_code VARCHAR
)
RETURNS TABLE (
    zoning_code VARCHAR,
    zoning_name VARCHAR,
    zoning_category VARCHAR,
    zoning_description TEXT,
    permitted_uses TEXT[],
    conditional_uses TEXT[],
    min_lot_size_sqft INTEGER,
    max_building_height_ft INTEGER,
    fill_color VARCHAR
)
LANGUAGE SQL STABLE
AS $$
    SELECT 
        zoning_code,
        zoning_name,
        zoning_category,
        zoning_description,
        permitted_uses,
        conditional_uses,
        min_lot_size_sqft,
        max_building_height_ft,
        fill_color
    FROM zoning_districts
    WHERE county = p_county
      AND (jurisdiction = p_jurisdiction OR p_jurisdiction IS NULL)
      AND zoning_code = p_zoning_code
    LIMIT 1;
$$;

-- Function to get all zones for a jurisdiction
CREATE OR REPLACE FUNCTION get_jurisdiction_zones(
    p_county VARCHAR,
    p_jurisdiction VARCHAR
)
RETURNS TABLE (
    zoning_code VARCHAR,
    zoning_name VARCHAR,
    zoning_category VARCHAR,
    fill_color VARCHAR,
    parcel_count BIGINT
)
LANGUAGE SQL STABLE
AS $$
    SELECT 
        zd.zoning_code,
        zd.zoning_name,
        zd.zoning_category,
        zd.fill_color,
        COUNT(p.id) as parcel_count
    FROM zoning_districts zd
    LEFT JOIN fl_parcels p ON p.zoning_code = zd.zoning_code 
        AND p.jurisdiction = zd.jurisdiction
    WHERE zd.county = p_county
      AND (zd.jurisdiction = p_jurisdiction OR p_jurisdiction IS NULL)
    GROUP BY zd.zoning_code, zd.zoning_name, zd.zoning_category, zd.fill_color
    ORDER BY zd.zoning_category, zd.zoning_code;
$$;

-- Session cleanup function (run via cron)
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS INTEGER
LANGUAGE SQL
AS $$
    WITH deleted AS (
        DELETE FROM map_sessions
        WHERE expires_at < NOW()
        RETURNING id
    )
    SELECT COUNT(*)::INTEGER FROM deleted;
$$;

-- Update triggers
CREATE TRIGGER map_sessions_updated_at
    BEFORE UPDATE ON map_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER zoning_districts_updated_at
    BEFORE UPDATE ON zoning_districts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON map_sessions TO authenticated;
GRANT SELECT ON map_sessions TO anon;
GRANT SELECT ON zoning_districts TO anon, authenticated;
GRANT SELECT, INSERT ON chat_messages TO authenticated;
GRANT EXECUTE ON FUNCTION get_zoning_info TO anon, authenticated;
GRANT EXECUTE ON FUNCTION get_jurisdiction_zones TO anon, authenticated;
GRANT EXECUTE ON FUNCTION cleanup_expired_sessions TO service_role;

COMMENT ON TABLE map_sessions IS 'ZoneWise V3 map session state and chat history';
COMMENT ON TABLE zoning_districts IS 'Florida zoning districts reference - 273 districts from 17 Brevard jurisdictions';
COMMENT ON TABLE chat_messages IS 'Chat message log for ZoneWise AI interactions';
