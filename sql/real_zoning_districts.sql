-- ZoneWise Real Zoning Districts Table
-- Stores actual ordinance data extracted from municipal code sources
-- Created: 2026-01-18

-- Drop existing table if needed (comment out in production)
-- DROP TABLE IF EXISTS real_zoning_districts;

CREATE TABLE IF NOT EXISTS real_zoning_districts (
    id BIGSERIAL PRIMARY KEY,
    
    -- Jurisdiction info
    jurisdiction_id INTEGER NOT NULL,
    jurisdiction_name TEXT NOT NULL,
    jurisdiction_type TEXT, -- city, town, county
    
    -- District identification
    district_code TEXT NOT NULL,
    district_name TEXT NOT NULL,
    category TEXT NOT NULL, -- Residential, Commercial, Industrial, Agricultural, Special
    
    -- Source tracking
    ordinance_section TEXT,
    source_url TEXT,
    extraction_date TIMESTAMPTZ DEFAULT NOW(),
    extraction_status TEXT DEFAULT 'pending', -- pending, success, partial, failed, scrape_failed
    extraction_confidence DECIMAL(3,2) DEFAULT 0.00,
    
    -- Lot dimensions
    min_lot_size_sqft INTEGER,
    min_lot_width_ft DECIMAL(6,2),
    min_lot_depth_ft DECIMAL(6,2),
    
    -- Building dimensions
    min_living_area_sqft INTEGER,
    max_height_ft INTEGER,
    max_stories INTEGER,
    max_lot_coverage_pct DECIMAL(5,2),
    max_impervious_pct DECIMAL(5,2),
    max_far DECIMAL(4,2),
    
    -- Setbacks - standard values
    front_setback_ft DECIMAL(6,2),
    side_setback_ft DECIMAL(6,2),
    rear_setback_ft DECIMAL(6,2),
    
    -- Setbacks - conditional values (stored as JSONB for flexibility)
    setback_conditions JSONB,
    
    -- Density and parking
    density_units_per_acre DECIMAL(6,2),
    parking_spaces_required DECIMAL(4,2),
    
    -- Uses
    permitted_uses JSONB,
    conditional_uses JSONB,
    prohibited_uses JSONB,
    
    -- Raw data and notes
    raw_text_excerpt TEXT,
    notes TEXT,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Unique constraint
    UNIQUE(jurisdiction_id, district_code)
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_real_zoning_jurisdiction ON real_zoning_districts(jurisdiction_name);
CREATE INDEX IF NOT EXISTS idx_real_zoning_category ON real_zoning_districts(category);
CREATE INDEX IF NOT EXISTS idx_real_zoning_status ON real_zoning_districts(extraction_status);
CREATE INDEX IF NOT EXISTS idx_real_zoning_confidence ON real_zoning_districts(extraction_confidence);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION update_real_zoning_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_real_zoning_updated_at ON real_zoning_districts;
CREATE TRIGGER trigger_real_zoning_updated_at
    BEFORE UPDATE ON real_zoning_districts
    FOR EACH ROW
    EXECUTE FUNCTION update_real_zoning_updated_at();

-- Grant permissions
GRANT ALL ON real_zoning_districts TO authenticated;
GRANT ALL ON real_zoning_districts TO service_role;

-- Insert extraction log table
CREATE TABLE IF NOT EXISTS zoning_extraction_logs (
    id BIGSERIAL PRIMARY KEY,
    run_id TEXT NOT NULL,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    status TEXT DEFAULT 'running', -- running, completed, failed
    total_jurisdictions INTEGER,
    total_districts INTEGER,
    successful_extractions INTEGER DEFAULT 0,
    partial_extractions INTEGER DEFAULT 0,
    failed_extractions INTEGER DEFAULT 0,
    error_message TEXT,
    workflow_run_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_extraction_logs_run ON zoning_extraction_logs(run_id);
CREATE INDEX IF NOT EXISTS idx_extraction_logs_status ON zoning_extraction_logs(status);

GRANT ALL ON zoning_extraction_logs TO authenticated;
GRANT ALL ON zoning_extraction_logs TO service_role;

-- View for latest extraction status by jurisdiction
CREATE OR REPLACE VIEW v_jurisdiction_extraction_status AS
SELECT 
    jurisdiction_name,
    COUNT(*) as total_districts,
    COUNT(*) FILTER (WHERE extraction_status = 'success') as successful,
    COUNT(*) FILTER (WHERE extraction_status = 'partial') as partial,
    COUNT(*) FILTER (WHERE extraction_status IN ('failed', 'scrape_failed')) as failed,
    AVG(extraction_confidence) as avg_confidence,
    MAX(extraction_date) as last_extraction
FROM real_zoning_districts
GROUP BY jurisdiction_name
ORDER BY jurisdiction_name;

COMMENT ON TABLE real_zoning_districts IS 'Real zoning ordinance data extracted from municipal code sources for Brevard County FL';
COMMENT ON TABLE zoning_extraction_logs IS 'Logs of extraction workflow runs';
