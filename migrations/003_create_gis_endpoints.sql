-- Migration: Create GIS endpoints table for ZoneWise
-- Date: 2026-01-23

-- Create GIS endpoints table
CREATE TABLE IF NOT EXISTS public.gis_endpoints (
    id SERIAL PRIMARY KEY,
    jurisdiction_id INTEGER NOT NULL REFERENCES jurisdictions(id),
    jurisdiction_name VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('WORKING', 'TEMPORARY_OUTAGE', 'MANUAL_DATA', 'NO_FEATURE_SERVICE', 'UNVERIFIED', 'NOT_FOUND')),
    parcels INTEGER DEFAULT 0,
    url TEXT,
    zone_field VARCHAR(50),
    geometry_type VARCHAR(50),
    spatial_reference INTEGER,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(jurisdiction_id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_gis_endpoints_status ON public.gis_endpoints(status);
CREATE INDEX IF NOT EXISTS idx_gis_endpoints_jurisdiction ON public.gis_endpoints(jurisdiction_id);

-- Enable RLS
ALTER TABLE public.gis_endpoints ENABLE ROW LEVEL SECURITY;

-- Create policy for public read
CREATE POLICY "Public read access" ON public.gis_endpoints FOR SELECT USING (true);

-- Insert verified endpoints
INSERT INTO public.gis_endpoints (jurisdiction_id, jurisdiction_name, status, parcels, url, zone_field, geometry_type, spatial_reference, notes)
VALUES
    (13, 'Unincorporated Brevard County', 'WORKING', 75350, 'https://gis.brevardfl.gov/gissrv/rest/services/Planning_Development/Zoning_WKID2881/MapServer/0', 'ZONING', 'esriGeometryPolygon', 2881, 'County-maintained, covers all unincorporated areas'),
    (5, 'Cocoa', 'WORKING', 29882, 'https://services1.arcgis.com/Tex1uhbqnOZPx6qT/arcgis/rest/services/Public_View_Cocoa_Zoning_with_Split_Lots_June_2023_view/FeatureServer/1', 'Zoning', 'esriGeometryPolygon', 4326, 'ArcGIS Online hosted, includes split lots'),
    (4, 'Titusville', 'WORKING', 28118, 'https://gis.titusville.com/arcgis/rest/services/CommunityDevelopment/MapServer/15', 'Zone_Code', 'esriGeometryPolygon', 2881, 'City-maintained ArcGIS Server'),
    (2, 'Palm Bay', 'TEMPORARY_OUTAGE', 78697, 'https://gis.palmbayflorida.org/arcgis/rest/services/GrowthManagement/Zoning/MapServer/0', 'ZONING', 'esriGeometryPolygon', 2881, 'City-maintained, currently returning 503 errors (temporary)'),
    (14, 'Malabar', 'MANUAL_DATA', 1430, NULL, NULL, NULL, NULL, 'Zone data embedded in zoning_districts.description as PARCELS arrays'),
    (1, 'Melbourne', 'NO_FEATURE_SERVICE', 0, 'https://tiles.arcgis.com/tiles/QNOUArW14R0lClPo/arcgis/rest/services/ped_atlas_zoning/MapServer', NULL, NULL, NULL, 'Only tile service available (no spatial queries). Need to contact city for feature service.'),
    (8, 'Rockledge', 'UNVERIFIED', 0, 'https://gis-rockledge.cityofrockledge.org/server/rest/services/Planning_Building_Public_to_create_a_Web_App/MapServer', 'Zoning', NULL, NULL, 'Server exists but returning errors. Need to verify access.'),
    (3, 'Indian Harbour Beach', 'NOT_FOUND', 4496, NULL, NULL, NULL, NULL, 'No public GIS found. May use eLaws like Malabar.'),
    (6, 'Satellite Beach', 'NOT_FOUND', 0, NULL, NULL, NULL, NULL, 'No public GIS found. Uses eLaws for ordinances.'),
    (7, 'Cocoa Beach', 'NOT_FOUND', 0, NULL, NULL, NULL, NULL, 'No public GIS found.'),
    (9, 'West Melbourne', 'NOT_FOUND', 10365, NULL, NULL, NULL, NULL, 'Only PDF maps available on city website.'),
    (10, 'Cape Canaveral', 'NOT_FOUND', 7355, NULL, NULL, NULL, NULL, 'No public GIS found.'),
    (11, 'Indialantic', 'NOT_FOUND', 5205, NULL, NULL, NULL, NULL, 'No public GIS found. Uses eLaws for ordinances.'),
    (12, 'Melbourne Beach', 'NOT_FOUND', 7337, NULL, NULL, NULL, NULL, 'No public GIS found. Uses eLaws for ordinances.'),
    (15, 'Grant-Valkaria', 'NOT_FOUND', 3065, NULL, NULL, NULL, NULL, 'No public GIS found.'),
    (16, 'Palm Shores', 'NOT_FOUND', 433, NULL, NULL, NULL, NULL, 'Small town, no public GIS.'),
    (17, 'Melbourne Village', 'NOT_FOUND', 0, NULL, NULL, NULL, NULL, 'Small village, no public GIS.')
ON CONFLICT (jurisdiction_id) DO UPDATE SET
    status = EXCLUDED.status,
    parcels = EXCLUDED.parcels,
    url = EXCLUDED.url,
    zone_field = EXCLUDED.zone_field,
    geometry_type = EXCLUDED.geometry_type,
    spatial_reference = EXCLUDED.spatial_reference,
    notes = EXCLUDED.notes,
    updated_at = NOW();

-- Verification query
SELECT jurisdiction_name, status, parcels FROM public.gis_endpoints ORDER BY parcels DESC;
