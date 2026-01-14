-- ZoneWise: Seed Zoning Requirements
-- Run this in Supabase SQL Editor to populate sample data

-- Ensure table exists with correct schema
CREATE TABLE IF NOT EXISTS zoning_requirements (
  id SERIAL PRIMARY KEY,
  jurisdiction VARCHAR(100) NOT NULL,
  district VARCHAR(20) NOT NULL,
  requirement_type VARCHAR(50),
  min_lot_size INTEGER,
  min_lot_width INTEGER,
  max_height INTEGER,
  front_setback INTEGER,
  rear_setback INTEGER,
  side_setback INTEGER,
  max_coverage DECIMAL,
  additional_requirements JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(jurisdiction, district)
);

-- Satellite Beach Districts
INSERT INTO zoning_requirements (jurisdiction, district, requirement_type, min_lot_size, min_lot_width, max_height, front_setback, rear_setback, side_setback, max_coverage, additional_requirements)
VALUES 
  ('SATELLITE BEACH', 'R-1', 'dimensional', 6000, 60, 35, 25, 20, 7, 40.0, '{"notes": "Single-family residential", "min_dwelling_size": 1200}'),
  ('SATELLITE BEACH', 'R-1A', 'dimensional', 7500, 75, 35, 25, 20, 10, 35.0, '{"notes": "Single-family residential, larger lots"}'),
  ('SATELLITE BEACH', 'R-2', 'dimensional', 5000, 50, 35, 25, 15, 5, 45.0, '{"notes": "Two-family residential"}'),
  ('SATELLITE BEACH', 'R-3', 'dimensional', 10000, 100, 45, 25, 20, 10, 50.0, '{"notes": "Multi-family residential"}'),
  ('SATELLITE BEACH', 'C-1', 'dimensional', 5000, 50, 45, 25, 10, 10, 60.0, '{"notes": "Commercial"}'),
  ('SATELLITE BEACH', 'C-2', 'dimensional', 7500, 75, 45, 25, 15, 10, 65.0, '{"notes": "Commercial intensive"}'),
  ('SATELLITE BEACH', 'I-1', 'dimensional', 10000, 100, 45, 30, 20, 15, 70.0, '{"notes": "Light industrial"}'),
  ('SATELLITE BEACH', 'PUD', 'dimensional', 20000, 150, 35, NULL, NULL, NULL, 40.0, '{"notes": "Planned Unit Development"}')
ON CONFLICT (jurisdiction, district) DO UPDATE
SET
  min_lot_size = EXCLUDED.min_lot_size,
  min_lot_width = EXCLUDED.min_lot_width,
  max_height = EXCLUDED.max_height,
  front_setback = EXCLUDED.front_setback,
  rear_setback = EXCLUDED.rear_setback,
  side_setback = EXCLUDED.side_setback,
  max_coverage = EXCLUDED.max_coverage,
  updated_at = NOW();

-- Indian Harbour Beach Districts
INSERT INTO zoning_requirements (jurisdiction, district, requirement_type, min_lot_size, min_lot_width, max_height, front_setback, rear_setback, side_setback, max_coverage, additional_requirements)
VALUES 
  ('INDIAN HARBOUR BEACH', 'R-1', 'dimensional', 7500, 75, 35, 25, 20, 10, 35.0, '{"notes": "Single-family residential"}'),
  ('INDIAN HARBOUR BEACH', 'R-1A', 'dimensional', 10000, 90, 35, 25, 25, 15, 30.0, '{"notes": "Single-family residential, waterfront"}'),
  ('INDIAN HARBOUR BEACH', 'R-2', 'dimensional', 5000, 50, 35, 25, 15, 7, 40.0, '{"notes": "Two-family residential"}'),
  ('INDIAN HARBOUR BEACH', 'R-3', 'dimensional', 12000, 100, 45, 25, 20, 10, 45.0, '{"notes": "Multi-family residential"}'),
  ('INDIAN HARBOUR BEACH', 'C-1', 'dimensional', 5000, 50, 45, 25, 10, 10, 65.0, '{"notes": "Commercial"}'),
  ('INDIAN HARBOUR BEACH', 'C-2', 'dimensional', 10000, 100, 45, 30, 15, 15, 70.0, '{"notes": "Commercial intensive"}')
ON CONFLICT (jurisdiction, district) DO UPDATE
SET
  min_lot_size = EXCLUDED.min_lot_size,
  min_lot_width = EXCLUDED.min_lot_width,
  max_height = EXCLUDED.max_height,
  front_setback = EXCLUDED.front_setback,
  rear_setback = EXCLUDED.rear_setback,
  side_setback = EXCLUDED.side_setback,
  max_coverage = EXCLUDED.max_coverage,
  updated_at = NOW();

-- Melbourne Districts
INSERT INTO zoning_requirements (jurisdiction, district, requirement_type, min_lot_size, min_lot_width, max_height, front_setback, rear_setback, side_setback, max_coverage, additional_requirements)
VALUES 
  ('MELBOURNE', 'RS-1', 'dimensional', 6000, 60, 35, 25, 15, 5, 40.0, '{"notes": "Single-family residential"}'),
  ('MELBOURNE', 'RS-2', 'dimensional', 7500, 75, 35, 25, 20, 7, 35.0, '{"notes": "Single-family residential, estate"}'),
  ('MELBOURNE', 'RM-4', 'dimensional', 10000, 100, 45, 25, 20, 10, 50.0, '{"notes": "Multi-family low density"}'),
  ('MELBOURNE', 'RM-6', 'dimensional', 12000, 100, 55, 25, 20, 10, 55.0, '{"notes": "Multi-family medium density"}'),
  ('MELBOURNE', 'C-1', 'dimensional', 5000, 50, 45, 20, 10, 10, 65.0, '{"notes": "Neighborhood commercial"}'),
  ('MELBOURNE', 'C-2', 'dimensional', 7500, 75, 60, 25, 15, 10, 70.0, '{"notes": "General commercial"}'),
  ('MELBOURNE', 'I-1', 'dimensional', 10000, 100, 45, 30, 20, 20, 75.0, '{"notes": "Light industrial"}')
ON CONFLICT (jurisdiction, district) DO UPDATE
SET
  min_lot_size = EXCLUDED.min_lot_size,
  min_lot_width = EXCLUDED.min_lot_width,
  max_height = EXCLUDED.max_height,
  front_setback = EXCLUDED.front_setback,
  rear_setback = EXCLUDED.rear_setback,
  side_setback = EXCLUDED.side_setback,
  max_coverage = EXCLUDED.max_coverage,
  updated_at = NOW();

-- Verify inserts
SELECT 
  jurisdiction, 
  COUNT(*) as districts,
  MIN(min_lot_size) as min_lot,
  MAX(min_lot_size) as max_lot
FROM zoning_requirements
GROUP BY jurisdiction
ORDER BY jurisdiction;
