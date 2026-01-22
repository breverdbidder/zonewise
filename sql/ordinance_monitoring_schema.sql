-- ============================================================
-- ZONEWISE ORDINANCE MONITORING SYSTEM
-- Complete schema to surpass Zoneomics/Gridics
-- Created: 2026-01-21
-- ============================================================

-- 1. ORDINANCES TABLE - Track all municipal ordinances
CREATE TABLE IF NOT EXISTS ordinances (
    id BIGSERIAL PRIMARY KEY,
    jurisdiction_id INTEGER NOT NULL,
    ordinance_number TEXT NOT NULL,          -- "2024-33"
    title TEXT NOT NULL,                     -- "Development Bonus Program"
    chapter TEXT,                            -- "Chapter 173"
    section TEXT,                            -- "§ 173.053"
    passed_date DATE NOT NULL,               -- "2024-09-19"
    effective_date DATE,
    summary TEXT,
    full_text TEXT,                          -- Full ordinance text
    source_url TEXT,
    source_pdf_url TEXT,
    status TEXT DEFAULT 'active',            -- active, amended, repealed
    supersedes_ordinance_id INTEGER,         -- Links to previous version
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(jurisdiction_id, ordinance_number)
);

-- 2. DEVELOPMENT BONUSES TABLE - Incentive zoning programs
CREATE TABLE IF NOT EXISTS development_bonuses (
    id BIGSERIAL PRIMARY KEY,
    jurisdiction_id INTEGER NOT NULL,
    ordinance_id INTEGER REFERENCES ordinances(id),
    program_name TEXT NOT NULL,              -- "Development Bonus Program"
    feature_name TEXT NOT NULL,              -- "Vertical mixed-use"
    
    -- Bonus amounts
    density_bonus TEXT,                      -- "2 additional units per acre"
    intensity_bonus TEXT,                    -- "0.02 additional FAR"
    height_bonus TEXT,                       -- "2 stories"
    parking_reduction TEXT,                  -- "10% reduction"
    other_bonus TEXT,
    
    -- Conditions/Requirements
    conditions TEXT NOT NULL,                -- Full condition text
    min_requirement TEXT,                    -- "Minimum of 5 residential units"
    commitment_period TEXT,                  -- "30 years"
    
    -- Applicability
    applicable_districts TEXT[],             -- Which zoning districts
    
    -- Source tracking
    table_reference TEXT,                    -- "Table 173-8"
    source_url TEXT,
    verified_date DATE,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. OVERLAY DISTRICTS TABLE
CREATE TABLE IF NOT EXISTS overlay_districts (
    id BIGSERIAL PRIMARY KEY,
    jurisdiction_id INTEGER NOT NULL,
    overlay_code TEXT NOT NULL,              -- "WF" for Waterfront
    overlay_name TEXT NOT NULL,              -- "Waterfront Overlay"
    overlay_type TEXT NOT NULL,              -- Historic, Flood, Coastal, Airport, etc.
    
    -- Requirements
    additional_setbacks JSONB,               -- {"front": 10, "waterside": 25}
    additional_restrictions TEXT,
    design_standards TEXT,
    
    -- Bonuses/Incentives
    available_bonuses TEXT[],
    
    -- Boundaries
    geometry GEOMETRY(MultiPolygon, 4326),
    boundary_description TEXT,
    
    -- Source
    ordinance_id INTEGER REFERENCES ordinances(id),
    source_url TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. CONDITIONAL USES TABLE
CREATE TABLE IF NOT EXISTS conditional_uses (
    id BIGSERIAL PRIMARY KEY,
    jurisdiction_id INTEGER NOT NULL,
    district_code TEXT NOT NULL,
    use_name TEXT NOT NULL,                  -- "Accessory Dwelling Unit"
    use_category TEXT,                       -- Residential, Commercial, etc.
    
    -- Approval process
    approval_type TEXT NOT NULL,             -- "Special Exception", "Conditional Use Permit"
    approval_body TEXT,                      -- "Planning Board", "City Council"
    estimated_timeline_days INTEGER,
    
    -- Requirements
    conditions TEXT[],
    standards TEXT,
    
    -- Fees
    application_fee DECIMAL(10,2),
    
    -- Source
    ordinance_section TEXT,
    source_url TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. ORDINANCE CHANGES LOG - Track amendments
CREATE TABLE IF NOT EXISTS ordinance_changes (
    id BIGSERIAL PRIMARY KEY,
    jurisdiction_id INTEGER NOT NULL,
    change_type TEXT NOT NULL,               -- 'new', 'amendment', 'repeal'
    
    old_ordinance_id INTEGER REFERENCES ordinances(id),
    new_ordinance_id INTEGER REFERENCES ordinances(id),
    
    affected_districts TEXT[],
    affected_sections TEXT[],
    
    change_summary TEXT NOT NULL,
    change_date DATE NOT NULL,
    
    -- Impact analysis
    impact_level TEXT,                       -- 'major', 'minor', 'technical'
    notification_sent BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. ENTITLEMENT TIMELINES TABLE (Zoneomics feature we're adding)
CREATE TABLE IF NOT EXISTS entitlement_timelines (
    id BIGSERIAL PRIMARY KEY,
    jurisdiction_id INTEGER NOT NULL,
    process_type TEXT NOT NULL,              -- "Site Plan", "Rezoning", "Variance"
    
    -- Timeline
    typical_days_min INTEGER,
    typical_days_max INTEGER,
    typical_days_avg INTEGER,
    
    -- Steps
    steps JSONB NOT NULL,                    -- [{name, days, fee, notes}]
    
    -- Fees
    base_fee DECIMAL(10,2),
    per_acre_fee DECIMAL(10,2),
    per_unit_fee DECIMAL(10,2),
    
    -- Contact
    department_name TEXT,
    department_phone TEXT,
    department_email TEXT,
    
    -- Source
    last_verified DATE,
    source_url TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. MUNICODE SCRAPE TRACKING
CREATE TABLE IF NOT EXISTS municode_scrape_log (
    id BIGSERIAL PRIMARY KEY,
    jurisdiction_id INTEGER NOT NULL,
    municode_url TEXT NOT NULL,
    
    -- Scrape results
    chapters_scraped TEXT[],
    ordinances_found INTEGER,
    new_ordinances INTEGER,
    amended_ordinances INTEGER,
    
    -- Status
    scrape_status TEXT,                      -- 'success', 'partial', 'failed'
    error_message TEXT,
    
    -- Timestamps
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    next_scheduled TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- INDEXES
CREATE INDEX idx_ordinances_jurisdiction ON ordinances(jurisdiction_id);
CREATE INDEX idx_ordinances_date ON ordinances(passed_date);
CREATE INDEX idx_bonuses_jurisdiction ON development_bonuses(jurisdiction_id);
CREATE INDEX idx_overlays_geometry ON overlay_districts USING GIST(geometry);
CREATE INDEX idx_changes_date ON ordinance_changes(change_date);

-- VIEWS
CREATE OR REPLACE VIEW v_recent_ordinance_changes AS
SELECT 
    oc.*,
    o.title AS ordinance_title,
    j.name AS jurisdiction_name
FROM ordinance_changes oc
JOIN ordinances o ON oc.new_ordinance_id = o.id
JOIN jurisdictions j ON oc.jurisdiction_id = j.id
WHERE oc.change_date >= NOW() - INTERVAL '90 days'
ORDER BY oc.change_date DESC;

-- Sample Palm Bay Development Bonus Data (from Ariel's photos)
-- This would be inserted after schema creation
/*
INSERT INTO development_bonuses (
    jurisdiction_id, program_name, feature_name,
    density_bonus, intensity_bonus, height_bonus, parking_reduction,
    conditions, table_reference
) VALUES
(2, 'Development Bonus Program', 'Vertical mixed-use (residential and commercial or office)',
 NULL, NULL, '2 stories', NULL,
 'Minimum of 5 residential units provided', 'Table 173-8'),
 
(2, 'Development Bonus Program', 'Affordable housing',
 'Max allowed in FLU category', NULL, '2 stories', NULL,
 'A minimum of 25% of total units in development shall be affordable. Developers agreement committing to keeping the units affordable for a minimum of 30 years.', 'Table 173-8'),

(2, 'Development Bonus Program', 'Public Open Space and Amenities',
 '2 additional units per acre for every 3,000 sq. ft. of amenities', '0.02 additional FAR for every 3,000 sq. ft. of amenities', '1 story for every 3,000 sq. ft. of amenities', NULL,
 'Urban plaza or park with amenities, at least three thousand (3,000) square feet in area or multi-use trails connecting to other systems outside the development. The amenities shall be privately-owned and maintained, but open to the public', 'Table 173-8'),

(2, 'Development Bonus Program', 'Parking garage under residential, office or commercial development',
 NULL, NULL, '1 additional floor per garage level provided', NULL,
 'The facade facing the street shall incorporate active uses (residential, commercial or office)', 'Table 173-8'),

(2, 'Development Bonus Program', 'Access to Waterfront (Turkey Creek, Palm Bay, and the Indian River Lagoon)',
 NULL, NULL, '1 additional floor', NULL,
 'One or combination of the following: 1. View of the water from the public right-of-way (in the form of breezeways); 2. Access to the water in the form of boat ramps, fishing piers, or beach; 3. Outdoor dining facing the water.', 'Table 173-8'),

(2, 'Development Bonus Program', 'Low Impact Design',
 '2 additional units per acre', '0.02 additional FAR', NULL, NULL,
 'Designs shall, at a minimum, manage and capture stormwater runoff, to the maximum extent feasible, in a manner consistent with the integrated management practices (IMPs) as outlined in the Citys Low Impact Development Manual.', 'Table 173-8'),

(2, 'Development Bonus Program', 'Emergency storm shelters in mobile home or RV parks',
 '2 additional units per acre', NULL, NULL, NULL,
 'shelters which meet the design and construction requirements established within the latest ICC 500 ICC/NSSA Standard for the Design and Construction of Storm Shelters', 'Table 173-8'),

(2, 'Development Bonus Program', 'Use of living shoreline techniques to prevent shoreline erosion',
 NULL, NULL, NULL, 'Reduced parking (up to 10% of the minimum number of spaces required)',
 'One or more techniques', 'Table 173-8'),

(2, 'Development Bonus Program', 'Co-location of water-dependent and water-related uses',
 NULL, NULL, NULL, 'Reduced parking (up to 10% of the minimum number of spaces required)',
 'Minimum of 2 water-dependent uses; or 1 water-dependent and 1 water-related uses. Uses must be located within the same structure or provide cross access via a shared pedestrian pathway.', 'Table 173-8');
*/
