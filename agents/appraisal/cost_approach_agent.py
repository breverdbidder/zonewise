"""
ZoneWise Cost Approach Agent
Performs professional cost approach valuation

Formula: Land Value + Replacement Cost New - Depreciation = Indicated Value

Components:
1. Land Value (via sales comparison of vacant land)
2. Replacement Cost New (Marshall & Swift regional costs)
3. Depreciation:
   - Physical depreciation (age/condition)
   - Functional obsolescence
   - External obsolescence

© 2026 ZoneWise - Ariel Shapira
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from ..data_sources.bcpao_client import BCPAOClient, BCPAOProperty
from ..data_sources.census_client import CensusClient
from ..data_sources.supabase_client import SupabaseClient

logger = logging.getLogger(__name__)


@dataclass
class CostApproachResult:
    """Result of cost approach analysis."""
    # Land Value
    land_value: float
    land_value_per_sf: float
    land_value_method: str
    
    # Replacement Cost New
    building_sf: int
    base_cost_per_sf: float
    base_cost: float
    quality_adjustment: float
    soft_costs: float
    entrepreneurial_profit: float
    replacement_cost_new: float
    
    # Depreciation
    physical_depreciation: float
    physical_depreciation_pct: float
    functional_obsolescence: float
    external_obsolescence: float
    total_depreciation: float
    
    # Final Value
    depreciated_cost: float
    site_improvements: float
    indicated_value: float
    
    confidence: str
    narrative: str
    created_at: str


class CostApproachAgent:
    """
    Agent for Cost Approach valuation.
    
    Best for:
    - New construction
    - Special purpose properties
    - Insurance valuations
    - When sales data is limited
    
    Usage:
        agent = CostApproachAgent()
        result = await agent.analyze(subject_property)
    """
    
    def __init__(self):
        self.bcpao = BCPAOClient()
        self.census = CensusClient()
        self.supabase = SupabaseClient()
        
        # Brevard County construction costs per SF (2025)
        # Based on Marshall & Swift regional multipliers
        self.construction_costs = {
            "economy": 125,      # Basic spec
            "standard": 165,     # Average quality
            "good": 200,         # Above average
            "excellent": 250,    # High-end
            "luxury": 325,       # Custom luxury
        }
        
        # Quality multipliers by construction type
        self.quality_multipliers = {
            "MASONRY": 1.05,
            "FRAME": 0.95,
            "CONCRETE": 1.10,
            "STEEL": 1.15,
            "MODULAR": 0.85,
        }
        
        # Land values by ZIP ($/SF for residential)
        self.land_values = {
            "32937": 45,   # Satellite Beach
            "32940": 40,   # Viera
            "32903": 55,   # Indialantic
            "32951": 65,   # Melbourne Beach
            "32953": 35,   # Merritt Island
            "32931": 50,   # Cocoa Beach
            "32935": 25,   # Eau Gallie
            "32901": 20,   # Melbourne downtown
            "32904": 22,   # Melbourne west
            "32905": 18,   # Palm Bay north
            "32907": 20,   # Palm Bay south
            "32780": 15,   # Titusville
        }
        
        # Economic life by construction type
        self.economic_life = {
            "MASONRY": 60,
            "FRAME": 50,
            "CONCRETE": 70,
            "STEEL": 75,
            "DEFAULT": 55,
        }
    
    async def analyze(
        self,
        subject: BCPAOProperty,
        analysis_id: str = None,
        store_results: bool = True
    ) -> CostApproachResult:
        """
        Perform cost approach analysis.
        
        Args:
            subject: BCPAOProperty object
            analysis_id: Optional existing analysis ID
            store_results: Whether to store in Supabase
            
        Returns:
            CostApproachResult with complete analysis
        """
        logger.info(f"Starting Cost Approach for {subject.address}")
        
        # 1. Estimate Land Value
        land_value, land_psf = await self._estimate_land_value(subject)
        
        # 2. Calculate Replacement Cost New
        rcn_data = self._calculate_rcn(subject)
        
        # 3. Calculate Depreciation
        depreciation = self._calculate_depreciation(subject, rcn_data["replacement_cost_new"])
        
        # 4. Calculate Site Improvements
        site_improvements = self._estimate_site_improvements(subject)
        
        # 5. Calculate Indicated Value
        depreciated_cost = rcn_data["replacement_cost_new"] - depreciation["total"]
        indicated_value = land_value + depreciated_cost + site_improvements
        
        # Round to nearest $1,000
        indicated_value = round(indicated_value / 1000) * 1000
        
        # 6. Determine confidence
        confidence = self._determine_confidence(subject, depreciation)
        
        # 7. Generate narrative
        narrative = self._generate_narrative(subject, land_value, rcn_data, depreciation, indicated_value)
        
        result = CostApproachResult(
            land_value=land_value,
            land_value_per_sf=land_psf,
            land_value_method="Sales Comparison / Market Data",
            
            building_sf=subject.living_area_sf,
            base_cost_per_sf=rcn_data["base_cost_per_sf"],
            base_cost=rcn_data["base_cost"],
            quality_adjustment=rcn_data["quality_adjustment"],
            soft_costs=rcn_data["soft_costs"],
            entrepreneurial_profit=rcn_data["entrepreneurial_profit"],
            replacement_cost_new=rcn_data["replacement_cost_new"],
            
            physical_depreciation=depreciation["physical"],
            physical_depreciation_pct=depreciation["physical_pct"],
            functional_obsolescence=depreciation["functional"],
            external_obsolescence=depreciation["external"],
            total_depreciation=depreciation["total"],
            
            depreciated_cost=depreciated_cost,
            site_improvements=site_improvements,
            indicated_value=indicated_value,
            
            confidence=confidence,
            narrative=narrative,
            created_at=datetime.now().isoformat()
        )
        
        # Store results
        if store_results and analysis_id:
            await self._store_results(analysis_id, result)
        
        logger.info(f"Cost Approach complete: ${indicated_value:,.0f} ({confidence} confidence)")
        
        return result
    
    async def _estimate_land_value(self, subject: BCPAOProperty) -> tuple:
        """Estimate land value using multiple methods."""
        
        # Method 1: BCPAO land value (if available and reasonable)
        if subject.land_value and subject.land_value > 10000:
            bcpao_psf = subject.land_value / subject.lot_size_sf if subject.lot_size_sf else 0
            
            # Sanity check - should be between $5-$100/SF for Brevard
            if 5 <= bcpao_psf <= 100:
                return subject.land_value, bcpao_psf
        
        # Method 2: Market-based estimate
        zip_code = subject.zip_code
        base_psf = self.land_values.get(zip_code, 25)
        
        # Adjustments
        multiplier = 1.0
        
        # Waterfront premium
        if subject.waterfront:
            multiplier *= 2.0
        
        # Corner lot premium
        # (would need data to implement)
        
        # Size adjustment (larger lots have lower $/SF)
        if subject.lot_size_sf:
            if subject.lot_size_sf > 20000:
                multiplier *= 0.85
            elif subject.lot_size_sf > 15000:
                multiplier *= 0.92
            elif subject.lot_size_sf < 5000:
                multiplier *= 1.10
        
        adjusted_psf = base_psf * multiplier
        land_value = adjusted_psf * (subject.lot_size_sf or 8000)
        
        return round(land_value, 0), round(adjusted_psf, 2)
    
    def _calculate_rcn(self, subject: BCPAOProperty) -> Dict[str, float]:
        """Calculate Replacement Cost New."""
        
        # Determine quality level
        quality = "standard"
        if subject.just_value and subject.living_area_sf:
            value_psf = subject.just_value / subject.living_area_sf
            if value_psf > 300:
                quality = "luxury"
            elif value_psf > 225:
                quality = "excellent"
            elif value_psf > 175:
                quality = "good"
            elif value_psf < 120:
                quality = "economy"
        
        base_cost_psf = self.construction_costs[quality]
        
        # Apply construction type multiplier
        const_type = (subject.construction_type or "").upper()
        type_mult = 1.0
        for key, mult in self.quality_multipliers.items():
            if key in const_type:
                type_mult = mult
                break
        
        adjusted_cost_psf = base_cost_psf * type_mult
        
        # Calculate components
        building_sf = subject.living_area_sf or 1500
        base_cost = building_sf * adjusted_cost_psf
        
        # Quality adjustment for specific features
        quality_adj = 0
        if subject.pool:
            quality_adj += 35000
        if subject.fireplace:
            quality_adj += 5000
        if subject.garage_spaces:
            quality_adj += subject.garage_spaces * 20000
        
        # Soft costs (15%)
        soft_costs = (base_cost + quality_adj) * 0.15
        
        # Entrepreneurial profit (10%)
        entrepreneurial = (base_cost + quality_adj + soft_costs) * 0.10
        
        rcn = base_cost + quality_adj + soft_costs + entrepreneurial
        
        return {
            "base_cost_per_sf": adjusted_cost_psf,
            "base_cost": base_cost,
            "quality_adjustment": quality_adj,
            "soft_costs": soft_costs,
            "entrepreneurial_profit": entrepreneurial,
            "replacement_cost_new": rcn
        }
    
    def _calculate_depreciation(self, subject: BCPAOProperty, rcn: float) -> Dict[str, float]:
        """Calculate total depreciation (physical + functional + external)."""
        
        # Physical Depreciation (age-life method)
        const_type = (subject.construction_type or "").upper()
        economic_life = self.economic_life.get(const_type, self.economic_life["DEFAULT"])
        
        effective_age = datetime.now().year - (subject.effective_year or subject.year_built or 1990)
        effective_age = max(0, min(effective_age, economic_life))  # Cap at economic life
        
        physical_pct = (effective_age / economic_life) * 100
        physical_depr = rcn * (physical_pct / 100)
        
        # Functional Obsolescence
        functional = 0
        
        # Poor layout penalty (proxy: bathroom count vs bedroom ratio)
        if subject.bedrooms and subject.bathrooms:
            bath_ratio = subject.bathrooms / subject.bedrooms
            if bath_ratio < 0.5:
                functional += rcn * 0.03  # 3% penalty
        
        # No garage in area that expects it
        if not subject.garage_spaces and subject.just_value and subject.just_value > 300000:
            functional += 15000
        
        # External Obsolescence
        external = 0
        
        # High crime area (would need data)
        # Major road noise (would need data)
        # Economic decline (would need data)
        
        total = physical_depr + functional + external
        
        return {
            "physical": round(physical_depr, 0),
            "physical_pct": round(physical_pct, 1),
            "functional": round(functional, 0),
            "external": round(external, 0),
            "total": round(total, 0)
        }
    
    def _estimate_site_improvements(self, subject: BCPAOProperty) -> float:
        """Estimate value of site improvements."""
        improvements = 0
        
        # Driveway/paving (estimate)
        improvements += 5000
        
        # Landscaping (estimate)
        improvements += 3000
        
        # Pool (if not already in building)
        # Already handled in RCN
        
        # Fencing (estimate)
        improvements += 2000
        
        return improvements
    
    def _determine_confidence(self, subject: BCPAOProperty, depreciation: Dict) -> str:
        """Determine confidence level for cost approach."""
        
        # Cost approach is most reliable for newer buildings
        age = datetime.now().year - (subject.year_built or 1990)
        
        if age <= 5:
            return "HIGH"
        elif age <= 15:
            return "MEDIUM"
        elif age <= 30:
            return "LOW"
        else:
            return "LOW"  # Cost approach unreliable for older buildings
    
    def _generate_narrative(
        self,
        subject: BCPAOProperty,
        land_value: float,
        rcn: Dict,
        depreciation: Dict,
        indicated_value: float
    ) -> str:
        """Generate professional narrative."""
        
        age = datetime.now().year - (subject.year_built or 1990)
        
        narrative = f"""
