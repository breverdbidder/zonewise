-- =============================================================================
-- ZONEWISE MODAL PIPELINE - SUPABASE SCHEMA
-- =============================================================================
-- 
-- Database: mocerqjnksmhcjzxrewo.supabase.co
-- 
-- This schema supports:
-- - 20 ZoneWise Data Phases
-- - 10 Data Stages (Malabar POC Framework)
-- - 67 FL Counties × 1,100+ jurisdictions
-- - Census API integration
-- - Location Intelligence scoring
-- 
-- =============================================================================


-- =============================================================================
-- CORE TABLES (Phases 1-5)
-- =============================================================================

-- Jurisdictions (17 Brevard, 1,100+ statewide)
CREATE TABLE IF NOT EXISTS jurisdictions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    county VARCHAR(50) NOT NULL,
    fips_code VARCHAR(10),
    state VARCHAR(2) DEFAULT 'FL',
    jurisdiction_type VARCHAR(20), -- 'municipality', 'county', 'special_district'
    municode_url TEXT,
    official_website TEXT,
    gis_endpoint TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(name, county)
);

-- Zoning Districts (Phase 2)
CREATE TABLE IF NOT EXISTS zoning_districts (
    id SERIAL PRIMARY KEY,
    jurisdiction_id INTEGER REFERENCES jurisdictions(id),
    zone_code VARCHAR(20) NOT NULL,
    zone_name VARCHAR(200),
    zone_category VARCHAR(50), -- 'residential', 'commercial', 'industrial', 'mixed', 'special'
    description TEXT,
    purpose TEXT,
    source_section VARCHAR(100),
    source_url TEXT,
    effective_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(jurisdiction_id, zone_code)
);

CREATE INDEX idx_zoning_districts_jurisdiction ON zoning_districts(jurisdiction_id);
CREATE INDEX idx_zoning_districts_category ON zoning_districts(zone_category);

-- Dimensional Standards (Phase 3)
CREATE TABLE IF NOT EXISTS dimensional_standards (
    id SERIAL PRIMARY KEY,
    district_id INTEGER REFERENCES zoning_districts(id),
    min_lot_size_sf INTEGER,
    min_lot_width_ft NUMERIC(10,2),
    min_lot_depth_ft NUMERIC(10,2),
    front_setback_ft NUMERIC(10,2),
    side_setback_ft NUMERIC(10,2),
    rear_setback_ft NUMERIC(10,2),
    corner_side_setback_ft NUMERIC(10,2),
    max_height_ft NUMERIC(10,2),
    max_stories INTEGER,
    max_building_coverage_pct NUMERIC(5,2),
    max_impervious_pct NUMERIC(5,2),
    max_far NUMERIC(5,2),
    max_density_units_acre NUMERIC(10,2),
    min_open_space_pct NUMERIC(5,2),
    source_section VARCHAR(100),
    source_url TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(district_id)
);

-- Permitted Uses (Phase 4)
CREATE TABLE IF NOT EXISTS permitted_uses (
    id SERIAL PRIMARY KEY,
    district_id INTEGER REFERENCES zoning_districts(id),
    use_category VARCHAR(50), -- 'residential', 'commercial', 'industrial', 'institutional'
    use_name VARCHAR(200) NOT NULL,
    use_code VARCHAR(20),
    permission_type CHAR(1), -- 'P'=Permitted, 'C'=Conditional, 'S'=Special, 'X'=Prohibited
    conditions TEXT,
    notes TEXT,
    source_section VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(district_id, use_name)
);

CREATE INDEX idx_permitted_uses_district ON permitted_uses(district_id);
CREATE INDEX idx_permitted_uses_category ON permitted_uses(use_category);
CREATE INDEX idx_permitted_uses_permission ON permitted_uses(permission_type);

