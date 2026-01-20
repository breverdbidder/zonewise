-- ============================================
-- ZoneWise Appraisal Module - Three Approaches to Value
-- MAI (Member of Appraisal Institute) Standards
-- Version: 1.0.0
-- Date: 2026-01-20
-- ============================================

-- ============================================
-- 1. SALES COMPARISON APPROACH (Market Approach)
-- ============================================

-- Comparable Sales Records
CREATE TABLE IF NOT EXISTS comparable_sales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES property_analyses(id) ON DELETE CASCADE,
    comp_number INTEGER NOT NULL, -- 1, 2, 3, etc.
    address TEXT NOT NULL,
    parcel_id VARCHAR(50),
    sale_date DATE NOT NULL,
    sale_price DECIMAL(15,2) NOT NULL,
    price_per_sf DECIMAL(10,2),
    year_built INTEGER,
    living_area_sf INTEGER,
    lot_size_sf INTEGER,
    bedrooms INTEGER,
    bathrooms DECIMAL(3,1),
    garage_spaces INTEGER,
    pool BOOLEAN DEFAULT FALSE,
    waterfront BOOLEAN DEFAULT FALSE,
    condition_rating VARCHAR(20), -- Excellent, Good, Average, Fair, Poor
    quality_rating VARCHAR(20),
    distance_miles DECIMAL(5,2),
    days_on_market INTEGER,
    financing_type VARCHAR(50), -- Conventional, FHA, VA, Cash, Seller Financing
    data_source VARCHAR(100), -- MLS, BCPAO, Public Records
    verification_status VARCHAR(20) DEFAULT 'VERIFIED',
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sales Comparison Adjustments Grid
CREATE TABLE IF NOT EXISTS sales_comparison_adjustments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES property_analyses(id) ON DELETE CASCADE,
    comp_id UUID REFERENCES comparable_sales(id) ON DELETE CASCADE,
    adjustment_category VARCHAR(50) NOT NULL, -- Location, Size, Age, Condition, Features
    adjustment_item VARCHAR(100) NOT NULL, -- e.g., "Living Area SF", "Pool", "Garage"
    subject_value TEXT, -- Subject property value
    comp_value TEXT, -- Comparable property value
    adjustment_amount DECIMAL(12,2), -- Dollar adjustment (positive or negative)
    adjustment_percent DECIMAL(6,2), -- Percentage adjustment
    adjustment_direction VARCHAR(10), -- UP or DOWN
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sales Comparison Reconciliation
CREATE TABLE IF NOT EXISTS sales_comparison_reconciliation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES property_analyses(id) ON DELETE CASCADE,
    comp_id UUID REFERENCES comparable_sales(id) ON DELETE CASCADE,
    unadjusted_price DECIMAL(15,2) NOT NULL,
    total_adjustments DECIMAL(12,2) NOT NULL,
    adjusted_price DECIMAL(15,2) NOT NULL,
    weight_assigned DECIMAL(5,2), -- Weight given to this comp (0-100%)
    reliability_score DECIMAL(5,2), -- How reliable is this comp (0-100)
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Final Sales Comparison Conclusion
CREATE TABLE IF NOT EXISTS sales_comparison_conclusions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES property_analyses(id) ON DELETE CASCADE,
    indicated_value_low DECIMAL(15,2),
    indicated_value_high DECIMAL(15,2),
    indicated_value_point DECIMAL(15,2) NOT NULL,
    confidence_level VARCHAR(20), -- High, Medium, Low
    reconciliation_narrative TEXT,
    limiting_conditions TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 2. COST APPROACH
-- ============================================

