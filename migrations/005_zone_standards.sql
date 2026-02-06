-- ZoneWise Migration 002: Zone Standards (Dimensional Standards)
-- Normalizes dimensional standards from embedded DIMS comments into proper relational table
-- Run via Supabase Dashboard SQL Editor or REST API
-- https://supabase.com/dashboard/project/mocerqjnksmhcjzxrewo/sql

-- Create zone_standards table
CREATE TABLE IF NOT EXISTS public.zone_standards (
    id BIGSERIAL PRIMARY KEY,
    jurisdiction_id INTEGER NOT NULL REFERENCES public.jurisdictions(id),
    district_id INTEGER REFERENCES public.zoning_districts(id),
    district_code VARCHAR(20) NOT NULL,
    district_name VARCHAR(200),

    -- Lot requirements
    min_lot_sqft INTEGER,
    min_lot_width_ft NUMERIC(8,2),
    min_lot_depth_ft NUMERIC(8,2),
    max_lot_coverage_pct NUMERIC(5,2),
    max_impervious_pct NUMERIC(5,2),

    -- Height limits
    max_height_ft NUMERIC(8,2),
    max_stories INTEGER,

    -- Setbacks (in feet)
    front_setback_ft NUMERIC(8,2),
    side_setback_ft NUMERIC(8,2),
    rear_setback_ft NUMERIC(8,2),
    corner_setback_ft NUMERIC(8,2),
    waterfront_setback_ft NUMERIC(8,2),

    -- Density & intensity
    max_density_units_per_acre NUMERIC(8,2),
    min_density_units_per_acre NUMERIC(8,2),
    floor_area_ratio NUMERIC(5,3),
    max_far NUMERIC(5,3),

    -- Parking
    min_parking_spaces_per_unit NUMERIC(6,2),
    min_parking_spaces_per_1000sf NUMERIC(6,2),

    -- Open space
    min_open_space_pct NUMERIC(5,2),
    min_landscape_pct NUMERIC(5,2),

    -- Source tracking
    source_url TEXT,
    source_section TEXT,
    ordinance_reference TEXT,

    -- Data quality
    extraction_method VARCHAR(50) DEFAULT 'agentql',
    extraction_confidence NUMERIC(3,2) CHECK (extraction_confidence >= 0 AND extraction_confidence <= 1),
    verified BOOLEAN DEFAULT FALSE,
    verified_date DATE,
    needs_review BOOLEAN DEFAULT FALSE,
    review_notes TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CONSTRAINT zone_standards_jurisdiction_district_unique
        UNIQUE(jurisdiction_id, district_code),
    CONSTRAINT zone_standards_height_positive
        CHECK (max_height_ft IS NULL OR max_height_ft > 0),
    CONSTRAINT zone_standards_lot_positive
        CHECK (min_lot_sqft IS NULL OR min_lot_sqft > 0),
    CONSTRAINT zone_standards_coverage_range
        CHECK (max_lot_coverage_pct IS NULL OR (max_lot_coverage_pct > 0 AND max_lot_coverage_pct <= 100)),
    CONSTRAINT zone_standards_density_positive
        CHECK (max_density_units_per_acre IS NULL OR max_density_units_per_acre >= 0),
    CONSTRAINT zone_standards_far_positive
        CHECK (floor_area_ratio IS NULL OR floor_area_ratio >= 0)
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_zone_standards_jurisdiction
    ON public.zone_standards(jurisdiction_id);
CREATE INDEX IF NOT EXISTS idx_zone_standards_district_code
    ON public.zone_standards(district_code);
CREATE INDEX IF NOT EXISTS idx_zone_standards_district_id
    ON public.zone_standards(district_id);
CREATE INDEX IF NOT EXISTS idx_zone_standards_jurisdiction_district
    ON public.zone_standards(jurisdiction_id, district_code);
CREATE INDEX IF NOT EXISTS idx_zone_standards_verified
    ON public.zone_standards(verified) WHERE verified = FALSE;
CREATE INDEX IF NOT EXISTS idx_zone_standards_needs_review
    ON public.zone_standards(needs_review) WHERE needs_review = TRUE;

-- Enable RLS
ALTER TABLE public.zone_standards ENABLE ROW LEVEL SECURITY;

-- Read-only policy for public (anon) access
DO $$ BEGIN
    DROP POLICY IF EXISTS "Public read zone_standards" ON public.zone_standards;
EXCEPTION WHEN undefined_object THEN NULL;
END $$;
CREATE POLICY "Public read zone_standards" ON public.zone_standards
    FOR SELECT USING (true);

-- Service role full access
DO $$ BEGIN
    DROP POLICY IF EXISTS "Service role full access zone_standards" ON public.zone_standards;
EXCEPTION WHEN undefined_object THEN NULL;
END $$;
CREATE POLICY "Service role full access zone_standards" ON public.zone_standards
    FOR ALL USING (auth.role() = 'service_role');

-- Grant access
GRANT SELECT ON public.zone_standards TO anon;
GRANT ALL ON public.zone_standards TO service_role;
GRANT USAGE, SELECT ON SEQUENCE zone_standards_id_seq TO service_role;

-- Auto-update updated_at trigger
CREATE OR REPLACE FUNCTION update_zone_standards_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS zone_standards_updated_at ON public.zone_standards;
CREATE TRIGGER zone_standards_updated_at
    BEFORE UPDATE ON public.zone_standards
    FOR EACH ROW
    EXECUTE FUNCTION update_zone_standards_updated_at();

-- Helper: Get standards for a jurisdiction
CREATE OR REPLACE FUNCTION get_zone_standards_by_jurisdiction(p_jurisdiction_id INTEGER)
RETURNS TABLE (
    district_code VARCHAR(20),
    district_name VARCHAR(200),
    min_lot_sqft INTEGER,
    max_height_ft NUMERIC(8,2),
    max_stories INTEGER,
    front_setback_ft NUMERIC(8,2),
    side_setback_ft NUMERIC(8,2),
    rear_setback_ft NUMERIC(8,2),
    max_density_units_per_acre NUMERIC(8,2),
    floor_area_ratio NUMERIC(5,3),
    max_lot_coverage_pct NUMERIC(5,2),
    verified BOOLEAN
)
LANGUAGE SQL SECURITY DEFINER
AS $$
    SELECT
        zs.district_code,
        zs.district_name,
        zs.min_lot_sqft,
        zs.max_height_ft,
        zs.max_stories,
        zs.front_setback_ft,
        zs.side_setback_ft,
        zs.rear_setback_ft,
        zs.max_density_units_per_acre,
        zs.floor_area_ratio,
        zs.max_lot_coverage_pct,
        zs.verified
    FROM public.zone_standards zs
    WHERE zs.jurisdiction_id = p_jurisdiction_id
    ORDER BY zs.district_code;
$$;

GRANT EXECUTE ON FUNCTION get_zone_standards_by_jurisdiction(INTEGER) TO anon;
GRANT EXECUTE ON FUNCTION get_zone_standards_by_jurisdiction(INTEGER) TO service_role;

-- Verify table creation
SELECT
    'zone_standards' as table_name,
    (SELECT count(*) FROM public.zone_standards) as current_rows,
    'Ready for population' as status;