-- Conditional Uses (Phase 5)
CREATE TABLE IF NOT EXISTS conditional_uses (
    id SERIAL PRIMARY KEY,
    district_id INTEGER REFERENCES zoning_districts(id),
    use_name VARCHAR(200) NOT NULL,
    approval_body VARCHAR(100), -- 'Planning Board', 'City Council', 'BZA'
    required_findings TEXT[],
    standard_conditions TEXT[],
    application_fee NUMERIC(10,2),
    review_timeline_days INTEGER,
    public_hearing_required BOOLEAN DEFAULT TRUE,
    source_section VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(district_id, use_name)
);


-- =============================================================================
-- ADVANCED ZONING TABLES (Phases 6-10)
-- =============================================================================

-- Prohibited Uses (Phase 6)
CREATE TABLE IF NOT EXISTS prohibited_uses (
    id SERIAL PRIMARY KEY,
    district_id INTEGER REFERENCES zoning_districts(id),
    use_name VARCHAR(200) NOT NULL,
    reason TEXT,
    variance_eligible BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(district_id, use_name)
);

-- Overlay Districts (Phase 7)
CREATE TABLE IF NOT EXISTS overlay_districts (
    id SERIAL PRIMARY KEY,
    jurisdiction_id INTEGER REFERENCES jurisdictions(id),
    overlay_code VARCHAR(20) NOT NULL,
    overlay_name VARCHAR(200),
    overlay_type VARCHAR(50), -- 'historic', 'flood', 'airport', 'environmental', 'downtown', 'corridor', 'tod'
    base_districts_affected TEXT[], -- Array of zone codes
    additional_setbacks JSONB,
    height_restrictions JSONB,
    design_standards TEXT,
    additional_requirements TEXT[],
    bonuses_available JSONB,
    source_section VARCHAR(100),
    source_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(jurisdiction_id, overlay_code)
);

-- Development Bonuses (Phase 8) - COMPETITIVE ADVANTAGE
CREATE TABLE IF NOT EXISTS development_bonuses (
    id SERIAL PRIMARY KEY,
    jurisdiction_id INTEGER REFERENCES jurisdictions(id),
    bonus_type VARCHAR(50), -- 'density', 'height', 'parking', 'setback', 'far', 'fee_waiver', 'expedited'
    bonus_name VARCHAR(200),
    bonus_percentage NUMERIC(5,2),
    bonus_amount VARCHAR(100), -- e.g., "10 additional units", "5 extra feet"
    qualifying_criteria TEXT[],
    eligible_districts TEXT[], -- Array of zone codes
    application_process TEXT,
    source_section VARCHAR(100),
    source_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(jurisdiction_id, bonus_type, bonus_name)
);

-- Parking Requirements (Phase 9)
CREATE TABLE IF NOT EXISTS parking_requirements (
    id SERIAL PRIMARY KEY,
    jurisdiction_id INTEGER REFERENCES jurisdictions(id),
    use_category VARCHAR(100),
    use_name VARCHAR(200) NOT NULL,
    min_spaces VARCHAR(100), -- e.g., "1 per 300 sf", "2 per unit"
    max_spaces VARCHAR(100),
    space_dimensions JSONB, -- {"width": 9, "length": 18, "accessible_width": 16}
    ev_required_pct NUMERIC(5,2),
    bicycle_spaces VARCHAR(100),
    shared_parking_allowed BOOLEAN DEFAULT FALSE,
    reduction_provisions TEXT,
    source_section VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(jurisdiction_id, use_name)
);

-- Density/Intensity (Phase 10)
CREATE TABLE IF NOT EXISTS density_intensity (
    id SERIAL PRIMARY KEY,
    district_id INTEGER REFERENCES zoning_districts(id),
    max_units_acre NUMERIC(10,2),
    min_unit_size_sf INTEGER,
    max_units_lot INTEGER,
    flum_max_density NUMERIC(10,2),
    flum_max_far NUMERIC(5,2),
    flum_designation VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(district_id)
);


-- =============================================================================
-- SPECIALTY TABLES (Phases 11-15)
-- =============================================================================

