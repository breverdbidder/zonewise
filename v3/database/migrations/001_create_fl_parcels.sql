-- ZoneWise V3 - fl_parcels PostGIS Table
-- Migration: 001_create_fl_parcels.sql
-- Created: 2026-01-21

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create fl_parcels table
CREATE TABLE IF NOT EXISTS fl_parcels (
    id BIGSERIAL PRIMARY KEY,
    parcel_id VARCHAR(50) UNIQUE NOT NULL,
    
    -- Location
    address TEXT,
    city VARCHAR(100),
    zip_code VARCHAR(10),
    county VARCHAR(50) DEFAULT 'Brevard',
    state VARCHAR(2) DEFAULT 'FL',
    jurisdiction VARCHAR(100),
    
    -- Geometry (PostGIS)
    geometry GEOMETRY(POLYGON, 4326),
    centroid GEOMETRY(POINT, 4326),
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    
    -- Zoning
    zone_code VARCHAR(20),
    zone_district VARCHAR(100),
    zone_description TEXT,
    future_land_use VARCHAR(50),
    
    -- Physical Characteristics
    lot_size_sqft DECIMAL(12, 2),
    lot_size_acres DECIMAL(10, 4),
    lot_width_ft DECIMAL(10, 2),
    lot_depth_ft DECIMAL(10, 2),
    living_area_sqft DECIMAL(12, 2),
    total_area_sqft DECIMAL(12, 2),
    
    -- Building Info
    year_built INTEGER,
    bedrooms INTEGER,
    bathrooms DECIMAL(3, 1),
    stories INTEGER,
    building_type VARCHAR(50),
    construction_type VARCHAR(50),
    roof_type VARCHAR(50),
    
    -- Values
    assessed_value DECIMAL(12, 2),
    land_value DECIMAL(12, 2),
    improvement_value DECIMAL(12, 2),
    market_value DECIMAL(12, 2),
    just_value DECIMAL(12, 2),
    
    -- Sales History
    last_sale_date DATE,
    last_sale_price DECIMAL(12, 2),
    
    -- Environmental
    flood_zone VARCHAR(10),
    flood_zone_description VARCHAR(100),
    wetlands_pct DECIMAL(5, 2),
    
    -- Utilities & Infrastructure
    utilities_available BOOLEAN DEFAULT TRUE,
    water_service VARCHAR(50),
    sewer_service VARCHAR(50),
    road_frontage_ft DECIMAL(10, 2),
    
    -- Status
    vacancy_status VARCHAR(20),
    homestead_exempt BOOLEAN DEFAULT FALSE,
    
    -- Owner Info (anonymized)
    owner_type VARCHAR(50), -- Individual, Corporate, Government, Trust
    
    -- Metadata
    bcpao_account VARCHAR(30),
    data_source VARCHAR(50) DEFAULT 'BCPAO',
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Indexes will be created separately
    CONSTRAINT valid_coordinates CHECK (
        latitude IS NULL OR (latitude BETWEEN 25.0 AND 31.0)
    ),
    CONSTRAINT valid_lot_size CHECK (
        lot_size_sqft IS NULL OR lot_size_sqft >= 0
    )
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_fl_parcels_parcel_id ON fl_parcels(parcel_id);
CREATE INDEX IF NOT EXISTS idx_fl_parcels_zone_code ON fl_parcels(zone_code);
CREATE INDEX IF NOT EXISTS idx_fl_parcels_jurisdiction ON fl_parcels(jurisdiction);
CREATE INDEX IF NOT EXISTS idx_fl_parcels_city ON fl_parcels(city);
CREATE INDEX IF NOT EXISTS idx_fl_parcels_zip ON fl_parcels(zip_code);

-- Spatial indexes
CREATE INDEX IF NOT EXISTS idx_fl_parcels_geometry ON fl_parcels USING GIST(geometry);
CREATE INDEX IF NOT EXISTS idx_fl_parcels_centroid ON fl_parcels USING GIST(centroid);

-- Value indexes for CMA queries
CREATE INDEX IF NOT EXISTS idx_fl_parcels_assessed_value ON fl_parcels(assessed_value);
CREATE INDEX IF NOT EXISTS idx_fl_parcels_last_sale_date ON fl_parcels(last_sale_date);

-- Enable Row Level Security
ALTER TABLE fl_parcels ENABLE ROW LEVEL SECURITY;

-- Public read policy (parcels are public record)
CREATE POLICY "Public read access" ON fl_parcels
    FOR SELECT USING (true);

-- Comment on table
COMMENT ON TABLE fl_parcels IS 'Florida parcel data with PostGIS geometry for ZoneWise V3';

-- Create function to find comparable sales
CREATE OR REPLACE FUNCTION find_comparable_sales(
    subject_parcel_id VARCHAR(50),
    search_radius_meters FLOAT DEFAULT 1609.34,  -- 1 mile
    max_results INTEGER DEFAULT 5
)
RETURNS TABLE (
    parcel_id VARCHAR(50),
    address TEXT,
    lot_size_sqft DECIMAL(12, 2),
    living_area_sqft DECIMAL(12, 2),
    year_built INTEGER,
    sale_price DECIMAL(12, 2),
    sale_date DATE,
    distance_miles FLOAT
) AS $$
BEGIN
    RETURN QUERY
    WITH subject AS (
        SELECT centroid, zone_code
        FROM fl_parcels
        WHERE fl_parcels.parcel_id = subject_parcel_id
    )
    SELECT 
        p.parcel_id,
        p.address,
        p.lot_size_sqft,
        p.living_area_sqft,
        p.year_built,
        p.last_sale_price AS sale_price,
        p.last_sale_date AS sale_date,
        ST_Distance(p.centroid::geography, s.centroid::geography) / 1609.34 AS distance_miles
    FROM fl_parcels p, subject s
    WHERE p.parcel_id != subject_parcel_id
        AND p.last_sale_price IS NOT NULL
        AND p.last_sale_date >= (CURRENT_DATE - INTERVAL '2 years')
        AND ST_DWithin(p.centroid::geography, s.centroid::geography, search_radius_meters)
        AND p.zone_code = s.zone_code
    ORDER BY ST_Distance(p.centroid::geography, s.centroid::geography)
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- Create function for parcels within bounds (for map viewport)
CREATE OR REPLACE FUNCTION get_parcels_in_bounds(
    min_lng FLOAT,
    min_lat FLOAT,
    max_lng FLOAT,
    max_lat FLOAT,
    max_parcels INTEGER DEFAULT 1000
)
RETURNS TABLE (
    parcel_id VARCHAR(50),
    address TEXT,
    zone_code VARCHAR(20),
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    assessed_value DECIMAL(12, 2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.parcel_id,
        p.address,
        p.zone_code,
        p.latitude,
        p.longitude,
        p.assessed_value
    FROM fl_parcels p
    WHERE p.centroid && ST_MakeEnvelope(min_lng, min_lat, max_lng, max_lat, 4326)
    LIMIT max_parcels;
END;
$$ LANGUAGE plpgsql;
