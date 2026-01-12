-- Migration: 001_initial_schema.sql
-- Created: 2026-01-13
-- Description: Initial ZoneWise database schema with zonewize skill integration

-- Enable PostGIS extension for spatial queries
CREATE EXTENSION IF NOT EXISTS postgis;

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Table: jurisdictions
-- 17 Brevard County jurisdictions
CREATE TABLE jurisdictions (
    id TEXT PRIMARY KEY,
    full_name TEXT NOT NULL UNIQUE,
    abbreviation TEXT NOT NULL,
    ordinance_url TEXT NOT NULL,
    zoning_map_url TEXT,
    contact_email TEXT,
    contact_phone TEXT,
    office_hours TEXT,
    parser_version TEXT NOT NULL DEFAULT 'municode_v2',
    population INTEGER,
    area_sqmi NUMERIC(10,2),
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: properties
-- Property master data
CREATE TABLE properties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    parcel_id TEXT UNIQUE NOT NULL,
    address TEXT NOT NULL,
    jurisdiction TEXT NOT NULL REFERENCES jurisdictions(id),
    property_type TEXT NOT NULL,
    zoning_district TEXT NOT NULL,
    lot_size_sqft INTEGER,
    building_sqft INTEGER,
    year_built INTEGER,
    front_setback NUMERIC(10,2),
    side_setback NUMERIC(10,2),
    rear_setback NUMERIC(10,2),
    building_height NUMERIC(10,2),
    current_use TEXT,
    owner_name TEXT,
    owner_address TEXT,
    latitude NUMERIC(10,6),
    longitude NUMERIC(10,6),
    geometry GEOMETRY(POINT, 4326),
    bcpao_account TEXT,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for properties
CREATE INDEX idx_properties_jurisdiction ON properties(jurisdiction);
CREATE INDEX idx_properties_zoning_district ON properties(zoning_district);
CREATE INDEX idx_properties_parcel_id ON properties(parcel_id);
CREATE INDEX idx_properties_geometry ON properties USING GIST(geometry);
CREATE INDEX idx_properties_address_fts ON properties USING GIN(to_tsvector('english', address));

-- Table: zoning_districts
-- Master list of all zoning districts across all jurisdictions
CREATE TABLE zoning_districts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    jurisdiction_id TEXT NOT NULL REFERENCES jurisdictions(id),
    district_code TEXT NOT NULL,
    district_name TEXT,
    description TEXT,
    allowed_uses JSONB,
    dimensional_requirements JSONB,
    special_conditions JSONB,
    ordinance_section TEXT,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(jurisdiction_id, district_code)
);

-- Indexes for zoning_districts
CREATE INDEX idx_zoning_districts_jurisdiction ON zoning_districts(jurisdiction_id);
CREATE INDEX idx_zoning_districts_code ON zoning_districts(district_code);

-- ============================================================================
-- ZONEWIZE SKILL TABLES
-- ============================================================================

-- Table: ordinance_cache
-- Cache for scraped ordinances (7-day TTL)
CREATE TABLE ordinance_cache (
    jurisdiction_id TEXT PRIMARY KEY REFERENCES jurisdictions(id),
    content TEXT NOT NULL,
    content_hash TEXT,
    scraped_at TIMESTAMPTZ NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    firecrawl_cost_usd NUMERIC(10,4),
    correlation_id UUID,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Function to automatically set expires_at
CREATE OR REPLACE FUNCTION set_ordinance_expiry()
RETURNS TRIGGER AS $$
BEGIN
    NEW.expires_at := NEW.scraped_at + INTERVAL '7 days';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for ordinance_cache
CREATE TRIGGER set_ordinance_expiry_trigger
BEFORE INSERT OR UPDATE ON ordinance_cache
FOR EACH ROW
EXECUTE FUNCTION set_ordinance_expiry();

-- Index for ordinance_cache
CREATE INDEX idx_ordinance_cache_expires ON ordinance_cache(expires_at);

-- Table: compliance_analyses
-- Results from zonewize skill analyses
CREATE TABLE compliance_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID NOT NULL REFERENCES properties(id),
    correlation_id UUID NOT NULL,
    
    -- Analysis results
    compliance_status TEXT NOT NULL,
    confidence_score INTEGER NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 100),
    zoning_district TEXT NOT NULL,
    allowed_uses JSONB,
    violations JSONB,
    requires_variance BOOLEAN,
    ordinance_sections JSONB,
    
    -- Data provenance
    data_source TEXT NOT NULL,
    cache_hit BOOLEAN NOT NULL,
    ordinance_last_updated TIMESTAMPTZ,
    
    -- Performance metrics
    execution_time_ms NUMERIC(10,2),
    cost_usd NUMERIC(10,4),
    
    -- Metadata
    analyzed_by TEXT DEFAULT 'zonewize_v1.0.0',
    analyzed_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Optional: user-provided context
    current_use TEXT,
    proposed_use TEXT,
    notes TEXT
);

