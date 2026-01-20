-- ZoneWise Appraisal Schema Migration
-- Run this in Supabase SQL Editor
-- Version: 1.0.0
-- Date: 2026-01-20

-- ============================================
-- APPRAISAL CORE TABLES
-- ============================================

-- Property Analysis Master Record
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

-- Property KPI Scores
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

-- ============================================
-- SALES COMPARISON APPROACH
-- ============================================

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
    condition_rating VARCHAR(20),
    distance_miles DECIMAL(5,2),
    days_on_market INTEGER,
    data_source VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sales_comparison_adjustments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES property_analyses(id) ON DELETE CASCADE,
    comp_id UUID REFERENCES comparable_sales(id) ON DELETE CASCADE,
    adjustment_category VARCHAR(50) NOT NULL,
    adjustment_item VARCHAR(100) NOT NULL,
    adjustment_amount DECIMAL(15,2) NOT NULL,
    adjustment_direction VARCHAR(10) CHECK (adjustment_direction IN ('UP', 'DOWN')),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

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

-- ============================================
-- COST APPROACH
-- ============================================

CREATE TABLE IF NOT EXISTS cost_approach_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES property_analyses(id) ON DELETE CASCADE,
    
    -- Land Value
    land_value DECIMAL(15,2),
    land_value_method VARCHAR(100),
    land_value_per_sf DECIMAL(10,2),
    
    -- Replacement Cost
    cost_type VARCHAR(20) CHECK (cost_type IN ('REPRODUCTION', 'REPLACEMENT')),
    building_sf INTEGER,
    base_cost_per_sf DECIMAL(10,2),
    base_cost DECIMAL(15,2),
    quality_adjustment_pct DECIMAL(5,2),
    quality_adjustment_amt DECIMAL(15,2),
    soft_costs_pct DECIMAL(5,2),
    soft_costs_amt DECIMAL(15,2),
    entrepreneurial_profit_pct DECIMAL(5,2),
    entrepreneurial_profit_amt DECIMAL(15,2),
    replacement_cost_new DECIMAL(15,2),
    
    -- Depreciation
    physical_depreciation_pct DECIMAL(5,2),
    physical_depreciation_amt DECIMAL(15,2),
    functional_obsolescence_amt DECIMAL(15,2),
    external_obsolescence_amt DECIMAL(15,2),
    total_depreciation_amt DECIMAL(15,2),
    depreciated_cost DECIMAL(15,2),
    
    -- Site Improvements
    site_improvements_value DECIMAL(15,2),
    
    -- Final
    indicated_value DECIMAL(15,2),
    confidence_level VARCHAR(20),
    narrative TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- INCOME APPROACH
-- ============================================

CREATE TABLE IF NOT EXISTS income_approach_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES property_analyses(id) ON DELETE CASCADE,
    
    -- Income
    rental_units INTEGER DEFAULT 1,
    monthly_rent_per_unit DECIMAL(10,2),
    annual_rent_per_unit DECIMAL(12,2),
    potential_gross_income DECIMAL(15,2),
    other_income DECIMAL(15,2),
    vacancy_rate_pct DECIMAL(5,2),
    vacancy_loss DECIMAL(15,2),
    effective_gross_income DECIMAL(15,2),
    
    -- Expenses
    property_taxes DECIMAL(15,2),
    insurance DECIMAL(15,2),
    management_fee_pct DECIMAL(5,2),
    management_fee DECIMAL(15,2),
    maintenance_repairs DECIMAL(15,2),
    reserves_for_replacement DECIMAL(15,2),
    hoa_fees DECIMAL(15,2),
    utilities DECIMAL(15,2),
    other_expenses DECIMAL(15,2),
    total_operating_expenses DECIMAL(15,2),
    expense_ratio_pct DECIMAL(5,2),
    
    -- NOI
    net_operating_income DECIMAL(15,2),
    
    -- Capitalization
    cap_rate_source VARCHAR(100),
    cap_rate DECIMAL(6,4),
    indicated_value DECIMAL(15,2),
    
    -- GRM Method
    gross_rent_multiplier DECIMAL(8,2),
    grm_indicated_value DECIMAL(15,2),
    
    -- Final
    confidence_level VARCHAR(20),
    narrative TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- RECONCILIATION
-- ============================================

CREATE TABLE IF NOT EXISTS appraisal_reconciliation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES property_analyses(id) ON DELETE CASCADE,
    
    -- Three Approaches
    sales_comparison_value DECIMAL(15,2),
    sales_comparison_weight INTEGER,
    cost_approach_value DECIMAL(15,2),
    cost_approach_weight INTEGER,
    income_approach_value DECIMAL(15,2),
    income_approach_weight INTEGER,
    
    -- Reconciled Value
    reconciled_value_low DECIMAL(15,2),
    reconciled_value_high DECIMAL(15,2),
    final_value_opinion DECIMAL(15,2) NOT NULL,
    
    -- Analysis
    most_applicable_approach VARCHAR(50),
    reconciliation_narrative TEXT,
    
    -- Certification
    effective_date DATE,
    appraiser_name VARCHAR(100),
    appraiser_license VARCHAR(50),
    appraiser_designation VARCHAR(50),
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- INDEXES
-- ============================================

CREATE INDEX IF NOT EXISTS idx_property_analyses_parcel ON property_analyses(parcel_id);
CREATE INDEX IF NOT EXISTS idx_property_analyses_date ON property_analyses(analysis_date);
CREATE INDEX IF NOT EXISTS idx_comparable_sales_analysis ON comparable_sales(analysis_id);
CREATE INDEX IF NOT EXISTS idx_property_kpi_scores_analysis ON property_kpi_scores(analysis_id);
CREATE INDEX IF NOT EXISTS idx_kpi_definitions_category ON kpi_definitions(category);

-- ============================================
-- RLS POLICIES (Enable Row Level Security)
-- ============================================

ALTER TABLE property_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE kpi_definitions ENABLE ROW LEVEL SECURITY;
ALTER TABLE property_kpi_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE comparable_sales ENABLE ROW LEVEL SECURITY;
ALTER TABLE sales_comparison_adjustments ENABLE ROW LEVEL SECURITY;
ALTER TABLE sales_comparison_conclusions ENABLE ROW LEVEL SECURITY;
ALTER TABLE cost_approach_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE income_approach_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE appraisal_reconciliation ENABLE ROW LEVEL SECURITY;

-- Service role can do everything
CREATE POLICY "Service role full access" ON property_analyses FOR ALL USING (true);
CREATE POLICY "Service role full access" ON kpi_definitions FOR ALL USING (true);
CREATE POLICY "Service role full access" ON property_kpi_scores FOR ALL USING (true);
CREATE POLICY "Service role full access" ON comparable_sales FOR ALL USING (true);
CREATE POLICY "Service role full access" ON sales_comparison_adjustments FOR ALL USING (true);
CREATE POLICY "Service role full access" ON sales_comparison_conclusions FOR ALL USING (true);
CREATE POLICY "Service role full access" ON cost_approach_analyses FOR ALL USING (true);
CREATE POLICY "Service role full access" ON income_approach_analyses FOR ALL USING (true);
CREATE POLICY "Service role full access" ON appraisal_reconciliation FOR ALL USING (true);

-- ============================================
-- DONE
-- ============================================
SELECT 'ZoneWise Appraisal Schema Created Successfully' as status;
