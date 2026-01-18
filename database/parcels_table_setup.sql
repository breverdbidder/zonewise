-- ZoneWise Parcels Table Setup
-- This must be run in Supabase SQL Editor or via migration

-- Drop existing table if corrupted
DROP TABLE IF EXISTS public.parcels CASCADE;

-- Create parcels table
CREATE TABLE public.parcels (
    id BIGSERIAL PRIMARY KEY,
    account VARCHAR(20) UNIQUE NOT NULL,
    parcel_id VARCHAR(50),
    address TEXT,
    city VARCHAR(100),
    owner TEXT,
    acres DECIMAL(10,4),
    zoning_code VARCHAR(20),
    land_use_code VARCHAR(20),
    land_use_desc TEXT,
    jurisdiction_id INTEGER,
    township VARCHAR(10),
    range VARCHAR(10),
    section VARCHAR(10),
    subdivision VARCHAR(100),
    lot VARCHAR(50),
    block VARCHAR(50),
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),
    centroid_x DECIMAL(15,6),
    centroid_y DECIMAL(15,6),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_parcels_account ON public.parcels(account);
CREATE INDEX idx_parcels_zoning ON public.parcels(zoning_code);
CREATE INDEX idx_parcels_city ON public.parcels(city);
CREATE INDEX idx_parcels_jurisdiction ON public.parcels(jurisdiction_id);
CREATE INDEX idx_parcels_coords ON public.parcels(latitude, longitude) WHERE latitude IS NOT NULL;

-- Enable RLS
ALTER TABLE public.parcels ENABLE ROW LEVEL SECURITY;

-- Policies for public read
CREATE POLICY "Allow public read" ON public.parcels FOR SELECT USING (true);

-- Policy for service role write
CREATE POLICY "Allow service write" ON public.parcels FOR ALL USING (auth.role() = 'service_role');

-- Grant permissions
GRANT SELECT ON public.parcels TO anon, authenticated;
GRANT ALL ON public.parcels TO service_role;
GRANT USAGE, SELECT ON SEQUENCE public.parcels_id_seq TO service_role;

-- Add comments
COMMENT ON TABLE public.parcels IS 'Brevard County parcels - 335,578 records from GIS';
COMMENT ON COLUMN public.parcels.account IS 'BCPAO Tax Account Number (unique identifier)';
COMMENT ON COLUMN public.parcels.zoning_code IS 'Official zoning designation (links to zoning_districts.code)';
