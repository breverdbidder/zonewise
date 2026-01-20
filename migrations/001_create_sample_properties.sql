-- ZoneWise Sample Properties Table
-- Run via Supabase Dashboard SQL Editor
-- https://supabase.com/dashboard/project/mocerqjnksmhcjzxrewo/sql

-- Create sample_properties table
CREATE TABLE IF NOT EXISTS sample_properties (
    id SERIAL PRIMARY KEY,
    jurisdiction_id INTEGER NOT NULL REFERENCES jurisdictions(id),
    parcel_id VARCHAR(100) NOT NULL UNIQUE,
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_sample_properties_jurisdiction 
    ON sample_properties(jurisdiction_id);
CREATE INDEX IF NOT EXISTS idx_sample_properties_zip 
    ON sample_properties(zip_code);
CREATE INDEX IF NOT EXISTS idx_sample_properties_use_code 
    ON sample_properties(use_code);
CREATE INDEX IF NOT EXISTS idx_sample_properties_centroid 
    ON sample_properties(centroid_lat, centroid_lon);

-- Enable RLS
ALTER TABLE sample_properties ENABLE ROW LEVEL SECURITY;

-- Read-only policy for API
CREATE POLICY "Allow read access" ON sample_properties
    FOR SELECT USING (true);

-- Grant access to anon role
GRANT SELECT ON sample_properties TO anon;

-- Verify table created
SELECT 
    'sample_properties' as table_name,
    count(*) as row_count
FROM sample_properties;
