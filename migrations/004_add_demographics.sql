-- Migration: Add demographic and score columns to sample_properties
-- Date: 2026-01-23

-- Add Census demographic columns
ALTER TABLE public.sample_properties
ADD COLUMN IF NOT EXISTS census_tract VARCHAR(10),
ADD COLUMN IF NOT EXISTS census_block_group VARCHAR(12),
ADD COLUMN IF NOT EXISTS median_household_income INTEGER,
ADD COLUMN IF NOT EXISTS total_population INTEGER,
ADD COLUMN IF NOT EXISTS population_density DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS poverty_count INTEGER,
ADD COLUMN IF NOT EXISTS poverty_rate DECIMAL(5,2),
ADD COLUMN IF NOT EXISTS median_home_value INTEGER,
ADD COLUMN IF NOT EXISTS median_rent INTEGER,
ADD COLUMN IF NOT EXISTS vacancy_rate DECIMAL(5,2);

-- Add score columns (for future API integrations)
ALTER TABLE public.sample_properties
ADD COLUMN IF NOT EXISTS walk_score INTEGER CHECK (walk_score >= 0 AND walk_score <= 100),
ADD COLUMN IF NOT EXISTS bike_score INTEGER CHECK (bike_score >= 0 AND bike_score <= 100),
ADD COLUMN IF NOT EXISTS transit_score INTEGER CHECK (transit_score >= 0 AND transit_score <= 100),
ADD COLUMN IF NOT EXISTS school_score INTEGER CHECK (school_score >= 0 AND school_score <= 100),
ADD COLUMN IF NOT EXISTS crime_score INTEGER CHECK (crime_score >= 0 AND crime_score <= 100);

-- Add timestamp for demographic data freshness
ALTER TABLE public.sample_properties
ADD COLUMN IF NOT EXISTS demographics_updated_at TIMESTAMP WITH TIME ZONE;

-- Create index on census_tract for faster lookups
CREATE INDEX IF NOT EXISTS idx_sample_properties_census_tract ON public.sample_properties(census_tract);

-- Create census_tracts lookup table for caching ACS data
CREATE TABLE IF NOT EXISTS public.census_tracts (
    id SERIAL PRIMARY KEY,
    geoid VARCHAR(11) UNIQUE NOT NULL,  -- Format: SSCCCTTTTTT (state, county, tract)
    state_fips VARCHAR(2) NOT NULL,
    county_fips VARCHAR(3) NOT NULL,
    tract_code VARCHAR(6) NOT NULL,
    name VARCHAR(255),
    
    -- ACS Demographics
    median_household_income INTEGER,
    total_population INTEGER,
    population_density DECIMAL(10,2),
    poverty_count INTEGER,
    poverty_rate DECIMAL(5,2),
    median_home_value INTEGER,
    median_rent INTEGER,
    vacancy_rate DECIMAL(5,2),
    median_age DECIMAL(4,1),
    owner_occupied_rate DECIMAL(5,2),
    
    -- Metadata
    acs_year INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for tract lookup
CREATE INDEX IF NOT EXISTS idx_census_tracts_geoid ON public.census_tracts(geoid);
CREATE INDEX IF NOT EXISTS idx_census_tracts_county ON public.census_tracts(state_fips, county_fips);

COMMENT ON TABLE public.census_tracts IS 'Census tract demographic data from ACS 5-year estimates';
COMMENT ON COLUMN public.sample_properties.census_tract IS '6-digit census tract code';
COMMENT ON COLUMN public.sample_properties.walk_score IS 'Walk Score (0-100) from walkscore.com API';
COMMENT ON COLUMN public.sample_properties.school_score IS 'School rating (0-100) from GreatSchools API';
COMMENT ON COLUMN public.sample_properties.crime_score IS 'Safety score (0-100, higher=safer) from crime data API';
