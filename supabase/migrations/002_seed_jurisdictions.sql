-- Seed: 002_seed_jurisdictions.sql
-- Created: 2026-01-13
-- Description: Insert 17 Brevard County jurisdictions

-- Insert all 17 Brevard County jurisdictions
INSERT INTO jurisdictions (id, full_name, abbreviation, ordinance_url, zoning_map_url, contact_email, contact_phone, office_hours, parser_version) VALUES
(
    'indian_harbour_beach',
    'Indian Harbour Beach',
    'IHB',
    'https://library.municode.com/fl/indian_harbour_beach/codes/code_of_ordinances',
    'https://ihb.maps.arcgis.com/apps/webappviewer/index.html',
    'planning@ihb-fl.gov',
    '(321) 773-2200',
    'Monday-Friday 8:00 AM - 4:30 PM',
    'municode_v2'
),
(
    'melbourne',
    'City of Melbourne',
    'MEL',
    'https://library.municode.com/fl/melbourne/codes/code_of_ordinances',
    'https://melbourne.maps.arcgis.com/apps/webappviewer/',
    'planning@melbourneflorida.org',
    '(321) 608-7500',
    'Monday-Friday 8:00 AM - 5:00 PM',
    'municode_v2'
),
(
    'palm_bay',
    'City of Palm Bay',
    'PB',
    'https://library.municode.com/fl/palm_bay/codes/code_of_ordinances',
    'https://www.palmbayflorida.org/our-city/departments/planning-zoning',
    'planning@palmbayflorida.org',
    '(321) 952-3410',
    'Monday-Friday 8:00 AM - 5:00 PM',
    'municode_v2'
),
(
    'cocoa',
    'City of Cocoa',
    'COC',
    'https://library.municode.com/fl/cocoa/codes/code_of_ordinances',
    'https://www.cocoafl.org/departments/growth-management',
    'planning@cocoafl.org',
    '(321) 433-8600',
    'Monday-Friday 8:00 AM - 5:00 PM',
    'municode_v2'
),
(
    'cocoa_beach',
    'City of Cocoa Beach',
    'CB',
    'https://library.municode.com/fl/cocoa_beach/codes/code_of_ordinances',
    'https://www.cityofcocoabeach.com/planning-zoning',
    'planning@cityofcocoabeach.com',
    '(321) 868-3258',
    'Monday-Friday 8:00 AM - 5:00 PM',
    'municode_v2'
),
(
    'rockledge',
    'City of Rockledge',
    'ROC',
    'https://library.municode.com/fl/rockledge/codes/code_of_ordinances',
    'https://www.cityofrockledge.org/planning',
    'planning@cityofrockledge.org',
    '(321) 690-3978',
    'Monday-Friday 8:00 AM - 5:00 PM',
    'municode_v2'
),
(
    'titusville',
    'City of Titusville',
    'TIT',
    'https://library.municode.com/fl/titusville/codes/code_of_ordinances',
    'https://www.titusville.com/planning-zoning',
    'planning@titusville.com',
    '(321) 567-3774',
    'Monday-Friday 8:00 AM - 5:00 PM',
    'municode_v2'
),
(
    'satellite_beach',
    'City of Satellite Beach',
    'SAT',
    'https://library.municode.com/fl/satellite_beach/codes/code_of_ordinances',
    'https://www.satellitebeach.org/planning',
    'planning@satellitebeach.org',
    '(321) 773-4407',
    'Monday-Friday 8:00 AM - 5:00 PM',
    'municode_v2'
),
(
    'west_melbourne',
    'City of West Melbourne',
    'WM',
    'https://library.municode.com/fl/west_melbourne/codes/code_of_ordinances',
    'https://www.westmelbourne.org/planning',
    'planning@westmelbourne.org',
    '(321) 837-7774',
    'Monday-Friday 8:00 AM - 5:00 PM',
    'municode_v2'
),
(
    'cape_canaveral',
    'City of Cape Canaveral',
    'CC',
    'https://library.municode.com/fl/cape_canaveral/codes/code_of_ordinances',
    'https://www.cityofcapecanaveral.org/planning',
    'planning@cityofcapecanaveral.org',
    '(321) 868-1220',
    'Monday-Friday 8:00 AM - 5:00 PM',
    'municode_v2'
),
(
    'malabar',
    'Town of Malabar',
    'MAL',
    'https://library.municode.com/fl/malabar/codes/code_of_ordinances',
    'https://www.malabarflorida.org/planning',
    'planning@malabarflorida.org',
    '(321) 727-7764',
    'Monday-Friday 9:00 AM - 5:00 PM',
    'municode_v2'
),
(
    'grant_valkaria',
    'Town of Grant-Valkaria',
    'GV',
    'https://library.municode.com/fl/grant-valkaria/codes/code_of_ordinances',
    'https://www.grantfl.us/planning',
    'planning@grantfl.us',
    '(321) 723-8696',
    'Monday-Friday 9:00 AM - 5:00 PM',
    'municode_v2'
),
(
    'indialantic',
    'Town of Indialantic',
    'IND',
    'https://library.municode.com/fl/indialantic/codes/code_of_ordinances',
    'https://www.indialantic.com/planning',
    'planning@indialantic.com',
    '(321) 723-2242',
    'Monday-Friday 8:00 AM - 5:00 PM',
    'municode_v2'
),
(
    'melbourne_beach',
    'Town of Melbourne Beach',
    'MB',
    'https://library.municode.com/fl/melbourne_beach/codes/code_of_ordinances',
    'https://www.melbournebeachfl.org/planning',
    'planning@melbournebeachfl.org',
    '(321) 724-5860',
    'Monday-Friday 8:00 AM - 4:30 PM',
    'municode_v2'
),
(
    'melbourne_village',
    'Town of Melbourne Village',
    'MV',
    'https://library.municode.com/fl/melbourne_village/codes/code_of_ordinances',
    'https://www.melbournevillage-fl.gov/planning',
    'planning@melbournevillage-fl.gov',
    '(321) 723-5462',
    'Monday-Friday 9:00 AM - 4:00 PM',
    'municode_v2'
),
(
    'palm_shores',
    'Town of Palm Shores',
    'PS',
    'https://library.municode.com/fl/palm_shores/codes/code_of_ordinances',
    'https://www.palmshores.com/planning',
    'planning@palmshores.com',
    '(321) 984-4420',
    'Monday-Friday 9:00 AM - 4:00 PM',
    'municode_v2'
),
(
    'brevard_county_unincorporated',
    'Brevard County (Unincorporated Areas)',
    'BC',
    'https://library.municode.com/fl/brevard_county/codes/code_of_ordinances',
    'https://www.brevardfl.gov/PlanningAndDevelopment/Zoning',
    'planning@brevardfl.gov',
    '(321) 633-2069',
    'Monday-Friday 8:00 AM - 5:00 PM',
    'municode_v2'
);

-- Verify insertion
SELECT COUNT(*) as jurisdiction_count FROM jurisdictions;

-- Display all jurisdictions
SELECT id, full_name, abbreviation FROM jurisdictions ORDER BY full_name;
