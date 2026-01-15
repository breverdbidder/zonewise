#!/usr/bin/env python3
"""
Comprehensive Brevard County Zoning Data Seed
All 17 jurisdictions with enhanced features:
- Setbacks (front, rear, side, corner)
- Height (max feet, max stories)
- Parking requirements
- Lot coverage
- FAR
- Density
"""

import urllib.request
import ssl
import json
from datetime import datetime

SUPABASE_URL = "https://mocerqjnksmhcjzxrewo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1vY2VycWpua3NtaGNqenhyZXdvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDUzMjUyNiwiZXhwIjoyMDgwMTA4NTI2fQ.fL255mO0V8-rrU0Il3L41cIdQXUau-HRQXiamTqp9nE"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# All 17 Brevard County Jurisdictions with comprehensive zoning data
JURISDICTIONS = {
    # 1. BREVARD COUNTY (Unincorporated)
    "BREVARD COUNTY": [
        {"district": "AU", "name": "Agricultural", "min_lot_size": 217800, "min_lot_width": 150, "max_height": 35, "front_setback": 50, "rear_setback": 30, "side_setback": 20, "max_coverage": 20.0, "additional": {"corner_setback": 30, "max_stories": 2, "parking_residential": 2, "density_max": 1, "min_dwelling_size": 1000, "notes": "Agricultural, single-family"}},
        {"district": "EU", "name": "Estate Residential", "min_lot_size": 43560, "min_lot_width": 100, "max_height": 35, "front_setback": 35, "rear_setback": 25, "side_setback": 15, "max_coverage": 30.0, "additional": {"corner_setback": 25, "max_stories": 2, "parking_residential": 2, "density_max": 1, "min_dwelling_size": 1200, "notes": "Estate, large lot residential"}},
        {"district": "GU", "name": "General Residential", "min_lot_size": 10000, "min_lot_width": 80, "max_height": 35, "front_setback": 25, "rear_setback": 20, "side_setback": 10, "max_coverage": 40.0, "additional": {"corner_setback": 20, "max_stories": 2, "parking_residential": 2, "density_max": 4, "min_dwelling_size": 1000, "notes": "General residential, single-family"}},
        {"district": "RU-1", "name": "Single-Family Residential", "min_lot_size": 7500, "min_lot_width": 75, "max_height": 35, "front_setback": 25, "rear_setback": 20, "side_setback": 8, "max_coverage": 45.0, "additional": {"corner_setback": 15, "max_stories": 2, "parking_residential": 2, "density_max": 6, "min_dwelling_size": 900, "notes": "Standard single-family"}},
        {"district": "RU-2", "name": "Multi-Family Residential", "min_lot_size": 10000, "min_lot_width": 100, "max_height": 45, "front_setback": 25, "rear_setback": 25, "side_setback": 10, "max_coverage": 50.0, "additional": {"corner_setback": 20, "max_stories": 3, "parking_residential": 1.5, "density_max": 15, "min_dwelling_size": 600, "notes": "Apartments, townhomes"}},
        {"district": "BU-1", "name": "Neighborhood Commercial", "min_lot_size": 10000, "min_lot_width": 100, "max_height": 35, "front_setback": 25, "rear_setback": 20, "side_setback": 10, "max_coverage": 60.0, "additional": {"corner_setback": 20, "max_stories": 2, "parking_commercial": 4, "floor_area_ratio": 0.5, "notes": "Neighborhood retail, office"}},
        {"district": "BU-2", "name": "General Commercial", "min_lot_size": 15000, "min_lot_width": 100, "max_height": 45, "front_setback": 30, "rear_setback": 20, "side_setback": 10, "max_coverage": 70.0, "additional": {"corner_setback": 20, "max_stories": 3, "parking_commercial": 4, "floor_area_ratio": 1.0, "notes": "General commercial, retail"}},
        {"district": "IU", "name": "Industrial", "min_lot_size": 20000, "min_lot_width": 100, "max_height": 50, "front_setback": 35, "rear_setback": 25, "side_setback": 15, "max_coverage": 60.0, "additional": {"corner_setback": 25, "max_stories": 3, "parking_commercial": 2, "floor_area_ratio": 1.5, "notes": "Light/heavy industrial"}},
    ],
    
    # 2. CAPE CANAVERAL
    "CAPE CANAVERAL": [
        {"district": "R-1", "name": "Single-Family Residential", "min_lot_size": 7500, "min_lot_width": 75, "max_height": 35, "front_setback": 25, "rear_setback": 20, "side_setback": 8, "max_coverage": 40.0, "additional": {"corner_setback": 15, "max_stories": 2, "parking_residential": 2, "density_max": 6, "min_dwelling_size": 1000, "notes": "Single-family residential"}},
        {"district": "R-2", "name": "Two-Family Residential", "min_lot_size": 6000, "min_lot_width": 60, "max_height": 35, "front_setback": 25, "rear_setback": 15, "side_setback": 8, "max_coverage": 45.0, "additional": {"corner_setback": 15, "max_stories": 2, "parking_residential": 2, "density_max": 10, "min_dwelling_size": 850, "notes": "Duplex permitted"}},
        {"district": "R-3", "name": "Multi-Family Residential", "min_lot_size": 10000, "min_lot_width": 100, "max_height": 60, "front_setback": 25, "rear_setback": 25, "side_setback": 15, "max_coverage": 50.0, "additional": {"corner_setback": 20, "max_stories": 5, "parking_residential": 1.5, "density_max": 20, "min_dwelling_size": 600, "notes": "High-rise permitted near beach"}},
        {"district": "C-1", "name": "Local Commercial", "min_lot_size": 10000, "min_lot_width": 100, "max_height": 35, "front_setback": 25, "rear_setback": 15, "side_setback": 10, "max_coverage": 60.0, "additional": {"corner_setback": 15, "max_stories": 2, "parking_commercial": 4, "floor_area_ratio": 0.5, "notes": "Local retail, service"}},
        {"district": "C-2", "name": "General Commercial", "min_lot_size": 15000, "min_lot_width": 100, "max_height": 60, "front_setback": 25, "rear_setback": 20, "side_setback": 10, "max_coverage": 65.0, "additional": {"corner_setback": 20, "max_stories": 5, "parking_commercial": 4, "floor_area_ratio": 1.5, "notes": "General commercial, A1A corridor"}},
        {"district": "I-1", "name": "Light Industrial", "min_lot_size": 20000, "min_lot_width": 100, "max_height": 45, "front_setback": 30, "rear_setback": 25, "side_setback": 15, "max_coverage": 55.0, "additional": {"corner_setback": 25, "max_stories": 3, "parking_commercial": 2, "floor_area_ratio": 1.0, "notes": "Light industrial, warehouse"}},
    ],
    
    # 3. COCOA
    "COCOA": [
        {"district": "RS-1", "name": "Single-Family Estate", "min_lot_size": 10000, "min_lot_width": 85, "max_height": 35, "front_setback": 30, "rear_setback": 25, "side_setback": 10, "max_coverage": 35.0, "additional": {"corner_setback": 20, "max_stories": 2, "parking_residential": 2, "density_max": 4, "min_dwelling_size": 1400, "notes": "Large lot single-family"}},
        {"district": "RS-2", "name": "Single-Family Standard", "min_lot_size": 7500, "min_lot_width": 70, "max_height": 35, "front_setback": 25, "rear_setback": 20, "side_setback": 8, "max_coverage": 40.0, "additional": {"corner_setback": 15, "max_stories": 2, "parking_residential": 2, "density_max": 6, "min_dwelling_size": 1000, "notes": "Standard single-family"}},
        {"district": "RS-3", "name": "Single-Family Small Lot", "min_lot_size": 6000, "min_lot_width": 60, "max_height": 35, "front_setback": 20, "rear_setback": 15, "side_setback": 5, "max_coverage": 45.0, "additional": {"corner_setback": 15, "max_stories": 2, "parking_residential": 2, "density_max": 7, "min_dwelling_size": 900, "notes": "Small lot single-family"}},
        {"district": "RM-1", "name": "Multi-Family Low", "min_lot_size": 8500, "min_lot_width": 80, "max_height": 35, "front_setback": 25, "rear_setback": 20, "side_setback": 10, "max_coverage": 45.0, "additional": {"corner_setback": 20, "max_stories": 2, "parking_residential": 2, "density_max": 12, "min_dwelling_size": 700, "notes": "Low-density multi-family"}},
        {"district": "RM-2", "name": "Multi-Family Medium", "min_lot_size": 10000, "min_lot_width": 100, "max_height": 45, "front_setback": 25, "rear_setback": 25, "side_setback": 15, "max_coverage": 50.0, "additional": {"corner_setback": 20, "max_stories": 3, "parking_residential": 1.5, "density_max": 18, "min_dwelling_size": 600, "notes": "Medium-density apartments"}},
        {"district": "C-1", "name": "Neighborhood Commercial", "min_lot_size": 7500, "min_lot_width": 75, "max_height": 35, "front_setback": 20, "rear_setback": 15, "side_setback": 10, "max_coverage": 60.0, "additional": {"corner_setback": 15, "max_stories": 2, "parking_commercial": 4, "floor_area_ratio": 0.5, "notes": "Neighborhood retail"}},
        {"district": "C-2", "name": "General Commercial", "min_lot_size": 10000, "min_lot_width": 100, "max_height": 45, "front_setback": 25, "rear_setback": 20, "side_setback": 10, "max_coverage": 70.0, "additional": {"corner_setback": 20, "max_stories": 3, "parking_commercial": 4, "floor_area_ratio": 1.0, "notes": "US-1 corridor commercial"}},
        {"district": "I-1", "name": "Light Industrial", "min_lot_size": 15000, "min_lot_width": 100, "max_height": 50, "front_setback": 30, "rear_setback": 25, "side_setback": 15, "max_coverage": 55.0, "additional": {"corner_setback": 25, "max_stories": 3, "parking_commercial": 2, "floor_area_ratio": 1.0, "notes": "Light industrial"}},
        {"district": "PUD", "name": "Planned Unit Development", "min_lot_size": 43560, "min_lot_width": 100, "max_height": 45, "front_setback": 25, "rear_setback": 25, "side_setback": 15, "max_coverage": 50.0, "additional": {"corner_setback": 20, "max_stories": 3, "parking_residential": 2, "parking_commercial": 4, "notes": "Flexible mixed-use"}},
    ],
    
    # 4. COCOA BEACH
    "COCOA BEACH": [
        {"district": "RS", "name": "Single-Family Residential", "min_lot_size": 6000, "min_lot_width": 60, "max_height": 35, "front_setback": 25, "rear_setback": 20, "side_setback": 8, "max_coverage": 40.0, "additional": {"corner_setback": 15, "max_stories": 2, "parking_residential": 2, "density_max": 7, "min_dwelling_size": 900, "notes": "Beach community single-family"}},
        {"district": "RD", "name": "Duplex Residential", "min_lot_size": 5000, "min_lot_width": 50, "max_height": 35, "front_setback": 25, "rear_setback": 15, "side_setback": 5, "max_coverage": 45.0, "additional": {"corner_setback": 15, "max_stories": 2, "parking_residential": 2, "density_max": 10, "min_dwelling_size": 800, "notes": "Duplex permitted"}},
        {"district": "RM-1", "name": "Multi-Family Low", "min_lot_size": 7500, "min_lot_width": 75, "max_height": 45, "front_setback": 25, "rear_setback": 20, "side_setback": 10, "max_coverage": 50.0, "additional": {"corner_setback": 15, "max_stories": 3, "parking_residential": 1.5, "density_max": 15, "min_dwelling_size": 700, "notes": "Low-rise apartments"}},
        {"district": "RM-2", "name": "Multi-Family High", "min_lot_size": 10000, "min_lot_width": 100, "max_height": 75, "front_setback": 25, "rear_setback": 25, "side_setback": 15, "max_coverage": 55.0, "additional": {"corner_setback": 20, "max_stories": 6, "parking_residential": 1.5, "density_max": 30, "min_dwelling_size": 600, "notes": "High-rise beachfront condos"}},
        {"district": "C-1", "name": "Local Commercial", "min_lot_size": 7500, "min_lot_width": 75, "max_height": 35, "front_setback": 20, "rear_setback": 15, "side_setback": 10, "max_coverage": 65.0, "additional": {"corner_setback": 15, "max_stories": 2, "parking_commercial": 5, "floor_area_ratio": 0.5, "notes": "Local retail, tourist"}},
        {"district": "C-2", "name": "General Commercial", "min_lot_size": 10000, "min_lot_width": 100, "max_height": 60, "front_setback": 25, "rear_setback": 20, "side_setback": 10, "max_coverage": 70.0, "additional": {"corner_setback": 20, "max_stories": 5, "parking_commercial": 5, "floor_area_ratio": 1.5, "notes": "A1A corridor commercial"}},
        {"district": "MU", "name": "Mixed Use", "min_lot_size": 10000, "min_lot_width": 100, "max_height": 65, "front_setback": 20, "rear_setback": 20, "side_setback": 10, "max_coverage": 65.0, "additional": {"corner_setback": 15, "max_stories": 5, "parking_residential": 1.5, "parking_commercial": 4, "floor_area_ratio": 2.0, "notes": "Downtown mixed-use"}},
    ],
    
    # 5. GRANT-VALKARIA
    "GRANT-VALKARIA": [
        {"district": "AG", "name": "Agricultural", "min_lot_size": 217800, "min_lot_width": 200, "max_height": 35, "front_setback": 75, "rear_setback": 50, "side_setback": 30, "max_coverage": 15.0, "additional": {"corner_setback": 50, "max_stories": 2, "parking_residential": 2, "density_max": 0.2, "min_dwelling_size": 1200, "notes": "Agricultural, farming"}},
        {"district": "RE", "name": "Rural Estate", "min_lot_size": 87120, "min_lot_width": 150, "max_height": 35, "front_setback": 50, "rear_setback": 40, "side_setback": 25, "max_coverage": 20.0, "additional": {"corner_setback": 35, "max_stories": 2, "parking_residential": 2, "density_max": 0.5, "min_dwelling_size": 1400, "notes": "Rural estate lots"}},
        {"district": "R-1", "name": "Single-Family Residential", "min_lot_size": 43560, "min_lot_width": 100, "max_height": 35, "front_setback": 35, "rear_setback": 30, "side_setback": 15, "max_coverage": 25.0, "additional": {"corner_setback": 25, "max_stories": 2, "parking_residential": 2, "density_max": 1, "min_dwelling_size": 1200, "notes": "1-acre minimum residential"}},
        {"district": "C-1", "name": "Neighborhood Commercial", "min_lot_size": 20000, "min_lot_width": 100, "max_height": 35, "front_setback": 35, "rear_setback": 25, "side_setback": 15, "max_coverage": 40.0, "additional": {"corner_setback": 25, "max_stories": 2, "parking_commercial": 4, "floor_area_ratio": 0.3, "notes": "Limited commercial"}},
    ],
    
    # 6. INDIALANTIC
    "INDIALANTIC": [
        {"district": "R-1", "name": "Single-Family Residential", "min_lot_size": 7500, "min_lot_width": 75, "max_height": 35, "front_setback": 25, "rear_setback": 25, "side_setback": 8, "max_coverage": 35.0, "additional": {"corner_setback": 15, "max_stories": 2, "parking_residential": 2, "density_max": 5, "min_dwelling_size": 1200, "notes": "Beachside single-family"}},
        {"district": "R-1A", "name": "Single-Family Large Lot", "min_lot_size": 10000, "min_lot_width": 90, "max_height": 35, "front_setback": 30, "rear_setback": 30, "side_setback": 10, "max_coverage": 30.0, "additional": {"corner_setback": 20, "max_stories": 2, "parking_residential": 2, "density_max": 4, "min_dwelling_size": 1400, "notes": "Larger beachside lots"}},
        {"district": "R-2", "name": "Two-Family Residential", "min_lot_size": 6000, "min_lot_width": 60, "max_height": 35, "front_setback": 25, "rear_setback": 20, "side_setback": 8, "max_coverage": 40.0, "additional": {"corner_setback": 15, "max_stories": 2, "parking_residential": 2, "density_max": 7, "min_dwelling_size": 900, "notes": "Duplex permitted"}},
        {"district": "R-3", "name": "Multi-Family Residential", "min_lot_size": 10000, "min_lot_width": 100, "max_height": 45, "front_setback": 25, "rear_setback": 25, "side_setback": 13, "max_coverage": 45.0, "additional": {"corner_setback": 20, "max_stories": 3, "parking_residential": 1.5, "density_max": 15, "min_dwelling_size": 700, "notes": "Multi-family near beach"}},
        {"district": "C-1", "name": "Local Commercial", "min_lot_size": 7500, "min_lot_width": 75, "max_height": 35, "front_setback": 20, "rear_setback": 15, "side_setback": 10, "max_coverage": 55.0, "additional": {"corner_setback": 15, "max_stories": 2, "parking_commercial": 5, "floor_area_ratio": 0.5, "notes": "A1A local retail"}},
        {"district": "C-2", "name": "General Commercial", "min_lot_size": 10000, "min_lot_width": 100, "max_height": 45, "front_setback": 25, "rear_setback": 20, "side_setback": 10, "max_coverage": 60.0, "additional": {"corner_setback": 20, "max_stories": 3, "parking_commercial": 4, "floor_area_ratio": 1.0, "notes": "General commercial"}},
    ],
    
    # 7. MALABAR
    "MALABAR": [
        {"district": "AG", "name": "Agricultural", "min_lot_size": 130680, "min_lot_width": 150, "max_height": 35, "front_setback": 50, "rear_setback": 40, "side_setback": 25, "max_coverage": 20.0, "additional": {"corner_setback": 35, "max_stories": 2, "parking_residential": 2, "density_max": 0.33, "min_dwelling_size": 1000, "notes": "3-acre minimum agricultural"}},
        {"district": "RE", "name": "Rural Estate", "min_lot_size": 65340, "min_lot_width": 125, "max_height": 35, "front_setback": 40, "rear_setback": 35, "side_setback": 20, "max_coverage": 25.0, "additional": {"corner_setback": 30, "max_stories": 2, "parking_residential": 2, "density_max": 0.66, "min_dwelling_size": 1200, "notes": "1.5-acre minimum estate"}},
        {"district": "R-1", "name": "Single-Family Residential", "min_lot_size": 43560, "min_lot_width": 100, "max_height": 35, "front_setback": 35, "rear_setback": 30, "side_setback": 15, "max_coverage": 30.0, "additional": {"corner_setback": 25, "max_stories": 2, "parking_residential": 2, "density_max": 1, "min_dwelling_size": 1200, "notes": "1-acre minimum single-family"}},
        {"district": "R-2", "name": "Single-Family Medium", "min_lot_size": 21780, "min_lot_width": 85, "max_height": 35, "front_setback": 30, "rear_setback": 25, "side_setback": 13, "max_coverage": 35.0, "additional": {"corner_setback": 20, "max_stories": 2, "parking_residential": 2, "density_max": 2, "min_dwelling_size": 1000, "notes": "Half-acre minimum"}},
        {"district": "C-1", "name": "Limited Commercial", "min_lot_size": 20000, "min_lot_width": 100, "max_height": 35, "front_setback": 35, "rear_setback": 25, "side_setback": 15, "max_coverage": 40.0, "additional": {"corner_setback": 25, "max_stories": 2, "parking_commercial": 4, "floor_area_ratio": 0.3, "notes": "US-1 limited commercial"}},
    ],
    
    # 8. MELBOURNE BEACH
    "MELBOURNE BEACH": [
        {"district": "R-1", "name": "Single-Family Residential", "min_lot_size": 7500, "min_lot_width": 75, "max_height": 35, "front_setback": 25, "rear_setback": 20, "side_setback": 8, "max_coverage": 35.0, "additional": {"corner_setback": 15, "max_stories": 2, "parking_residential": 2, "density_max": 5, "min_dwelling_size": 1200, "notes": "Beach town single-family"}},
        {"district": "R-2", "name": "Two-Family Residential", "min_lot_size": 6000, "min_lot_width": 60, "max_height": 35, "front_setback": 25, "rear_setback": 15, "side_setback": 8, "max_coverage": 40.0, "additional": {"corner_setback": 15, "max_stories": 2, "parking_residential": 2, "density_max": 7, "min_dwelling_size": 900, "notes": "Duplex permitted"}},
        {"district": "R-3", "name": "Multi-Family Residential", "min_lot_size": 10000, "min_lot_width": 100, "max_height": 45, "front_setback": 25, "rear_setback": 25, "side_setback": 10, "max_coverage": 45.0, "additional": {"corner_setback": 20, "max_stories": 3, "parking_residential": 1.5, "density_max": 12, "min_dwelling_size": 700, "notes": "Oceanfront multi-family"}},
        {"district": "C-1", "name": "Commercial", "min_lot_size": 7500, "min_lot_width": 75, "max_height": 35, "front_setback": 20, "rear_setback": 15, "side_setback": 10, "max_coverage": 55.0, "additional": {"corner_setback": 15, "max_stories": 2, "parking_commercial": 5, "floor_area_ratio": 0.5, "notes": "Town center commercial"}},
    ],
    
    # 9. MELBOURNE VILLAGE
    "MELBOURNE VILLAGE": [
        {"district": "R-1", "name": "Single-Family Low Density", "min_lot_size": 15000, "min_lot_width": 100, "max_height": 35, "front_setback": 35, "rear_setback": 30, "side_setback": 15, "max_coverage": 25.0, "additional": {"corner_setback": 25, "max_stories": 2, "parking_residential": 2, "density_max": 2.9, "min_dwelling_size": 1400, "notes": "Village character preservation"}},
        {"district": "R-2", "name": "Single-Family Medium Density", "min_lot_size": 10000, "min_lot_width": 80, "max_height": 35, "front_setback": 30, "rear_setback": 25, "side_setback": 13, "max_coverage": 30.0, "additional": {"corner_setback": 20, "max_stories": 2, "parking_residential": 2, "density_max": 4, "min_dwelling_size": 1200, "notes": "Traditional village residential"}},
    ],
    
    # 10. PALM BAY
    "PALM BAY": [
        {"district": "RS-1", "name": "Single-Family Estate", "min_lot_size": 15000, "min_lot_width": 100, "max_height": 35, "front_setback": 30, "rear_setback": 25, "side_setback": 10, "max_coverage": 35.0, "additional": {"corner_setback": 20, "max_stories": 2, "parking_residential": 2, "density_max": 3, "min_dwelling_size": 1500, "notes": "Estate single-family"}},
        {"district": "RS-2", "name": "Single-Family Standard", "min_lot_size": 7500, "min_lot_width": 75, "max_height": 35, "front_setback": 25, "rear_setback": 20, "side_setback": 8, "max_coverage": 40.0, "additional": {"corner_setback": 15, "max_stories": 2, "parking_residential": 2, "density_max": 6, "min_dwelling_size": 1000, "notes": "Standard single-family"}},
        {"district": "RS-3", "name": "Single-Family Small Lot", "min_lot_size": 6000, "min_lot_width": 60, "max_height": 35, "front_setback": 20, "rear_setback": 15, "side_setback": 5, "max_coverage": 45.0, "additional": {"corner_setback": 15, "max_stories": 2, "parking_residential": 2, "density_max": 7, "min_dwelling_size": 900, "notes": "Compact single-family"}},
        {"district": "RM-4", "name": "Multi-Family Low", "min_lot_size": 6000, "min_lot_width": 70, "max_height": 35, "front_setback": 25, "rear_setback": 20, "side_setback": 10, "max_coverage": 45.0, "additional": {"corner_setback": 15, "max_stories": 2, "parking_residential": 2, "density_max": 10, "min_dwelling_size": 800, "notes": "Low-density multi-family"}},
        {"district": "RM-6", "name": "Multi-Family Medium", "min_lot_size": 8000, "min_lot_width": 80, "max_height": 45, "front_setback": 25, "rear_setback": 25, "side_setback": 13, "max_coverage": 50.0, "additional": {"corner_setback": 20, "max_stories": 3, "parking_residential": 1.5, "density_max": 15, "min_dwelling_size": 650, "notes": "Medium-density apartments"}},
        {"district": "RM-10", "name": "Multi-Family High", "min_lot_size": 10000, "min_lot_width": 100, "max_height": 55, "front_setback": 30, "rear_setback": 30, "side_setback": 15, "max_coverage": 55.0, "additional": {"corner_setback": 25, "max_stories": 4, "parking_residential": 1.5, "density_max": 20, "min_dwelling_size": 600, "notes": "High-density apartments"}},
        {"district": "CN", "name": "Neighborhood Commercial", "min_lot_size": 10000, "min_lot_width": 100, "max_height": 35, "front_setback": 25, "rear_setback": 20, "side_setback": 10, "max_coverage": 60.0, "additional": {"corner_setback": 15, "max_stories": 2, "parking_commercial": 4, "floor_area_ratio": 0.5, "notes": "Neighborhood retail"}},
        {"district": "CC", "name": "Community Commercial", "min_lot_size": 20000, "min_lot_width": 150, "max_height": 45, "front_setback": 30, "rear_setback": 25, "side_setback": 15, "max_coverage": 65.0, "additional": {"corner_setback": 25, "max_stories": 3, "parking_commercial": 4, "floor_area_ratio": 1.0, "notes": "Shopping centers"}},
        {"district": "CR", "name": "Regional Commercial", "min_lot_size": 43560, "min_lot_width": 200, "max_height": 55, "front_setback": 35, "rear_setback": 30, "side_setback": 20, "max_coverage": 70.0, "additional": {"corner_setback": 30, "max_stories": 4, "parking_commercial": 5, "floor_area_ratio": 1.5, "notes": "Regional malls, major retail"}},
        {"district": "IL", "name": "Light Industrial", "min_lot_size": 20000, "min_lot_width": 100, "max_height": 50, "front_setback": 30, "rear_setback": 25, "side_setback": 15, "max_coverage": 60.0, "additional": {"corner_setback": 25, "max_stories": 3, "parking_commercial": 2, "floor_area_ratio": 1.0, "notes": "Light industrial, flex space"}},
        {"district": "IH", "name": "Heavy Industrial", "min_lot_size": 43560, "min_lot_width": 150, "max_height": 60, "front_setback": 40, "rear_setback": 35, "side_setback": 25, "max_coverage": 55.0, "additional": {"corner_setback": 30, "max_stories": 4, "parking_commercial": 1, "floor_area_ratio": 1.5, "notes": "Heavy industrial, manufacturing"}},
    ],
    
    # 11. PALM SHORES
    "PALM SHORES": [
        {"district": "R-1", "name": "Single-Family Residential", "min_lot_size": 10000, "min_lot_width": 80, "max_height": 35, "front_setback": 30, "rear_setback": 25, "side_setback": 10, "max_coverage": 35.0, "additional": {"corner_setback": 20, "max_stories": 2, "parking_residential": 2, "density_max": 4, "min_dwelling_size": 1200, "notes": "Riverfront single-family"}},
        {"district": "R-2", "name": "Single-Family Medium", "min_lot_size": 7500, "min_lot_width": 75, "max_height": 35, "front_setback": 25, "rear_setback": 20, "side_setback": 8, "max_coverage": 40.0, "additional": {"corner_setback": 15, "max_stories": 2, "parking_residential": 2, "density_max": 5, "min_dwelling_size": 1000, "notes": "Standard single-family"}},
        {"district": "C-1", "name": "Limited Commercial", "min_lot_size": 10000, "min_lot_width": 100, "max_height": 35, "front_setback": 25, "rear_setback": 20, "side_setback": 10, "max_coverage": 50.0, "additional": {"corner_setback": 20, "max_stories": 2, "parking_commercial": 4, "floor_area_ratio": 0.4, "notes": "US-1 limited commercial"}},
    ],
    
    # 12. ROCKLEDGE
    "ROCKLEDGE": [
        {"district": "R-1A", "name": "Single-Family Large Lot", "min_lot_size": 12000, "min_lot_width": 100, "max_height": 35, "front_setback": 30, "rear_setback": 25, "side_setback": 10, "max_coverage": 35.0, "additional": {"corner_setback": 20, "max_stories": 2, "parking_residential": 2, "density_max": 3.5, "min_dwelling_size": 1400, "notes": "Large lot single-family"}},
        {"district": "R-1", "name": "Single-Family Standard", "min_lot_size": 7500, "min_lot_width": 75, "max_height": 35, "front_setback": 25, "rear_setback": 20, "side_setback": 8, "max_coverage": 40.0, "additional": {"corner_setback": 15, "max_stories": 2, "parking_residential": 2, "density_max": 6, "min_dwelling_size": 1000, "notes": "Standard single-family"}},
        {"district": "R-2", "name": "Two-Family Residential", "min_lot_size": 6000, "min_lot_width": 60, "max_height": 35, "front_setback": 25, "rear_setback": 15, "side_setback": 8, "max_coverage": 45.0, "additional": {"corner_setback": 15, "max_stories": 2, "parking_residential": 2, "density_max": 8, "min_dwelling_size": 850, "notes": "Duplex permitted"}},
        {"district": "R-3", "name": "Multi-Family Residential", "min_lot_size": 10000, "min_lot_width": 100, "max_height": 45, "front_setback": 25, "rear_setback": 25, "side_setback": 13, "max_coverage": 50.0, "additional": {"corner_setback": 20, "max_stories": 3, "parking_residential": 1.5, "density_max": 15, "min_dwelling_size": 650, "notes": "Apartments, townhomes"}},
        {"district": "C-1", "name": "Neighborhood Commercial", "min_lot_size": 10000, "min_lot_width": 100, "max_height": 35, "front_setback": 25, "rear_setback": 20, "side_setback": 10, "max_coverage": 60.0, "additional": {"corner_setback": 15, "max_stories": 2, "parking_commercial": 4, "floor_area_ratio": 0.5, "notes": "Neighborhood retail"}},
        {"district": "C-2", "name": "General Commercial", "min_lot_size": 15000, "min_lot_width": 125, "max_height": 45, "front_setback": 30, "rear_setback": 25, "side_setback": 15, "max_coverage": 65.0, "additional": {"corner_setback": 20, "max_stories": 3, "parking_commercial": 4, "floor_area_ratio": 1.0, "notes": "US-1 corridor commercial"}},
        {"district": "I-1", "name": "Light Industrial", "min_lot_size": 20000, "min_lot_width": 100, "max_height": 50, "front_setback": 30, "rear_setback": 25, "side_setback": 15, "max_coverage": 55.0, "additional": {"corner_setback": 25, "max_stories": 3, "parking_commercial": 2, "floor_area_ratio": 1.0, "notes": "Light industrial, warehouse"}},
        {"district": "PUD", "name": "Planned Unit Development", "min_lot_size": 43560, "min_lot_width": 100, "max_height": 55, "front_setback": 25, "rear_setback": 25, "side_setback": 15, "max_coverage": 50.0, "additional": {"corner_setback": 20, "max_stories": 4, "parking_residential": 2, "parking_commercial": 4, "notes": "Flexible mixed-use"}},
    ],
    
    # 13. TITUSVILLE
    "TITUSVILLE": [
        {"district": "RS-1", "name": "Single-Family Estate", "min_lot_size": 15000, "min_lot_width": 100, "max_height": 35, "front_setback": 30, "rear_setback": 25, "side_setback": 13, "max_coverage": 35.0, "additional": {"corner_setback": 20, "max_stories": 2, "parking_residential": 2, "density_max": 3, "min_dwelling_size": 1600, "notes": "Estate single-family"}},
        {"district": "RS-2", "name": "Single-Family Standard", "min_lot_size": 7500, "min_lot_width": 75, "max_height": 35, "front_setback": 25, "rear_setback": 20, "side_setback": 8, "max_coverage": 40.0, "additional": {"corner_setback": 15, "max_stories": 2, "parking_residential": 2, "density_max": 6, "min_dwelling_size": 1200, "notes": "Standard single-family"}},
        {"district": "RS-3", "name": "Single-Family Small Lot", "min_lot_size": 6000, "min_lot_width": 60, "max_height": 35, "front_setback": 20, "rear_setback": 15, "side_setback": 5, "max_coverage": 45.0, "additional": {"corner_setback": 15, "max_stories": 2, "parking_residential": 2, "density_max": 7, "min_dwelling_size": 1000, "notes": "Compact single-family"}},
        {"district": "RM-1", "name": "Multi-Family Low", "min_lot_size": 7500, "min_lot_width": 75, "max_height": 35, "front_setback": 25, "rear_setback": 20, "side_setback": 10, "max_coverage": 45.0, "additional": {"corner_setback": 15, "max_stories": 2, "parking_residential": 2, "density_max": 12, "min_dwelling_size": 750, "notes": "Low-density multi-family"}},
        {"district": "RM-2", "name": "Multi-Family Medium", "min_lot_size": 10000, "min_lot_width": 100, "max_height": 45, "front_setback": 25, "rear_setback": 25, "side_setback": 15, "max_coverage": 50.0, "additional": {"corner_setback": 20, "max_stories": 3, "parking_residential": 1.5, "density_max": 18, "min_dwelling_size": 650, "notes": "Medium-density apartments"}},
        {"district": "RM-3", "name": "Multi-Family High", "min_lot_size": 15000, "min_lot_width": 125, "max_height": 55, "front_setback": 30, "rear_setback": 30, "side_setback": 20, "max_coverage": 55.0, "additional": {"corner_setback": 25, "max_stories": 4, "parking_residential": 1.5, "density_max": 25, "min_dwelling_size": 600, "notes": "High-density apartments"}},
        {"district": "C-1", "name": "Neighborhood Commercial", "min_lot_size": 10000, "min_lot_width": 100, "max_height": 35, "front_setback": 25, "rear_setback": 20, "side_setback": 10, "max_coverage": 60.0, "additional": {"corner_setback": 15, "max_stories": 2, "parking_commercial": 4, "floor_area_ratio": 0.5, "notes": "Neighborhood retail"}},
        {"district": "C-2", "name": "General Commercial", "min_lot_size": 15000, "min_lot_width": 125, "max_height": 45, "front_setback": 30, "rear_setback": 25, "side_setback": 15, "max_coverage": 65.0, "additional": {"corner_setback": 20, "max_stories": 3, "parking_commercial": 4, "floor_area_ratio": 1.0, "notes": "US-1 corridor commercial"}},
        {"district": "C-3", "name": "Central Business District", "min_lot_size": 5000, "min_lot_width": 50, "max_height": 65, "front_setback": 0, "rear_setback": 10, "side_setback": 0, "max_coverage": 80.0, "additional": {"corner_setback": 0, "max_stories": 5, "parking_commercial": 2, "floor_area_ratio": 2.5, "notes": "Downtown zero lot line"}},
        {"district": "I-1", "name": "Light Industrial", "min_lot_size": 20000, "min_lot_width": 100, "max_height": 50, "front_setback": 30, "rear_setback": 25, "side_setback": 15, "max_coverage": 55.0, "additional": {"corner_setback": 25, "max_stories": 3, "parking_commercial": 2, "floor_area_ratio": 1.0, "notes": "Light industrial"}},
        {"district": "I-2", "name": "Heavy Industrial", "min_lot_size": 43560, "min_lot_width": 150, "max_height": 60, "front_setback": 40, "rear_setback": 35, "side_setback": 25, "max_coverage": 50.0, "additional": {"corner_setback": 30, "max_stories": 4, "parking_commercial": 1, "floor_area_ratio": 1.5, "notes": "Heavy industrial, space coast"}},
        {"district": "PUD", "name": "Planned Unit Development", "min_lot_size": 43560, "min_lot_width": 100, "max_height": 55, "front_setback": 25, "rear_setback": 25, "side_setback": 15, "max_coverage": 50.0, "additional": {"corner_setback": 20, "max_stories": 4, "parking_residential": 2, "parking_commercial": 4, "notes": "Flexible mixed-use"}},
    ],
    
    # 14. SATELLITE BEACH
    "SATELLITE BEACH": [
        {"district": "R-1", "name": "Single-Family Residential", "min_lot_size": 6000, "min_lot_width": 60, "max_height": 35, "front_setback": 25, "rear_setback": 20, "side_setback": 7, "max_coverage": 40.0, "additional": {"corner_setback": 15, "max_stories": 2, "parking_residential": 2, "density_max": 7, "min_dwelling_size": 1200, "notes": "Single-family residential"}},
        {"district": "R-1A", "name": "Single-Family Large Lot", "min_lot_size": 7500, "min_lot_width": 75, "max_height": 35, "front_setback": 25, "rear_setback": 20, "side_setback": 10, "max_coverage": 35.0, "additional": {"corner_setback": 20, "max_stories": 2, "parking_residential": 2, "density_max": 6, "min_dwelling_size": 1400, "notes": "Single-family residential, larger lots"}},
        {"district": "R-2", "name": "Two-Family Residential", "min_lot_size": 5000, "min_lot_width": 50, "max_height": 35, "front_setback": 25, "rear_setback": 15, "side_setback": 5, "max_coverage": 45.0, "additional": {"corner_setback": 15, "max_stories": 2, "parking_residential": 2, "density_max": 10, "min_dwelling_size": 900, "notes": "Two-family residential, duplex"}},
        {"district": "R-3", "name": "Multi-Family Residential", "min_lot_size": 10000, "min_lot_width": 100, "max_height": 45, "front_setback": 25, "rear_setback": 25, "side_setback": 10, "max_coverage": 50.0, "additional": {"corner_setback": 20, "max_stories": 3, "parking_residential": 1.5, "density_max": 15, "min_dwelling_size": 700, "notes": "Multi-family apartments"}},
        {"district": "C-1", "name": "Neighborhood Commercial", "min_lot_size": 7500, "min_lot_width": 75, "max_height": 35, "front_setback": 25, "rear_setback": 15, "side_setback": 10, "max_coverage": 55.0, "additional": {"corner_setback": 15, "max_stories": 2, "parking_commercial": 5, "floor_area_ratio": 0.5, "notes": "Neighborhood retail, A1A"}},
        {"district": "C-2", "name": "General Commercial", "min_lot_size": 10000, "min_lot_width": 100, "max_height": 45, "front_setback": 25, "rear_setback": 20, "side_setback": 10, "max_coverage": 60.0, "additional": {"corner_setback": 20, "max_stories": 3, "parking_commercial": 4, "floor_area_ratio": 1.0, "notes": "General commercial"}},
        {"district": "I-1", "name": "Light Industrial", "min_lot_size": 15000, "min_lot_width": 100, "max_height": 45, "front_setback": 30, "rear_setback": 25, "side_setback": 15, "max_coverage": 55.0, "additional": {"corner_setback": 25, "max_stories": 3, "parking_commercial": 2, "floor_area_ratio": 1.0, "notes": "Light industrial"}},
        {"district": "PUD", "name": "Planned Unit Development", "min_lot_size": 43560, "min_lot_width": 100, "max_height": 45, "front_setback": 25, "rear_setback": 25, "side_setback": 15, "max_coverage": 50.0, "additional": {"corner_setback": 20, "max_stories": 3, "parking_residential": 2, "parking_commercial": 4, "notes": "Flexible mixed-use"}},
    ],
    
    # 15. MELBOURNE
    "MELBOURNE": [
        {"district": "RS-1", "name": "Single-Family Estate", "min_lot_size": 15000, "min_lot_width": 100, "max_height": 35, "front_setback": 30, "rear_setback": 25, "side_setback": 12, "max_coverage": 35.0, "additional": {"corner_setback": 20, "max_stories": 2, "parking_residential": 2, "density_max": 3, "min_dwelling_size": 1600, "notes": "Estate single-family"}},
        {"district": "RS-2", "name": "Single-Family Standard", "min_lot_size": 7500, "min_lot_width": 75, "max_height": 35, "front_setback": 25, "rear_setback": 20, "side_setback": 8, "max_coverage": 40.0, "additional": {"corner_setback": 15, "max_stories": 2, "parking_residential": 2, "density_max": 6, "min_dwelling_size": 1200, "notes": "Standard single-family"}},
        {"district": "RM-4", "name": "Multi-Family Low", "min_lot_size": 7500, "min_lot_width": 75, "max_height": 35, "front_setback": 25, "rear_setback": 20, "side_setback": 10, "max_coverage": 45.0, "additional": {"corner_setback": 15, "max_stories": 2, "parking_residential": 2, "density_max": 10, "min_dwelling_size": 800, "notes": "Low-density multi-family"}},
        {"district": "RM-6", "name": "Multi-Family Medium", "min_lot_size": 10000, "min_lot_width": 100, "max_height": 45, "front_setback": 25, "rear_setback": 25, "side_setback": 15, "max_coverage": 50.0, "additional": {"corner_setback": 20, "max_stories": 3, "parking_residential": 1.5, "density_max": 15, "min_dwelling_size": 650, "notes": "Medium-density apartments"}},
        {"district": "C-1", "name": "Neighborhood Commercial", "min_lot_size": 10000, "min_lot_width": 100, "max_height": 35, "front_setback": 25, "rear_setback": 20, "side_setback": 10, "max_coverage": 60.0, "additional": {"corner_setback": 15, "max_stories": 2, "parking_commercial": 4, "floor_area_ratio": 0.5, "notes": "Neighborhood retail"}},
        {"district": "C-2", "name": "General Commercial", "min_lot_size": 15000, "min_lot_width": 125, "max_height": 55, "front_setback": 30, "rear_setback": 25, "side_setback": 15, "max_coverage": 65.0, "additional": {"corner_setback": 20, "max_stories": 4, "parking_commercial": 4, "floor_area_ratio": 1.5, "notes": "US-1 corridor commercial"}},
        {"district": "C-3", "name": "Central Business District", "min_lot_size": 5000, "min_lot_width": 50, "max_height": 75, "front_setback": 0, "rear_setback": 10, "side_setback": 0, "max_coverage": 85.0, "additional": {"corner_setback": 0, "max_stories": 6, "parking_commercial": 2, "floor_area_ratio": 3.0, "notes": "Downtown Melbourne zero lot line"}},
        {"district": "I-1", "name": "Light Industrial", "min_lot_size": 20000, "min_lot_width": 100, "max_height": 50, "front_setback": 30, "rear_setback": 25, "side_setback": 15, "max_coverage": 55.0, "additional": {"corner_setback": 25, "max_stories": 3, "parking_commercial": 2, "floor_area_ratio": 1.0, "notes": "Light industrial, tech corridor"}},
        {"district": "PUD", "name": "Planned Unit Development", "min_lot_size": 43560, "min_lot_width": 100, "max_height": 65, "front_setback": 25, "rear_setback": 25, "side_setback": 15, "max_coverage": 50.0, "additional": {"corner_setback": 20, "max_stories": 5, "parking_residential": 2, "parking_commercial": 4, "notes": "Flexible mixed-use, Viera area"}},
    ],
    
    # 16. INDIAN HARBOUR BEACH
    "INDIAN HARBOUR BEACH": [
        {"district": "R-1", "name": "Single-Family Residential", "min_lot_size": 7500, "min_lot_width": 75, "max_height": 35, "front_setback": 25, "rear_setback": 20, "side_setback": 8, "max_coverage": 40.0, "additional": {"corner_setback": 15, "max_stories": 2, "parking_residential": 2, "density_max": 6, "min_dwelling_size": 1200, "notes": "Beachside single-family"}},
        {"district": "R-1A", "name": "Single-Family Large Lot", "min_lot_size": 10000, "min_lot_width": 100, "max_height": 35, "front_setback": 30, "rear_setback": 25, "side_setback": 10, "max_coverage": 35.0, "additional": {"corner_setback": 20, "max_stories": 2, "parking_residential": 2, "density_max": 4, "min_dwelling_size": 1400, "notes": "Larger beachside lots"}},
        {"district": "R-2", "name": "Two-Family Residential", "min_lot_size": 6000, "min_lot_width": 60, "max_height": 35, "front_setback": 25, "rear_setback": 15, "side_setback": 8, "max_coverage": 45.0, "additional": {"corner_setback": 15, "max_stories": 2, "parking_residential": 2, "density_max": 8, "min_dwelling_size": 900, "notes": "Duplex permitted"}},
        {"district": "R-3", "name": "Multi-Family Residential", "min_lot_size": 10000, "min_lot_width": 100, "max_height": 55, "front_setback": 25, "rear_setback": 25, "side_setback": 12, "max_coverage": 50.0, "additional": {"corner_setback": 20, "max_stories": 4, "parking_residential": 1.5, "density_max": 20, "min_dwelling_size": 650, "notes": "Beachfront condos"}},
        {"district": "C-1", "name": "Neighborhood Commercial", "min_lot_size": 7500, "min_lot_width": 75, "max_height": 35, "front_setback": 20, "rear_setback": 15, "side_setback": 10, "max_coverage": 55.0, "additional": {"corner_setback": 15, "max_stories": 2, "parking_commercial": 5, "floor_area_ratio": 0.5, "notes": "A1A neighborhood retail"}},
        {"district": "C-2", "name": "General Commercial", "min_lot_size": 10000, "min_lot_width": 100, "max_height": 45, "front_setback": 25, "rear_setback": 20, "side_setback": 10, "max_coverage": 60.0, "additional": {"corner_setback": 20, "max_stories": 3, "parking_commercial": 4, "floor_area_ratio": 1.0, "notes": "General commercial"}},
    ],
    
    # 17. WEST MELBOURNE
    "WEST MELBOURNE": [
        {"district": "RS-1", "name": "Single-Family Estate", "min_lot_size": 20000, "min_lot_width": 110, "max_height": 35, "front_setback": 35, "rear_setback": 30, "side_setback": 13, "max_coverage": 30.0, "additional": {"corner_setback": 25, "max_stories": 2, "parking_residential": 2, "density_max": 2, "min_dwelling_size": 1800, "notes": "Estate single-family"}},
        {"district": "RS-2", "name": "Single-Family Standard", "min_lot_size": 10000, "min_lot_width": 85, "max_height": 35, "front_setback": 25, "rear_setback": 25, "side_setback": 10, "max_coverage": 35.0, "additional": {"corner_setback": 20, "max_stories": 2, "parking_residential": 2, "density_max": 4, "min_dwelling_size": 1400, "notes": "Standard single-family"}},
        {"district": "RS-3", "name": "Single-Family Medium", "min_lot_size": 7500, "min_lot_width": 70, "max_height": 35, "front_setback": 25, "rear_setback": 20, "side_setback": 8, "max_coverage": 40.0, "additional": {"corner_setback": 15, "max_stories": 2, "parking_residential": 2, "density_max": 6, "min_dwelling_size": 1200, "notes": "Medium lot single-family"}},
        {"district": "RM-1", "name": "Multi-Family Low", "min_lot_size": 10000, "min_lot_width": 100, "max_height": 40, "front_setback": 25, "rear_setback": 25, "side_setback": 13, "max_coverage": 45.0, "additional": {"corner_setback": 20, "max_stories": 2, "parking_residential": 2, "density_max": 10, "min_dwelling_size": 800, "notes": "Low-density multi-family"}},
        {"district": "RM-2", "name": "Multi-Family Medium", "min_lot_size": 15000, "min_lot_width": 125, "max_height": 50, "front_setback": 30, "rear_setback": 30, "side_setback": 15, "max_coverage": 50.0, "additional": {"corner_setback": 25, "max_stories": 3, "parking_residential": 1.5, "density_max": 15, "min_dwelling_size": 700, "notes": "Medium-density apartments"}},
        {"district": "C-1", "name": "Neighborhood Commercial", "min_lot_size": 15000, "min_lot_width": 125, "max_height": 35, "front_setback": 30, "rear_setback": 25, "side_setback": 15, "max_coverage": 55.0, "additional": {"corner_setback": 20, "max_stories": 2, "parking_commercial": 5, "floor_area_ratio": 0.4, "notes": "Neighborhood retail"}},
        {"district": "C-2", "name": "General Commercial", "min_lot_size": 20000, "min_lot_width": 150, "max_height": 50, "front_setback": 35, "rear_setback": 30, "side_setback": 20, "max_coverage": 65.0, "additional": {"corner_setback": 25, "max_stories": 4, "parking_commercial": 4, "floor_area_ratio": 1.0, "notes": "Minton Road corridor"}},
        {"district": "C-3", "name": "Regional Commercial", "min_lot_size": 43560, "min_lot_width": 200, "max_height": 60, "front_setback": 40, "rear_setback": 35, "side_setback": 25, "max_coverage": 70.0, "additional": {"corner_setback": 30, "max_stories": 5, "parking_commercial": 5, "floor_area_ratio": 1.5, "notes": "I-95 interchange commercial"}},
        {"district": "I-1", "name": "Light Industrial", "min_lot_size": 20000, "min_lot_width": 100, "max_height": 50, "front_setback": 30, "rear_setback": 25, "side_setback": 15, "max_coverage": 55.0, "additional": {"corner_setback": 25, "max_stories": 3, "parking_commercial": 2, "floor_area_ratio": 1.0, "notes": "Light industrial, business park"}},
        {"district": "PUD", "name": "Planned Unit Development", "min_lot_size": 87120, "min_lot_width": 150, "max_height": 55, "front_setback": 30, "rear_setback": 30, "side_setback": 20, "max_coverage": 50.0, "additional": {"corner_setback": 25, "max_stories": 4, "parking_residential": 2, "parking_commercial": 4, "notes": "Master-planned communities"}},
    ],
}