Cost Approach Analysis for {subject.address}

LAND VALUE:
Site Size: {subject.lot_size_sf:,.0f} SF ({subject.lot_size_acres:.3f} acres)
Land Value: ${land_value:,.0f}
Method: Sales comparison of similar sites in {subject.zip_code}

REPLACEMENT COST NEW:
Building Area: {subject.living_area_sf:,} SF
Base Cost @ ${rcn['base_cost_per_sf']:.0f}/SF: ${rcn['base_cost']:,.0f}
Quality Adjustments: ${rcn['quality_adjustment']:,.0f}
Soft Costs (15%): ${rcn['soft_costs']:,.0f}
Entrepreneurial Profit (10%): ${rcn['entrepreneurial_profit']:,.0f}
Total RCN: ${rcn['replacement_cost_new']:,.0f}

DEPRECIATION:
Effective Age: {age} years
Physical Depreciation ({depreciation['physical_pct']:.1f}%): ${depreciation['physical']:,.0f}
Functional Obsolescence: ${depreciation['functional']:,.0f}
External Obsolescence: ${depreciation['external']:,.0f}
Total Depreciation: ${depreciation['total']:,.0f}

INDICATED VALUE:
Land Value: ${land_value:,.0f}
+ Depreciated Cost: ${rcn['replacement_cost_new'] - depreciation['total']:,.0f}
+ Site Improvements: $10,000
= Indicated Value: ${indicated_value:,.0f}
"""
        return narrative.strip()
    
    async def _store_results(self, analysis_id: str, result: CostApproachResult):
        """Store results in Supabase."""
        try:
            cost_data = {
                "land_value": result.land_value,
                "land_value_method": result.land_value_method,
                "land_value_per_sf": result.land_value_per_sf,
                "cost_type": "REPLACEMENT",
                "building_sf": result.building_sf,
                "base_cost_per_sf": result.base_cost_per_sf,
                "base_cost": result.base_cost,
                "quality_adjustment_amt": result.quality_adjustment,
                "soft_costs_pct": 15.0,
                "soft_costs_amt": result.soft_costs,
                "replacement_cost_new": result.replacement_cost_new,
                "physical_depreciation_pct": result.physical_depreciation_pct,
                "physical_depreciation_amt": result.physical_depreciation,
                "functional_obsolescence_amt": result.functional_obsolescence,
                "external_obsolescence_amt": result.external_obsolescence,
                "total_depreciation_amt": result.total_depreciation,
                "depreciated_cost": result.depreciated_cost,
                "site_improvements_value": result.site_improvements,
                "indicated_value": result.indicated_value,
                "confidence": result.confidence,
                "narrative": result.narrative
            }
            
            await self.supabase.store_cost_approach(analysis_id, cost_data)
            
        except Exception as e:
            logger.error(f"Error storing cost approach: {e}")
    
    async def close(self):
        await self.bcpao.close()
        await self.census.close()
        await self.supabase.close()
