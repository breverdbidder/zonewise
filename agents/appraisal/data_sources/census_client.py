"""
ZoneWise Census API Client
Demographics data from US Census Bureau API

Data includes:
- Median household income
- Median home value
- Population/housing stats
- Vacancy rates
- Education levels
- Rental market data

© 2026 ZoneWise - Ariel Shapira
"""

import os
import httpx
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)

CENSUS_API_KEY = os.getenv("CENSUS_API_KEY", "")
CENSUS_BASE_URL = "https://api.census.gov/data"

# Variables for ACS 5-year estimates
CENSUS_VARIABLES = {
    "B19013_001E": "median_household_income",
    "B25077_001E": "median_home_value",
    "B01003_001E": "total_population",
    "B25003_002E": "owner_occupied_units",
    "B25003_001E": "total_housing_units",
    "B25064_001E": "median_gross_rent",
    "B25002_002E": "occupied_units",
    "B25002_003E": "vacant_units",
    "B25035_001E": "median_year_built",
    "B25018_001E": "median_rooms",
}


@dataclass
class DemographicData:
    """Census demographic data for a location."""
    zip_code: str
    median_household_income: Optional[float] = None
    median_home_value: Optional[float] = None
    total_population: Optional[int] = None
    owner_occupied_rate: Optional[float] = None
    vacancy_rate: Optional[float] = None
    median_gross_rent: Optional[float] = None
    median_year_built: Optional[int] = None
    population_density: Optional[float] = None  # per sq mile
    data_year: str = "2023"
    source: str = "US Census ACS 5-Year"


class CensusClient:
    """
    Async Census Bureau API client.
    
    Usage:
        client = CensusClient()
        data = await client.get_demographics("32937")
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or CENSUS_API_KEY
        self.client = None
        
        # Brevard County estimates for fallback
        self.brevard_estimates = {
            "32937": {"income": 78000, "home_value": 380000, "rent": 1800, "vacancy": 5.2},
            "32940": {"income": 82000, "home_value": 420000, "rent": 1900, "vacancy": 4.8},
            "32953": {"income": 75000, "home_value": 340000, "rent": 1650, "vacancy": 5.6},
            "32903": {"income": 80000, "home_value": 450000, "rent": 2000, "vacancy": 5.1},
            "32901": {"income": 52000, "home_value": 220000, "rent": 1400, "vacancy": 8.5},
            "32904": {"income": 58000, "home_value": 280000, "rent": 1500, "vacancy": 7.2},
            "32905": {"income": 55000, "home_value": 250000, "rent": 1450, "vacancy": 7.8},
            "32907": {"income": 62000, "home_value": 290000, "rent": 1550, "vacancy": 6.5},
            "32908": {"income": 60000, "home_value": 275000, "rent": 1500, "vacancy": 6.8},
            "32909": {"income": 58000, "home_value": 265000, "rent": 1480, "vacancy": 7.0},
            "32935": {"income": 60000, "home_value": 270000, "rent": 1520, "vacancy": 6.8},
            "32922": {"income": 48000, "home_value": 180000, "rent": 1300, "vacancy": 9.2},
            "32926": {"income": 55000, "home_value": 240000, "rent": 1400, "vacancy": 7.5},
            "32927": {"income": 58000, "home_value": 260000, "rent": 1480, "vacancy": 7.0},
            "32931": {"income": 72000, "home_value": 350000, "rent": 1750, "vacancy": 5.8},
            "32780": {"income": 50000, "home_value": 200000, "rent": 1350, "vacancy": 8.0},  # Titusville
            "32796": {"income": 52000, "home_value": 210000, "rent": 1380, "vacancy": 7.8},  # Titusville
        }
    
    async def _ensure_client(self):
        if not self.client:
            self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_demographics(self, zip_code: str) -> Dict[str, Any]:
        """
        Get demographic data for a ZIP code.
        
        Args:
            zip_code: 5-digit ZIP code
            
        Returns:
            Dictionary with demographic data and metadata
        """
        await self._ensure_client()
        zip_code = str(zip_code).strip()[:5]
        
        try:
            var_list = ",".join(CENSUS_VARIABLES.keys())
            url = f"{CENSUS_BASE_URL}/2023/acs/acs5"
            
            params = {
                "get": f"NAME,{var_list}",
                "for": f"zip code tabulation area:{zip_code}",
                "key": self.api_key
            }
            
            response = await self.client.get(url, params=params)
            
            if response.status_code != 200:
                logger.warning(f"Census API error: {response.status_code}")
                return self._get_estimate(zip_code)
            
            data = response.json()
            
            if len(data) < 2:
                logger.warning(f"No Census data for ZIP {zip_code}")
                return self._get_estimate(zip_code)
            
            headers = data[0]
            values = data[1]
            raw_data = dict(zip(headers, values))
            
            demographics = self._parse_response(zip_code, raw_data)
            
            return {
                "zip_code": zip_code,
                "demographics": asdict(demographics),
                "raw_data": raw_data,
                "source": "census_api",
                "fetched_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Census API error: {e}")
            return self._get_estimate(zip_code)
    
    def _parse_response(self, zip_code: str, raw: Dict[str, str]) -> DemographicData:
        """Parse raw Census data."""
        
        def safe_float(key: str) -> Optional[float]:
            val = raw.get(key)
            if val and val not in ["-", "null", "", "-666666666"]:
                try:
                    return float(val)
                except:
                    pass
            return None
        
        def safe_int(key: str) -> Optional[int]:
            val = safe_float(key)
            return int(val) if val else None
        
        # Calculate rates
        owner_rate = None
        total_units = safe_int("B25003_001E")
        owner_units = safe_int("B25003_002E")
        if total_units and owner_units and total_units > 0:
            owner_rate = round(owner_units / total_units * 100, 1)
        
        vacancy_rate = None
        occupied = safe_int("B25002_002E")
        vacant = safe_int("B25002_003E")
        if occupied and vacant:
            total = occupied + vacant
            if total > 0:
                vacancy_rate = round(vacant / total * 100, 1)
        
        return DemographicData(
            zip_code=zip_code,
            median_household_income=safe_float("B19013_001E"),
            median_home_value=safe_float("B25077_001E"),
            total_population=safe_int("B01003_001E"),
            owner_occupied_rate=owner_rate,
            vacancy_rate=vacancy_rate,
            median_gross_rent=safe_float("B25064_001E"),
            median_year_built=safe_int("B25035_001E")
        )
    
    def _get_estimate(self, zip_code: str) -> Dict[str, Any]:
        """Get Brevard County estimate for ZIP code."""
        est = self.brevard_estimates.get(
            zip_code, 
            {"income": 65000, "home_value": 300000, "rent": 1550, "vacancy": 6.5}
        )
        
        demographics = DemographicData(
            zip_code=zip_code,
            median_household_income=est["income"],
            median_home_value=est["home_value"],
            total_population=25000,
            owner_occupied_rate=68.0,
            vacancy_rate=est["vacancy"],
            median_gross_rent=est["rent"]
        )
        
        return {
            "zip_code": zip_code,
            "demographics": asdict(demographics),
            "source": "brevard_estimates",
            "note": "Estimated from Brevard County averages",
            "fetched_at": datetime.now().isoformat()
        }
    
    async def close(self):
        if self.client:
            await self.client.aclose()
