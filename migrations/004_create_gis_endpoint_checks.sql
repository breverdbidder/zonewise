-- Migration: Create GIS endpoint monitoring table
-- Run in Supabase SQL Editor

-- Table for tracking GIS endpoint health checks
CREATE TABLE IF NOT EXISTS gis_endpoint_checks (
  id SERIAL PRIMARY KEY,
  jurisdiction_id INTEGER NOT NULL,
  jurisdiction TEXT NOT NULL,
  endpoint TEXT,
  http_code INTEGER,
  status TEXT CHECK (status IN ('WORKING', 'DOWN', 'RECOVERED', 'ERROR', 'TIMEOUT')),
  error_message TEXT,
  response_time_ms INTEGER,
  checked_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for querying by jurisdiction
CREATE INDEX IF NOT EXISTS idx_gis_checks_jurisdiction ON gis_endpoint_checks(jurisdiction_id);

-- Index for time-based queries
CREATE INDEX IF NOT EXISTS idx_gis_checks_time ON gis_endpoint_checks(checked_at DESC);

-- Enable RLS
ALTER TABLE gis_endpoint_checks ENABLE ROW LEVEL SECURITY;

-- Allow read access
CREATE POLICY "Allow read access" ON gis_endpoint_checks FOR SELECT USING (true);

-- Allow insert from service role
CREATE POLICY "Allow insert from service role" ON gis_endpoint_checks FOR INSERT WITH CHECK (true);

-- View for latest status per jurisdiction
CREATE OR REPLACE VIEW gis_endpoint_latest AS
SELECT DISTINCT ON (jurisdiction_id)
  jurisdiction_id,
  jurisdiction,
  endpoint,
  http_code,
  status,
  error_message,
  checked_at
FROM gis_endpoint_checks
ORDER BY jurisdiction_id, checked_at DESC;

-- Insert initial Palm Bay outage record
INSERT INTO gis_endpoint_checks (jurisdiction_id, jurisdiction, endpoint, http_code, status, error_message)
VALUES (
  2,
  'Palm Bay',
  'https://gis.palmbayflorida.org/arcgis/rest/services/GrowthManagement/Zoning/MapServer/0',
  503,
  'DOWN',
  'TLS connection reset - server infrastructure issue since 2026-01-22'
);

-- Insert initial Rockledge outage record
INSERT INTO gis_endpoint_checks (jurisdiction_id, jurisdiction, endpoint, http_code, status, error_message)
VALUES (
  8,
  'Rockledge',
  'https://gis-rockledge.cityofrockledge.org/server/rest/services',
  0,
  'DOWN',
  'Server not responding - connection timeout'
);

COMMENT ON TABLE gis_endpoint_checks IS 'Tracks GIS endpoint health for ZoneWise monitoring';