def make_request(method, endpoint, data=None):
    """Make HTTP request to Supabase"""
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    
    if data:
        data = json.dumps(data).encode()
    
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("apikey", SUPABASE_KEY)
    req.add_header("Authorization", f"Bearer {SUPABASE_KEY}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Prefer", "return=representation")
    
    try:
        with urllib.request.urlopen(req, timeout=30, context=ctx) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"HTTP Error {e.code}: {body[:200]}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def clear_existing_data():
    """Clear existing zoning data"""
    print("Clearing existing data...")
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/zoning_requirements?id=gt.0",
        method="DELETE"
    )
    req.add_header("apikey", SUPABASE_KEY)
    req.add_header("Authorization", f"Bearer {SUPABASE_KEY}")
    
    try:
        with urllib.request.urlopen(req, timeout=30, context=ctx) as response:
            print("✅ Existing data cleared")
            return True
    except Exception as e:
        print(f"Warning: Could not clear data: {e}")
        return False

def insert_jurisdiction_data():
    """Insert all jurisdiction data"""
    total_records = 0
    
    for jurisdiction, districts in JURISDICTIONS.items():
        print(f"\n📍 Processing: {jurisdiction}")
        
        for district in districts:
            record = {
                "jurisdiction": jurisdiction,
                "district": district["district"],
                "requirement_type": "dimensional",
                "min_lot_size": district["min_lot_size"],
                "min_lot_width": district["min_lot_width"],
                "max_height": district["max_height"],
                "front_setback": district["front_setback"],
                "rear_setback": district["rear_setback"],
                "side_setback": district["side_setback"],
                "max_coverage": district["max_coverage"],
                "additional_requirements": district["additional"]
            }
            
            result = make_request("POST", "zoning_requirements", record)
            if result:
                total_records += 1
                print(f"   ✓ {district['district']} - {district['name']}")
            else:
                print(f"   ✗ FAILED: {district['district']}")
    
    return total_records

