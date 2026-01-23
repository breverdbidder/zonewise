-- ============================================================
-- ZONEWISE FK MIGRATION
-- Add foreign key constraints for data integrity
-- Run in Supabase SQL Editor: https://supabase.com/dashboard/project/mocerqjnksmhcjzxrewo/sql/new
-- ============================================================

-- Step 1: Add unique constraint on zoning_districts (jurisdiction_id, code)
-- Required for composite FK reference
ALTER TABLE zoning_districts 
ADD CONSTRAINT uq_zoning_districts_jurisdiction_code 
UNIQUE (jurisdiction_id, code);

-- Step 2: Add FK from sample_properties.jurisdiction_id to jurisdictions.id
ALTER TABLE sample_properties 
ADD CONSTRAINT fk_sample_properties_jurisdiction 
FOREIGN KEY (jurisdiction_id) 
REFERENCES jurisdictions(id) 
ON DELETE RESTRICT 
ON UPDATE CASCADE;

-- Step 3: Add composite FK from sample_properties (jurisdiction_id, zone_code) 
-- to zoning_districts (jurisdiction_id, code)
ALTER TABLE sample_properties 
ADD CONSTRAINT fk_sample_properties_zone 
FOREIGN KEY (jurisdiction_id, zone_code) 
REFERENCES zoning_districts(jurisdiction_id, code) 
ON DELETE RESTRICT 
ON UPDATE CASCADE;

-- Step 4: Create indexes for FK performance
CREATE INDEX IF NOT EXISTS idx_sample_properties_jurisdiction_id 
ON sample_properties(jurisdiction_id);

CREATE INDEX IF NOT EXISTS idx_sample_properties_zone_code 
ON sample_properties(zone_code);

CREATE INDEX IF NOT EXISTS idx_sample_properties_jurisdiction_zone 
ON sample_properties(jurisdiction_id, zone_code);

-- ============================================================
-- VERIFICATION QUERIES (Run after migration)
-- ============================================================

-- Check FK constraints exist
SELECT 
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_name = 'sample_properties';

-- Check indexes exist
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'sample_properties' 
    AND indexname LIKE 'idx_sample_properties%';
