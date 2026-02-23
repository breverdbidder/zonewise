-- Migration 007: County Skill File Paths
-- Adds skill_file_path column to jurisdictions table
-- Links each jurisdiction to its CraftAgents county skill file
-- Generated: 2026-02-23

-- Add skill_file_path column
ALTER TABLE public.jurisdictions
ADD COLUMN IF NOT EXISTS skill_file_path TEXT,
ADD COLUMN IF NOT EXISTS skill_validated_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS portal_type TEXT DEFAULT 'unknown'
    CHECK (portal_type IN ('municode','arcgis','custom','pdf','unknown')),
ADD COLUMN IF NOT EXISTS anti_scrape BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS rate_limit_rpm INTEGER DEFAULT 30;

-- Index for fast lookups by skill path
CREATE INDEX IF NOT EXISTS idx_jurisdictions_skill_path
    ON public.jurisdictions(skill_file_path)
    WHERE skill_file_path IS NOT NULL;

-- Index for county grouping (used heavily by generator)
CREATE INDEX IF NOT EXISTS idx_jurisdictions_county_lower
    ON public.jurisdictions(LOWER(county));

-- Populate skill_file_path for all counties
-- Using UPDATE pattern: match county name → set path
DO $$
DECLARE
    county_map JSONB := '{
        "alachua":      "zonewise/skills/county-alachua/SKILL.md",
        "baker":        "zonewise/skills/county-baker/SKILL.md",
        "bay":          "zonewise/skills/county-bay/SKILL.md",
        "bradford":     "zonewise/skills/county-bradford/SKILL.md",
        "brevard":      "zonewise/skills/county-brevard/SKILL.md",
        "broward":      "zonewise/skills/county-broward/SKILL.md",
        "calhoun":      "zonewise/skills/county-calhoun/SKILL.md",
        "charlotte":    "zonewise/skills/county-charlotte/SKILL.md",
        "citrus":       "zonewise/skills/county-citrus/SKILL.md",
        "clay":         "zonewise/skills/county-clay/SKILL.md",
        "collier":      "zonewise/skills/county-collier/SKILL.md",
        "columbia":     "zonewise/skills/county-columbia/SKILL.md",
        "miami-dade":   "zonewise/skills/county-miami-dade/SKILL.md",
        "desoto":       "zonewise/skills/county-desoto/SKILL.md",
        "dixie":        "zonewise/skills/county-dixie/SKILL.md",
        "duval":        "zonewise/skills/county-duval/SKILL.md",
        "escambia":     "zonewise/skills/county-escambia/SKILL.md",
        "flagler":      "zonewise/skills/county-flagler/SKILL.md",
        "franklin":     "zonewise/skills/county-franklin/SKILL.md",
        "gadsden":      "zonewise/skills/county-gadsden/SKILL.md",
        "gilchrist":    "zonewise/skills/county-gilchrist/SKILL.md",
        "glades":       "zonewise/skills/county-glades/SKILL.md",
        "gulf":         "zonewise/skills/county-gulf/SKILL.md",
        "hamilton":     "zonewise/skills/county-hamilton/SKILL.md",
        "hardee":       "zonewise/skills/county-hardee/SKILL.md",
        "hendry":       "zonewise/skills/county-hendry/SKILL.md",
        "hernando":     "zonewise/skills/county-hernando/SKILL.md",
        "highlands":    "zonewise/skills/county-highlands/SKILL.md",
        "hillsborough": "zonewise/skills/county-hillsborough/SKILL.md",
        "holmes":       "zonewise/skills/county-holmes/SKILL.md",
        "indian river": "zonewise/skills/county-indian-river/SKILL.md",
        "jackson":      "zonewise/skills/county-jackson/SKILL.md",
        "jefferson":    "zonewise/skills/county-jefferson/SKILL.md",
        "lafayette":    "zonewise/skills/county-lafayette/SKILL.md",
        "lake":         "zonewise/skills/county-lake/SKILL.md",
        "lee":          "zonewise/skills/county-lee/SKILL.md",
        "leon":         "zonewise/skills/county-leon/SKILL.md",
        "levy":         "zonewise/skills/county-levy/SKILL.md",
        "liberty":      "zonewise/skills/county-liberty/SKILL.md",
        "madison":      "zonewise/skills/county-madison/SKILL.md",
        "manatee":      "zonewise/skills/county-manatee/SKILL.md",
        "marion":       "zonewise/skills/county-marion/SKILL.md",
        "martin":       "zonewise/skills/county-martin/SKILL.md",
        "monroe":       "zonewise/skills/county-monroe/SKILL.md",
        "nassau":       "zonewise/skills/county-nassau/SKILL.md",
        "okaloosa":     "zonewise/skills/county-okaloosa/SKILL.md",
        "okeechobee":   "zonewise/skills/county-okeechobee/SKILL.md",
        "orange":       "zonewise/skills/county-orange/SKILL.md",
        "osceola":      "zonewise/skills/county-osceola/SKILL.md",
        "palm beach":   "zonewise/skills/county-palm-beach/SKILL.md",
        "pasco":        "zonewise/skills/county-pasco/SKILL.md",
        "pinellas":     "zonewise/skills/county-pinellas/SKILL.md",
        "polk":         "zonewise/skills/county-polk/SKILL.md",
        "putnam":       "zonewise/skills/county-putnam/SKILL.md",
        "st. johns":    "zonewise/skills/county-st-johns/SKILL.md",
        "st. lucie":    "zonewise/skills/county-st-lucie/SKILL.md",
        "santa rosa":   "zonewise/skills/county-santa-rosa/SKILL.md",
        "sarasota":     "zonewise/skills/county-sarasota/SKILL.md",
        "seminole":     "zonewise/skills/county-seminole/SKILL.md",
        "sumter":       "zonewise/skills/county-sumter/SKILL.md",
        "suwannee":     "zonewise/skills/county-suwannee/SKILL.md",
        "taylor":       "zonewise/skills/county-taylor/SKILL.md",
        "union":        "zonewise/skills/county-union/SKILL.md",
        "volusia":      "zonewise/skills/county-volusia/SKILL.md",
        "wakulla":      "zonewise/skills/county-wakulla/SKILL.md",
        "walton":       "zonewise/skills/county-walton/SKILL.md",
        "washington":   "zonewise/skills/county-washington/SKILL.md"
    }'::JSONB;
    county_key TEXT;
    skill_path TEXT;
BEGIN
    FOR county_key IN SELECT jsonb_object_keys(county_map)
    LOOP
        skill_path := county_map ->> county_key;
        UPDATE public.jurisdictions
        SET skill_file_path = skill_path,
            skill_validated_at = NOW()
        WHERE LOWER(county) = county_key
          AND skill_file_path IS NULL;
    END LOOP;
END;
$$;

-- Set anti_scrape flags for complex counties
UPDATE public.jurisdictions
SET anti_scrape = true, rate_limit_rpm = 10
WHERE LOWER(county) IN (
    'miami-dade', 'duval', 'hillsborough',
    'palm beach', 'pinellas', 'broward', 'orange'
);

-- Add comment
COMMENT ON COLUMN public.jurisdictions.skill_file_path IS
    'Path to CraftAgents county skill file in zonewise-desktop repo. '
    'Format: zonewise/skills/county-{slug}/SKILL.md. '
    'Used by county_research_agent to load instructions before scraping.';

COMMENT ON COLUMN public.jurisdictions.anti_scrape IS
    'True if county portal has rate limiting / bot detection. '
    'Triggers AgentQL Mode 3 instead of direct WebFetch.';
