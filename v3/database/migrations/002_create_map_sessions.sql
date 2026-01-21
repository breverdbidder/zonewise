-- ZoneWise V3 - map_sessions Table
-- Migration: 002_create_map_sessions.sql
-- Created: 2026-01-21

-- Create map_sessions table for tracking user map state
CREATE TABLE IF NOT EXISTS map_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(100) UNIQUE NOT NULL,
    user_id VARCHAR(100),  -- Optional, for authenticated users
    
    -- Map State
    center_lat DECIMAL(10, 7) DEFAULT 28.3922,  -- Brevard County center
    center_lng DECIMAL(10, 7) DEFAULT -80.6077,
    zoom_level DECIMAL(4, 2) DEFAULT 10.0,
    bearing DECIMAL(5, 2) DEFAULT 0,
    pitch DECIMAL(5, 2) DEFAULT 0,
    
    -- Viewport Bounds
    bounds_sw_lat DECIMAL(10, 7),
    bounds_sw_lng DECIMAL(10, 7),
    bounds_ne_lat DECIMAL(10, 7),
    bounds_ne_lng DECIMAL(10, 7),
    
    -- Selection State
    selected_parcel_id VARCHAR(50),
    selected_parcels JSONB DEFAULT '[]'::jsonb,  -- Array of selected parcel IDs
    
    -- Layer State
    active_layers JSONB DEFAULT '["zoning", "parcels"]'::jsonb,
    layer_opacity JSONB DEFAULT '{"zoning": 0.7, "parcels": 1.0}'::jsonb,
    
    -- Filter State
    zone_filter JSONB DEFAULT '[]'::jsonb,  -- Filter by zone codes
    value_range_min DECIMAL(12, 2),
    value_range_max DECIMAL(12, 2),
    
    -- Conversation Context
    last_query TEXT,
    conversation_history JSONB DEFAULT '[]'::jsonb,
    
    -- Analysis Results (cached)
    cached_analysis JSONB,
    analysis_timestamp TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    device_type VARCHAR(20),  -- desktop, tablet, mobile
    browser VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '24 hours')
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_map_sessions_session_id ON map_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_map_sessions_user_id ON map_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_map_sessions_selected_parcel ON map_sessions(selected_parcel_id);
CREATE INDEX IF NOT EXISTS idx_map_sessions_expires_at ON map_sessions(expires_at);

-- Enable Row Level Security
ALTER TABLE map_sessions ENABLE ROW LEVEL SECURITY;

-- Users can only access their own sessions
CREATE POLICY "Users access own sessions" ON map_sessions
    FOR ALL USING (
        session_id = current_setting('app.session_id', true)
        OR user_id = current_setting('app.user_id', true)
    );

-- Public read for anonymous sessions (by session_id header)
CREATE POLICY "Anonymous session access" ON map_sessions
    FOR SELECT USING (true);

-- Comment on table
COMMENT ON TABLE map_sessions IS 'Stores map viewport state and conversation context for ZoneWise V3';

-- Function to update session timestamp
CREATE OR REPLACE FUNCTION update_map_session_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update timestamp
CREATE TRIGGER map_sessions_updated_at
    BEFORE UPDATE ON map_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_map_session_timestamp();