-- Short-Term Rentals (Phase 11)
CREATE TABLE IF NOT EXISTS str_regulations (
    id SERIAL PRIMARY KEY,
    jurisdiction_id INTEGER REFERENCES jurisdictions(id),
    str_allowed BOOLEAN,
    license_required BOOLEAN,
    license_fee NUMERIC(10,2),
    max_nights_year INTEGER,
    min_stay_nights INTEGER,
    zones_allowed TEXT[],
    zones_prohibited TEXT[],
    owner_occupancy_required BOOLEAN,
    parking_per_bedroom INTEGER,
    noise_restrictions TEXT,
    registration_url TEXT,
    source_section VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(jurisdiction_id)
);

-- ADU Regulations (Phase 12)
CREATE TABLE IF NOT EXISTS adu_regulations (
    id SERIAL PRIMARY KEY,
    jurisdiction_id INTEGER REFERENCES jurisdictions(id),
    adu_allowed BOOLEAN,
    max_size_sf INTEGER,
    max_size_pct NUMERIC(5,2), -- % of primary dwelling
    owner_occupancy_required BOOLEAN,
    parking_required INTEGER,
    setback_modifications JSONB,
    zones_allowed TEXT[],
    approval_process VARCHAR(50), -- 'by-right', 'administrative', 'hearing'
    source_section VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(jurisdiction_id)
);