-- Indexes for compliance_analyses
CREATE INDEX idx_compliance_analyses_property ON compliance_analyses(property_id);
CREATE INDEX idx_compliance_analyses_correlation ON compliance_analyses(correlation_id);
CREATE INDEX idx_compliance_analyses_status ON compliance_analyses(compliance_status);
CREATE INDEX idx_compliance_analyses_date ON compliance_analyses(analyzed_at DESC);

-- Table: violations
-- Detailed violation records
CREATE TABLE violations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID NOT NULL REFERENCES compliance_analyses(id) ON DELETE CASCADE,
    violation_type TEXT NOT NULL,
    description TEXT NOT NULL,
    severity TEXT NOT NULL,
    code_reference TEXT,
    current_value TEXT,
    required_value TEXT,
    estimated_fix_cost NUMERIC(10,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for violations
CREATE INDEX idx_violations_analysis ON violations(analysis_id);
CREATE INDEX idx_violations_type ON violations(violation_type);
CREATE INDEX idx_violations_severity ON violations(severity);

-- ============================================================================
-- OBSERVABILITY TABLES
-- ============================================================================

-- Table: zonewise_metrics
-- Performance and business metrics
CREATE TABLE zonewise_metrics (
    id BIGSERIAL PRIMARY KEY,
    metric_name TEXT NOT NULL,
    value NUMERIC NOT NULL,
    labels JSONB,
    correlation_id UUID,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for zonewise_metrics
CREATE INDEX idx_zonewise_metrics_name ON zonewise_metrics(metric_name);
CREATE INDEX idx_zonewise_metrics_timestamp ON zonewise_metrics(timestamp DESC);
CREATE INDEX idx_zonewise_metrics_correlation ON zonewise_metrics(correlation_id);
CREATE INDEX idx_zonewise_metrics_labels ON zonewise_metrics USING GIN(labels);

-- Table: zonewise_errors
-- Error tracking for debugging and monitoring
CREATE TABLE zonewise_errors (
    id BIGSERIAL PRIMARY KEY,
    error_type TEXT NOT NULL,
    error_message TEXT,
    skill_name TEXT,
    stage TEXT,
    context JSONB,
    correlation_id UUID,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for zonewise_errors
CREATE INDEX idx_zonewise_errors_type ON zonewise_errors(error_type);
CREATE INDEX idx_zonewise_errors_timestamp ON zonewise_errors(timestamp DESC);
CREATE INDEX idx_zonewise_errors_correlation ON zonewise_errors(correlation_id);
CREATE INDEX idx_zonewise_errors_skill ON zonewise_errors(skill_name);

-- ============================================================================
-- REPORTS & HISTORY TABLES
-- ============================================================================

-- Table: reports
-- Generated compliance reports (DOCX/PDF)
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID NOT NULL REFERENCES compliance_analyses(id),
    property_id UUID NOT NULL REFERENCES properties(id),
    report_type TEXT NOT NULL,
    format TEXT NOT NULL,
    file_url TEXT NOT NULL,
    file_size_bytes INTEGER,
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    generated_by TEXT DEFAULT 'zonewize_v1.0.0',
    expires_at TIMESTAMPTZ,
    metadata JSONB
);

-- Indexes for reports
CREATE INDEX idx_reports_analysis ON reports(analysis_id);
CREATE INDEX idx_reports_property ON reports(property_id);
CREATE INDEX idx_reports_date ON reports(generated_at DESC);

-- Table: variance_requests
-- Track variance requests and outcomes (future ML training data)
CREATE TABLE variance_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID NOT NULL REFERENCES properties(id),
    jurisdiction_id TEXT NOT NULL REFERENCES jurisdictions(id),
    request_type TEXT NOT NULL,
    requested_use TEXT,
    justification TEXT,
    submission_date DATE,
    hearing_date DATE,
    decision TEXT,
    decision_date DATE,
    conditions TEXT[],
    vote_record JSONB,
    case_number TEXT,
    documents JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for variance_requests
CREATE INDEX idx_variance_requests_property ON variance_requests(property_id);
CREATE INDEX idx_variance_requests_jurisdiction ON variance_requests(jurisdiction_id);
CREATE INDEX idx_variance_requests_decision ON variance_requests(decision);

-- ============================================================================
-- DASHBOARD VIEWS
-- ============================================================================

-- View: compliance_overview
-- Compliance rates by jurisdiction (last 30 days)
CREATE VIEW compliance_overview AS
SELECT 
    j.full_name AS jurisdiction,
    COUNT(*) AS total_analyses,
    COUNT(*) FILTER (WHERE ca.compliance_status = 'COMPLIANT') AS compliant_count,
    COUNT(*) FILTER (WHERE ca.compliance_status = 'NON_COMPLIANT') AS non_compliant_count,
    COUNT(*) FILTER (WHERE ca.compliance_status = 'MANUAL_REVIEW') AS manual_review_count,
    ROUND(AVG(ca.confidence_score), 1) AS avg_confidence,
    ROUND(AVG(ca.execution_time_ms), 0) AS avg_execution_ms,
    ROUND(SUM(ca.cost_usd), 4) AS total_cost_usd
FROM compliance_analyses ca
JOIN properties p ON ca.property_id = p.id
JOIN jurisdictions j ON p.jurisdiction = j.id
WHERE ca.analyzed_at > NOW() - INTERVAL '30 days'
GROUP BY j.full_name
ORDER BY total_analyses DESC;

-- View: cache_performance
-- Cache hit rates and freshness (last 7 days)
CREATE VIEW cache_performance AS
SELECT 
    j.full_name AS jurisdiction,
    COUNT(*) AS total_requests,
    COUNT(*) FILTER (WHERE ca.cache_hit) AS cache_hits,
    ROUND(COUNT(*) FILTER (WHERE ca.cache_hit) * 100.0 / COUNT(*), 1) AS cache_hit_rate,
    MAX(oc.scraped_at) AS last_cache_update,
    EXTRACT(EPOCH FROM (NOW() - MAX(oc.scraped_at))) / 86400 AS cache_age_days
FROM compliance_analyses ca
JOIN properties p ON ca.property_id = p.id
JOIN jurisdictions j ON p.jurisdiction = j.id
LEFT JOIN ordinance_cache oc ON j.id = oc.jurisdiction_id
WHERE ca.analyzed_at > NOW() - INTERVAL '7 days'
GROUP BY j.full_name
ORDER BY cache_hit_rate DESC;

-- View: top_violations
-- Most common violations (last 90 days)
CREATE VIEW top_violations AS
SELECT 
    v.violation_type,
    v.severity,
    COUNT(*) AS occurrence_count,
    ROUND(AVG(v.estimated_fix_cost), 2) AS avg_fix_cost,
    j.full_name AS most_common_jurisdiction
FROM violations v
JOIN compliance_analyses ca ON v.analysis_id = ca.id
JOIN properties p ON ca.property_id = p.id
JOIN jurisdictions j ON p.jurisdiction = j.id
WHERE ca.analyzed_at > NOW() - INTERVAL '90 days'
GROUP BY v.violation_type, v.severity, j.full_name
ORDER BY occurrence_count DESC
LIMIT 20;

-- View: skill_performance
-- Execution time metrics by skill and stage (last 7 days)
CREATE VIEW skill_performance AS
SELECT 
    (labels->>'skill') AS skill_name,
    (labels->>'stage') AS stage,
    COUNT(*) AS execution_count,
    ROUND(AVG(value), 2) AS avg_value,
    ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY value), 2) AS p95_value,
    ROUND(MIN(value), 2) AS min_value,
    ROUND(MAX(value), 2) AS max_value
