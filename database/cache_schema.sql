-- =============================================================================
-- ZoneWise Cache Schema V1.0
-- Three-Layer Caching Architecture for Firecrawl Cost Optimization
-- =============================================================================
-- Target: 70%+ cache hit rate → $20-40/month Alpha, $50-83/month Beta
-- =============================================================================

-- -----------------------------------------------------------------------------
-- LAYER 1: JURISDICTION ZONING CODES (Static - Monthly Refresh)
-- Purpose: Store complete zoning code definitions per jurisdiction
-- Refresh: Monthly (zoning codes rarely change mid-year)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS zonewise_jurisdiction_codes (
    id BIGSERIAL PRIMARY KEY,
    jurisdiction_id VARCHAR(50) NOT NULL,
    jurisdiction_name VARCHAR(100) NOT NULL,
    
    -- Zoning districts array
    districts JSONB NOT NULL DEFAULT '[]',
    -- Example: [{"code": "R-1", "name": "Single Family", "category": "residential"}]
    
    -- Full code document (compressed text)
    code_document TEXT,
    code_document_url VARCHAR(500),
    code_last_updated DATE,
    
    -- Permitted uses matrix by district
    permitted_uses JSONB DEFAULT '{}',
    -- Example: {"R-1": {"residential": true, "commercial": false, "industrial": false}}
    
    -- Dimensional requirements by district (backup/fallback)
    dimensional_standards JSONB DEFAULT '{}',
    
    -- Metadata
    source_url VARCHAR(500),
    scrape_method VARCHAR(50) DEFAULT 'firecrawl',
    data_quality_score INTEGER CHECK (data_quality_score BETWEEN 0 AND 100),
    
    -- Cache management
    cached_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '30 days'),
    cache_hits INTEGER DEFAULT 0,
    last_hit_at TIMESTAMPTZ,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(jurisdiction_id)
);

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_jurisdiction_codes_name ON zonewise_jurisdiction_codes(jurisdiction_name);
CREATE INDEX IF NOT EXISTS idx_jurisdiction_codes_expires ON zonewise_jurisdiction_codes(expires_at);

-- -----------------------------------------------------------------------------
-- LAYER 2: PARCEL ZONING CACHE (Semi-Static - 90 Day Refresh)
-- Purpose: Cache parcel-to-zoning mappings after first lookup
-- Refresh: 90 days or on-demand when user requests fresh data
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS zonewise_parcel_cache (
    id BIGSERIAL PRIMARY KEY,
    parcel_id VARCHAR(50) NOT NULL,
    account_number VARCHAR(30),
    
    -- Location
    jurisdiction_id VARCHAR(50) NOT NULL,
    address VARCHAR(255),
    city VARCHAR(100),
    zip_code VARCHAR(10),
    
    -- Zoning data
    zoning_code VARCHAR(20) NOT NULL,
    zoning_description VARCHAR(255),
    future_land_use VARCHAR(100),
    overlay_districts JSONB DEFAULT '[]',
    
    -- Dimensional requirements (denormalized for fast access)
    min_lot_size INTEGER,
    min_lot_width INTEGER,
    max_height INTEGER,
    front_setback INTEGER,
    rear_setback INTEGER,
    side_setback INTEGER,
    max_lot_coverage DECIMAL(5,2),
    
    -- Permitted uses for this parcel
    permitted_uses JSONB DEFAULT '{}',
    conditional_uses JSONB DEFAULT '{}',
    prohibited_uses JSONB DEFAULT '{}',
    
    -- Source linkage
    bcpao_url VARCHAR(500),
    jurisdiction_code_url VARCHAR(500),
    
    -- Cache management
    cached_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '90 days'),
    cache_hits INTEGER DEFAULT 0,
    last_hit_at TIMESTAMPTZ,
    is_stale BOOLEAN DEFAULT FALSE,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(parcel_id)
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_parcel_cache_jurisdiction ON zonewise_parcel_cache(jurisdiction_id);
CREATE INDEX IF NOT EXISTS idx_parcel_cache_zoning ON zonewise_parcel_cache(zoning_code);
CREATE INDEX IF NOT EXISTS idx_parcel_cache_address ON zonewise_parcel_cache(address);
CREATE INDEX IF NOT EXISTS idx_parcel_cache_expires ON zonewise_parcel_cache(expires_at);
CREATE INDEX IF NOT EXISTS idx_parcel_cache_account ON zonewise_parcel_cache(account_number);

