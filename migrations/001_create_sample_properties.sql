-- ZoneWise Sample Properties Table - Full Brevard County
-- 351,531 parcels with proper indexing for performance
-- Run via Supabase Dashboard SQL Editor
-- https://supabase.com/dashboard/project/mocerqjnksmhcjzxrewo/sql

-- Drop existing table if needed (uncomment if resetting)
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
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT sample_properties_parcel_id_unique UNIQUE(parcel_id)
);

-- Performance indexes for 351K+ records
CREATE INDEX IF NOT EXISTS idx_sample_properties_jurisdiction 
    ON sample_properties(jurisdiction_id);
CREATE INDEX IF NOT EXISTS idx_sample_properties_zip 
    ON sample_properties(zip_code);
CREATE INDEX IF NOT EXISTS idx_sample_properties_use_code 
    ON sample_properties(use_code);
CREATE INDEX IF NOT EXISTS idx_sample_properties_city 
    ON sample_properties(city);
CREATE INDEX IF NOT EXISTS idx_sample_properties_centroid 
    ON sample_properties(centroid_lat, centroid_lon)
    WHERE centroid_lat IS NOT NULL;

-- Composite index for common queries
CREATE INDEX IF NOT EXISTS idx_sample_properties_jurisdiction_use 
    ON sample_properties(jurisdiction_id, use_code);

-- Enable RLS
ALTER TABLE sample_properties ENABLE ROW LEVEL SECURITY;

-- Read-only policy for API
DROP POLICY IF EXISTS "Allow read access" ON sample_properties;
CREATE POLICY "Allow read access" ON sample_properties
    FOR SELECT USING (true);

-- Allow service_role full access for inserts/updates
DROP POLICY IF EXISTS "Service role full access" ON sample_properties;
CREATE POLICY "Service role full access" ON sample_properties
    FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

-- Grant access to anon role (read only)
GRANT SELECT ON sample_properties TO anon;

-- Grant full access to service_role
GRANT ALL ON sample_properties TO service_role;
GRANT USAGE, SELECT ON SEQUENCE sample_properties_id_seq TO service_role;

-- Trigger to update updated_at on modification
CREATE OR REPLACE FUNCTION update_sample_properties_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS sample_properties_updated_at ON sample_properties;
CREATE TRIGGER sample_properties_updated_at
    BEFORE UPDATE ON sample_properties
    FOR EACH ROW
    EXECUTE FUNCTION update_sample_properties_timestamp();

-- Helper function: Count by jurisdiction
CREATE OR REPLACE FUNCTION count_by_jurisdiction()
RETURNS TABLE(jurisdiction_id INTEGER, jurisdiction_name TEXT, parcel_count BIGINT) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        sp.jurisdiction_id,
        j.name::TEXT as jurisdiction_name,
        COUNT(*)::BIGINT as parcel_count
    FROM sample_properties sp
    JOIN jurisdictions j ON sp.jurisdiction_id = j.id
    GROUP BY sp.jurisdiction_id, j.name
    ORDER BY parcel_count DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Verify table created
SELECT 
    'sample_properties' as table_name,
    (SELECT count(*) FROM sample_properties) as row_count,
    (SELECT count(*) FROM pg_indexes WHERE tablename = 'sample_properties') as index_count;
