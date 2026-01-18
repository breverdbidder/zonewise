-- ZoneWise Database Schema
-- Supabase PostgreSQL

-- Jurisdictions table
CREATE TABLE IF NOT EXISTS public.jurisdictions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    state VARCHAR(2) DEFAULT 'FL',
    county VARCHAR(100) DEFAULT 'Brevard',
    code_source TEXT,
    data_completeness INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Zoning Districts table  
CREATE TABLE IF NOT EXISTS public.zoning_districts (
    id SERIAL PRIMARY KEY,
    jurisdiction_id INTEGER REFERENCES jurisdictions(id),
    code VARCHAR(20) NOT NULL,
    name VARCHAR(200),
    category VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(jurisdiction_id, code)
);

-- Parcels table
CREATE TABLE IF NOT EXISTS public.parcels (
    id SERIAL PRIMARY KEY,
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_parcels_account ON public.parcels(account);
CREATE INDEX IF NOT EXISTS idx_parcels_zoning ON public.parcels(zoning_code);
CREATE INDEX IF NOT EXISTS idx_zoning_districts_code ON public.zoning_districts(code);
CREATE INDEX IF NOT EXISTS idx_zoning_districts_jurisdiction ON public.zoning_districts(jurisdiction_id);

-- Enable RLS
ALTER TABLE public.parcels ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.zoning_districts ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY "Public read parcels" ON public.parcels FOR SELECT USING (true);
CREATE POLICY "Public read districts" ON public.zoning_districts FOR SELECT USING (true);
