-- ZoneWise Migration 003: Permitted Uses
-- Tracks permitted, conditional, and prohibited uses per zoning district
-- Run via Supabase Dashboard SQL Editor or REST API
-- https://supabase.com/dashboard/project/mocerqjnksmhcjzxrewo/sql

-- Create enum-like reference for permission types
CREATE TABLE IF NOT EXISTS public.permission_types (
    code VARCHAR(5) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT
);

INSERT INTO public.permission_types (code, name, description) VALUES
    ('P', 'Permitted', 'By-right use, no special approval needed'),
    ('C', 'Conditional', 'Requires conditional use permit (CUP)'),
    ('S', 'Special Exception', 'Requires special exception approval'),
    ('A', 'Accessory', 'Allowed only as accessory to primary use'),
    ('T', 'Temporary', 'Allowed with temporary use permit'),
    ('X', 'Prohibited', 'Not allowed in this district')
ON CONFLICT (code) DO NOTHING;

-- Create use categories reference
CREATE TABLE IF NOT EXISTS public.use_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    parent_category VARCHAR(100),
    description TEXT
);

INSERT INTO public.use_categories (name, parent_category, description) VALUES
    ('Residential', NULL, 'Housing and dwelling uses'),
    ('Single-Family Residential', 'Residential', 'Detached single-family homes'),
    ('Two-Family Residential', 'Residential', 'Duplexes and two-family dwellings'),
    ('Multi-Family Residential', 'Residential', 'Apartments, condos, townhomes'),
    ('Mobile Home', 'Residential', 'Manufactured and mobile homes'),
    ('Accessory Dwelling Unit', 'Residential', 'ADUs, granny flats, in-law suites'),
    ('Commercial', NULL, 'Business and retail uses'),
    ('Retail', 'Commercial', 'Stores, shops, retail sales'),
    ('Restaurant', 'Commercial', 'Eating and drinking establishments'),
    ('Office', 'Commercial', 'Professional and business offices'),
    ('Hotel/Motel', 'Commercial', 'Lodging and hospitality'),
    ('Auto-Related', 'Commercial', 'Gas stations, car washes, auto repair'),
    ('Industrial', NULL, 'Manufacturing and warehouse uses'),
    ('Light Industrial', 'Industrial', 'Light manufacturing, assembly'),
    ('Heavy Industrial', 'Industrial', 'Heavy manufacturing, processing'),
    ('Warehouse', 'Industrial', 'Storage and distribution'),
    ('Institutional', NULL, 'Government, education, religious'),
    ('Religious', 'Institutional', 'Churches, temples, mosques'),
    ('Education', 'Institutional', 'Schools, colleges, training facilities'),
    ('Government', 'Institutional', 'Government offices, public facilities'),
    ('Medical', 'Institutional', 'Hospitals, clinics, medical offices'),
    ('Agricultural', NULL, 'Farming and agricultural uses'),
    ('Recreation', NULL, 'Parks, sports, entertainment'),
    ('Utility', NULL, 'Infrastructure and utility uses'),
    ('Mixed Use', NULL, 'Combined residential and commercial')
ON CONFLICT (name) DO NOTHING;

