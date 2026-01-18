"""ZoneWise Configuration"""
import os

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

GIS_PARCELS_URL = "https://services7.arcgis.com/BDKC97XHbtyzbfkd/ArcGIS/rest/services/Brevard_County_Parcels/FeatureServer/0/query"
GIS_ZONING_URL = "https://gis.brevardfl.gov/gissrv/rest/services/Planning_Development/Zoning_WKID2881/MapServer/0/query"

JURISDICTIONS = {
    1: "Melbourne",
    2: "Palm Bay", 
    3: "Indian Harbour Beach",
    4: "Titusville",
    5: "Cocoa",
    6: "Satellite Beach",
    7: "Cocoa Beach",
    8: "Rockledge",
    9: "West Melbourne",
    10: "Cape Canaveral",
    11: "Indialantic",
    12: "Melbourne Beach",
    13: "Brevard County (Unincorporated)",
    14: "Malabar",
    15: "Grant-Valkaria",
    16: "Palm Shores",
    17: "Melbourne Village"
}