FROM zonewise_metrics
WHERE metric_name LIKE '%_execution_ms'
AND timestamp > NOW() - INTERVAL '7 days'
GROUP BY skill_name, stage
ORDER BY execution_count DESC;

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on tables
ALTER TABLE properties ENABLE ROW LEVEL SECURITY;
ALTER TABLE compliance_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;

-- Properties: Public read, service role write
CREATE POLICY "Public can read properties"
ON properties FOR SELECT
USING (true);

CREATE POLICY "Service role can insert/update properties"
ON properties FOR ALL
USING (auth.role() = 'service_role');

-- Compliance Analyses: Service role only (for now)
CREATE POLICY "Service role can access analyses"
ON compliance_analyses FOR ALL
USING (auth.role() = 'service_role');

-- Reports: Service role only (for now)
CREATE POLICY "Service role can access reports"
ON reports FOR ALL
USING (auth.role() = 'service_role');

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE properties IS 'Property master data with PostGIS geometry for spatial queries';
COMMENT ON TABLE jurisdictions IS '17 Brevard County jurisdictions with ordinance URLs and contact info';
COMMENT ON TABLE zoning_districts IS 'All zoning districts across all jurisdictions with JSONB allowed_uses';
COMMENT ON TABLE ordinance_cache IS 'Cache for scraped ordinances with 7-day TTL and auto-expiry trigger';
COMMENT ON TABLE compliance_analyses IS 'Results from zonewize skill analyses with correlation IDs';
COMMENT ON TABLE violations IS 'Normalized violation records from compliance_analyses.violations JSONB';
COMMENT ON TABLE zonewise_metrics IS 'Performance and business metrics for observability';
COMMENT ON TABLE zonewise_errors IS 'Error tracking for debugging and monitoring';
COMMENT ON TABLE reports IS 'Generated DOCX/PDF compliance reports stored in Supabase Storage';
COMMENT ON TABLE variance_requests IS 'Historical variance data for future ML model training';

COMMENT ON VIEW compliance_overview IS 'Compliance rates by jurisdiction (last 30 days)';
COMMENT ON VIEW cache_performance IS 'Cache hit rates and freshness (last 7 days)';
COMMENT ON VIEW top_violations IS 'Most common violations by type and severity (last 90 days)';
COMMENT ON VIEW skill_performance IS 'Execution time metrics by skill and stage (last 7 days)';

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================
