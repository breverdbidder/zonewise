-- =============================================================================
-- ZoneWise Migration: Add Demographic and Score Columns
-- =============================================================================
-- Date: 2026-01-23
-- Target: sample_properties table
-- 
-- Run this in Supabase SQL Editor:
-- https://supabase.com/dashboard/project/mocerqjnksmhcjzxrewo/sql/new
-- =============================================================================

-- Census demographic columns
ALTER TABLE public.sample_properties
ADD COLUMN IF NOT EXISTS census_tract VARCHAR(20),
ADD COLUMN IF NOT EXISTS census_block_group VARCHAR(20),
ADD COLUMN IF NOT EXISTS median_household_income INTEGER,
ADD COLUMN IF NOT EXISTS population_density DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS poverty_rate DECIMAL(5,2),
ADD COLUMN IF NOT EXISTS median_age DECIMAL(4,1),
ADD COLUMN IF NOT EXISTS owner_occupied_pct DECIMAL(5,2),
ADD COLUMN IF NOT EXISTS median_home_value_census INTEGER;

-- Location score columns (0-100 scale)
ALTER TABLE public.sample_properties
ADD COLUMN IF NOT EXISTS walk_score INTEGER CHECK (walk_score IS NULL OR (walk_score >= 0 AND walk_score <= 100)),
ADD COLUMN IF NOT EXISTS bike_score INTEGER CHECK (bike_score IS NULL OR (bike_score >= 0 AND bike_score <= 100)),
ADD COLUMN IF NOT EXISTS transit_score INTEGER CHECK (transit_score IS NULL OR (transit_score >= 0 AND transit_score <= 100)),
ADD COLUMN IF NOT EXISTS school_score INTEGER CHECK (school_score IS NULL OR (school_score >= 0 AND school_score <= 100)),
ADD COLUMN IF NOT EXISTS crime_score INTEGER CHECK (crime_score IS NULL OR (crime_score >= 0 AND crime_score <= 100));

-- Metadata columns
ALTER TABLE public.sample_properties
ADD COLUMN IF NOT EXISTS demographics_updated_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS scores_updated_at TIMESTAMPTZ;

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_sp_census_tract ON public.sample_properties(census_tract);
CREATE INDEX IF NOT EXISTS idx_sp_median_income ON public.sample_properties(median_household_income);
CREATE INDEX IF NOT EXISTS idx_sp_walk_score ON public.sample_properties(walk_score);
CREATE INDEX IF NOT EXISTS idx_sp_school_score ON public.sample_properties(school_score);

-- Verification query
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_name = 'sample_properties' 
AND column_name IN (
    'census_tract', 'median_household_income', 'poverty_rate',
    'walk_score', 'bike_score', 'transit_score', 'school_score', 'crime_score'
)
ORDER BY column_name;