-- Function to cleanup expired sessions
CREATE OR REPLACE FUNCTION cleanup_expired_map_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM map_sessions WHERE expires_at < NOW();
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Create fl_zoning_districts table for zone rules
CREATE TABLE IF NOT EXISTS fl_zoning_districts (
    id SERIAL PRIMARY KEY,
    zone_code VARCHAR(20) NOT NULL,
    zone_name VARCHAR(100),
    jurisdiction VARCHAR(100) DEFAULT 'Brevard County',
    
    -- Dimensional Standards
    min_lot_size_sqft DECIMAL(12, 2),
    min_lot_width_ft DECIMAL(10, 2),
    max_height_ft DECIMAL(10, 2),
    max_lot_coverage_pct DECIMAL(5, 2),
    max_floor_area_ratio DECIMAL(5, 2),
    
    -- Setbacks
    front_setback_ft DECIMAL(10, 2),
    side_setback_ft DECIMAL(10, 2),
    rear_setback_ft DECIMAL(10, 2),
    corner_lot_setback_ft DECIMAL(10, 2),
    
    -- Uses
    permitted_uses JSONB DEFAULT '[]'::jsonb,
    conditional_uses JSONB DEFAULT '[]'::jsonb,
    prohibited_uses JSONB DEFAULT '[]'::jsonb,
    
    -- Density
    max_dwelling_units_per_acre DECIMAL(6, 2),
    
    -- Display
    color_hex VARCHAR(7) DEFAULT '#808080',
    description TEXT,
    
    -- Metadata
    ordinance_reference VARCHAR(100),
    effective_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(zone_code, jurisdiction)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_zoning_districts_zone_code ON fl_zoning_districts(zone_code);
CREATE INDEX IF NOT EXISTS idx_zoning_districts_jurisdiction ON fl_zoning_districts(jurisdiction);

-- Insert common Brevard County zones
INSERT INTO fl_zoning_districts (zone_code, zone_name, min_lot_size_sqft, min_lot_width_ft, max_height_ft, max_lot_coverage_pct, front_setback_ft, side_setback_ft, rear_setback_ft, permitted_uses, color_hex) VALUES
('RS-1', 'Residential Single Family 1', 43560, 100, 35, 35, 30, 10, 25, '["single-family residential", "home occupation", "accessory structures"]', '#90EE90'),
('RS-2', 'Residential Single Family 2', 15000, 85, 35, 40, 25, 7.5, 20, '["single-family residential", "home occupation", "accessory structures"]', '#98FB98'),
('RS-3', 'Residential Single Family 3', 10000, 75, 35, 40, 25, 7.5, 20, '["single-family residential", "home occupation", "accessory structures"]', '#7CFC00'),
('RS-4', 'Residential Single Family 4', 7500, 60, 35, 45, 20, 5, 15, '["single-family residential", "duplex", "home occupation"]', '#32CD32'),
('RM-4', 'Residential Multi-Family 4', 10000, 100, 35, 40, 25, 10, 20, '["multi-family residential", "townhouses", "condominiums"]', '#FFD700'),
('RM-8', 'Residential Multi-Family 8', 10000, 100, 45, 50, 25, 10, 20, '["multi-family residential", "apartments", "condominiums"]', '#FFA500'),
('RM-12', 'Residential Multi-Family 12', 10000, 100, 55, 55, 25, 15, 20, '["multi-family residential", "apartments", "mixed-use"]', '#FF8C00'),
('BU-1', 'Business/Commercial 1', 10000, 100, 35, 60, 25, 10, 20, '["retail", "office", "restaurant", "personal services"]', '#4169E1'),
('BU-1-A', 'Business/Commercial 1-A', 10000, 100, 45, 65, 25, 10, 20, '["retail", "office", "restaurant", "hotel", "entertainment"]', '#0000CD'),
('BU-2', 'Business/Commercial 2', 20000, 100, 55, 70, 30, 15, 25, '["retail", "office", "wholesale", "light manufacturing"]', '#00008B'),
('IU-1', 'Industrial 1', 20000, 100, 50, 60, 30, 20, 25, '["light industrial", "warehouse", "distribution", "research"]', '#808080'),
('IU-2', 'Industrial 2', 43560, 150, 60, 65, 50, 25, 30, '["heavy industrial", "manufacturing", "processing"]', '#696969'),
('AU', 'Agricultural', 217800, 200, 35, 20, 50, 25, 50, '["agricultural", "single-family", "farm stands"]', '#8B4513'),
('PUD', 'Planned Unit Development', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '["varies by approval"]', '#DDA0DD')
ON CONFLICT (zone_code, jurisdiction) DO NOTHING;

-- Enable RLS
ALTER TABLE fl_zoning_districts ENABLE ROW LEVEL SECURITY;

-- Public read access
CREATE POLICY "Public read zoning" ON fl_zoning_districts
    FOR SELECT USING (true);