-- -----------------------------------------------------------------------------
-- LAYER 3: LIVE LOOKUP LOG (Audit Trail + Analytics)
-- Purpose: Track all live Firecrawl calls for cost monitoring
-- Retention: 365 days
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS zonewise_lookup_log (
    id BIGSERIAL PRIMARY KEY,
    
    -- Request details
    lookup_type VARCHAR(20) NOT NULL CHECK (lookup_type IN ('parcel', 'jurisdiction', 'bulk', 'refresh')),
    query_input JSONB NOT NULL,
    -- Example: {"parcel_id": "123456"} or {"jurisdiction": "Satellite Beach"}
    
    -- Cache result
    cache_hit BOOLEAN NOT NULL,
    cache_layer VARCHAR(10) CHECK (cache_layer IN ('L1', 'L2', 'MISS')),
    
    -- If cache miss, Firecrawl details
    firecrawl_called BOOLEAN DEFAULT FALSE,
    firecrawl_pages_scraped INTEGER DEFAULT 0,
    firecrawl_cost_estimate DECIMAL(10,4) DEFAULT 0,
    firecrawl_duration_ms INTEGER,
    
    -- Response
    response_success BOOLEAN,
    response_data JSONB,
    error_message TEXT,
    
    -- User context (for Beta)
    user_id VARCHAR(100),
    session_id VARCHAR(100),
    source VARCHAR(50) DEFAULT 'api',
    -- Source: 'api', 'biddeed_integration', 'spd_integration', 'web_ui'
    
    -- Timing
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for analytics
CREATE INDEX IF NOT EXISTS idx_lookup_log_created ON zonewise_lookup_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_lookup_log_cache_hit ON zonewise_lookup_log(cache_hit);
CREATE INDEX IF NOT EXISTS idx_lookup_log_user ON zonewise_lookup_log(user_id);
CREATE INDEX IF NOT EXISTS idx_lookup_log_type ON zonewise_lookup_log(lookup_type);

-- -----------------------------------------------------------------------------
-- CACHE STATISTICS VIEW
-- Purpose: Real-time monitoring of cache performance
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW zonewise_cache_stats AS
SELECT 
    -- Overall stats
    (SELECT COUNT(*) FROM zonewise_jurisdiction_codes) AS l1_jurisdiction_count,
    (SELECT COUNT(*) FROM zonewise_parcel_cache) AS l2_parcel_count,
    (SELECT COUNT(*) FROM zonewise_parcel_cache WHERE is_stale = FALSE AND expires_at > NOW()) AS l2_valid_count,
    
    -- Cache hit rate (last 30 days)
    (SELECT 
        ROUND(
            COUNT(*) FILTER (WHERE cache_hit = TRUE)::DECIMAL / 
            NULLIF(COUNT(*), 0) * 100, 
            2
        )
     FROM zonewise_lookup_log 
     WHERE created_at > NOW() - INTERVAL '30 days'
    ) AS cache_hit_rate_30d,
    
    -- Firecrawl costs (last 30 days)
    (SELECT COALESCE(SUM(firecrawl_cost_estimate), 0) 
     FROM zonewise_lookup_log 
     WHERE created_at > NOW() - INTERVAL '30 days'
    ) AS firecrawl_cost_30d,
    
    -- Total lookups (last 30 days)
    (SELECT COUNT(*) 
     FROM zonewise_lookup_log 
     WHERE created_at > NOW() - INTERVAL '30 days'
    ) AS total_lookups_30d,
    
    -- Lookups today
    (SELECT COUNT(*) 
     FROM zonewise_lookup_log 
     WHERE created_at > NOW() - INTERVAL '1 day'
    ) AS lookups_today;

-- -----------------------------------------------------------------------------
-- DAILY METRICS TABLE (for tracking over time)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS zonewise_daily_metrics (
    id BIGSERIAL PRIMARY KEY,
    metric_date DATE NOT NULL UNIQUE,
    
    -- Lookup counts
    total_lookups INTEGER DEFAULT 0,
    cache_hits INTEGER DEFAULT 0,
    cache_misses INTEGER DEFAULT 0,
    
    -- By layer
    l1_hits INTEGER DEFAULT 0,
    l2_hits INTEGER DEFAULT 0,
    
    -- Firecrawl usage
    firecrawl_calls INTEGER DEFAULT 0,
    firecrawl_pages INTEGER DEFAULT 0,
    firecrawl_cost DECIMAL(10,4) DEFAULT 0,
    
    -- By source
    api_lookups INTEGER DEFAULT 0,
    biddeed_lookups INTEGER DEFAULT 0,
    spd_lookups INTEGER DEFAULT 0,
    web_lookups INTEGER DEFAULT 0,
    
    -- Unique users (Beta)
    unique_users INTEGER DEFAULT 0,
    
    -- Computed
    cache_hit_rate DECIMAL(5,2),
    avg_response_time_ms INTEGER,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_daily_metrics_date ON zonewise_daily_metrics(metric_date DESC);

-- -----------------------------------------------------------------------------
-- HELPER FUNCTIONS
-- -----------------------------------------------------------------------------

-- Function to record cache hit and update stats
CREATE OR REPLACE FUNCTION record_cache_hit(
    p_table_name TEXT,
    p_record_id BIGINT
) RETURNS VOID AS $$
BEGIN
    IF p_table_name = 'jurisdiction' THEN
        UPDATE zonewise_jurisdiction_codes 
        SET cache_hits = cache_hits + 1, last_hit_at = NOW()
        WHERE id = p_record_id;
    ELSIF p_table_name = 'parcel' THEN
        UPDATE zonewise_parcel_cache 
        SET cache_hits = cache_hits + 1, last_hit_at = NOW()
        WHERE id = p_record_id;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Function to check if cache entry is valid
CREATE OR REPLACE FUNCTION is_cache_valid(
    p_expires_at TIMESTAMPTZ,
    p_is_stale BOOLEAN DEFAULT FALSE
) RETURNS BOOLEAN AS $$
BEGIN
    RETURN p_expires_at > NOW() AND NOT COALESCE(p_is_stale, FALSE);
END;
$$ LANGUAGE plpgsql;

-- Function to get cost summary for date range
CREATE OR REPLACE FUNCTION get_firecrawl_cost_summary(
    p_start_date DATE,
    p_end_date DATE
) RETURNS TABLE (
    total_lookups BIGINT,
    cache_hits BIGINT,
    cache_misses BIGINT,
    hit_rate DECIMAL,
    total_firecrawl_cost DECIMAL,
    avg_cost_per_lookup DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::BIGINT AS total_lookups,
        COUNT(*) FILTER (WHERE cache_hit = TRUE)::BIGINT AS cache_hits,
        COUNT(*) FILTER (WHERE cache_hit = FALSE)::BIGINT AS cache_misses,
        ROUND(COUNT(*) FILTER (WHERE cache_hit = TRUE)::DECIMAL / NULLIF(COUNT(*), 0) * 100, 2) AS hit_rate,
        COALESCE(SUM(firecrawl_cost_estimate), 0) AS total_firecrawl_cost,
        ROUND(COALESCE(SUM(firecrawl_cost_estimate), 0) / NULLIF(COUNT(*), 0), 4) AS avg_cost_per_lookup
    FROM zonewise_lookup_log
    WHERE created_at::DATE BETWEEN p_start_date AND p_end_date;
END;
$$ LANGUAGE plpgsql;

-- -----------------------------------------------------------------------------
-- SEED DATA: 17 BREVARD JURISDICTIONS
-- -----------------------------------------------------------------------------
INSERT INTO zonewise_jurisdiction_codes (jurisdiction_id, jurisdiction_name, source_url, data_quality_score)
VALUES 
    ('brevard_county', 'Brevard County', 'https://www.brevardfl.gov/PlanningDev/ZoningDivision', 0),
    ('cape_canaveral', 'Cape Canaveral', 'https://www.cityofcapecanaveral.org/departments/community_development/', 0),
    ('cocoa', 'Cocoa', 'https://www.cocoafl.org/', 0),
    ('cocoa_beach', 'Cocoa Beach', 'https://www.cityofcocoabeach.com/', 0),
    ('grant_valkaria', 'Grant-Valkaria', 'https://www.grantvalkaria.org/', 0),
    ('indian_harbour_beach', 'Indian Harbour Beach', 'https://www.indianharbourbeach.org/', 0),
    ('indialantic', 'Indialantic', 'https://www.indialantic.com/', 0),
    ('malabar', 'Malabar', 'https://www.townofmalabar.org/', 0),
    ('melbourne', 'Melbourne', 'https://www.melbourneflorida.org/', 0),
    ('melbourne_beach', 'Melbourne Beach', 'https://www.melbournebeachfl.org/', 0),
    ('melbourne_village', 'Melbourne Village', 'https://www.melbournevillage.org/', 0),
    ('palm_bay', 'Palm Bay', 'https://www.pbfl.org/', 0),
    ('palm_shores', 'Palm Shores', 'https://www.palmshoresfl.org/', 0),
    ('rockledge', 'Rockledge', 'https://www.cityofrockledge.org/', 0),
    ('satellite_beach', 'Satellite Beach', 'https://www.satellitebeach.org/', 0),
    ('titusville', 'Titusville', 'https://www.titusville.com/', 0),
    ('west_melbourne', 'West Melbourne', 'https://www.westmelbourne.gov/', 0)
ON CONFLICT (jurisdiction_id) DO UPDATE
SET 
    jurisdiction_name = EXCLUDED.jurisdiction_name,
    source_url = EXCLUDED.source_url,
    updated_at = NOW();

-- -----------------------------------------------------------------------------
-- ROW LEVEL SECURITY (RLS) - For Beta Multi-User
-- -----------------------------------------------------------------------------
-- Enable RLS on lookup_log for user isolation
ALTER TABLE zonewise_lookup_log ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own lookups (Beta phase)
-- Note: Admin/service role bypasses RLS
CREATE POLICY lookup_log_user_isolation ON zonewise_lookup_log
    FOR SELECT
    USING (user_id = auth.uid()::TEXT OR user_id IS NULL);

-- Allow inserts from any authenticated user
CREATE POLICY lookup_log_insert ON zonewise_lookup_log
    FOR INSERT
    WITH CHECK (TRUE);

-- -----------------------------------------------------------------------------
-- MAINTENANCE: Scheduled Cleanup (Run via pg_cron or GitHub Actions)
-- -----------------------------------------------------------------------------
-- Delete lookup logs older than 365 days
-- CREATE OR REPLACE FUNCTION cleanup_old_logs() RETURNS void AS $$
-- BEGIN
--     DELETE FROM zonewise_lookup_log WHERE created_at < NOW() - INTERVAL '365 days';
-- END;
-- $$ LANGUAGE plpgsql;

-- Mark expired parcel cache as stale
-- CREATE OR REPLACE FUNCTION mark_stale_parcels() RETURNS void AS $$
-- BEGIN
--     UPDATE zonewise_parcel_cache SET is_stale = TRUE WHERE expires_at < NOW();
-- END;
-- $$ LANGUAGE plpgsql;

-- =============================================================================
-- END OF SCHEMA
-- =============================================================================