-- Create permitted_uses table
CREATE TABLE IF NOT EXISTS public.permitted_uses (
    id BIGSERIAL PRIMARY KEY,
    jurisdiction_id INTEGER NOT NULL REFERENCES public.jurisdictions(id),
    district_id INTEGER REFERENCES public.zoning_districts(id),
    district_code VARCHAR(20) NOT NULL,

    -- Use identification
    use_name VARCHAR(200) NOT NULL,
    use_category VARCHAR(100) REFERENCES public.use_categories(name),
    standardized_name VARCHAR(200),

    -- Permission
    permission_type VARCHAR(5) NOT NULL REFERENCES public.permission_types(code),

    -- Conditions and requirements
    conditions TEXT,
    min_lot_size_sqft INTEGER,
    max_density NUMERIC(8,2),
    parking_required VARCHAR(200),
    special_requirements TEXT,
    footnotes TEXT,

    -- Source tracking
    source_url TEXT,
    source_section TEXT,
    ordinance_reference TEXT,
    table_reference TEXT,

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
    CONSTRAINT permitted_uses_jurisdiction_district_use_unique
        UNIQUE(jurisdiction_id, district_code, use_name),
    CONSTRAINT permitted_uses_valid_permission
        CHECK (permission_type IN ('P', 'C', 'S', 'A', 'T', 'X'))
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_permitted_uses_jurisdiction
    ON public.permitted_uses(jurisdiction_id);
CREATE INDEX IF NOT EXISTS idx_permitted_uses_district_code
    ON public.permitted_uses(district_code);
CREATE INDEX IF NOT EXISTS idx_permitted_uses_district_id
    ON public.permitted_uses(district_id);
CREATE INDEX IF NOT EXISTS idx_permitted_uses_use_name
    ON public.permitted_uses(use_name);
CREATE INDEX IF NOT EXISTS idx_permitted_uses_use_category
    ON public.permitted_uses(use_category);
CREATE INDEX IF NOT EXISTS idx_permitted_uses_permission_type
    ON public.permitted_uses(permission_type);
CREATE INDEX IF NOT EXISTS idx_permitted_uses_jurisdiction_district
    ON public.permitted_uses(jurisdiction_id, district_code);
CREATE INDEX IF NOT EXISTS idx_permitted_uses_jurisdiction_permission
    ON public.permitted_uses(jurisdiction_id, permission_type);
CREATE INDEX IF NOT EXISTS idx_permitted_uses_verified
    ON public.permitted_uses(verified) WHERE verified = FALSE;
CREATE INDEX IF NOT EXISTS idx_permitted_uses_needs_review
    ON public.permitted_uses(needs_review) WHERE needs_review = TRUE;

-- Full-text search on use names
CREATE INDEX IF NOT EXISTS idx_permitted_uses_use_name_gin
    ON public.permitted_uses USING gin(to_tsvector('english', use_name));

-- Enable RLS
ALTER TABLE public.permitted_uses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.permission_types ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.use_categories ENABLE ROW LEVEL SECURITY;

-- Public read policies
DO $$ BEGIN
    DROP POLICY IF EXISTS "Public read permitted_uses" ON public.permitted_uses;
EXCEPTION WHEN undefined_object THEN NULL;
END $$;
CREATE POLICY "Public read permitted_uses" ON public.permitted_uses
    FOR SELECT USING (true);

DO $$ BEGIN
    DROP POLICY IF EXISTS "Public read permission_types" ON public.permission_types;
EXCEPTION WHEN undefined_object THEN NULL;
END $$;
CREATE POLICY "Public read permission_types" ON public.permission_types
    FOR SELECT USING (true);

DO $$ BEGIN
    DROP POLICY IF EXISTS "Public read use_categories" ON public.use_categories;
EXCEPTION WHEN undefined_object THEN NULL;
END $$;
CREATE POLICY "Public read use_categories" ON public.use_categories
    FOR SELECT USING (true);

-- Service role full access
DO $$ BEGIN
    DROP POLICY IF EXISTS "Service role full access permitted_uses" ON public.permitted_uses;
EXCEPTION WHEN undefined_object THEN NULL;
END $$;
CREATE POLICY "Service role full access permitted_uses" ON public.permitted_uses
    FOR ALL USING (auth.role() = 'service_role');

DO $$ BEGIN
    DROP POLICY IF EXISTS "Service role full access permission_types" ON public.permission_types;
EXCEPTION WHEN undefined_object THEN NULL;
END $$;
CREATE POLICY "Service role full access permission_types" ON public.permission_types
    FOR ALL USING (auth.role() = 'service_role');

DO $$ BEGIN
    DROP POLICY IF EXISTS "Service role full access use_categories" ON public.use_categories;
EXCEPTION WHEN undefined_object THEN NULL;
END $$;
CREATE POLICY "Service role full access use_categories" ON public.use_categories
    FOR ALL USING (auth.role() = 'service_role');

-- Grant access
GRANT SELECT ON public.permitted_uses TO anon;
GRANT SELECT ON public.permission_types TO anon;
GRANT SELECT ON public.use_categories TO anon;
GRANT ALL ON public.permitted_uses TO service_role;
GRANT ALL ON public.permission_types TO service_role;
GRANT ALL ON public.use_categories TO service_role;
GRANT USAGE, SELECT ON SEQUENCE permitted_uses_id_seq TO service_role;
GRANT USAGE, SELECT ON SEQUENCE use_categories_id_seq TO service_role;

-- Auto-update updated_at trigger
CREATE OR REPLACE FUNCTION update_permitted_uses_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS permitted_uses_updated_at ON public.permitted_uses;
CREATE TRIGGER permitted_uses_updated_at
    BEFORE UPDATE ON public.permitted_uses
    FOR EACH ROW
    EXECUTE FUNCTION update_permitted_uses_updated_at();

-- Helper: Get permitted uses for a district
CREATE OR REPLACE FUNCTION get_permitted_uses_by_district(
    p_jurisdiction_id INTEGER,
    p_district_code VARCHAR(20)
)
RETURNS TABLE (
    use_name VARCHAR(200),
    use_category VARCHAR(100),
    permission_type VARCHAR(5),
    conditions TEXT,
    parking_required VARCHAR(200),
    verified BOOLEAN
)
LANGUAGE SQL SECURITY DEFINER
AS $$
    SELECT
        pu.use_name,
        pu.use_category,
        pu.permission_type,
        pu.conditions,
        pu.parking_required,
        pu.verified
    FROM public.permitted_uses pu
    WHERE pu.jurisdiction_id = p_jurisdiction_id
      AND pu.district_code = p_district_code
    ORDER BY pu.use_category, pu.use_name;
$$;

-- Helper: Search uses across all districts
CREATE OR REPLACE FUNCTION search_permitted_uses(
    p_jurisdiction_id INTEGER,
    p_search_term TEXT
)
RETURNS TABLE (
    district_code VARCHAR(20),
    use_name VARCHAR(200),
    use_category VARCHAR(100),
    permission_type VARCHAR(5),
    conditions TEXT
)
LANGUAGE SQL SECURITY DEFINER
AS $$
    SELECT
        pu.district_code,
        pu.use_name,
        pu.use_category,
        pu.permission_type,
        pu.conditions
    FROM public.permitted_uses pu
    WHERE pu.jurisdiction_id = p_jurisdiction_id
      AND to_tsvector('english', pu.use_name) @@ plainto_tsquery('english', p_search_term)
    ORDER BY pu.district_code, pu.use_name;
$$;

-- Helper: Count uses by jurisdiction and permission type
CREATE OR REPLACE FUNCTION count_uses_by_jurisdiction()
RETURNS TABLE (
    jurisdiction_id INTEGER,
    jurisdiction_name TEXT,
    total_uses BIGINT,
    permitted_count BIGINT,
    conditional_count BIGINT,
    prohibited_count BIGINT
)
LANGUAGE SQL SECURITY DEFINER
AS $$
    SELECT
        pu.jurisdiction_id,
        j.name::TEXT as jurisdiction_name,
        COUNT(*) as total_uses,
        SUM(CASE WHEN pu.permission_type = 'P' THEN 1 ELSE 0 END) as permitted_count,
        SUM(CASE WHEN pu.permission_type = 'C' THEN 1 ELSE 0 END) as conditional_count,
        SUM(CASE WHEN pu.permission_type = 'X' THEN 1 ELSE 0 END) as prohibited_count
    FROM public.permitted_uses pu
    JOIN public.jurisdictions j ON pu.jurisdiction_id = j.id
    GROUP BY pu.jurisdiction_id, j.name
    ORDER BY total_uses DESC;
$$;

GRANT EXECUTE ON FUNCTION get_permitted_uses_by_district(INTEGER, VARCHAR) TO anon;
GRANT EXECUTE ON FUNCTION get_permitted_uses_by_district(INTEGER, VARCHAR) TO service_role;
GRANT EXECUTE ON FUNCTION search_permitted_uses(INTEGER, TEXT) TO anon;
GRANT EXECUTE ON FUNCTION search_permitted_uses(INTEGER, TEXT) TO service_role;
GRANT EXECUTE ON FUNCTION count_uses_by_jurisdiction() TO anon;
GRANT EXECUTE ON FUNCTION count_uses_by_jurisdiction() TO service_role;

-- Verify table creation
SELECT
    'permitted_uses' as table_name,
    (SELECT count(*) FROM public.permitted_uses) as current_rows,
    'Ready for population' as status;

SELECT
    'permission_types' as table_name,
    (SELECT count(*) FROM public.permission_types) as current_rows,
    'Seeded with 6 types' as status;

SELECT
    'use_categories' as table_name,
    (SELECT count(*) FROM public.use_categories) as current_rows,
    'Seeded with 25 categories' as status;
