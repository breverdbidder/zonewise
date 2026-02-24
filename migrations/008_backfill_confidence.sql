-- Migration 008: Backfill NULL confidence_score in zone_standards
-- Based on key field completeness (front/rear/side setback, height, lot, coverage)
-- Only updates rows where confidence_score IS NULL
-- Does NOT touch 1,109 rows that already have scores set

UPDATE public.zone_standards
SET confidence_score = CASE
  -- 5-6 of 6 key fields populated → same confidence as AgentQL-scraped rows
  WHEN (
    (CASE WHEN front_setback_ft     IS NOT NULL THEN 1 ELSE 0 END) +
    (CASE WHEN rear_setback_ft      IS NOT NULL THEN 1 ELSE 0 END) +
    (CASE WHEN side_setback_ft      IS NOT NULL THEN 1 ELSE 0 END) +
    (CASE WHEN max_height_ft        IS NOT NULL THEN 1 ELSE 0 END) +
    (CASE WHEN min_lot_sqft         IS NOT NULL THEN 1 ELSE 0 END) +
    (CASE WHEN max_lot_coverage_pct IS NOT NULL THEN 1 ELSE 0 END)
  ) >= 5 THEN 0.70

  -- 3-4 key fields populated → partial data
  WHEN (
    (CASE WHEN front_setback_ft     IS NOT NULL THEN 1 ELSE 0 END) +
    (CASE WHEN rear_setback_ft      IS NOT NULL THEN 1 ELSE 0 END) +
    (CASE WHEN side_setback_ft      IS NOT NULL THEN 1 ELSE 0 END) +
    (CASE WHEN max_height_ft        IS NOT NULL THEN 1 ELSE 0 END) +
    (CASE WHEN min_lot_sqft         IS NOT NULL THEN 1 ELSE 0 END) +
    (CASE WHEN max_lot_coverage_pct IS NOT NULL THEN 1 ELSE 0 END)
  ) >= 3 THEN 0.60

  -- 1-2 key fields → sparse data
  WHEN (
    (CASE WHEN front_setback_ft     IS NOT NULL THEN 1 ELSE 0 END) +
    (CASE WHEN rear_setback_ft      IS NOT NULL THEN 1 ELSE 0 END) +
    (CASE WHEN side_setback_ft      IS NOT NULL THEN 1 ELSE 0 END) +
    (CASE WHEN max_height_ft        IS NOT NULL THEN 1 ELSE 0 END) +
    (CASE WHEN min_lot_sqft         IS NOT NULL THEN 1 ELSE 0 END) +
    (CASE WHEN max_lot_coverage_pct IS NOT NULL THEN 1 ELSE 0 END)
  ) >= 1 THEN 0.45

  -- 0 key fields → leave NULL (no data to score)
  ELSE NULL
END
WHERE confidence_score IS NULL;
