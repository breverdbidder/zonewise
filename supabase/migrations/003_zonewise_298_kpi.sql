-- ZoneWise 298 KPI Framework - Complete Schema Migration
-- Version: 1.0.0
-- Date: 2026-01-20

-- ============================================
-- CORE TABLES
-- ============================================

-- KPI Definitions (298 total)
CREATE TABLE IF NOT EXISTS kpi_definitions (
    id SERIAL PRIMARY KEY,
    kpi_code VARCHAR(20) UNIQUE NOT NULL,
    kpi_name VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL,
    subcategory VARCHAR(100),
    description TEXT,
    data_source VARCHAR(100),
    calculation_method TEXT,
    weight DECIMAL(5,4) DEFAULT 0.0100,
    is_exclusive BOOLEAN DEFAULT FALSE,
    competitor_coverage JSONB DEFAULT '{"zoneomics": false, "propertyonion": false, "gridics": false}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Property Analysis Results
CREATE TABLE IF NOT EXISTS property_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parcel_id VARCHAR(50) NOT NULL,
    address TEXT NOT NULL,
    jurisdiction_id INTEGER REFERENCES jurisdictions(id),
    analysis_date TIMESTAMPTZ DEFAULT NOW(),
    zonewise_score DECIMAL(5,2),
    recommendation VARCHAR(20) CHECK (recommendation IN ('BID', 'REVIEW', 'SKIP')),
    max_bid DECIMAL(15,2),
    confidence_level DECIMAL(5,2),
    analysis_json JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Individual KPI Scores per Property
CREATE TABLE IF NOT EXISTS property_kpi_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES property_analyses(id) ON DELETE CASCADE,
    kpi_id INTEGER REFERENCES kpi_definitions(id),
    raw_value TEXT,
    normalized_score DECIMAL(5,2),
    weight_applied DECIMAL(5,4),
    weighted_score DECIMAL(8,4),
    data_source VARCHAR(100),
    confidence VARCHAR(20) CHECK (confidence IN ('HIGH', 'MEDIUM', 'LOW', 'ESTIMATED')),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- HBU (Highest & Best Use) Analyses
CREATE TABLE IF NOT EXISTS hbu_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES property_analyses(id) ON DELETE CASCADE,
    current_use VARCHAR(100),
    current_use_value DECIMAL(15,2),
    hbu_recommended VARCHAR(100),
    hbu_potential_value DECIMAL(15,2),
    value_uplift_pct DECIMAL(8,2),
    physically_possible BOOLEAN DEFAULT TRUE,
    legally_permissible BOOLEAN DEFAULT TRUE,
    financially_feasible BOOLEAN DEFAULT TRUE,
    maximally_productive BOOLEAN DEFAULT TRUE,
    rezoning_required BOOLEAN DEFAULT FALSE,
    rezoning_probability DECIMAL(5,2),
    rezoning_timeline_months INTEGER,
    development_scenarios JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- CMA (Comparable Market Analysis)
CREATE TABLE IF NOT EXISTS cma_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES property_analyses(id) ON DELETE CASCADE,
    subject_arv DECIMAL(15,2),
    comp_count INTEGER,
    avg_price_psf DECIMAL(10,2),
    median_dom INTEGER,
    market_trend VARCHAR(20),
    confidence_score DECIMAL(5,2),
    comps_json JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Environmental Risk Assessments
CREATE TABLE IF NOT EXISTS environmental_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES property_analyses(id) ON DELETE CASCADE,
    flood_zone VARCHAR(20),
    flood_risk_score DECIMAL(5,2),
    wetland_present BOOLEAN,
    contamination_risk VARCHAR(20),
    historical_use TEXT,
    phase1_recommended BOOLEAN,
    environmental_score DECIMAL(5,2),
    risk_factors JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ML Predictions
CREATE TABLE IF NOT EXISTS ml_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES property_analyses(id) ON DELETE CASCADE,
    model_version VARCHAR(50),
    predicted_sale_price DECIMAL(15,2),
    prediction_confidence DECIMAL(5,2),
    third_party_probability DECIMAL(5,2),
    days_to_sale_estimate INTEGER,
    feature_importance JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Zoning Compliance Checks
CREATE TABLE IF NOT EXISTS zoning_compliance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES property_analyses(id) ON DELETE CASCADE,
    current_zoning VARCHAR(50),
    zoning_district_id INTEGER REFERENCES zoning_districts(id),
    is_conforming BOOLEAN,
    setback_front_required DECIMAL(8,2),
    setback_front_actual DECIMAL(8,2),
    setback_side_required DECIMAL(8,2),
    setback_side_actual DECIMAL(8,2),
    setback_rear_required DECIMAL(8,2),
    setback_rear_actual DECIMAL(8,2),
    max_height_allowed DECIMAL(8,2),
    lot_coverage_allowed DECIMAL(5,2),
    far_allowed DECIMAL(5,2),
    parking_required INTEGER,
    variances_needed JSONB,
    compliance_score DECIMAL(5,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Data Source Audit Trail
CREATE TABLE IF NOT EXISTS data_source_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES property_analyses(id) ON DELETE CASCADE,
    source_name VARCHAR(100) NOT NULL,
    source_url TEXT,
    query_timestamp TIMESTAMPTZ DEFAULT NOW(),
    response_status INTEGER,
    data_freshness_days INTEGER,
    records_retrieved INTEGER,
    raw_response JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Agent Execution Logs (LangGraph)
CREATE TABLE IF NOT EXISTS agent_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES property_analyses(id) ON DELETE CASCADE,
    agent_name VARCHAR(50) NOT NULL,
    stage_number INTEGER,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    duration_seconds INTEGER,
    tokens_used INTEGER,
    model_used VARCHAR(50),
    input_summary TEXT,
    output_summary TEXT,
    errors JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Competitive Analysis Tracking
CREATE TABLE IF NOT EXISTS competitive_coverage (
    id SERIAL PRIMARY KEY,
    kpi_id INTEGER REFERENCES kpi_definitions(id),
    competitor VARCHAR(50) NOT NULL,
    has_coverage BOOLEAN DEFAULT FALSE,
    coverage_quality VARCHAR(20),
    notes TEXT,
    last_verified TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================
CREATE INDEX IF NOT EXISTS idx_property_analyses_parcel ON property_analyses(parcel_id);
CREATE INDEX IF NOT EXISTS idx_property_analyses_date ON property_analyses(analysis_date DESC);
CREATE INDEX IF NOT EXISTS idx_property_kpi_scores_analysis ON property_kpi_scores(analysis_id);
CREATE INDEX IF NOT EXISTS idx_kpi_definitions_category ON kpi_definitions(category);
CREATE INDEX IF NOT EXISTS idx_kpi_definitions_exclusive ON kpi_definitions(is_exclusive);
CREATE INDEX IF NOT EXISTS idx_agent_logs_analysis ON agent_logs(analysis_id);

-- ============================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================
ALTER TABLE kpi_definitions ENABLE ROW LEVEL SECURITY;
ALTER TABLE property_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE property_kpi_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE hbu_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE cma_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE environmental_assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE ml_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE zoning_compliance ENABLE ROW LEVEL SECURITY;
ALTER TABLE data_source_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitive_coverage ENABLE ROW LEVEL SECURITY;

-- Service role bypass policies
CREATE POLICY "Service role full access kpi_definitions" ON kpi_definitions FOR ALL USING (true);
CREATE POLICY "Service role full access property_analyses" ON property_analyses FOR ALL USING (true);
CREATE POLICY "Service role full access property_kpi_scores" ON property_kpi_scores FOR ALL USING (true);
CREATE POLICY "Service role full access hbu_analyses" ON hbu_analyses FOR ALL USING (true);
CREATE POLICY "Service role full access cma_analyses" ON cma_analyses FOR ALL USING (true);
CREATE POLICY "Service role full access environmental_assessments" ON environmental_assessments FOR ALL USING (true);
CREATE POLICY "Service role full access ml_predictions" ON ml_predictions FOR ALL USING (true);
CREATE POLICY "Service role full access zoning_compliance" ON zoning_compliance FOR ALL USING (true);
CREATE POLICY "Service role full access data_source_logs" ON data_source_logs FOR ALL USING (true);
CREATE POLICY "Service role full access agent_logs" ON agent_logs FOR ALL USING (true);
CREATE POLICY "Service role full access competitive_coverage" ON competitive_coverage FOR ALL USING (true);
-- ZoneWise 298 KPI Definitions Seed Data
-- Categories: Property, Zoning, Market, Financial, Risk, Development, Environmental, Legal, Infrastructure, Demographic

-- ============================================
-- CATEGORY 1: PROPERTY FUNDAMENTALS (30 KPIs)
-- ============================================
INSERT INTO kpi_definitions (kpi_code, kpi_name, category, subcategory, description, data_source, weight, is_exclusive) VALUES
('PROP_001', 'Parcel Size (Acres)', 'Property', 'Physical', 'Total land area in acres', 'BCPAO', 0.0050, false),
('PROP_002', 'Building Square Footage', 'Property', 'Physical', 'Total heated/cooled building area', 'BCPAO', 0.0050, false),
('PROP_003', 'Year Built', 'Property', 'Physical', 'Original construction year', 'BCPAO', 0.0040, false),
('PROP_004', 'Effective Age', 'Property', 'Physical', 'Effective age considering renovations', 'BCPAO', 0.0045, true),
('PROP_005', 'Building Condition Score', 'Property', 'Physical', 'Condition rating 1-10', 'BCPAO', 0.0060, false),
('PROP_006', 'Number of Buildings', 'Property', 'Physical', 'Count of structures on parcel', 'BCPAO', 0.0030, false),
('PROP_007', 'Stories Count', 'Property', 'Physical', 'Number of floors', 'BCPAO', 0.0025, false),
('PROP_008', 'Unit Count', 'Property', 'Physical', 'Number of residential/commercial units', 'BCPAO', 0.0040, false),
('PROP_009', 'Parking Spaces', 'Property', 'Physical', 'Total parking capacity', 'BCPAO', 0.0035, false),
('PROP_010', 'Lot Coverage Actual', 'Property', 'Physical', 'Current building footprint percentage', 'BCPAO', 0.0040, true),
('PROP_011', 'FAR Actual', 'Property', 'Physical', 'Current floor area ratio', 'BCPAO', 0.0045, true),
('PROP_012', 'Frontage (Linear Feet)', 'Property', 'Physical', 'Street frontage length', 'BCPAO', 0.0035, true),
('PROP_013', 'Depth (Linear Feet)', 'Property', 'Physical', 'Lot depth measurement', 'BCPAO', 0.0025, true),
('PROP_014', 'Corner Lot Status', 'Property', 'Physical', 'Boolean corner lot indicator', 'BCPAO', 0.0030, false),
('PROP_015', 'Waterfront Status', 'Property', 'Physical', 'Water access type if any', 'BCPAO', 0.0045, false),
('PROP_016', 'Pool Present', 'Property', 'Amenities', 'Swimming pool indicator', 'BCPAO', 0.0020, false),
('PROP_017', 'Garage Type', 'Property', 'Amenities', 'Attached/detached/carport/none', 'BCPAO', 0.0025, false),
('PROP_018', 'HVAC Type', 'Property', 'Systems', 'Central air, heat pump, etc.', 'BCPAO', 0.0030, false),
('PROP_019', 'Roof Type', 'Property', 'Systems', 'Shingle, tile, metal, flat', 'BCPAO', 0.0035, false),
('PROP_020', 'Foundation Type', 'Property', 'Systems', 'Slab, crawl, basement', 'BCPAO', 0.0030, false),
('PROP_021', 'Construction Class', 'Property', 'Physical', 'A/B/C/D construction quality', 'BCPAO', 0.0040, false),
('PROP_022', 'Renovation History', 'Property', 'History', 'Documented improvements since built', 'BCPAO', 0.0035, true),
('PROP_023', 'Permit History Count', 'Property', 'History', 'Number of building permits pulled', 'BCPAO', 0.0030, true),
('PROP_024', 'Last Sale Date', 'Property', 'History', 'Most recent arms-length sale', 'BCPAO', 0.0025, false),
('PROP_025', 'Last Sale Price', 'Property', 'History', 'Most recent sale amount', 'BCPAO', 0.0040, false),
('PROP_026', 'Price Per SF History', 'Property', 'History', 'Historical $/SF trend', 'BCPAO', 0.0045, true),
('PROP_027', 'Days Since Last Sale', 'Property', 'History', 'Time since last transaction', 'BCPAO', 0.0020, false),
('PROP_028', 'Owner Occupied Status', 'Property', 'Ownership', 'Homestead exemption indicator', 'BCPAO', 0.0030, false),
('PROP_029', 'Corporate Ownership', 'Property', 'Ownership', 'LLC/Corp vs individual owner', 'BCPAO', 0.0025, true),
('PROP_030', 'Multi-Parcel Assembly', 'Property', 'Ownership', 'Same owner adjacent parcels', 'BCPAO', 0.0050, true);

-- ============================================
-- CATEGORY 2: ZONING & LAND USE (45 KPIs)
-- ============================================
INSERT INTO kpi_definitions (kpi_code, kpi_name, category, subcategory, description, data_source, weight, is_exclusive) VALUES
('ZONE_001', 'Current Zoning Code', 'Zoning', 'Classification', 'Official zoning designation', 'Municipal', 0.0060, false),
('ZONE_002', 'Future Land Use', 'Zoning', 'Classification', 'Comprehensive plan designation', 'Municipal', 0.0055, false),
('ZONE_003', 'Zoning District Area', 'Zoning', 'Classification', 'Total acres in same zoning district', 'Municipal', 0.0035, true),
('ZONE_004', 'Max Density Allowed', 'Zoning', 'Dimensional', 'Units per acre permitted', 'Municipal', 0.0060, false),
('ZONE_005', 'Current Density Utilized', 'Zoning', 'Dimensional', 'Actual units per acre', 'Municipal', 0.0050, true),
('ZONE_006', 'Density Upside Potential', 'Zoning', 'Dimensional', 'Additional units possible', 'Municipal', 0.0065, true),
('ZONE_007', 'Max Building Height', 'Zoning', 'Dimensional', 'Height limit in feet', 'Municipal', 0.0045, false),
('ZONE_008', 'Max FAR Allowed', 'Zoning', 'Dimensional', 'Floor area ratio limit', 'Municipal', 0.0050, false),
('ZONE_009', 'FAR Upside Potential', 'Zoning', 'Dimensional', 'Additional buildable SF', 'Municipal', 0.0060, true),
('ZONE_010', 'Max Lot Coverage', 'Zoning', 'Dimensional', 'Building footprint limit %', 'Municipal', 0.0040, false),
('ZONE_011', 'Setback Front Required', 'Zoning', 'Dimensional', 'Front yard minimum', 'Municipal', 0.0030, false),
('ZONE_012', 'Setback Side Required', 'Zoning', 'Dimensional', 'Side yard minimum', 'Municipal', 0.0030, false),
('ZONE_013', 'Setback Rear Required', 'Zoning', 'Dimensional', 'Rear yard minimum', 'Municipal', 0.0030, false),
('ZONE_014', 'Setback Compliance Status', 'Zoning', 'Compliance', 'All setbacks met boolean', 'Municipal', 0.0045, true),
('ZONE_015', 'Parking Ratio Required', 'Zoning', 'Dimensional', 'Spaces per unit/1000SF', 'Municipal', 0.0035, false),
('ZONE_016', 'Parking Compliance Status', 'Zoning', 'Compliance', 'Parking requirements met', 'Municipal', 0.0040, true),
('ZONE_017', 'Open Space Required %', 'Zoning', 'Dimensional', 'Minimum open/green space', 'Municipal', 0.0030, false),
('ZONE_018', 'Permitted Uses List', 'Zoning', 'Uses', 'By-right allowed uses', 'Municipal', 0.0055, false),
('ZONE_019', 'Conditional Uses List', 'Zoning', 'Uses', 'Special exception uses', 'Municipal', 0.0045, false),
('ZONE_020', 'Prohibited Uses List', 'Zoning', 'Uses', 'Explicitly banned uses', 'Municipal', 0.0040, true),
('ZONE_021', 'Current Use Conformity', 'Zoning', 'Compliance', 'Legal conforming/non-conforming', 'Municipal', 0.0060, false),
('ZONE_022', 'Non-Conforming Rights', 'Zoning', 'Compliance', 'Grandfathered use protections', 'Municipal', 0.0050, true),
('ZONE_023', 'Variance History', 'Zoning', 'History', 'Previously granted variances', 'Municipal', 0.0045, true),
('ZONE_024', 'Rezoning History', 'Zoning', 'History', 'Past zoning changes', 'Municipal', 0.0040, true),
('ZONE_025', 'Rezoning Probability', 'Zoning', 'Potential', 'Likelihood of approval 0-100%', 'ZoneWise ML', 0.0070, true),
('ZONE_026', 'Rezoning Timeline Est.', 'Zoning', 'Potential', 'Expected months to approval', 'ZoneWise ML', 0.0055, true),
('ZONE_027', 'Rezoning Cost Estimate', 'Zoning', 'Potential', 'Application and legal fees', 'ZoneWise ML', 0.0045, true),
('ZONE_028', 'Overlay District Status', 'Zoning', 'Overlays', 'Special overlay zones', 'Municipal', 0.0050, false),
('ZONE_029', 'Historic District Status', 'Zoning', 'Overlays', 'Historic preservation overlay', 'Municipal', 0.0055, false),
('ZONE_030', 'CRA District Status', 'Zoning', 'Overlays', 'Community Redevelopment Area', 'Municipal', 0.0060, true),
('ZONE_031', 'TIF District Status', 'Zoning', 'Overlays', 'Tax Increment Financing zone', 'Municipal', 0.0055, true),
('ZONE_032', 'Opportunity Zone Status', 'Zoning', 'Overlays', 'Federal OZ designation', 'Census', 0.0065, false),
('ZONE_033', 'Enterprise Zone Status', 'Zoning', 'Overlays', 'State enterprise zone', 'State', 0.0050, true),
('ZONE_034', 'Airport Noise Zone', 'Zoning', 'Overlays', 'Aviation noise contour', 'FAA', 0.0040, false),
('ZONE_035', 'Coastal High Hazard', 'Zoning', 'Overlays', 'CHHA coastal zone', 'FEMA', 0.0055, false),
('ZONE_036', 'Adjacent Zoning North', 'Zoning', 'Context', 'Neighboring parcel zoning', 'Municipal', 0.0025, true),
('ZONE_037', 'Adjacent Zoning South', 'Zoning', 'Context', 'Neighboring parcel zoning', 'Municipal', 0.0025, true),
('ZONE_038', 'Adjacent Zoning East', 'Zoning', 'Context', 'Neighboring parcel zoning', 'Municipal', 0.0025, true),
('ZONE_039', 'Adjacent Zoning West', 'Zoning', 'Context', 'Neighboring parcel zoning', 'Municipal', 0.0025, true),
('ZONE_040', 'Transition Zone Buffer', 'Zoning', 'Context', 'Between incompatible uses', 'Municipal', 0.0035, true),
('ZONE_041', 'Upzoning Trend Score', 'Zoning', 'Trends', 'Area densification pattern', 'ZoneWise ML', 0.0055, true),
('ZONE_042', 'Downzoning Risk Score', 'Zoning', 'Trends', 'Preservation pressure risk', 'ZoneWise ML', 0.0050, true),
('ZONE_043', 'Form-Based Code Status', 'Zoning', 'Classification', 'Modern zoning type indicator', 'Municipal', 0.0035, true),
('ZONE_044', 'Mixed-Use Eligibility', 'Zoning', 'Uses', 'Residential + commercial combo', 'Municipal', 0.0060, false),
('ZONE_045', 'ADU Permissibility', 'Zoning', 'Uses', 'Accessory dwelling unit allowed', 'Municipal', 0.0050, true);

-- ============================================
-- CATEGORY 3: MARKET & VALUATION (50 KPIs)
-- ============================================
INSERT INTO kpi_definitions (kpi_code, kpi_name, category, subcategory, description, data_source, weight, is_exclusive) VALUES
('MKT_001', 'Assessed Value Total', 'Market', 'Valuation', 'County tax assessed value', 'BCPAO', 0.0045, false),
('MKT_002', 'Assessed Value Land', 'Market', 'Valuation', 'Land-only assessed value', 'BCPAO', 0.0040, false),
('MKT_003', 'Assessed Value Building', 'Market', 'Valuation', 'Improvement assessed value', 'BCPAO', 0.0040, false),
('MKT_004', 'Market Value Estimate', 'Market', 'Valuation', 'ZoneWise AVM estimate', 'ZoneWise ML', 0.0060, true),
('MKT_005', 'ARV Estimate', 'Market', 'Valuation', 'After repair value', 'ZoneWise ML', 0.0065, true),
('MKT_006', 'Price Per SF Current', 'Market', 'Valuation', 'Current $/SF market rate', 'MLS', 0.0050, false),
('MKT_007', 'Price Per SF Submarket', 'Market', 'Valuation', 'Submarket average $/SF', 'MLS', 0.0045, false),
('MKT_008', 'Price Per Unit', 'Market', 'Valuation', 'Multi-family $/unit metric', 'MLS', 0.0050, false),
('MKT_009', 'Cap Rate Current', 'Market', 'Investment', 'NOI / Value ratio', 'ZoneWise ML', 0.0055, true),
('MKT_010', 'Cap Rate Submarket', 'Market', 'Investment', 'Submarket average cap rate', 'MLS', 0.0045, false),
('MKT_011', 'GRM Estimate', 'Market', 'Investment', 'Gross rent multiplier', 'ZoneWise ML', 0.0040, true),
('MKT_012', 'Cash on Cash Potential', 'Market', 'Investment', 'Annual return on equity', 'ZoneWise ML', 0.0055, true),
('MKT_013', 'IRR 5-Year Projection', 'Market', 'Investment', 'Internal rate of return', 'ZoneWise ML', 0.0050, true),
('MKT_014', 'Equity Multiple Projection', 'Market', 'Investment', 'Total return multiple', 'ZoneWise ML', 0.0045, true),
('MKT_015', 'Comparable Sales Count', 'Market', 'CMA', 'Number of valid comps', 'MLS', 0.0040, false),
('MKT_016', 'Comparable Avg Price', 'Market', 'CMA', 'Mean comp sale price', 'MLS', 0.0050, false),
('MKT_017', 'Comparable Median Price', 'Market', 'CMA', 'Median comp sale price', 'MLS', 0.0055, false),
('MKT_018', 'Comparable Avg DOM', 'Market', 'CMA', 'Average days on market', 'MLS', 0.0045, false),
('MKT_019', 'Comparable Price Range', 'Market', 'CMA', 'High-low price spread', 'MLS', 0.0035, false),
('MKT_020', 'Comparable Distance Avg', 'Market', 'CMA', 'Average comp distance miles', 'MLS', 0.0030, true),
('MKT_021', 'Absorption Rate Local', 'Market', 'Trends', 'Months of inventory', 'MLS', 0.0055, false),
('MKT_022', 'Absorption Rate Trend', 'Market', 'Trends', '6-month trend direction', 'MLS', 0.0045, true),
('MKT_023', 'Price Trend 12-Month', 'Market', 'Trends', 'YoY price change %', 'MLS', 0.0055, false),
('MKT_024', 'Price Trend 3-Month', 'Market', 'Trends', 'QoQ price change %', 'MLS', 0.0050, false),
('MKT_025', 'Volume Trend 12-Month', 'Market', 'Trends', 'YoY transaction change %', 'MLS', 0.0040, false),
('MKT_026', 'List to Sale Ratio', 'Market', 'Trends', 'Avg sale/list price %', 'MLS', 0.0045, false),
('MKT_027', 'New Construction Comp', 'Market', 'Competition', 'New build inventory nearby', 'MLS', 0.0040, true),
('MKT_028', 'Distressed Sale Comp %', 'Market', 'Competition', 'REO/Short sale ratio', 'MLS', 0.0050, true),
('MKT_029', 'Investor Activity Index', 'Market', 'Competition', 'Cash/LLC buyer ratio', 'BCPAO', 0.0055, true),
('MKT_030', 'Rental Rate Estimate', 'Market', 'Income', 'Monthly rent projection', 'Rentometer', 0.0050, false),
('MKT_031', 'Rental Yield Estimate', 'Market', 'Income', 'Annual rent / value %', 'ZoneWise ML', 0.0055, true),
('MKT_032', 'Vacancy Rate Local', 'Market', 'Income', 'Submarket vacancy %', 'Census', 0.0045, false),
('MKT_033', 'Rent Growth 12-Month', 'Market', 'Income', 'YoY rent change %', 'Rentometer', 0.0040, false),
('MKT_034', 'NOI Estimate', 'Market', 'Income', 'Net operating income', 'ZoneWise ML', 0.0050, true),
('MKT_035', 'Expense Ratio Estimate', 'Market', 'Income', 'OpEx / Revenue %', 'ZoneWise ML', 0.0040, true),
('MKT_036', 'Repair Cost Estimate', 'Market', 'Costs', 'Estimated rehab cost', 'ZoneWise ML', 0.0060, true),
('MKT_037', 'Repair Cost Per SF', 'Market', 'Costs', 'Rehab $/SF estimate', 'ZoneWise ML', 0.0045, true),
('MKT_038', 'Holding Cost Monthly', 'Market', 'Costs', 'Monthly carry cost', 'ZoneWise ML', 0.0040, true),
('MKT_039', 'Transaction Cost Est', 'Market', 'Costs', 'Buy/sell costs estimate', 'ZoneWise ML', 0.0035, true),
('MKT_040', 'Development Cost Est', 'Market', 'Costs', 'New construction $/SF', 'Marshall&Swift', 0.0050, false),
('MKT_041', 'Land Value Residual', 'Market', 'Development', 'Land value via residual method', 'ZoneWise ML', 0.0055, true),
('MKT_042', 'Development Profit Margin', 'Market', 'Development', 'Expected dev profit %', 'ZoneWise ML', 0.0050, true),
('MKT_043', 'Highest Price Achieved', 'Market', 'Context', 'Area record sale price', 'MLS', 0.0030, true),
('MKT_044', 'Price Ceiling Estimate', 'Market', 'Context', 'Max achievable price', 'ZoneWise ML', 0.0045, true),
('MKT_045', 'Price Floor Estimate', 'Market', 'Context', 'Minimum liquidation value', 'ZoneWise ML', 0.0050, true),
('MKT_046', 'Institutional Interest', 'Market', 'Demand', 'Large investor activity', 'BCPAO', 0.0045, true),
('MKT_047', 'Days to Sale Estimate', 'Market', 'Liquidity', 'Expected time to sell', 'ZoneWise ML', 0.0040, true),
('MKT_048', 'Liquidity Score', 'Market', 'Liquidity', 'Ease of sale rating 1-100', 'ZoneWise ML', 0.0055, true),
('MKT_049', 'Marketability Score', 'Market', 'Liquidity', 'Buyer appeal rating 1-100', 'ZoneWise ML', 0.0050, true),
('MKT_050', 'Value Confidence Score', 'Market', 'Quality', 'Valuation certainty 1-100', 'ZoneWise ML', 0.0045, true);

-- ============================================
-- CATEGORY 4: FINANCIAL & AUCTION (35 KPIs)
-- ============================================
INSERT INTO kpi_definitions (kpi_code, kpi_name, category, subcategory, description, data_source, weight, is_exclusive) VALUES
('FIN_001', 'Judgment Amount', 'Financial', 'Foreclosure', 'Total foreclosure judgment', 'Clerk', 0.0065, false),
('FIN_002', 'Opening Bid Amount', 'Financial', 'Foreclosure', 'Auction starting bid', 'RealForeclose', 0.0060, false),
('FIN_003', 'Bid to Judgment Ratio', 'Financial', 'Foreclosure', 'Opening bid / judgment %', 'Calculated', 0.0070, true),
('FIN_004', 'Max Bid Recommended', 'Financial', 'Foreclosure', 'ZoneWise max bid calc', 'ZoneWise ML', 0.0075, true),
('FIN_005', 'Equity Cushion Estimate', 'Financial', 'Foreclosure', 'ARV - judgment - repairs', 'ZoneWise ML', 0.0070, true),
('FIN_006', 'ROI at Max Bid', 'Financial', 'Foreclosure', 'Return if bought at max', 'ZoneWise ML', 0.0065, true),
('FIN_007', 'Plaintiff Type', 'Financial', 'Foreclosure', 'Bank/servicer/HOA/tax', 'Clerk', 0.0055, false),
('FIN_008', 'Plaintiff Track Record', 'Financial', 'Foreclosure', 'Historical bidding pattern', 'ZoneWise ML', 0.0060, true),
('FIN_009', 'Third Party Win Prob', 'Financial', 'Foreclosure', 'ML predicted 3P probability', 'ZoneWise ML', 0.0070, true),
('FIN_010', 'Certificate Holder Type', 'Financial', 'Foreclosure', 'Who holds certificates', 'Clerk', 0.0045, true),
('FIN_011', 'Auction Postponement Count', 'Financial', 'Foreclosure', 'Number of delays', 'RealForeclose', 0.0050, true),
('FIN_012', 'Days Since Filing', 'Financial', 'Foreclosure', 'Age of foreclosure case', 'Clerk', 0.0040, false),
('FIN_013', 'Senior Lien Total', 'Financial', 'Liens', 'Sum of priority liens', 'AcclaimWeb', 0.0065, true),
('FIN_014', 'Junior Lien Total', 'Financial', 'Liens', 'Sum of subordinate liens', 'AcclaimWeb', 0.0055, true),
('FIN_015', 'Mortgage 1st Position', 'Financial', 'Liens', 'Primary mortgage balance', 'AcclaimWeb', 0.0060, false),
('FIN_016', 'Mortgage 2nd Position', 'Financial', 'Liens', 'Second mortgage balance', 'AcclaimWeb', 0.0050, false),
('FIN_017', 'HOA Lien Amount', 'Financial', 'Liens', 'Homeowner assoc liens', 'AcclaimWeb', 0.0055, true),
('FIN_018', 'HOA Super Lien Amount', 'Financial', 'Liens', 'HOA super priority portion', 'AcclaimWeb', 0.0060, true),
('FIN_019', 'Tax Certificate Amount', 'Financial', 'Liens', 'Outstanding tax certs', 'RealTDM', 0.0055, true),
('FIN_020', 'Tax Certificate Years', 'Financial', 'Liens', 'Years of delinquent taxes', 'RealTDM', 0.0045, true),
('FIN_021', 'Code Enforcement Liens', 'Financial', 'Liens', 'Municipal violation liens', 'Municipal', 0.0050, true),
('FIN_022', 'Mechanics Liens', 'Financial', 'Liens', 'Construction/contractor liens', 'AcclaimWeb', 0.0045, true),
('FIN_023', 'IRS/State Tax Liens', 'Financial', 'Liens', 'Federal/state tax liens', 'AcclaimWeb', 0.0055, true),
('FIN_024', 'Judgment Liens Other', 'Financial', 'Liens', 'Other civil judgments', 'AcclaimWeb', 0.0045, true),
('FIN_025', 'Lien Priority Analysis', 'Financial', 'Liens', 'What survives foreclosure', 'ZoneWise ML', 0.0070, true),
('FIN_026', 'Property Tax Annual', 'Financial', 'Taxes', 'Annual property tax amount', 'BCPAO', 0.0040, false),
('FIN_027', 'Tax Rate Millage', 'Financial', 'Taxes', 'Combined millage rate', 'BCPAO', 0.0035, false),
('FIN_028', 'Tax Delinquent Status', 'Financial', 'Taxes', 'Current on taxes boolean', 'Tax Collector', 0.0050, false),
('FIN_029', 'Homestead Exemption', 'Financial', 'Taxes', 'Exemption amount', 'BCPAO', 0.0030, false),
('FIN_030', 'Other Exemptions', 'Financial', 'Taxes', 'Senior/veteran/disability', 'BCPAO', 0.0025, false),
('FIN_031', 'Insurance Cost Est', 'Financial', 'Costs', 'Annual insurance estimate', 'ZoneWise ML', 0.0040, true),
('FIN_032', 'Flood Insurance Req', 'Financial', 'Costs', 'Mandatory flood insurance', 'FEMA', 0.0050, false),
('FIN_033', 'Wind Insurance Cost', 'Financial', 'Costs', 'Hurricane coverage est', 'ZoneWise ML', 0.0045, true),
('FIN_034', 'Utility Cost Monthly', 'Financial', 'Costs', 'Estimated utility cost', 'ZoneWise ML', 0.0030, true),
('FIN_035', 'Total Carry Cost Monthly', 'Financial', 'Costs', 'All holding costs combined', 'ZoneWise ML', 0.0050, true);
-- ============================================
-- CATEGORY 5: RISK ASSESSMENT (40 KPIs)
-- ============================================
INSERT INTO kpi_definitions (kpi_code, kpi_name, category, subcategory, description, data_source, weight, is_exclusive) VALUES
('RISK_001', 'Flood Zone Category', 'Risk', 'Environmental', 'FEMA flood zone designation', 'FEMA', 0.0060, false),
('RISK_002', 'Flood Risk Score', 'Risk', 'Environmental', 'Combined flood risk 1-100', 'ZoneWise ML', 0.0065, true),
('RISK_003', 'Base Flood Elevation', 'Risk', 'Environmental', 'BFE if in flood zone', 'FEMA', 0.0040, false),
('RISK_004', 'Building Elevation', 'Risk', 'Environmental', 'Actual structure elevation', 'Survey', 0.0035, true),
('RISK_005', 'Flood Claims History', 'Risk', 'Environmental', 'NFIP claims on property', 'FEMA', 0.0055, true),
('RISK_006', 'Hurricane Risk Score', 'Risk', 'Environmental', 'Wind damage probability', 'ZoneWise ML', 0.0060, true),
('RISK_007', 'Sinkhole Risk Score', 'Risk', 'Environmental', 'Karst geology risk', 'FL Geological', 0.0050, true),
('RISK_008', 'Coastal Erosion Risk', 'Risk', 'Environmental', 'Shoreline retreat rate', 'FDEP', 0.0045, true),
('RISK_009', 'Sea Level Rise Impact', 'Risk', 'Environmental', '2050 projection impact', 'NOAA', 0.0050, true),
('RISK_010', 'Wildfire Risk Score', 'Risk', 'Environmental', 'Fire hazard severity', 'FL Forest Service', 0.0040, true),
('RISK_011', 'Wetland Presence', 'Risk', 'Environmental', 'Jurisdictional wetlands', 'SJRWMD', 0.0055, false),
('RISK_012', 'Wetland Acreage', 'Risk', 'Environmental', 'Wetland area on parcel', 'SJRWMD', 0.0045, true),
('RISK_013', 'Wetland Buffer Impact', 'Risk', 'Environmental', 'Upland buffer requirements', 'SJRWMD', 0.0050, true),
('RISK_014', 'Contamination Risk', 'Risk', 'Environmental', 'Brownfield/EPA site risk', 'EPA', 0.0060, false),
('RISK_015', 'Historical Use Risk', 'Risk', 'Environmental', 'Past use contamination', 'ZoneWise ML', 0.0055, true),
('RISK_016', 'Underground Tank Risk', 'Risk', 'Environmental', 'UST registry check', 'FDEP', 0.0045, true),
('RISK_017', 'Asbestos Risk Score', 'Risk', 'Environmental', 'Building age-based risk', 'ZoneWise ML', 0.0040, true),
('RISK_018', 'Lead Paint Risk Score', 'Risk', 'Environmental', 'Pre-1978 building risk', 'ZoneWise ML', 0.0040, true),
('RISK_019', 'Phase 1 Recommended', 'Risk', 'Environmental', 'ESA recommendation', 'ZoneWise ML', 0.0050, true),
('RISK_020', 'Environmental Score', 'Risk', 'Environmental', 'Combined env risk 1-100', 'ZoneWise ML', 0.0065, true),
('RISK_021', 'Title Clear Probability', 'Risk', 'Legal', 'Clean title likelihood', 'ZoneWise ML', 0.0060, true),
('RISK_022', 'Title Issue Types', 'Risk', 'Legal', 'Identified title problems', 'AcclaimWeb', 0.0055, true),
('RISK_023', 'Lien Priority Clear', 'Risk', 'Legal', 'Priority analysis clean', 'ZoneWise ML', 0.0065, true),
('RISK_024', 'Foreclosure Defense Risk', 'Risk', 'Legal', 'Contested case probability', 'ZoneWise ML', 0.0050, true),
('RISK_025', 'Bankruptcy Risk', 'Risk', 'Legal', 'Owner bankruptcy check', 'PACER', 0.0055, true),
('RISK_026', 'Probate Complication', 'Risk', 'Legal', 'Estate/heir issues', 'Clerk', 0.0045, true),
('RISK_027', 'HOA Litigation Risk', 'Risk', 'Legal', 'HOA legal disputes', 'HOA Records', 0.0040, true),
('RISK_028', 'Code Violation Count', 'Risk', 'Legal', 'Active code violations', 'Municipal', 0.0055, false),
('RISK_029', 'Demolition Order Risk', 'Risk', 'Legal', 'Condemned/demo status', 'Municipal', 0.0060, true),
('RISK_030', 'Legal Risk Score', 'Risk', 'Legal', 'Combined legal risk 1-100', 'ZoneWise ML', 0.0060, true),
('RISK_031', 'Market Cycle Position', 'Risk', 'Market', 'Current cycle phase', 'ZoneWise ML', 0.0050, true),
('RISK_032', 'Price Volatility Index', 'Risk', 'Market', 'Historical price variance', 'ZoneWise ML', 0.0045, true),
('RISK_033', 'Demand Decline Risk', 'Risk', 'Market', 'Buyer pool shrinkage', 'ZoneWise ML', 0.0050, true),
('RISK_034', 'Supply Surge Risk', 'Risk', 'Market', 'Inventory increase risk', 'ZoneWise ML', 0.0045, true),
('RISK_035', 'Interest Rate Sensitivity', 'Risk', 'Market', 'Rate change impact', 'ZoneWise ML', 0.0040, true),
('RISK_036', 'Economic Shock Risk', 'Risk', 'Market', 'Macro downturn exposure', 'ZoneWise ML', 0.0050, true),
('RISK_037', 'Execution Risk Score', 'Risk', 'Execution', 'Project completion risk', 'ZoneWise ML', 0.0045, true),
('RISK_038', 'Contractor Availability', 'Risk', 'Execution', 'Local labor availability', 'ZoneWise ML', 0.0035, true),
('RISK_039', 'Permit Timeline Risk', 'Risk', 'Execution', 'Approval delay risk', 'ZoneWise ML', 0.0040, true),
('RISK_040', 'Overall Risk Score', 'Risk', 'Summary', 'Aggregate risk 1-100', 'ZoneWise ML', 0.0070, true);

-- ============================================
-- CATEGORY 6: DEVELOPMENT POTENTIAL (30 KPIs)
-- ============================================
INSERT INTO kpi_definitions (kpi_code, kpi_name, category, subcategory, description, data_source, weight, is_exclusive) VALUES
('DEV_001', 'Developable Acreage', 'Development', 'Land', 'Buildable land after setbacks', 'Calculated', 0.0055, true),
('DEV_002', 'Max Buildable SF', 'Development', 'Land', 'Maximum allowed building SF', 'Calculated', 0.0060, true),
('DEV_003', 'Max Unit Count', 'Development', 'Land', 'Maximum residential units', 'Calculated', 0.0060, true),
('DEV_004', 'Highest Best Use Current', 'Development', 'HBU', 'Current HBU determination', 'ZoneWise ML', 0.0055, true),
('DEV_005', 'HBU Alternative 1', 'Development', 'HBU', 'Best alternative use', 'ZoneWise ML', 0.0050, true),
('DEV_006', 'HBU Alternative 2', 'Development', 'HBU', 'Second alternative use', 'ZoneWise ML', 0.0045, true),
('DEV_007', 'HBU Value Uplift', 'Development', 'HBU', 'Value gain from HBU change', 'ZoneWise ML', 0.0065, true),
('DEV_008', 'Subdivision Potential', 'Development', 'Land', 'Lot split feasibility', 'Municipal', 0.0055, true),
('DEV_009', 'Assemblage Opportunity', 'Development', 'Land', 'Adjacent parcel combination', 'BCPAO', 0.0050, true),
('DEV_010', 'Infill Status', 'Development', 'Land', 'Infill vs greenfield', 'ZoneWise ML', 0.0040, true),
('DEV_011', 'Teardown Candidate', 'Development', 'Rehab', 'Demolish vs renovate', 'ZoneWise ML', 0.0055, true),
('DEV_012', 'Renovation ROI Score', 'Development', 'Rehab', 'Rehab return potential', 'ZoneWise ML', 0.0060, true),
('DEV_013', 'Addition Potential SF', 'Development', 'Rehab', 'Expansion opportunity', 'Calculated', 0.0045, true),
('DEV_014', 'Conversion Potential', 'Development', 'Rehab', 'Use conversion feasibility', 'ZoneWise ML', 0.0050, true),
('DEV_015', 'Ground-Up Dev Profit', 'Development', 'New Build', 'New construction margin', 'ZoneWise ML', 0.0055, true),
('DEV_016', 'Entitlement Complexity', 'Development', 'Approvals', 'Approval difficulty 1-10', 'ZoneWise ML', 0.0050, true),
('DEV_017', 'Impact Fee Estimate', 'Development', 'Costs', 'Total impact fees', 'Municipal', 0.0045, false),
('DEV_018', 'Utility Connection Cost', 'Development', 'Costs', 'Water/sewer tap fees', 'Utility', 0.0040, false),
('DEV_019', 'Site Work Cost Est', 'Development', 'Costs', 'Grading/clearing costs', 'ZoneWise ML', 0.0045, true),
('DEV_020', 'Stormwater Mgmt Cost', 'Development', 'Costs', 'Retention/drainage cost', 'ZoneWise ML', 0.0040, true),
('DEV_021', 'Concurrency Available', 'Development', 'Approvals', 'Adequate public facilities', 'Municipal', 0.0055, true),
('DEV_022', 'Traffic Study Required', 'Development', 'Approvals', 'TIS requirement trigger', 'Municipal', 0.0040, true),
('DEV_023', 'DRI Threshold', 'Development', 'Approvals', 'Development of Regional Impact', 'State', 0.0045, true),
('DEV_024', 'Environmental Permit Req', 'Development', 'Approvals', 'SJRWMD/ACOE permits', 'SJRWMD', 0.0050, true),
('DEV_025', 'Affordable Housing Req', 'Development', 'Approvals', 'Inclusionary zoning', 'Municipal', 0.0040, true),
('DEV_026', 'Community Benefit Req', 'Development', 'Approvals', 'Public contribution needs', 'Municipal', 0.0035, true),
('DEV_027', 'Developer Experience Fit', 'Development', 'Execution', 'Match to project type', 'ZoneWise ML', 0.0040, true),
('DEV_028', 'Timeline to Completion', 'Development', 'Execution', 'Months to stabilization', 'ZoneWise ML', 0.0045, true),
('DEV_029', 'Development Risk Score', 'Development', 'Summary', 'Overall dev risk 1-100', 'ZoneWise ML', 0.0055, true),
('DEV_030', 'Development Score', 'Development', 'Summary', 'Dev potential 1-100', 'ZoneWise ML', 0.0065, true);

-- ============================================
-- CATEGORY 7: INFRASTRUCTURE (25 KPIs)
-- ============================================
INSERT INTO kpi_definitions (kpi_code, kpi_name, category, subcategory, description, data_source, weight, is_exclusive) VALUES
('INFRA_001', 'Water Service Available', 'Infrastructure', 'Utilities', 'Municipal water access', 'Utility', 0.0045, false),
('INFRA_002', 'Sewer Service Available', 'Infrastructure', 'Utilities', 'Municipal sewer access', 'Utility', 0.0050, false),
('INFRA_003', 'Septic System Status', 'Infrastructure', 'Utilities', 'Septic present/condition', 'Health Dept', 0.0040, false),
('INFRA_004', 'Electric Service Capacity', 'Infrastructure', 'Utilities', 'Power capacity available', 'FPL', 0.0035, false),
('INFRA_005', 'Natural Gas Available', 'Infrastructure', 'Utilities', 'Gas line access', 'Gas Utility', 0.0025, false),
('INFRA_006', 'Fiber Internet Available', 'Infrastructure', 'Utilities', 'High-speed fiber access', 'ISP', 0.0030, false),
('INFRA_007', 'Road Access Type', 'Infrastructure', 'Transportation', 'Public/private road', 'Municipal', 0.0040, false),
('INFRA_008', 'Road Condition Score', 'Infrastructure', 'Transportation', 'Pavement quality 1-10', 'Municipal', 0.0030, true),
('INFRA_009', 'Traffic Count Daily', 'Infrastructure', 'Transportation', 'Average daily traffic', 'FDOT', 0.0035, false),
('INFRA_010', 'Highway Access Distance', 'Infrastructure', 'Transportation', 'Miles to major highway', 'Calculated', 0.0040, false),
('INFRA_011', 'Public Transit Access', 'Infrastructure', 'Transportation', 'Bus/rail proximity', 'Transit Agency', 0.0035, false),
('INFRA_012', 'Airport Distance', 'Infrastructure', 'Transportation', 'Miles to major airport', 'Calculated', 0.0030, false),
('INFRA_013', 'Port Distance', 'Infrastructure', 'Transportation', 'Miles to seaport', 'Calculated', 0.0025, true),
('INFRA_014', 'Walk Score', 'Infrastructure', 'Accessibility', 'Walkability index', 'Walk Score', 0.0040, false),
('INFRA_015', 'Bike Score', 'Infrastructure', 'Accessibility', 'Bikeability index', 'Walk Score', 0.0030, false),
('INFRA_016', 'Transit Score', 'Infrastructure', 'Accessibility', 'Transit accessibility', 'Walk Score', 0.0035, false),
('INFRA_017', 'School District Rating', 'Infrastructure', 'Amenities', 'District quality score', 'GreatSchools', 0.0050, false),
('INFRA_018', 'Nearest Elem School Dist', 'Infrastructure', 'Amenities', 'Miles to elementary', 'Calculated', 0.0030, false),
('INFRA_019', 'Hospital Distance', 'Infrastructure', 'Amenities', 'Miles to hospital', 'Calculated', 0.0035, false),
('INFRA_020', 'Grocery Distance', 'Infrastructure', 'Amenities', 'Miles to grocery store', 'Calculated', 0.0030, false),
('INFRA_021', 'Major Employer Distance', 'Infrastructure', 'Economic', 'Miles to employment center', 'Calculated', 0.0040, true),
('INFRA_022', 'Retail Density', 'Infrastructure', 'Economic', 'Retail SF per capita', 'CoStar', 0.0035, true),
('INFRA_023', 'Office Density', 'Infrastructure', 'Economic', 'Office SF per capita', 'CoStar', 0.0030, true),
('INFRA_024', 'Industrial Proximity', 'Infrastructure', 'Economic', 'Distance to industrial', 'Calculated', 0.0025, true),
('INFRA_025', 'Infrastructure Score', 'Infrastructure', 'Summary', 'Overall infra quality 1-100', 'ZoneWise ML', 0.0055, true);

-- ============================================
-- CATEGORY 8: DEMOGRAPHIC & ECONOMIC (28 KPIs)
-- ============================================
INSERT INTO kpi_definitions (kpi_code, kpi_name, category, subcategory, description, data_source, weight, is_exclusive) VALUES
('DEMO_001', 'Population Total', 'Demographic', 'Population', 'Census tract population', 'Census', 0.0040, false),
('DEMO_002', 'Population Growth 5yr', 'Demographic', 'Population', '5-year pop change %', 'Census', 0.0050, false),
('DEMO_003', 'Population Density', 'Demographic', 'Population', 'People per square mile', 'Census', 0.0035, false),
('DEMO_004', 'Median Age', 'Demographic', 'Population', 'Tract median age', 'Census', 0.0030, false),
('DEMO_005', 'Household Count', 'Demographic', 'Households', 'Total households', 'Census', 0.0035, false),
('DEMO_006', 'Household Size Avg', 'Demographic', 'Households', 'Average persons/household', 'Census', 0.0025, false),
('DEMO_007', 'Owner Occupied Rate', 'Demographic', 'Households', 'Homeownership rate', 'Census', 0.0045, false),
('DEMO_008', 'Renter Occupied Rate', 'Demographic', 'Households', 'Rental rate', 'Census', 0.0040, false),
('DEMO_009', 'Median Household Income', 'Demographic', 'Income', 'Tract median income', 'Census', 0.0055, false),
('DEMO_010', 'Income Growth 5yr', 'Demographic', 'Income', '5-year income change %', 'Census', 0.0050, true),
('DEMO_011', 'Per Capita Income', 'Demographic', 'Income', 'Income per person', 'Census', 0.0040, false),
('DEMO_012', 'Poverty Rate', 'Demographic', 'Income', 'Below poverty line %', 'Census', 0.0045, false),
('DEMO_013', 'Unemployment Rate', 'Demographic', 'Employment', 'Local unemployment %', 'BLS', 0.0050, false),
('DEMO_014', 'Labor Force Part Rate', 'Demographic', 'Employment', 'Working age employed %', 'Census', 0.0040, false),
('DEMO_015', 'Job Growth 5yr', 'Demographic', 'Employment', '5-year job change %', 'BLS', 0.0055, true),
('DEMO_016', 'Top Employer 1', 'Demographic', 'Employment', 'Largest local employer', 'Local Data', 0.0030, true),
('DEMO_017', 'Industry Diversity Index', 'Demographic', 'Employment', 'Economic diversification', 'BLS', 0.0045, true),
('DEMO_018', 'Education Bachelors+', 'Demographic', 'Education', 'College degree rate', 'Census', 0.0040, false),
('DEMO_019', 'Education HS+', 'Demographic', 'Education', 'HS diploma rate', 'Census', 0.0030, false),
('DEMO_020', 'Crime Index', 'Demographic', 'Safety', 'Crime rate index', 'FBI', 0.0055, false),
('DEMO_021', 'Property Crime Rate', 'Demographic', 'Safety', 'Property crime index', 'FBI', 0.0045, false),
('DEMO_022', 'Violent Crime Rate', 'Demographic', 'Safety', 'Violent crime index', 'FBI', 0.0050, false),
('DEMO_023', 'Insurance Claims Index', 'Demographic', 'Safety', 'Claims frequency', 'Insurance Data', 0.0040, true),
('DEMO_024', 'Neighborhood Trend', 'Demographic', 'Trends', 'Improving/stable/declining', 'ZoneWise ML', 0.0060, true),
('DEMO_025', 'Gentrification Index', 'Demographic', 'Trends', 'Gentrification pressure', 'ZoneWise ML', 0.0055, true),
('DEMO_026', 'Displacement Risk', 'Demographic', 'Trends', 'Affordability pressure', 'ZoneWise ML', 0.0045, true),
('DEMO_027', 'Migration Pattern', 'Demographic', 'Trends', 'In/out migration flow', 'Census', 0.0050, true),
('DEMO_028', 'Demographic Score', 'Demographic', 'Summary', 'Overall demo quality 1-100', 'ZoneWise ML', 0.0060, true);

-- ============================================
-- CATEGORY 9: LEGAL & TITLE (15 KPIs)
-- ============================================
INSERT INTO kpi_definitions (kpi_code, kpi_name, category, subcategory, description, data_source, weight, is_exclusive) VALUES
('LEGAL_001', 'Deed Type', 'Legal', 'Title', 'Warranty/quitclaim/special', 'Clerk', 0.0045, false),
('LEGAL_002', 'Chain of Title Clean', 'Legal', 'Title', 'Clear ownership history', 'AcclaimWeb', 0.0060, true),
('LEGAL_003', 'Easement Count', 'Legal', 'Encumbrances', 'Number of easements', 'AcclaimWeb', 0.0040, false),
('LEGAL_004', 'Easement Impact Score', 'Legal', 'Encumbrances', 'Easement severity 1-10', 'ZoneWise ML', 0.0050, true),
('LEGAL_005', 'Restrictive Covenants', 'Legal', 'Encumbrances', 'Private restrictions', 'AcclaimWeb', 0.0045, false),
('LEGAL_006', 'HOA Mandatory', 'Legal', 'Encumbrances', 'Required HOA membership', 'HOA Records', 0.0040, false),
('LEGAL_007', 'HOA Fee Monthly', 'Legal', 'Encumbrances', 'Monthly HOA dues', 'HOA Records', 0.0035, false),
('LEGAL_008', 'HOA Financial Health', 'Legal', 'Encumbrances', 'Association reserves score', 'HOA Records', 0.0045, true),
('LEGAL_009', 'Survey Date', 'Legal', 'Survey', 'Most recent survey date', 'Survey Records', 0.0030, false),
('LEGAL_010', 'Boundary Dispute Risk', 'Legal', 'Survey', 'Encroachment issues', 'ZoneWise ML', 0.0045, true),
('LEGAL_011', 'Access Rights Clear', 'Legal', 'Access', 'Legal access confirmed', 'AcclaimWeb', 0.0055, true),
('LEGAL_012', 'Mineral Rights Status', 'Legal', 'Rights', 'Subsurface rights status', 'AcclaimWeb', 0.0035, true),
('LEGAL_013', 'Air Rights Status', 'Legal', 'Rights', 'Development rights above', 'Municipal', 0.0030, true),
('LEGAL_014', 'Pending Litigation', 'Legal', 'Litigation', 'Active lawsuits on property', 'Clerk', 0.0055, true),
('LEGAL_015', 'Legal Clarity Score', 'Legal', 'Summary', 'Overall legal clarity 1-100', 'ZoneWise ML', 0.0060, true);

-- Verify count
SELECT category, COUNT(*) as kpi_count 
FROM kpi_definitions 
GROUP BY category 
ORDER BY category;

