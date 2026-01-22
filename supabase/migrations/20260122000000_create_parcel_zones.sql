
-- Migration: Create parcel_zones table
-- Generated: 2026-01-22

CREATE TABLE IF NOT EXISTS parcel_zones (
    id SERIAL PRIMARY KEY,
    jurisdiction_id INTEGER,
    parcel_id TEXT NOT NULL,
    zone_code TEXT NOT NULL,
    source TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (jurisdiction_id, parcel_id)
);

CREATE INDEX IF NOT EXISTS idx_parcel_zones_parcel ON parcel_zones(parcel_id);
CREATE INDEX IF NOT EXISTS idx_parcel_zones_jurisdiction ON parcel_zones(jurisdiction_id);
CREATE INDEX IF NOT EXISTS idx_parcel_zones_zone ON parcel_zones(zone_code);
