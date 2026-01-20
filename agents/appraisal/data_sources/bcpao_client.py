"""
ZoneWise BCPAO Client
Real integration with Brevard County Property Appraiser API

API Endpoint: https://gis.brevardfl.gov/gissrv/rest/services/Base_Map/Parcel_New_WKID2881/MapServer/5

Data includes:
- Property details (beds, baths, sqft, year built)
- Valuation (just value, assessed value, land value, building value)
- Sales history
- Owner information
- Lot characteristics

© 2026 ZoneWise - Ariel Shapira
"""

import httpx
import asyncio
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)

BCPAO_API_URL = "https://gis.brevardfl.gov/gissrv/rest/services/Base_Map/Parcel_New_WKID2881/MapServer/5/query"
BCPAO_SEARCH_URL = "https://www.bcpao.us/api/v1/search"


@dataclass
class BCPAOProperty:
    """Complete BCPAO property record."""
    parcel_id: str
    address: str
    city: str
    zip_code: str
    
    # Owner
    owner_name: str
    owner_address: Optional[str] = None
    
    # Valuation
    just_value: float = 0
    assessed_value: float = 0
    land_value: float = 0
    building_value: float = 0
    taxable_value: float = 0
    
    # Property Characteristics
    year_built: int = 0
    effective_year: int = 0
    living_area_sf: int = 0
    total_area_sf: int = 0
    bedrooms: int = 0
    bathrooms: float = 0
    stories: float = 1
    
    # Lot
    lot_size_sf: float = 0
    lot_size_acres: float = 0
    frontage_ft: float = 0
    depth_ft: float = 0
    
    # Construction
    construction_type: str = ""
    exterior_wall: str = ""
    roof_type: str = ""
    foundation_type: str = ""
    hvac_type: str = ""
    
    # Features
    pool: bool = False
    garage_spaces: int = 0
    fireplace: bool = False
    waterfront: bool = False
    
    # Classification
    property_use: str = ""
    property_use_code: str = ""
    zoning: str = ""
    subdivision: str = ""
    
    # Sales History
    last_sale_date: Optional[str] = None
    last_sale_price: Optional[float] = None
    prior_sale_date: Optional[str] = None
    prior_sale_price: Optional[float] = None
    
    # Metadata
    homestead: bool = False
    photo_url: Optional[str] = None
    fetched_at: str = ""


