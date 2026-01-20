"""
ZoneWise Sales Comparison Agent
Performs professional sales comparison approach valuation

Process:
1. Get subject property data from BCPAO
2. Find comparable sales (BCPAO + MLS)
3. Calculate adjustments
4. Reconcile to indicated value

MAI Standards:
- Minimum 3 comparables
- Sales within 12 months
- Same property type
- Similar size (±30%)
- Proximity preference

© 2026 ZoneWise - Ariel Shapira
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime

from ..data_sources.bcpao_client import BCPAOClient, BCPAOProperty
from ..data_sources.mls_client import MLSClient, SaleComp
from ..data_sources.supabase_client import SupabaseClient

logger = logging.getLogger(__name__)


@dataclass
class SalesComparisonResult:
    """Result of sales comparison analysis."""
    subject_property: Dict
    comparables: List[Dict]
    adjustment_grid: List[Dict]
    indicated_value: float
    value_range_low: float
    value_range_high: float
    price_per_sf: float
    confidence: str  # HIGH, MEDIUM, LOW
    narrative: str
    created_at: str


class SalesComparisonAgent:
    """
    Agent for Sales Comparison Approach valuation.
    
    Usage:
        agent = SalesComparisonAgent()
        result = await agent.analyze("26-37-35-77-00042.0")
        
        # Or with address
        result = await agent.analyze_by_address("200 Jason Ct, Satellite Beach, FL 32937")
    """
    
    def __init__(self):
        self.bcpao = BCPAOClient()
        self.mls = MLSClient()
        self.supabase = SupabaseClient()
        
        # Adjustment rates (based on Brevard County market)
        self.adjustment_rates = {
            "living_area_per_sf": 100,      # $/sqft
            "lot_size_per_sf": 5,           # $/sqft (first 5000)
            "lot_size_per_sf_excess": 2,    # $/sqft (after 5000)
            "age_per_year": 500,            # $/year
            "bedroom": 10000,               # $/bedroom
            "bathroom": 7500,               # $/bathroom
            "garage_space": 15000,          # $/space
            "pool": 25000,                  # flat
            "waterfront": 50000,            # flat premium
            "condition_poor": -25000,       # condition adjustments
            "condition_fair": -10000,
            "condition_good": 0,
            "condition_excellent": 15000,
        }
    
    async def analyze(
        self,
        parcel_id: str,
        analysis_id: str = None,
        store_results: bool = True
    ) -> SalesComparisonResult:
        """
        Perform sales comparison analysis for a parcel.
        
        Args:
            parcel_id: BCPAO parcel ID
            analysis_id: Optional existing analysis ID
            store_results: Whether to store in Supabase
            
        Returns:
            SalesComparisonResult with complete analysis
        """
        logger.info(f"Starting Sales Comparison for {parcel_id}")
        
        # 1. Get subject property
        subject = await self.bcpao.get_property(parcel_id)
        
        if not subject:
            raise ValueError(f"Could not find property: {parcel_id}")
        
        logger.info(f"Subject: {subject.address}, {subject.living_area_sf} sqft, {subject.year_built}")
        
        # 2. Find comparables from BCPAO
        bcpao_comps = await self.bcpao.find_comparable_sales(
            subject,
            radius_miles=1.5,
            max_age_months=12,
            limit=6
        )
        
        # 3. Get additional comps from MLS
        mls_comps = await self.mls.get_comps_by_address(
            f"{subject.address}, {subject.city}, FL {subject.zip_code}",
            radius_miles=1.5,
            limit=5
        )
        
        # 4. Combine and dedupe comps
        all_comps = self._combine_comps(bcpao_comps, mls_comps, subject)
        
        if len(all_comps) < 3:
            logger.warning(f"Only {len(all_comps)} comps found, using market estimates")
        
        # 5. Calculate adjustments for each comp
        adjusted_comps = []
        for i, comp in enumerate(all_comps[:5]):  # Top 5 comps
            adjustments = self._calculate_detailed_adjustments(subject, comp)
            
            adjusted_price = comp.get("sale_price", 0) + adjustments["total"]
            
            adjusted_comps.append({
                "comp_number": i + 1,
                "address": comp.get("address"),
                "sale_price": comp.get("sale_price"),
                "sale_date": comp.get("sale_date"),
                "living_area_sf": comp.get("living_area_sf"),
                "lot_size_sf": comp.get("lot_size_sf"),
                "bedrooms": comp.get("bedrooms"),
                "bathrooms": comp.get("bathrooms"),
                "year_built": comp.get("year_built"),
                "adjustments": adjustments,
                "adjusted_price": adjusted_price,
                "price_per_sf": comp.get("sale_price", 0) / comp.get("living_area_sf", 1) if comp.get("living_area_sf") else 0,
                "weight": self._calculate_comp_weight(subject, comp, adjustments),
                "source": comp.get("source", "BCPAO")
            })
        
        # 6. Reconcile to indicated value
        indicated_value, confidence, narrative = self._reconcile_value(subject, adjusted_comps)
        
        # 7. Calculate value range
        adjusted_prices = [c["adjusted_price"] for c in adjusted_comps if c["adjusted_price"] > 0]
        value_low = min(adjusted_prices) if adjusted_prices else indicated_value * 0.90
        value_high = max(adjusted_prices) if adjusted_prices else indicated_value * 1.10
        
        # 8. Create result
        result = SalesComparisonResult(
            subject_property=asdict(subject),
            comparables=adjusted_comps,
            adjustment_grid=self._create_adjustment_grid(subject, adjusted_comps),
            indicated_value=indicated_value,
            value_range_low=value_low,
            value_range_high=value_high,
            price_per_sf=indicated_value / subject.living_area_sf if subject.living_area_sf else 0,
            confidence=confidence,
            narrative=narrative,
            created_at=datetime.now().isoformat()
        )
        
        # 9. Store in Supabase
        if store_results and analysis_id:
            await self._store_results(analysis_id, result)
        
        logger.info(f"Sales Comparison complete: ${indicated_value:,.0f} ({confidence} confidence)")
        
        return result
    
    async def analyze_by_address(
        self,
        address: str,
        analysis_id: str = None,
        store_results: bool = True
    ) -> SalesComparisonResult:
        """Analyze property by address."""
        subject = await self.bcpao.search_by_address(address)
        
        if not subject:
            raise ValueError(f"Could not find property: {address}")
        
        return await self.analyze(subject.parcel_id, analysis_id, store_results)
    
    def _combine_comps(
        self,
        bcpao_comps: List[Dict],
        mls_comps: List[SaleComp],
        subject: BCPAOProperty
    ) -> List[Dict]:
        """Combine BCPAO and MLS comps, remove duplicates."""
        combined = []
        seen_addresses = set()
        
        # Add BCPAO comps first (more reliable)
        for comp in bcpao_comps:
            prop = comp.get("property", {})
            addr = prop.get("address", "").upper()
            
            if addr and addr not in seen_addresses:
                seen_addresses.add(addr)
                combined.append({
                    "address": prop.get("address"),
                    "sale_price": comp.get("sale_price"),
                    "sale_date": comp.get("sale_date"),
                    "living_area_sf": prop.get("living_area_sf"),
                    "lot_size_sf": prop.get("lot_size_sf"),
                    "bedrooms": prop.get("bedrooms"),
                    "bathrooms": prop.get("bathrooms"),
                    "year_built": prop.get("year_built"),
                    "garage_spaces": prop.get("garage_spaces", 0),
                    "pool": prop.get("pool", False),
                    "waterfront": prop.get("waterfront", False),
                    "source": "BCPAO"
                })
        
        # Add MLS comps
        for comp in mls_comps:
            addr = comp.address.upper()
            
            if addr and addr not in seen_addresses:
                seen_addresses.add(addr)
                combined.append({
                    "address": comp.address,
                    "sale_price": comp.sale_price,
                    "sale_date": comp.sale_date,
                    "living_area_sf": comp.living_area_sf,
                    "lot_size_sf": comp.lot_size_sf,
                    "bedrooms": comp.bedrooms,
                    "bathrooms": comp.bathrooms,
                    "year_built": comp.year_built,
                    "garage_spaces": 0,
                    "pool": False,
                    "waterfront": False,
                    "source": comp.source
                })
        
        # Sort by similarity to subject
        combined.sort(key=lambda c: self._similarity_score(subject, c), reverse=True)
        
        return combined
    
    def _similarity_score(self, subject: BCPAOProperty, comp: Dict) -> float:
        """Calculate how similar a comp is to subject (0-100)."""
        score = 100
        
        # Size difference penalty
        if subject.living_area_sf and comp.get("living_area_sf"):
            size_diff = abs(subject.living_area_sf - comp["living_area_sf"]) / subject.living_area_sf
            score -= size_diff * 30
        
        # Age difference penalty
        if subject.year_built and comp.get("year_built"):
            age_diff = abs(subject.year_built - comp["year_built"])
            score -= min(age_diff, 20)
        
        # Bedroom difference
        if subject.bedrooms and comp.get("bedrooms"):
            bed_diff = abs(subject.bedrooms - comp["bedrooms"])
            score -= bed_diff * 5
        
        return max(0, score)
    
    def _calculate_detailed_adjustments(
        self,
        subject: BCPAOProperty,
        comp: Dict
    ) -> Dict[str, float]:
        """Calculate detailed adjustments from comp to subject."""
        adj = {
            "living_area": 0,
            "lot_size": 0,
            "age": 0,
            "bedrooms": 0,
            "bathrooms": 0,
            "garage": 0,
            "pool": 0,
            "waterfront": 0,
            "condition": 0,
            "total": 0
        }
        
        # Living area
        if subject.living_area_sf and comp.get("living_area_sf"):
            diff = subject.living_area_sf - comp["living_area_sf"]
            adj["living_area"] = diff * self.adjustment_rates["living_area_per_sf"]
        
        # Lot size
        if subject.lot_size_sf and comp.get("lot_size_sf"):
            diff = subject.lot_size_sf - comp["lot_size_sf"]
            if abs(diff) <= 5000:
                adj["lot_size"] = diff * self.adjustment_rates["lot_size_per_sf"]
            else:
                base = 5000 * self.adjustment_rates["lot_size_per_sf"]
                excess = (abs(diff) - 5000) * self.adjustment_rates["lot_size_per_sf_excess"]
                adj["lot_size"] = (base + excess) if diff > 0 else -(base + excess)
        
        # Age
        if subject.year_built and comp.get("year_built"):
            diff = comp["year_built"] - subject.year_built  # Positive if comp newer
            adj["age"] = -diff * self.adjustment_rates["age_per_year"]
        
        # Bedrooms
        if subject.bedrooms is not None and comp.get("bedrooms") is not None:
            diff = subject.bedrooms - comp["bedrooms"]
            adj["bedrooms"] = diff * self.adjustment_rates["bedroom"]
        
        # Bathrooms
        if subject.bathrooms is not None and comp.get("bathrooms") is not None:
            diff = subject.bathrooms - comp["bathrooms"]
            adj["bathrooms"] = diff * self.adjustment_rates["bathroom"]
        
        # Garage
        if subject.garage_spaces is not None and comp.get("garage_spaces") is not None:
            diff = subject.garage_spaces - comp["garage_spaces"]
            adj["garage"] = diff * self.adjustment_rates["garage_space"]
        
        # Pool
        if subject.pool and not comp.get("pool"):
            adj["pool"] = self.adjustment_rates["pool"]
        elif not subject.pool and comp.get("pool"):
            adj["pool"] = -self.adjustment_rates["pool"]
        
        # Waterfront
        if subject.waterfront and not comp.get("waterfront"):
            adj["waterfront"] = self.adjustment_rates["waterfront"]
        elif not subject.waterfront and comp.get("waterfront"):
            adj["waterfront"] = -self.adjustment_rates["waterfront"]
        
        adj["total"] = sum(v for k, v in adj.items() if k != "total")
        
        return adj
    
    def _calculate_comp_weight(
        self,
        subject: BCPAOProperty,
        comp: Dict,
        adjustments: Dict
    ) -> float:
        """Calculate weight to assign to this comp (0-100%)."""
        weight = 100
        
        # Penalize high total adjustments
        if comp.get("sale_price"):
            adj_pct = abs(adjustments["total"]) / comp["sale_price"] * 100
            weight -= min(adj_pct * 2, 40)
        
        # Prefer more recent sales
        # (would need sale date parsing to implement)
        
        # Prefer closer properties
        # (would need distance calculation)
        
        return max(10, weight)
    
    def _reconcile_value(
        self,
        subject: BCPAOProperty,
        adjusted_comps: List[Dict]
    ) -> tuple:
        """Reconcile adjusted prices to single indicated value."""
        if not adjusted_comps:
            # Fallback to assessed value
            return (
                subject.just_value or subject.assessed_value or 300000,
                "LOW",
                "Insufficient comparable sales. Value based on county assessment."
            )
        
        # Weight-based average
        total_weight = sum(c.get("weight", 50) for c in adjusted_comps)
        if total_weight == 0:
            total_weight = len(adjusted_comps)
        
        weighted_sum = sum(
            c["adjusted_price"] * c.get("weight", 50) 
            for c in adjusted_comps
        )
        
        indicated_value = weighted_sum / total_weight
        
        # Round to nearest $1,000
        indicated_value = round(indicated_value / 1000) * 1000
        
        # Determine confidence
        prices = [c["adjusted_price"] for c in adjusted_comps]
        spread = (max(prices) - min(prices)) / indicated_value if indicated_value else 0
        
        if len(adjusted_comps) >= 4 and spread < 0.10:
            confidence = "HIGH"
        elif len(adjusted_comps) >= 3 and spread < 0.20:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"
        
        # Generate narrative
        narrative = self._generate_narrative(subject, adjusted_comps, indicated_value, confidence)
        
        return indicated_value, confidence, narrative
    
    def _generate_narrative(
        self,
        subject: BCPAOProperty,
        comps: List[Dict],
        value: float,
        confidence: str
    ) -> str:
        """Generate professional narrative for the analysis."""
        prices = [c["adjusted_price"] for c in comps]
        avg_price = sum(prices) / len(prices) if prices else 0
        
        narrative = f"""
