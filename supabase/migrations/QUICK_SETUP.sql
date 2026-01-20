-- ========================================
-- ZONEWISE APPRAISAL SCHEMA - QUICK SETUP
-- ========================================
-- Copy this entire file into Supabase SQL Editor and click RUN
-- Time: < 30 seconds
-- Tables created: 9
-- ========================================

-- 1. Property Analyses (Master Record)
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
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. KPI Definitions
CREATE TABLE IF NOT EXISTS kpi_definitions (
    id SERIAL PRIMARY KEY,
    kpi_code VARCHAR(20) UNIQUE NOT NULL,
    kpi_name VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL,
    subcategory VARCHAR(100),
    description TEXT,
    data_source VARCHAR(100),
    weight DECIMAL(5,4) DEFAULT 0.0100,
    is_exclusive BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Property KPI Scores
CREATE TABLE IF NOT EXISTS property_kpi_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES property_analyses(id) ON DELETE CASCADE,
    kpi_id INTEGER REFERENCES kpi_definitions(id),
    raw_value TEXT,
    normalized_score DECIMAL(5,2),
    weight_applied DECIMAL(5,4),
    weighted_score DECIMAL(8,4),
    data_source VARCHAR(100),
    confidence VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Comparable Sales
CREATE TABLE IF NOT EXISTS comparable_sales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES property_analyses(id) ON DELETE CASCADE,
    comp_number INTEGER NOT NULL,
    address TEXT,
    parcel_id VARCHAR(50),
    sale_date DATE,
    sale_price DECIMAL(15,2),
    price_per_sf DECIMAL(10,2),
    year_built INTEGER,
    living_area_sf INTEGER,
    lot_size_sf DECIMAL(15,2),
    bedrooms INTEGER,
    bathrooms DECIMAL(3,1),
    garage_spaces INTEGER DEFAULT 0,
    pool BOOLEAN DEFAULT FALSE,
    distance_miles DECIMAL(5,2),
    data_source VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Sales Comparison Adjustments
CREATE TABLE IF NOT EXISTS sales_comparison_adjustments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES property_analyses(id) ON DELETE CASCADE,
    comp_id UUID REFERENCES comparable_sales(id) ON DELETE CASCADE,
    adjustment_category VARCHAR(50) NOT NULL,
    adjustment_item VARCHAR(100) NOT NULL,
    adjustment_amount DECIMAL(15,2) NOT NULL,
    adjustment_direction VARCHAR(10),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Sales Comparison Conclusions
CREATE TABLE IF NOT EXISTS sales_comparison_conclusions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES property_analyses(id) ON DELETE CASCADE,
    indicated_value_low DECIMAL(15,2),
    indicated_value_high DECIMAL(15,2),
    indicated_value_point DECIMAL(15,2) NOT NULL,
    confidence_level VARCHAR(20),
    reconciliation_narrative TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. Cost Approach Analyses
CREATE TABLE IF NOT EXISTS cost_approach_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES property_analyses(id) ON DELETE CASCADE,
    land_value DECIMAL(15,2),
    land_value_method VARCHAR(100),
    land_value_per_sf DECIMAL(10,2),
    cost_type VARCHAR(20),
    building_sf INTEGER,
    base_cost_per_sf DECIMAL(10,2),
    base_cost DECIMAL(15,2),
    quality_adjustment_amt DECIMAL(15,2),
    soft_costs_amt DECIMAL(15,2),
    replacement_cost_new DECIMAL(15,2),
    physical_depreciation_pct DECIMAL(5,2),
    physical_depreciation_amt DECIMAL(15,2),
    functional_obsolescence_amt DECIMAL(15,2),
    external_obsolescence_amt DECIMAL(15,2),
    total_depreciation_amt DECIMAL(15,2),
    depreciated_cost DECIMAL(15,2),
    site_improvements_value DECIMAL(15,2),
    indicated_value DECIMAL(15,2),
    confidence_level VARCHAR(20),
    narrative TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 8. Income Approach Analyses
CREATE TABLE IF NOT EXISTS income_approach_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES property_analyses(id) ON DELETE CASCADE,
    rental_units INTEGER DEFAULT 1,
    monthly_rent_per_unit DECIMAL(10,2),
    annual_rent_per_unit DECIMAL(12,2),
    potential_gross_income DECIMAL(15,2),
    other_income DECIMAL(15,2),
    vacancy_rate_pct DECIMAL(5,2),
    vacancy_loss DECIMAL(15,2),
    effective_gross_income DECIMAL(15,2),
    property_taxes DECIMAL(15,2),
    insurance DECIMAL(15,2),
    management_fee_pct DECIMAL(5,2),
    management_fee DECIMAL(15,2),
    maintenance_repairs DECIMAL(15,2),
    reserves_for_replacement DECIMAL(15,2),
    hoa_fees DECIMAL(15,2),
    total_operating_expenses DECIMAL(15,2),
    expense_ratio_pct DECIMAL(5,2),
    net_operating_income DECIMAL(15,2),
    cap_rate_source VARCHAR(100),
    cap_rate DECIMAL(6,4),
    indicated_value DECIMAL(15,2),
    gross_rent_multiplier DECIMAL(8,2),
    grm_indicated_value DECIMAL(15,2),
    confidence_level VARCHAR(20),
    narrative TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 9. Appraisal Reconciliation
CREATE TABLE IF NOT EXISTS appraisal_reconciliation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES property_analyses(id) ON DELETE CASCADE,
    sales_comparison_value DECIMAL(15,2),
    sales_comparison_weight INTEGER,
    cost_approach_value DECIMAL(15,2),
    cost_approach_weight INTEGER,
    income_approach_value DECIMAL(15,2),
    income_approach_weight INTEGER,
    reconciled_value_low DECIMAL(15,2),
    reconciled_value_high DECIMAL(15,2),
    final_value_opinion DECIMAL(15,2) NOT NULL,
    most_applicable_approach VARCHAR(50),
    reconciliation_narrative TEXT,
    effective_date DATE,
    appraiser_name VARCHAR(100),
    appraiser_designation VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create Indexes
CREATE INDEX IF NOT EXISTS idx_property_analyses_parcel ON property_analyses(parcel_id);
CREATE INDEX IF NOT EXISTS idx_property_analyses_date ON property_analyses(analysis_date);
CREATE INDEX IF NOT EXISTS idx_comparable_sales_analysis ON comparable_sales(analysis_id);
CREATE INDEX IF NOT EXISTS idx_property_kpi_scores_analysis ON property_kpi_scores(analysis_id);

-- Enable RLS
ALTER TABLE property_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE kpi_definitions ENABLE ROW LEVEL SECURITY;
ALTER TABLE property_kpi_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE comparable_sales ENABLE ROW LEVEL SECURITY;
ALTER TABLE sales_comparison_adjustments ENABLE ROW LEVEL SECURITY;
ALTER TABLE sales_comparison_conclusions ENABLE ROW LEVEL SECURITY;
ALTER TABLE cost_approach_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE income_approach_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE appraisal_reconciliation ENABLE ROW LEVEL SECURITY;

-- Policies for service role
DO $$ 
BEGIN
    -- Drop existing policies if they exist
    DROP POLICY IF EXISTS "service_full_access" ON property_analyses;
    DROP POLICY IF EXISTS "service_full_access" ON kpi_definitions;
    DROP POLICY IF EXISTS "service_full_access" ON property_kpi_scores;
    DROP POLICY IF EXISTS "service_full_access" ON comparable_sales;
    DROP POLICY IF EXISTS "service_full_access" ON sales_comparison_adjustments;
    DROP POLICY IF EXISTS "service_full_access" ON sales_comparison_conclusions;
    DROP POLICY IF EXISTS "service_full_access" ON cost_approach_analyses;
    DROP POLICY IF EXISTS "service_full_access" ON income_approach_analyses;
    DROP POLICY IF EXISTS "service_full_access" ON appraisal_reconciliation;
END $$;

CREATE POLICY "service_full_access" ON property_analyses FOR ALL USING (true);
CREATE POLICY "service_full_access" ON kpi_definitions FOR ALL USING (true);
CREATE POLICY "service_full_access" ON property_kpi_scores FOR ALL USING (true);
CREATE POLICY "service_full_access" ON comparable_sales FOR ALL USING (true);
CREATE POLICY "service_full_access" ON sales_comparison_adjustments FOR ALL USING (true);
CREATE POLICY "service_full_access" ON sales_comparison_conclusions FOR ALL USING (true);
CREATE POLICY "service_full_access" ON cost_approach_analyses FOR ALL USING (true);
CREATE POLICY "service_full_access" ON income_approach_analyses FOR ALL USING (true);
CREATE POLICY "service_full_access" ON appraisal_reconciliation FOR ALL USING (true);

-- Verification
SELECT 'SUCCESS: ZoneWise Appraisal Schema Created' as status,
       (SELECT count(*) FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('property_analyses', 'kpi_definitions', 'property_kpi_scores',
                          'comparable_sales', 'sales_comparison_adjustments', 
                          'sales_comparison_conclusions', 'cost_approach_analyses',
                          'income_approach_analyses', 'appraisal_reconciliation')) as tables_created;