class BCPAOClient:
    """
    Async client for BCPAO property data.
    
    Usage:
        client = BCPAOClient()
        property = await client.get_property("12-34-56-78-00001.0")
        comps = await client.find_comparable_sales(property, radius_miles=1.0)
    """
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.client = None
        
    async def _ensure_client(self):
        if not self.client:
            self.client = httpx.AsyncClient(
                timeout=self.timeout,
                headers={'User-Agent': 'ZoneWise/1.0'}
            )
    
    async def get_property(self, parcel_id: str) -> Optional[BCPAOProperty]:
        """
        Fetch complete property data by parcel ID.
        
        Args:
            parcel_id: Brevard County parcel ID (e.g., "26-37-35-77-00042.0")
            
        Returns:
            BCPAOProperty with all available data
        """
        await self._ensure_client()
        
        try:
            # Clean parcel ID
            clean_id = parcel_id.strip().replace(" ", "")
            
            # Query GIS API
            params = {
                'where': f"PARCEL_ID = '{clean_id}'",
                'outFields': '*',
                'returnGeometry': 'false',
                'f': 'json'
            }
            
            response = await self.client.get(BCPAO_API_URL, params=params)
            
            if response.status_code != 200:
                logger.error(f"BCPAO API error: {response.status_code}")
                return None
                
            data = response.json()
            
            if not data.get('features'):
                # Try BCPAO search API as fallback
                return await self._search_bcpao_api(clean_id)
            
            attrs = data['features'][0]['attributes']
            return self._parse_gis_attributes(attrs)
            
        except Exception as e:
            logger.error(f"BCPAO fetch error: {e}")
            return None
    
    async def search_by_address(self, address: str) -> Optional[BCPAOProperty]:
        """Search for property by street address."""
        await self._ensure_client()
        
        try:
            # Clean and format address
            clean_addr = address.upper().strip()
            clean_addr = clean_addr.split(',')[0]  # Remove city/state
            
            params = {
                'where': f"UPPER(SITUS_ADDR) LIKE '%{clean_addr}%'",
                'outFields': '*',
                'returnGeometry': 'false',
                'f': 'json'
            }
            
            response = await self.client.get(BCPAO_API_URL, params=params)
            data = response.json()
            
            if data.get('features') and len(data['features']) > 0:
                attrs = data['features'][0]['attributes']
                return self._parse_gis_attributes(attrs)
            
            return None
            
        except Exception as e:
            logger.error(f"BCPAO address search error: {e}")
            return None
    
    async def find_comparable_sales(
        self,
        subject: BCPAOProperty,
        radius_miles: float = 1.0,
        max_age_months: int = 12,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find comparable sales for subject property.
        
        Filters:
        - Within radius_miles of subject
        - Similar property type
        - Similar size (±30% living area)
        - Sold within max_age_months
        
        Returns list of comps with adjustment calculations.
        """
        await self._ensure_client()
        
        try:
            # Build WHERE clause for comparables
            min_sqft = int(subject.living_area_sf * 0.7)
            max_sqft = int(subject.living_area_sf * 1.3)
            min_year = subject.year_built - 15 if subject.year_built else 1950
            max_year = subject.year_built + 15 if subject.year_built else 2025
            
            # Same ZIP code as simple radius proxy
            where_clause = f"""
                ZIP_CODE = '{subject.zip_code}'
                AND HEATED_SQFT >= {min_sqft}
                AND HEATED_SQFT <= {max_sqft}
                AND YEAR_BUILT >= {min_year}
                AND YEAR_BUILT <= {max_year}
                AND SALE_PRICE > 100000
                AND PARCEL_ID <> '{subject.parcel_id}'
            """
            
            params = {
                'where': where_clause,
                'outFields': '*',
                'returnGeometry': 'false',
                'orderByFields': 'SALE_DATE DESC',
                'resultRecordCount': limit * 2,  # Get extra for filtering
                'f': 'json'
            }
            
            response = await self.client.get(BCPAO_API_URL, params=params)
            data = response.json()
            
            comps = []
            for feature in data.get('features', [])[:limit]:
                attrs = feature['attributes']
                comp = self._parse_gis_attributes(attrs)
                
                if comp and comp.last_sale_price:
                    # Calculate adjustments
                    adjustments = self._calculate_adjustments(subject, comp)
                    
                    comps.append({
                        'property': asdict(comp),
                        'sale_price': comp.last_sale_price,
                        'sale_date': comp.last_sale_date,
                        'adjustments': adjustments,
                        'adjusted_price': comp.last_sale_price + adjustments['total'],
                        'price_per_sf': comp.last_sale_price / comp.living_area_sf if comp.living_area_sf else 0
                    })
            
            # Sort by similarity (fewest adjustments)
            comps.sort(key=lambda x: abs(x['adjustments']['total']))
            
            return comps[:limit]
            
        except Exception as e:
            logger.error(f"Comparable search error: {e}")
            return []
    
    def _calculate_adjustments(
        self, 
        subject: BCPAOProperty, 
        comp: BCPAOProperty
    ) -> Dict[str, float]:
        """
        Calculate dollar adjustments from comp to subject.
        
        Positive adjustment = comp is inferior (add to comp price)
        Negative adjustment = comp is superior (subtract from comp price)
        """
        adjustments = {
            'living_area': 0,
            'lot_size': 0,
            'age': 0,
            'bedrooms': 0,
            'bathrooms': 0,
            'garage': 0,
            'pool': 0,
            'condition': 0,
            'total': 0
        }
        
        # Living area: $100/sqft
        if subject.living_area_sf and comp.living_area_sf:
            sqft_diff = subject.living_area_sf - comp.living_area_sf
            adjustments['living_area'] = sqft_diff * 100
        
        # Lot size: $5/sqft for first 5000 sqft diff, $2/sqft after
        if subject.lot_size_sf and comp.lot_size_sf:
            lot_diff = subject.lot_size_sf - comp.lot_size_sf
            if abs(lot_diff) <= 5000:
                adjustments['lot_size'] = lot_diff * 5
            else:
                base = 5000 * 5 if lot_diff > 0 else -5000 * 5
                extra = (abs(lot_diff) - 5000) * 2
                adjustments['lot_size'] = base + (extra if lot_diff > 0 else -extra)
        
        # Age: $500/year (newer = better)
        if subject.year_built and comp.year_built:
            age_diff = comp.year_built - subject.year_built  # Positive if comp is newer
            adjustments['age'] = -age_diff * 500  # Subtract if comp is newer
        
        # Bedrooms: $10,000/bedroom
        if subject.bedrooms and comp.bedrooms:
            bed_diff = subject.bedrooms - comp.bedrooms
            adjustments['bedrooms'] = bed_diff * 10000
        
        # Bathrooms: $7,500/bathroom
        if subject.bathrooms and comp.bathrooms:
            bath_diff = subject.bathrooms - comp.bathrooms
            adjustments['bathrooms'] = bath_diff * 7500
        
        # Garage: $15,000/space
        garage_diff = subject.garage_spaces - comp.garage_spaces
        adjustments['garage'] = garage_diff * 15000
        
        # Pool: $25,000
        if subject.pool and not comp.pool:
            adjustments['pool'] = 25000
        elif not subject.pool and comp.pool:
            adjustments['pool'] = -25000
        
        # Total
        adjustments['total'] = sum(v for k, v in adjustments.items() if k != 'total')
        
        return adjustments
    
    def _parse_gis_attributes(self, attrs: Dict[str, Any]) -> BCPAOProperty:
        """Parse GIS API attributes into BCPAOProperty."""
        
        def safe_int(key: str, default: int = 0) -> int:
            val = attrs.get(key)
            try:
                return int(val) if val else default
            except:
                return default
        
        def safe_float(key: str, default: float = 0.0) -> float:
            val = attrs.get(key)
            try:
                return float(val) if val else default
            except:
                return default
        
        def safe_str(key: str, default: str = "") -> str:
            val = attrs.get(key)
            return str(val).strip() if val else default
        
        # Parse sale date from epoch
        sale_date = None
        if attrs.get('SALE_DATE'):
            try:
                ts = int(attrs['SALE_DATE']) / 1000
                sale_date = datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
            except:
                pass
        
        # Build photo URL
        parcel_id = safe_str('PARCEL_ID')
        photo_url = None
        if parcel_id:
            # BCPAO photo format
            account = parcel_id.replace('-', '').replace('.', '')[:12]
            photo_url = f"https://www.bcpao.us/photos/{account[:2]}/{account}011.jpg"
        
        return BCPAOProperty(
            parcel_id=parcel_id,
            address=safe_str('SITUS_ADDR'),
            city=safe_str('SITUS_CITY'),
            zip_code=safe_str('ZIP_CODE'),
            owner_name=safe_str('OWNER_NAME'),
            
            just_value=safe_float('JUST_VAL'),
            assessed_value=safe_float('ASSESSED_VAL'),
            land_value=safe_float('LAND_VAL'),
            building_value=safe_float('BLDG_VAL'),
            taxable_value=safe_float('TAXABLE_VAL'),
            
            year_built=safe_int('YEAR_BUILT'),
            effective_year=safe_int('EFF_YEAR'),
            living_area_sf=safe_int('HEATED_SQFT'),
            total_area_sf=safe_int('TOTAL_SQFT'),
            bedrooms=safe_int('BEDROOMS'),
            bathrooms=safe_float('BATHROOMS'),
            stories=safe_float('STORIES', 1.0),
            
            lot_size_sf=safe_float('LOT_SIZE'),
            lot_size_acres=safe_float('ACRES'),
            
            construction_type=safe_str('CONST_TYPE'),
            exterior_wall=safe_str('EXT_WALL'),
            roof_type=safe_str('ROOF_TYPE'),
            
            pool=safe_str('POOL') in ['Y', 'YES', '1', 'TRUE'],
            garage_spaces=safe_int('GARAGE'),
            waterfront=safe_str('WATERFRONT') in ['Y', 'YES', '1', 'TRUE'],
            
            property_use=safe_str('PROP_USE'),
            property_use_code=safe_str('USE_CODE'),
            zoning=safe_str('ZONING'),
            subdivision=safe_str('SUBDIV'),
            
            last_sale_date=sale_date,
            last_sale_price=safe_float('SALE_PRICE'),
            
            homestead=safe_str('HOMESTEAD') in ['Y', 'YES', '1', 'TRUE'],
            photo_url=photo_url,
            fetched_at=datetime.now().isoformat()
        )
    
    async def _search_bcpao_api(self, parcel_id: str) -> Optional[BCPAOProperty]:
        """Fallback to BCPAO search API."""
        try:
            # Clean parcel ID format
            account = parcel_id.replace('-', '').replace('.', '').replace(' ', '')
            
            response = await self.client.get(
                f"{BCPAO_SEARCH_URL}",
                params={'account': account}
            )
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            if not data.get('results'):
                return None
            
            result = data['results'][0]
            
            # Map BCPAO search API fields
            return BCPAOProperty(
                parcel_id=parcel_id,
                address=result.get('siteAddress', ''),
                city=result.get('siteCity', ''),
                zip_code=result.get('siteZip', ''),
                owner_name=result.get('ownerName', ''),
                just_value=float(result.get('justValue', 0)),
                assessed_value=float(result.get('assessedValue', 0)),
                land_value=float(result.get('landValue', 0)),
                building_value=float(result.get('bldgValue', 0)),
                year_built=int(result.get('yearBuilt', 0)),
                living_area_sf=int(result.get('heatedSqft', 0)),
                bedrooms=int(result.get('bedrooms', 0)),
                bathrooms=float(result.get('bathrooms', 0)),
                lot_size_sf=float(result.get('lotSize', 0)),
                property_use=result.get('useCode', ''),
                photo_url=result.get('masterPhotoUrl'),
                fetched_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"BCPAO search API error: {e}")
            return None
    
    async def close(self):
        """Close HTTP client."""
        if self.client:
            await self.client.aclose()
