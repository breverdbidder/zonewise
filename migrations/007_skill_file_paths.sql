-- Migration 007: Add skill_file_path and co_no to jurisdictions
-- Generated: 2026-02-23 by Claude AI (Architect)

ALTER TABLE public.jurisdictions
  ADD COLUMN IF NOT EXISTS skill_file_path TEXT,
  ADD COLUMN IF NOT EXISTS co_no SMALLINT,
  ADD COLUMN IF NOT EXISTS skill_last_validated DATE;

CREATE INDEX IF NOT EXISTS idx_jurisdictions_co_no ON public.jurisdictions(co_no);

-- Map co_no for all 67 FL counties
UPDATE public.jurisdictions SET co_no = sub.co_no
FROM (VALUES
  ('Alachua',1),
  ('Baker',2),
  ('Bay',3),
  ('Bradford',4),
  ('Brevard',5),
  ('Broward',6),
  ('Calhoun',7),
  ('Charlotte',8),
  ('Citrus',9),
  ('Clay',10),
  ('Collier',11),
  ('Columbia',12),
  ('Miami-Dade',13),
  ('DeSoto',14),
  ('Dixie',15),
  ('Duval',16),
  ('Escambia',17),
  ('Flagler',18),
  ('Franklin',19),
  ('Gadsden',20),
  ('Gilchrist',21),
  ('Glades',22),
  ('Gulf',23),
  ('Hamilton',24),
  ('Hardee',25),
  ('Hendry',26),
  ('Hernando',27),
  ('Highlands',28),
  ('Hillsborough',29),
  ('Holmes',30),
  ('Indian River',31),
  ('Jackson',32),
  ('Jefferson',33),
  ('Lafayette',34),
  ('Lake',35),
  ('Lee',36),
  ('Leon',37),
  ('Levy',38),
  ('Liberty',39),
  ('Madison',40),
  ('Manatee',41),
  ('Marion',42),
  ('Martin',43),
  ('Monroe',44),
  ('Nassau',45),
  ('Okaloosa',46),
  ('Okeechobee',47),
  ('Orange',48),
  ('Osceola',49),
  ('Palm Beach',50),
  ('Pasco',51),
  ('Pinellas',52),
  ('Polk',53),
  ('Putnam',54),
  ('St. Johns',55),
  ('St. Lucie',56),
  ('Santa Rosa',57),
  ('Sarasota',58),
  ('Seminole',59),
  ('Sumter',60),
  ('Suwannee',61),
  ('Taylor',62),
  ('Union',63),
  ('Volusia',64),
  ('Wakulla',65),
  ('Walton',66),
  ('Washington',67)
) AS sub(county_name, co_no)
WHERE public.jurisdictions.county ILIKE '%' || sub.county_name || '%';

-- Set skill_file_path for all jurisdictions
UPDATE public.jurisdictions
SET skill_file_path = 'zonewise/skills/county-' ||
  LOWER(REGEXP_REPLACE(
    REPLACE(REPLACE(county, '.', ''), ' ', '-'),
    '[^a-z0-9-]', '', 'g'
  )) || '/SKILL.md'
WHERE county IS NOT NULL;

COMMENT ON COLUMN public.jurisdictions.skill_file_path IS 'Path to county SKILL.md in zonewise-desktop repo';
COMMENT ON COLUMN public.jurisdictions.co_no IS 'FDOR county number 1-67';
COMMENT ON COLUMN public.jurisdictions.skill_last_validated IS 'Date SKILL.md was last validated';
