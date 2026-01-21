-- 001_create_fl_parcels.sql
-- ZoneWise V3: Florida Parcels with PostGIS Support
-- Run in Supabase SQL Editor

-- Enable PostGIS extension if not already enabled
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create fl_parcels table with spatial geometry
CREATE TABLE IF NOT EXISTS fl_parcels (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    parcel_id VARCHAR(50) UNIQUE NOT NULL,
    county VARCHAR(50) NOT NULL DEFAULT 'Brevard',
    
    -- Property identifiers
    account_number VARCHAR(30),
    alt_key VARCHAR(30),
    
    -- Address info
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(2) DEFAULT 'FL',
    zip_code VARCHAR(10),
    
    -- Owner info
    owner_name VARCHAR(255),
    owner_address VARCHAR(500),
    
    -- Zoning and land use
    zoning_code VARCHAR(20),
    zoning_description VARCHAR(255),
    jurisdiction VARCHAR(100),
    land_use_code VARCHAR(20),
    land_use_description VARCHAR(255),
    
    -- Property characteristics
    lot_size_sqft NUMERIC(12, 2),
    lot_size_acres NUMERIC(10, 4),
    year_built INTEGER,
    bedrooms INTEGER,
    bathrooms NUMERIC(4, 2),
    living_area_sqft INTEGER,
    total_area_sqft INTEGER,
    
    -- Valuations
    just_value NUMERIC(14, 2),
    assessed_value NUMERIC(14, 2),
    taxable_value NUMERIC(14, 2),
    land_value NUMERIC(14, 2),
    improvement_value NUMERIC(14, 2),
    
    -- ML predictions (from BidDeed.AI)
    ml_predicted_value NUMERIC(14, 2),
    ml_confidence NUMERIC(5, 4),
    ml_model_version VARCHAR(20),
    
    -- Spatial data
    geom GEOMETRY(Point, 4326),
    centroid_lat NUMERIC(10, 7),
    centroid_lon NUMERIC(11, 7),
    parcel_boundary GEOMETRY(Polygon, 4326),
    
    -- Metadata
    data_source VARCHAR(50) DEFAULT 'BCPAO',
    last_sale_date DATE,
    last_sale_price NUMERIC(14, 2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create spatial index for fast geographic queries
CREATE INDEX IF NOT EXISTS idx_fl_parcels_geom ON fl_parcels USING GIST(geom);
CREATE INDEX IF NOT EXISTS idx_fl_parcels_boundary ON fl_parcels USING GIST(parcel_boundary);

-- Create standard indexes
CREATE INDEX IF NOT EXISTS idx_fl_parcels_county ON fl_parcels(county);
CREATE INDEX IF NOT EXISTS idx_fl_parcels_zoning ON fl_parcels(zoning_code);
CREATE INDEX IF NOT EXISTS idx_fl_parcels_jurisdiction ON fl_parcels(jurisdiction);
CREATE INDEX IF NOT EXISTS idx_fl_parcels_city ON fl_parcels(city);
CREATE INDEX IF NOT EXISTS idx_fl_parcels_zip ON fl_parcels(zip_code);

-- Enable RLS
ALTER TABLE fl_parcels ENABLE ROW LEVEL SECURITY;

-- Public read access for parcels
CREATE POLICY "fl_parcels_public_read" ON fl_parcels 
    FOR SELECT USING (true);

-- Function to find nearby parcels within radius (meters)
CREATE OR REPLACE FUNCTION find_nearby_parcels(
    p_lat NUMERIC,
    p_lon NUMERIC,
    p_radius_meters INTEGER DEFAULT 1609  -- 1 mile default
)
RETURNS TABLE (
    parcel_id VARCHAR,
    address_line1 VARCHAR,
    city VARCHAR,
    zoning_code VARCHAR,
    just_value NUMERIC,
    distance_meters NUMERIC
)
LANGUAGE SQL STABLE
AS $$
    SELECT 
        parcel_id,
        address_line1,
        city,
        zoning_code,
        just_value,
        ST_Distance(
            geom::geography, 
            ST_SetSRID(ST_MakePoint(p_lon, p_lat), 4326)::geography
        ) AS distance_meters
    FROM fl_parcels
    WHERE ST_DWithin(
        geom::geography,
        ST_SetSRID(ST_MakePoint(p_lon, p_lat), 4326)::geography,
        p_radius_meters
    )
    ORDER BY distance_meters
    LIMIT 50;
$$;

-- Function to get parcels in bounding box (for map viewport)
CREATE OR REPLACE FUNCTION get_parcels_in_bbox(
    min_lon NUMERIC,
    min_lat NUMERIC,
    max_lon NUMERIC,
    max_lat NUMERIC,
    p_limit INTEGER DEFAULT 500
)
RETURNS TABLE (
    id UUID,
    parcel_id VARCHAR,
    address_line1 VARCHAR,
    city VARCHAR,
    zoning_code VARCHAR,
    just_value NUMERIC,
    centroid_lat NUMERIC,
    centroid_lon NUMERIC
)
LANGUAGE SQL STABLE
AS $$
    SELECT 
        id,
        parcel_id,
        address_line1,
        city,
        zoning_code,
        just_value,
        centroid_lat,
        centroid_lon
    FROM fl_parcels
    WHERE geom && ST_MakeEnvelope(min_lon, min_lat, max_lon, max_lat, 4326)
    ORDER BY just_value DESC NULLS LAST
    LIMIT p_limit;
$$;

-- Function to find comparable properties (for CMA)
CREATE OR REPLACE FUNCTION find_comparables(
    p_parcel_id VARCHAR,
    p_radius_meters INTEGER DEFAULT 3218,  -- 2 miles default
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    parcel_id VARCHAR,
    address_line1 VARCHAR,
    city VARCHAR,
    zoning_code VARCHAR,
    year_built INTEGER,
    living_area_sqft INTEGER,
    bedrooms INTEGER,
    bathrooms NUMERIC,
    just_value NUMERIC,
    last_sale_price NUMERIC,
    last_sale_date DATE,
    distance_meters NUMERIC
)
LANGUAGE SQL STABLE
AS $$
    WITH subject AS (
        SELECT geom, zoning_code, year_built, living_area_sqft, bedrooms
        FROM fl_parcels
        WHERE parcel_id = p_parcel_id
    )
    SELECT 
        p.parcel_id,
        p.address_line1,
        p.city,
        p.zoning_code,
        p.year_built,
        p.living_area_sqft,
        p.bedrooms,
        p.bathrooms,
        p.just_value,
        p.last_sale_price,
        p.last_sale_date,
        ST_Distance(p.geom::geography, s.geom::geography) AS distance_meters
    FROM fl_parcels p, subject s
    WHERE p.parcel_id != p_parcel_id
      AND p.zoning_code = s.zoning_code
      AND ABS(COALESCE(p.year_built, 2000) - COALESCE(s.year_built, 2000)) <= 15
      AND ABS(COALESCE(p.living_area_sqft, 1500) - COALESCE(s.living_area_sqft, 1500)) <= 500
      AND ST_DWithin(p.geom::geography, s.geom::geography, p_radius_meters)
    ORDER BY 
        ABS(COALESCE(p.living_area_sqft, 1500) - COALESCE(s.living_area_sqft, 1500)),
        distance_meters
    LIMIT p_limit;
$$;

-- Add updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER fl_parcels_updated_at
    BEFORE UPDATE ON fl_parcels
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT SELECT ON fl_parcels TO anon, authenticated;
GRANT EXECUTE ON FUNCTION find_nearby_parcels TO anon, authenticated;
GRANT EXECUTE ON FUNCTION get_parcels_in_bbox TO anon, authenticated;
GRANT EXECUTE ON FUNCTION find_comparables TO anon, authenticated;

COMMENT ON TABLE fl_parcels IS 'Florida parcels with PostGIS spatial support for ZoneWise V3';