-- Cost Approach Summary
CREATE TABLE IF NOT EXISTS cost_approach_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES property_analyses(id) ON DELETE CASCADE,
    
    -- Land Value
    land_value DECIMAL(15,2) NOT NULL,
    land_value_method VARCHAR(50), -- Sales Comparison, Allocation, Extraction, Residual
    land_value_per_sf DECIMAL(10,2),
    land_value_per_acre DECIMAL(15,2),
    
    -- Replacement/Reproduction Cost New
    cost_type VARCHAR(20) DEFAULT 'REPLACEMENT', -- REPLACEMENT or REPRODUCTION
    building_sf INTEGER NOT NULL,
    base_cost_per_sf DECIMAL(10,2) NOT NULL,
    base_cost DECIMAL(15,2) NOT NULL,
    
    -- Adjustments to Cost
    quality_adjustment_pct DECIMAL(6,2),
    quality_adjustment_amt DECIMAL(12,2),
    feature_adjustments DECIMAL(12,2),
    soft_costs_pct DECIMAL(6,2) DEFAULT 15.0,
    soft_costs_amt DECIMAL(12,2),
    entrepreneurial_profit_pct DECIMAL(6,2),
    entrepreneurial_profit_amt DECIMAL(12,2),
    
    -- Total Cost New
    replacement_cost_new DECIMAL(15,2) NOT NULL,
    
    -- Depreciation
    physical_depreciation_pct DECIMAL(6,2),
    physical_depreciation_amt DECIMAL(12,2),
    functional_obsolescence_amt DECIMAL(12,2),
    external_obsolescence_amt DECIMAL(12,2),
    total_depreciation_amt DECIMAL(12,2),
    total_depreciation_pct DECIMAL(6,2),
    
    -- Depreciated Cost
    depreciated_cost DECIMAL(15,2) NOT NULL,
    
    -- Site Improvements
    site_improvements_value DECIMAL(12,2),
    
    -- Final Value
    indicated_value DECIMAL(15,2) NOT NULL,
    confidence_level VARCHAR(20),
    narrative TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Land Comparables (for land value portion of cost approach)