-- Historic/Design Standards (Phase 13)
CREATE TABLE IF NOT EXISTS historic_design (
    id SERIAL PRIMARY KEY,
    jurisdiction_id INTEGER REFERENCES jurisdictions(id),
    district_name VARCHAR(200),
    designation_type VARCHAR(50), -- 'local', 'national_register', 'contributing'
    design_review_required BOOLEAN,
    review_body VARCHAR(100),
    material_requirements TEXT,
    color_palette TEXT,
    signage_restrictions TEXT,
    demolition_delay_days INTEGER,
    source_section VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- FLUM Designations (Phase 14)
CREATE TABLE IF NOT EXISTS flum_designations (
    id SERIAL PRIMARY KEY,
    jurisdiction_id INTEGER REFERENCES jurisdictions(id),
    flum_code VARCHAR(20),
    flum_name VARCHAR(200),
    max_density NUMERIC(10,2),
    max_intensity NUMERIC(5,2),
    compatible_zones TEXT[],
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(jurisdiction_id, flum_code)
);

-- Entitlement Timelines (Phase 15) - COMPETITIVE ADVANTAGE
CREATE TABLE IF NOT EXISTS entitlement_timelines (
    id SERIAL PRIMARY KEY,
    jurisdiction_id INTEGER REFERENCES jurisdictions(id),
    entitlement_type VARCHAR(50), -- 'site_plan', 'rezoning', 'variance', 'cup', 'plat'
    typical_timeline_days INTEGER,
    expedited_timeline_days INTEGER,
    application_fee NUMERIC(10,2),
    review_stages TEXT[],
    pre_application_meeting BOOLEAN,
    public_hearing_required BOOLEAN,
    appeal_process TEXT,
    source_section VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(jurisdiction_id, entitlement_type)
);


-- =============================================================================
-- INFRASTRUCTURE TABLES (Phases 16-20)
-- =============================================================================

-- Ordinance Library (Phase 16)
CREATE TABLE IF NOT EXISTS ordinances (
    id SERIAL PRIMARY KEY,
    jurisdiction_id INTEGER REFERENCES jurisdictions(id),
    ordinance_number VARCHAR(50),
    title VARCHAR(500),
    chapter VARCHAR(50),
    section VARCHAR(50),
    content TEXT,
    effective_date DATE,
    amended_date DATE,
    source_url TEXT,
    content_hash VARCHAR(64), -- For change detection
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(jurisdiction_id, ordinance_number)
);

CREATE INDEX idx_ordinances_jurisdiction ON ordinances(jurisdiction_id);
CREATE INDEX idx_ordinances_content_hash ON ordinances(content_hash);

-- Ordinance Changes (Phase 17) - COMPETITIVE ADVANTAGE
CREATE TABLE IF NOT EXISTS ordinance_changes (
    id SERIAL PRIMARY KEY,
    ordinance_id INTEGER REFERENCES ordinances(id),
    change_type VARCHAR(20), -- 'added', 'modified', 'repealed'
    previous_content TEXT,
    new_content TEXT,
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    change_summary TEXT,
    impact_zones TEXT[] -- Affected zone codes
);

-- Parcel Data (Phase 18)
CREATE TABLE IF NOT EXISTS sample_properties (
    id SERIAL PRIMARY KEY,
    parcel_id VARCHAR(50) NOT NULL,
    tax_account VARCHAR(20),
    jurisdiction VARCHAR(100),
    jurisdiction_id INTEGER REFERENCES jurisdictions(id),
    county VARCHAR(50),
    address TEXT,
    owner_name VARCHAR(200),
    owner_address TEXT,
    property_type VARCHAR(50),
    use_code VARCHAR(20),
    zone_code VARCHAR(20),
    acres NUMERIC(10,4),
    land_value NUMERIC(12,2),
    building_value NUMERIC(12,2),
    market_value NUMERIC(12,2),
    assessed_value NUMERIC(12,2),
    taxable_value NUMERIC(12,2),
    lat NUMERIC(10,7),
    lon NUMERIC(11,7),
    photo_url TEXT,
    legal_description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sample_properties_parcel ON sample_properties(parcel_id);
CREATE INDEX idx_sample_properties_jurisdiction ON sample_properties(jurisdiction_id);
CREATE INDEX idx_sample_properties_zone ON sample_properties(zone_code);

-- Environmental Overlays (Phase 19)
CREATE TABLE IF NOT EXISTS environmental_overlays (
    id SERIAL PRIMARY KEY,
    parcel_id VARCHAR(50),
    flood_zone VARCHAR(20), -- 'X', 'A', 'AE', 'VE', etc.
    flood_panel VARCHAR(20),
    base_flood_elevation NUMERIC(10,2),
    wetland_type VARCHAR(50),
    wetland_acres NUMERIC(10,4),
    coastal_high_hazard BOOLEAN DEFAULT FALSE,
    conservation_easement BOOLEAN DEFAULT FALSE,
    sjrwmd_regulated BOOLEAN DEFAULT FALSE,
    environmental_constraints TEXT[],
    source TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_environmental_parcel ON environmental_overlays(parcel_id);

-- Census Demographics (Phase 20)
CREATE TABLE IF NOT EXISTS census_demographics (
    id SERIAL PRIMARY KEY,
    county_id VARCHAR(20),
    tract_id VARCHAR(20),
    block_group VARCHAR(20),
    total_population INTEGER,
    median_income INTEGER,
    housing_units INTEGER,
    vacant_units INTEGER,
    owner_occupied INTEGER,
    renter_occupied INTEGER,
    median_home_value INTEGER,
    median_rent INTEGER,
    poverty_rate NUMERIC(5,2),
    unemployment_rate NUMERIC(5,2),
    median_age NUMERIC(5,2),
    data_year INTEGER,
    source VARCHAR(50), -- 'ACS 5-Year', 'Decennial'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(county_id, tract_id, block_group)
);

CREATE INDEX idx_census_county ON census_demographics(county_id);
CREATE INDEX idx_census_tract ON census_demographics(tract_id);


-- =============================================================================
-- 10-STAGE DATA FRAMEWORK TABLES
-- =============================================================================

-- Stage 1 & 10: Parcel-Zone Assignment
CREATE TABLE IF NOT EXISTS parcel_zones (
    id SERIAL PRIMARY KEY,
    parcel_id VARCHAR(50) NOT NULL,
    tax_account VARCHAR(20),
    jurisdiction_id INTEGER REFERENCES jurisdictions(id),
    zone_code VARCHAR(20) NOT NULL,
    zone_name VARCHAR(200),
    overlay_codes TEXT[],
    flum_code VARCHAR(20),
    source VARCHAR(50), -- 'GIS', 'Manual', 'ArcGIS'
    confidence_score NUMERIC(5,2), -- 0-100
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(parcel_id, jurisdiction_id)
);

CREATE INDEX idx_parcel_zones_parcel ON parcel_zones(parcel_id);
CREATE INDEX idx_parcel_zones_zone ON parcel_zones(zone_code);
CREATE INDEX idx_parcel_zones_jurisdiction ON parcel_zones(jurisdiction_id);

-- Stage 7: Location Scores
CREATE TABLE IF NOT EXISTS location_scores (
    id SERIAL PRIMARY KEY,
    parcel_id VARCHAR(50) NOT NULL,
    walk_score INTEGER,
    transit_score INTEGER,
    bike_score INTEGER,
    school_score INTEGER,
    crime_score INTEGER, -- Inverted: higher = safer
    composite_score INTEGER, -- Weighted average
    nearest_school_name VARCHAR(200),
    nearest_school_grade VARCHAR(2), -- 'A', 'B', 'C', 'D', 'F'
    nearest_school_distance_mi NUMERIC(5,2),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(parcel_id)
);

CREATE INDEX idx_location_scores_composite ON location_scores(composite_score DESC);

-- Stage 8: Sales History
CREATE TABLE IF NOT EXISTS sales_history (
    id SERIAL PRIMARY KEY,
    tax_account VARCHAR(20) NOT NULL,
    parcel_id VARCHAR(50),
    sale_date DATE,
    sale_price NUMERIC(12,2),
    price_per_sf NUMERIC(10,2),
    deed_type VARCHAR(50),
    grantor VARCHAR(200),
    grantee VARCHAR(200),
    or_book VARCHAR(20),
    or_page VARCHAR(20),
    qualified_sale BOOLEAN,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tax_account, sale_date)
);

CREATE INDEX idx_sales_history_account ON sales_history(tax_account);
CREATE INDEX idx_sales_history_date ON sales_history(sale_date DESC);

-- Stage 9: Building Records
CREATE TABLE IF NOT EXISTS building_details (
    id SERIAL PRIMARY KEY,
    tax_account VARCHAR(20) NOT NULL,
    parcel_id VARCHAR(50),
    building_num INTEGER DEFAULT 1,
    year_built INTEGER,
    year_renovated INTEGER,
    actual_sqft INTEGER,
    living_sqft INTEGER,
    bedrooms INTEGER,
    bathrooms NUMERIC(4,1),
    half_baths INTEGER,
    stories NUMERIC(4,1),
    construction_type VARCHAR(50),
    exterior_wall VARCHAR(50),
    roof_type VARCHAR(50),
    roof_material VARCHAR(50),
    heating_type VARCHAR(50),
    cooling_type VARCHAR(50),
    pool BOOLEAN DEFAULT FALSE,
    garage_sqft INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tax_account, building_num)
);

CREATE INDEX idx_building_details_account ON building_details(tax_account);


-- =============================================================================
-- PIPELINE MANAGEMENT
-- =============================================================================

-- Pipeline Runs (tracking)
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id SERIAL PRIMARY KEY,
    run_type VARCHAR(50), -- 'nightly', 'full_county', 'deploy', 'manual'
    county VARCHAR(50),
    status VARCHAR(20), -- 'running', 'complete', 'failed'
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    results JSONB,
    error_message TEXT,
    commit VARCHAR(40),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_pipeline_runs_type ON pipeline_runs(run_type);
CREATE INDEX idx_pipeline_runs_county ON pipeline_runs(county);

-- Stage Completion Tracking
CREATE TABLE IF NOT EXISTS stage_completion (
    id SERIAL PRIMARY KEY,
    jurisdiction_id INTEGER REFERENCES jurisdictions(id),
    stage_number INTEGER, -- 1-10
    stage_name VARCHAR(50),
    total_records INTEGER,
    completed_records INTEGER,
    completion_pct NUMERIC(5,2),
    last_run TIMESTAMPTZ,
    status VARCHAR(20), -- 'complete', 'partial', 'pending'
    notes TEXT,
    UNIQUE(jurisdiction_id, stage_number)
);


-- =============================================================================
-- VIEWS FOR REPORTING
-- =============================================================================

-- Jurisdiction completion summary
CREATE OR REPLACE VIEW v_jurisdiction_completion AS
SELECT 
    j.id,
    j.name,
    j.county,
    COUNT(DISTINCT zd.id) AS districts,
    COUNT(DISTINCT pz.id) AS parcels_assigned,
    COUNT(DISTINCT pu.id) AS uses_defined,
    COUNT(DISTINCT ob.id) AS overlays,
    COUNT(DISTINCT db.id) AS bonuses,
    (
        SELECT COALESCE(AVG(completion_pct), 0) 
        FROM stage_completion sc 
        WHERE sc.jurisdiction_id = j.id
    ) AS avg_completion_pct
FROM jurisdictions j
LEFT JOIN zoning_districts zd ON zd.jurisdiction_id = j.id
LEFT JOIN parcel_zones pz ON pz.jurisdiction_id = j.id
LEFT JOIN permitted_uses pu ON pu.district_id = zd.id
LEFT JOIN overlay_districts ob ON ob.jurisdiction_id = j.id
LEFT JOIN development_bonuses db ON db.jurisdiction_id = j.id
GROUP BY j.id, j.name, j.county;


-- Enable Row Level Security (optional)
-- ALTER TABLE jurisdictions ENABLE ROW LEVEL SECURITY;


-- =============================================================================
-- INITIAL DATA: Brevard County Jurisdictions
-- =============================================================================

INSERT INTO jurisdictions (name, county, jurisdiction_type, municode_url) VALUES
    ('Brevard County', 'Brevard', 'county', 'https://library.municode.com/fl/brevard_county'),
    ('Melbourne', 'Brevard', 'municipality', 'https://library.municode.com/fl/melbourne'),
    ('Palm Bay', 'Brevard', 'municipality', 'https://library.municode.com/fl/palm_bay'),
    ('Titusville', 'Brevard', 'municipality', 'https://library.municode.com/fl/titusville'),
    ('Cocoa', 'Brevard', 'municipality', 'https://library.municode.com/fl/cocoa'),
    ('Cocoa Beach', 'Brevard', 'municipality', 'https://library.municode.com/fl/cocoa_beach'),
    ('Rockledge', 'Brevard', 'municipality', 'https://library.municode.com/fl/rockledge'),
    ('Satellite Beach', 'Brevard', 'municipality', 'https://library.municode.com/fl/satellite_beach'),
    ('Indian Harbour Beach', 'Brevard', 'municipality', 'https://library.municode.com/fl/indian_harbour_beach'),
    ('Melbourne Beach', 'Brevard', 'municipality', 'https://library.municode.com/fl/melbourne_beach'),
    ('Indialantic', 'Brevard', 'municipality', 'https://library.municode.com/fl/indialantic'),
    ('West Melbourne', 'Brevard', 'municipality', 'https://library.municode.com/fl/west_melbourne'),
    ('Cape Canaveral', 'Brevard', 'municipality', 'https://library.municode.com/fl/cape_canaveral'),
    ('Town of Malabar', 'Brevard', 'municipality', 'https://library.municode.com/fl/malabar'),
    ('Grant-Valkaria', 'Brevard', 'municipality', 'https://library.municode.com/fl/grant-valkaria'),
    ('Palm Shores', 'Brevard', 'municipality', NULL),
    ('Melbourne Village', 'Brevard', 'municipality', NULL)
ON CONFLICT (name, county) DO NOTHING;
