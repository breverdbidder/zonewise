-- ZoneWise Sample Properties Table - FULL BREVARD COUNTY
-- Run via Supabase Dashboard SQL Editor
-- https://supabase.com/dashboard/project/mocerqjnksmhcjzxrewo/sql
-- Expected: ~351,531 parcels

-- Drop existing table if needed (comment out if you want to preserve data)
-- DROP TABLE IF EXISTS sample_properties CASCADE;

-- Create sample_properties table
CREATE TABLE IF NOT EXISTS sample_properties (
    id SERIAL PRIMARY KEY,
    jurisdiction_id INTEGER NOT NULL REFERENCES jurisdictions(id),
    parcel_id VARCHAR(100) NOT NULL,
    tax_account VARCHAR(50),
    address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(2) DEFAULT 'FL',
    zip_code VARCHAR(10),
    acres DECIMAL(10,4),
    land_value DECIMAL(12,2),
    building_value DECIMAL(12,2),
    use_code VARCHAR(20),
    use_description VARCHAR(255),
    geometry_wkt TEXT,
    centroid_lat DECIMAL(10,7),
    centroid_lon DECIMAL(10,7),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT sample_properties_parcel_id_unique UNIQUE(parcel_id)
);

-- Indexes for performance at scale
CREATE INDEX IF NOT EXISTS idx_sp_jurisdiction ON sample_properties(jurisdiction_id);
CREATE INDEX IF NOT EXISTS idx_sp_zip ON sample_properties(zip_code);
CREATE INDEX IF NOT EXISTS idx_sp_use_code ON sample_properties(use_code);
CREATE INDEX IF NOT EXISTS idx_sp_city ON sample_properties(city);
CREATE INDEX IF NOT EXISTS idx_sp_centroid ON sample_properties(centroid_lat, centroid_lon) 
    WHERE centroid_lat IS NOT NULL;

-- Composite index for common queries
CREATE INDEX IF NOT EXISTS idx_sp_jurisdiction_use ON sample_properties(jurisdiction_id, use_code);

-- Enable RLS
ALTER TABLE sample_properties ENABLE ROW LEVEL SECURITY;

-- Read-only policy for API (public read)
DROP POLICY IF EXISTS "Allow read access" ON sample_properties;
CREATE POLICY "Allow read access" ON sample_properties
    FOR SELECT USING (true);

-- Service role can insert/update
DROP POLICY IF EXISTS "Service role full access" ON sample_properties;
CREATE POLICY "Service role full access" ON sample_properties
    FOR ALL USING (auth.role() = 'service_role');

-- Grant access
GRANT SELECT ON sample_properties TO anon;
GRANT ALL ON sample_properties TO service_role;

-- Helper function to count by jurisdiction
CREATE OR REPLACE FUNCTION count_by_jurisdiction()
RETURNS TABLE (
    jurisdiction_id INTEGER,
    jurisdiction_name TEXT,
    parcel_count BIGINT
) 
LANGUAGE SQL
SECURITY DEFINER
AS $$
    SELECT 
        sp.jurisdiction_id,
        j.name as jurisdiction_name,
        COUNT(*) as parcel_count
    FROM sample_properties sp
    JOIN jurisdictions j ON sp.jurisdiction_id = j.id
    GROUP BY sp.jurisdiction_id, j.name
    ORDER BY parcel_count DESC;
$$;

-- Grant execute on function
GRANT EXECUTE ON FUNCTION count_by_jurisdiction() TO anon;
GRANT EXECUTE ON FUNCTION count_by_jurisdiction() TO service_role;

-- Verify table exists
SELECT 
    'sample_properties' as table_name,
    (SELECT count(*) FROM sample_properties) as current_rows,
    '~351,531 expected after full load' as target;