def main():
    print("=" * 60)
    print("BREVARD COUNTY COMPREHENSIVE ZONING DATA SEED")
    print("All 17 Jurisdictions with Enhanced Features")
    print("=" * 60)
    
    # Calculate totals
    total_districts = sum(len(districts) for districts in JURISDICTIONS.values())
    print(f"\n📊 Jurisdictions: {len(JURISDICTIONS)}")
    print(f"📊 Total Districts: {total_districts}")
    
    # Clear and insert
    clear_existing_data()
    
    print("\n" + "=" * 60)
    print("INSERTING DATA...")
    print("=" * 60)
    
    inserted = insert_jurisdiction_data()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"✅ Jurisdictions processed: {len(JURISDICTIONS)}")
    print(f"✅ Records inserted: {inserted}/{total_districts}")
    
    # List enhanced features
    print("\n📋 ENHANCED FEATURES INCLUDED:")
    print("   • Front/Rear/Side/Corner Setbacks")
    print("   • Max Height (feet)")
    print("   • Max Stories")
    print("   • Parking (residential & commercial)")
    print("   • Lot Coverage %")
    print("   • Floor Area Ratio (commercial)")
    print("   • Max Density (units/acre)")
    print("   • Min Dwelling Size")

if __name__ == "__main__":
    main()