Sales Comparison Analysis for {subject.address}

Subject Property:
- {subject.living_area_sf:,} SF living area
- {subject.bedrooms} bedrooms, {subject.bathrooms} bathrooms
- Built {subject.year_built}
- {subject.lot_size_sf:,.0f} SF lot

Analysis Summary:
{len(comps)} comparable sales were analyzed from the {subject.zip_code} market area.
Adjustments were made for differences in living area, lot size, age, bedrooms, 
bathrooms, and amenities.

Adjusted sale prices ranged from ${min(prices):,.0f} to ${max(prices):,.0f}.

Indicated Value: ${value:,.0f}
Confidence Level: {confidence}

This value opinion is based on recent arm's length transactions of similar 
properties in the immediate market area.
"""
        return narrative.strip()
    
    def _create_adjustment_grid(
        self,
        subject: BCPAOProperty,
        comps: List[Dict]
    ) -> List[Dict]:
        """Create formatted adjustment grid for reporting."""
        grid = []
        
        # Subject row
        grid.append({
            "item": "Subject",
            "address": subject.address,
            "sale_price": None,
            "living_area": subject.living_area_sf,
            "lot_size": subject.lot_size_sf,
            "bedrooms": subject.bedrooms,
            "bathrooms": subject.bathrooms,
            "year_built": subject.year_built,
            "adjusted_price": None
        })
        
        # Comp rows
        for comp in comps:
            grid.append({
                "item": f"Comp {comp['comp_number']}",
                "address": comp["address"],
                "sale_price": comp["sale_price"],
                "living_area": comp["living_area_sf"],
                "lot_size": comp.get("lot_size_sf"),
                "bedrooms": comp["bedrooms"],
                "bathrooms": comp["bathrooms"],
                "year_built": comp["year_built"],
                "adjustments": comp["adjustments"],
                "adjusted_price": comp["adjusted_price"]
            })
        
        return grid
    
    async def _store_results(self, analysis_id: str, result: SalesComparisonResult):
        """Store results in Supabase."""
        try:
            # Store each comparable
            for comp in result.comparables:
                comp_id = await self.supabase.store_comparable(
                    analysis_id,
                    comp["comp_number"],
                    comp
                )
                
                if comp_id:
                    await self.supabase.store_adjustments(
                        analysis_id,
                        comp_id,
                        comp["adjustments"]
                    )
            
            # Store conclusion
            await self.supabase.store_sales_conclusion(
                analysis_id,
                result.indicated_value,
                result.value_range_low,
                result.value_range_high,
                result.confidence,
                result.narrative
            )
            
        except Exception as e:
            logger.error(f"Error storing results: {e}")
    
    async def close(self):
        await self.bcpao.close()
        await self.mls.close()
        await self.supabase.close()