CREATE TABLE IF NOT EXISTS land_comparables (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES property_analyses(id) ON DELETE CASCADE,
    address TEXT NOT NULL,
    parcel_id VARCHAR(50),
    sale_date DATE,
    sale_price DECIMAL(15,2),
    lot_size_sf INTEGER,
    lot_size_acres DECIMAL(8,4),
    price_per_sf DECIMAL(10,2),
    price_per_acre DECIMAL(15,2),
    zoning VARCHAR(50),
    utilities_available BOOLEAN,
    topography VARCHAR(50),
    shape VARCHAR(50),
    road_frontage_ft INTEGER,
    adjustments_made JSONB,
    adjusted_price DECIMAL(15,2),
    data_source VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 3. INCOME APPROACH
-- ============================================

-- Income Approach Analysis
CREATE TABLE IF NOT EXISTS income_approach_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES property_analyses(id) ON DELETE CASCADE,
    
    -- Potential Gross Income
    rental_units INTEGER DEFAULT 1,
    monthly_rent_per_unit DECIMAL(10,2),
    annual_rent_per_unit DECIMAL(12,2),
    potential_gross_income DECIMAL(15,2) NOT NULL,
    
    -- Other Income
    other_income DECIMAL(12,2) DEFAULT 0, -- Parking, laundry, etc.
    
    -- Vacancy & Collection Loss
    vacancy_rate_pct DECIMAL(5,2) DEFAULT 5.0,
    vacancy_loss DECIMAL(12,2),
    collection_loss DECIMAL(12,2),
    
    -- Effective Gross Income
    effective_gross_income DECIMAL(15,2) NOT NULL,
    
    -- Operating Expenses
    property_taxes DECIMAL(12,2),
    insurance DECIMAL(12,2),
    utilities DECIMAL(12,2),
    management_fee_pct DECIMAL(5,2),
    management_fee DECIMAL(12,2),
    maintenance_repairs DECIMAL(12,2),
    reserves_for_replacement DECIMAL(12,2),
    hoa_fees DECIMAL(12,2),
    other_expenses DECIMAL(12,2),
    total_operating_expenses DECIMAL(15,2),
    expense_ratio_pct DECIMAL(5,2),
    
    -- Net Operating Income
    net_operating_income DECIMAL(15,2) NOT NULL,
    
    -- Capitalization
    cap_rate_source VARCHAR(100), -- Survey, Market, Band of Investment
    cap_rate DECIMAL(6,4) NOT NULL, -- e.g., 0.0700 for 7%
    
    -- Value by Direct Capitalization
    indicated_value DECIMAL(15,2) NOT NULL, -- NOI / Cap Rate
    
    -- GRM Method (alternative)
    gross_rent_multiplier DECIMAL(8,2),
    grm_indicated_value DECIMAL(15,2),
    
    -- DSCR Analysis
    annual_debt_service DECIMAL(12,2),
    dscr DECIMAL(6,2), -- NOI / Debt Service
    
    -- Cash on Cash
    down_payment DECIMAL(15,2),
    cash_flow_before_tax DECIMAL(12,2),
    cash_on_cash_return DECIMAL(6,4),
    
    confidence_level VARCHAR(20),
    narrative TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Rent Comparables
CREATE TABLE IF NOT EXISTS rent_comparables (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES property_analyses(id) ON DELETE CASCADE,
    address TEXT NOT NULL,
    monthly_rent DECIMAL(10,2) NOT NULL,
    bedrooms INTEGER,
    bathrooms DECIMAL(3,1),
    living_area_sf INTEGER,
    rent_per_sf DECIMAL(8,2),
    lease_date DATE,
    lease_term_months INTEGER,
    amenities TEXT,
    condition VARCHAR(20),
    distance_miles DECIMAL(5,2),
    data_source VARCHAR(100),
    adjustments JSONB,
    adjusted_rent DECIMAL(10,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 4. FINAL VALUE RECONCILIATION
-- ============================================

CREATE TABLE IF NOT EXISTS appraisal_reconciliation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES property_analyses(id) ON DELETE CASCADE,
    
    -- Values from Three Approaches
    sales_comparison_value DECIMAL(15,2),
    sales_comparison_weight DECIMAL(5,2), -- Weight assigned (0-100%)
    cost_approach_value DECIMAL(15,2),
    cost_approach_weight DECIMAL(5,2),
    income_approach_value DECIMAL(15,2),
    income_approach_weight DECIMAL(5,2),
    
    -- Reconciled Value
    reconciled_value_low DECIMAL(15,2),
    reconciled_value_high DECIMAL(15,2),
    final_value_opinion DECIMAL(15,2) NOT NULL,
    
    -- Basis for Reconciliation
    most_applicable_approach VARCHAR(30), -- Sales Comparison, Cost, Income
    reconciliation_narrative TEXT,
    
    -- Effective Date
    effective_date DATE NOT NULL,
    report_date DATE DEFAULT CURRENT_DATE,
    
    -- Certifications
    appraiser_name VARCHAR(100),
    appraiser_license VARCHAR(50),
    appraiser_designation VARCHAR(50), -- MAI, SRA, etc.
    
    -- Limiting Conditions
    assumptions TEXT,
    limiting_conditions TEXT,
    extraordinary_assumptions TEXT,
    hypothetical_conditions TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 5. ENHANCED HBU (Highest & Best Use) ANALYSIS
-- ============================================

-- Drop and recreate with MAI-standard structure
DROP TABLE IF EXISTS hbu_analyses CASCADE;

CREATE TABLE hbu_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES property_analyses(id) ON DELETE CASCADE,
    
    -- Current Use Analysis
    current_use VARCHAR(100) NOT NULL,
    current_use_legal BOOLEAN DEFAULT TRUE,
    current_use_value DECIMAL(15,2),
    
    -- Four Tests of HBU (As Vacant)
    
    -- Test 1: Legally Permissible (As Vacant)
    legally_permissible_uses JSONB, -- Array of permitted uses
    zoning_restrictions TEXT,
    deed_restrictions TEXT,
    easements_impact TEXT,
    legal_conclusion TEXT,
    
    -- Test 2: Physically Possible (As Vacant)
    site_size_adequate BOOLEAN,
    topography_suitable BOOLEAN,
    soil_conditions_ok BOOLEAN,
    utilities_available BOOLEAN,
    access_adequate BOOLEAN,
    physical_conclusion TEXT,
    
    -- Test 3: Financially Feasible (As Vacant)
    market_demand_exists BOOLEAN,
    development_cost_estimate DECIMAL(15,2),
    expected_return DECIMAL(15,2),
    roi_projected DECIMAL(6,2),
    financially_feasible BOOLEAN,
    financial_conclusion TEXT,
    
    -- Test 4: Maximally Productive (As Vacant)
    alternative_uses_analyzed JSONB,
    hbu_as_vacant VARCHAR(100),
    hbu_as_vacant_value DECIMAL(15,2),
    maximally_productive_conclusion TEXT,
    
    -- HBU As Improved (if applicable)
    hbu_as_improved VARCHAR(100),
    hbu_as_improved_value DECIMAL(15,2),
    demolition_recommended BOOLEAN DEFAULT FALSE,
    conversion_recommended BOOLEAN DEFAULT FALSE,
    renovation_recommended BOOLEAN DEFAULT FALSE,
    
    -- Final HBU Conclusion
    final_hbu_conclusion VARCHAR(100),
    hbu_narrative TEXT,
    
    -- Development Potential
    max_buildable_sf INTEGER,
    max_units_allowed INTEGER,
    rezoning_required BOOLEAN DEFAULT FALSE,
    rezoning_probability DECIMAL(5,2),
    rezoning_timeline_months INTEGER,
    rezoning_cost_estimate DECIMAL(12,2),
    
    -- Value Impact
    value_uplift_potential DECIMAL(15,2),
    value_uplift_percent DECIMAL(6,2),
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 6. ENHANCED CMA TABLE
-- ============================================

-- Already have cma_analyses, add supporting table for adjustments
CREATE TABLE IF NOT EXISTS cma_adjustment_grid (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cma_id UUID REFERENCES cma_analyses(id) ON DELETE CASCADE,
    comp_address TEXT NOT NULL,
    comp_sale_price DECIMAL(15,2),
    comp_sale_date DATE,
    
    -- Standard Adjustment Categories
    location_adj DECIMAL(12,2) DEFAULT 0,
    condition_adj DECIMAL(12,2) DEFAULT 0,
    size_adj DECIMAL(12,2) DEFAULT 0,
    age_adj DECIMAL(12,2) DEFAULT 0,
    features_adj DECIMAL(12,2) DEFAULT 0,
    lot_size_adj DECIMAL(12,2) DEFAULT 0,
    garage_adj DECIMAL(12,2) DEFAULT 0,
    pool_adj DECIMAL(12,2) DEFAULT 0,
    view_adj DECIMAL(12,2) DEFAULT 0,
    other_adj DECIMAL(12,2) DEFAULT 0,
    
    total_adjustments DECIMAL(12,2),
    adjusted_price DECIMAL(15,2),
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- INDEXES
-- ============================================
CREATE INDEX IF NOT EXISTS idx_comparable_sales_analysis ON comparable_sales(analysis_id);
CREATE INDEX IF NOT EXISTS idx_sales_adjustments_analysis ON sales_comparison_adjustments(analysis_id);
CREATE INDEX IF NOT EXISTS idx_cost_approach_analysis ON cost_approach_analyses(analysis_id);
CREATE INDEX IF NOT EXISTS idx_income_approach_analysis ON income_approach_analyses(analysis_id);
CREATE INDEX IF NOT EXISTS idx_reconciliation_analysis ON appraisal_reconciliation(analysis_id);
CREATE INDEX IF NOT EXISTS idx_hbu_analysis ON hbu_analyses(analysis_id);

-- ============================================
-- RLS POLICIES
-- ============================================
ALTER TABLE comparable_sales ENABLE ROW LEVEL SECURITY;
ALTER TABLE sales_comparison_adjustments ENABLE ROW LEVEL SECURITY;
ALTER TABLE sales_comparison_reconciliation ENABLE ROW LEVEL SECURITY;
ALTER TABLE sales_comparison_conclusions ENABLE ROW LEVEL SECURITY;
ALTER TABLE cost_approach_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE land_comparables ENABLE ROW LEVEL SECURITY;
ALTER TABLE income_approach_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE rent_comparables ENABLE ROW LEVEL SECURITY;
ALTER TABLE appraisal_reconciliation ENABLE ROW LEVEL SECURITY;
ALTER TABLE cma_adjustment_grid ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role full access" ON comparable_sales FOR ALL USING (true);
CREATE POLICY "Service role full access" ON sales_comparison_adjustments FOR ALL USING (true);
CREATE POLICY "Service role full access" ON sales_comparison_reconciliation FOR ALL USING (true);
CREATE POLICY "Service role full access" ON sales_comparison_conclusions FOR ALL USING (true);
CREATE POLICY "Service role full access" ON cost_approach_analyses FOR ALL USING (true);
CREATE POLICY "Service role full access" ON land_comparables FOR ALL USING (true);
CREATE POLICY "Service role full access" ON income_approach_analyses FOR ALL USING (true);
CREATE POLICY "Service role full access" ON rent_comparables FOR ALL USING (true);
CREATE POLICY "Service role full access" ON appraisal_reconciliation FOR ALL USING (true);
CREATE POLICY "Service role full access" ON cma_adjustment_grid FOR ALL USING (true);

-- ============================================
-- VERIFICATION
-- ============================================
SELECT 'Three Approaches to Value Tables Created:' as status;
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
    'comparable_sales',
    'sales_comparison_adjustments',
    'sales_comparison_reconciliation',
    'sales_comparison_conclusions',
    'cost_approach_analyses',
    'land_comparables',
    'income_approach_analyses',
    'rent_comparables',
    'appraisal_reconciliation',
    'hbu_analyses',
    'cma_adjustment_grid'
)
ORDER BY table_name;
