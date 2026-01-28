"""
ZoneWise Supabase Client
Database client for storing/retrieving appraisal data

Tables used:
- property_analyses
- comparable_sales
- sales_comparison_adjustments
- cost_approach_analyses
- income_approach_analyses
- appraisal_reconciliation
- kpi_definitions
- property_kpi_scores

© 2026 ZoneWise - ZoneWise.AI
"""

import os
import httpx
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")


class SupabaseClient:
    """
    Async Supabase client for ZoneWise data.
    
    Usage:
        client = SupabaseClient()
        
        # Create analysis
        analysis_id = await client.create_analysis(parcel_id, address)
        
        # Store results
        await client.store_comparable(analysis_id, comp_data)
        await client.store_cost_approach(analysis_id, cost_data)
        await client.store_income_approach(analysis_id, income_data)
        
        # Finalize
        await client.store_reconciliation(analysis_id, reconciliation_data)
    """
    
    def __init__(self, url: str = None, key: str = None):
        self.url = url or SUPABASE_URL
        self.key = key or SUPABASE_KEY
        self.client = None
    
    async def _ensure_client(self):
        if not self.client:
            self.client = httpx.AsyncClient(
                timeout=30.0,
                headers={
                    'apikey': self.key,
                    'Authorization': f'Bearer {self.key}',
                    'Content-Type': 'application/json',
                    'Prefer': 'return=representation'
                }
            )
    
    async def _request(
        self,
        method: str,
        table: str,
        data: Dict = None,
        params: Dict = None
    ) -> Optional[Dict]:
        """Make request to Supabase REST API."""
        await self._ensure_client()
        
        url = f"{self.url}/rest/v1/{table}"
        
        try:
            if method == "GET":
                response = await self.client.get(url, params=params)
            elif method == "POST":
                response = await self.client.post(url, json=data)
            elif method == "PATCH":
                response = await self.client.patch(url, json=data, params=params)
            elif method == "DELETE":
                response = await self.client.delete(url, params=params)
            else:
                raise ValueError(f"Invalid method: {method}")
            
            if response.status_code not in [200, 201, 204]:
                logger.error(f"Supabase error: {response.status_code} - {response.text}")
                return None
            
            if response.status_code == 204:
                return {}
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Supabase request error: {e}")
            return None
    
    # ==========================================
    # ANALYSIS OPERATIONS
    # ==========================================
    
    async def create_analysis(
        self,
        parcel_id: str,
        address: str,
        jurisdiction_id: int = None
    ) -> Optional[str]:
        """
        Create new property analysis record.
        Returns analysis UUID.
        """
        data = {
            "parcel_id": parcel_id,
            "address": address,
            "jurisdiction_id": jurisdiction_id,
            "analysis_date": datetime.now().isoformat()
        }
        
        result = await self._request("POST", "property_analyses", data)
        
        if result and len(result) > 0:
            return result[0].get("id")
        return None
    
    async def update_analysis(
        self,
        analysis_id: str,
        zonewise_score: float = None,
        recommendation: str = None,
        max_bid: float = None,
        confidence: float = None
    ) -> bool:
        """Update analysis with final results."""
        data = {}
        if zonewise_score is not None:
            data["zonewise_score"] = zonewise_score
        if recommendation:
            data["recommendation"] = recommendation
        if max_bid is not None:
            data["max_bid"] = max_bid
        if confidence is not None:
            data["confidence_level"] = confidence
        
        result = await self._request(
            "PATCH", 
            "property_analyses",
            data,
            params={"id": f"eq.{analysis_id}"}
        )
        
        return result is not None
    
    async def get_analysis(self, analysis_id: str) -> Optional[Dict]:
        """Get analysis by ID."""
        result = await self._request(
            "GET",
            "property_analyses",
            params={"id": f"eq.{analysis_id}"}
        )
        return result[0] if result else None
    
    # ==========================================
    # SALES COMPARISON APPROACH
    # ==========================================
    
    async def store_comparable(
        self,
        analysis_id: str,
        comp_number: int,
        comp_data: Dict
    ) -> Optional[str]:
        """Store a comparable sale."""
        data = {
            "analysis_id": analysis_id,
            "comp_number": comp_number,
            "address": comp_data.get("address"),
            "parcel_id": comp_data.get("parcel_id"),
            "sale_date": comp_data.get("sale_date"),
            "sale_price": comp_data.get("sale_price"),
            "price_per_sf": comp_data.get("price_per_sf"),
            "year_built": comp_data.get("year_built"),
            "living_area_sf": comp_data.get("living_area_sf"),
            "lot_size_sf": comp_data.get("lot_size_sf"),
            "bedrooms": comp_data.get("bedrooms"),
            "bathrooms": comp_data.get("bathrooms"),
            "garage_spaces": comp_data.get("garage_spaces"),
            "pool": comp_data.get("pool", False),
            "condition_rating": comp_data.get("condition"),
            "distance_miles": comp_data.get("distance_miles"),
            "days_on_market": comp_data.get("days_on_market"),
            "data_source": comp_data.get("source", "BCPAO")
        }
        
        result = await self._request("POST", "comparable_sales", data)
        return result[0].get("id") if result else None
    
    async def store_adjustments(
        self,
        analysis_id: str,
        comp_id: str,
        adjustments: Dict
    ) -> bool:
        """Store adjustment grid for a comparable."""
        records = []
        
        for category, amount in adjustments.items():
            if category == "total" or amount == 0:
                continue
            
            records.append({
                "analysis_id": analysis_id,
                "comp_id": comp_id,
                "adjustment_category": "Features" if category in ["pool", "garage"] else "Size" if "area" in category or "lot" in category else "Age" if category == "age" else "Other",
                "adjustment_item": category.replace("_", " ").title(),
                "adjustment_amount": amount,
                "adjustment_direction": "UP" if amount > 0 else "DOWN"
            })
        
        for record in records:
            await self._request("POST", "sales_comparison_adjustments", record)
        
        return True
    
    async def store_sales_conclusion(
        self,
        analysis_id: str,
        indicated_value: float,
        value_low: float = None,
        value_high: float = None,
        confidence: str = "MEDIUM",
        narrative: str = None
    ) -> bool:
        """Store sales comparison conclusion."""
        data = {
            "analysis_id": analysis_id,
            "indicated_value_point": indicated_value,
            "indicated_value_low": value_low or indicated_value * 0.95,
            "indicated_value_high": value_high or indicated_value * 1.05,
            "confidence_level": confidence,
            "reconciliation_narrative": narrative
        }
        
        result = await self._request("POST", "sales_comparison_conclusions", data)
        return result is not None
    
    # ==========================================
    # COST APPROACH
    # ==========================================
    
    async def store_cost_approach(
        self,
        analysis_id: str,
        cost_data: Dict
    ) -> bool:
        """Store cost approach analysis."""
        data = {
            "analysis_id": analysis_id,
            "land_value": cost_data.get("land_value"),
            "land_value_method": cost_data.get("land_value_method", "Sales Comparison"),
            "land_value_per_sf": cost_data.get("land_value_per_sf"),
            "cost_type": cost_data.get("cost_type", "REPLACEMENT"),
            "building_sf": cost_data.get("building_sf"),
            "base_cost_per_sf": cost_data.get("base_cost_per_sf"),
            "base_cost": cost_data.get("base_cost"),
            "quality_adjustment_pct": cost_data.get("quality_adjustment_pct"),
            "quality_adjustment_amt": cost_data.get("quality_adjustment_amt"),
            "soft_costs_pct": cost_data.get("soft_costs_pct", 15.0),
            "soft_costs_amt": cost_data.get("soft_costs_amt"),
            "replacement_cost_new": cost_data.get("replacement_cost_new"),
            "physical_depreciation_pct": cost_data.get("physical_depreciation_pct"),
            "physical_depreciation_amt": cost_data.get("physical_depreciation_amt"),
            "functional_obsolescence_amt": cost_data.get("functional_obsolescence_amt", 0),
            "external_obsolescence_amt": cost_data.get("external_obsolescence_amt", 0),
            "total_depreciation_amt": cost_data.get("total_depreciation_amt"),
            "depreciated_cost": cost_data.get("depreciated_cost"),
            "site_improvements_value": cost_data.get("site_improvements_value", 0),
            "indicated_value": cost_data.get("indicated_value"),
            "confidence_level": cost_data.get("confidence", "MEDIUM"),
            "narrative": cost_data.get("narrative")
        }
        
        result = await self._request("POST", "cost_approach_analyses", data)
        return result is not None
    
    # ==========================================
    # INCOME APPROACH
    # ==========================================
    
    async def store_income_approach(
        self,
        analysis_id: str,
        income_data: Dict
    ) -> bool:
        """Store income approach analysis."""
        data = {
            "analysis_id": analysis_id,
            "rental_units": income_data.get("rental_units", 1),
            "monthly_rent_per_unit": income_data.get("monthly_rent"),
            "annual_rent_per_unit": income_data.get("monthly_rent", 0) * 12,
            "potential_gross_income": income_data.get("potential_gross_income"),
            "other_income": income_data.get("other_income", 0),
            "vacancy_rate_pct": income_data.get("vacancy_rate", 5.0),
            "vacancy_loss": income_data.get("vacancy_loss"),
            "effective_gross_income": income_data.get("effective_gross_income"),
            "property_taxes": income_data.get("property_taxes"),
            "insurance": income_data.get("insurance"),
            "management_fee_pct": income_data.get("management_fee_pct", 8.0),
            "management_fee": income_data.get("management_fee"),
            "maintenance_repairs": income_data.get("maintenance"),
            "reserves_for_replacement": income_data.get("reserves"),
            "hoa_fees": income_data.get("hoa", 0),
            "total_operating_expenses": income_data.get("total_operating_expenses"),
            "expense_ratio_pct": income_data.get("expense_ratio"),
            "net_operating_income": income_data.get("net_operating_income"),
            "cap_rate_source": income_data.get("cap_rate_source", "Market"),
            "cap_rate": income_data.get("cap_rate", 0.07),
            "indicated_value": income_data.get("indicated_value"),
            "gross_rent_multiplier": income_data.get("grm"),
            "grm_indicated_value": income_data.get("grm_value"),
            "confidence_level": income_data.get("confidence", "MEDIUM"),
            "narrative": income_data.get("narrative")
        }
        
        result = await self._request("POST", "income_approach_analyses", data)
        return result is not None
    
    # ==========================================
    # RECONCILIATION
    # ==========================================
    
    async def store_reconciliation(
        self,
        analysis_id: str,
        recon_data: Dict
    ) -> bool:
        """Store final reconciliation."""
        data = {
            "analysis_id": analysis_id,
            "sales_comparison_value": recon_data.get("sales_comparison_value"),
            "sales_comparison_weight": recon_data.get("sales_comparison_weight", 50),
            "cost_approach_value": recon_data.get("cost_approach_value"),
            "cost_approach_weight": recon_data.get("cost_approach_weight", 25),
            "income_approach_value": recon_data.get("income_approach_value"),
            "income_approach_weight": recon_data.get("income_approach_weight", 25),
            "reconciled_value_low": recon_data.get("value_low"),
            "reconciled_value_high": recon_data.get("value_high"),
            "final_value_opinion": recon_data.get("final_value"),
            "most_applicable_approach": recon_data.get("most_applicable_approach", "Sales Comparison"),
            "reconciliation_narrative": recon_data.get("narrative"),
            "effective_date": datetime.now().date().isoformat(),
            "appraiser_name": "ZoneWise AI",
            "appraiser_designation": "AI Valuation System"
        }
        
        result = await self._request("POST", "appraisal_reconciliation", data)
        return result is not None
    
    # ==========================================
    # KPI OPERATIONS
    # ==========================================
    
    async def get_kpi_definitions(self, category: str = None) -> List[Dict]:
        """Get KPI definitions, optionally filtered by category."""
        params = {"select": "*"}
        if category:
            params["category"] = f"eq.{category}"
        
        result = await self._request("GET", "kpi_definitions", params=params)
        return result or []
    
    async def store_kpi_scores(
        self,
        analysis_id: str,
        kpi_scores: List[Dict]
    ) -> bool:
        """Store KPI scores for an analysis."""
        for score in kpi_scores:
            data = {
                "analysis_id": analysis_id,
                "kpi_id": score.get("kpi_id"),
                "raw_value": str(score.get("raw_value")),
                "normalized_score": score.get("normalized_score"),
                "weight_applied": score.get("weight"),
                "weighted_score": score.get("weighted_score"),
                "data_source": score.get("source"),
                "confidence": score.get("confidence", "MEDIUM")
            }
            await self._request("POST", "property_kpi_scores", data)
        
        return True
    
    async def close(self):
        if self.client:
            await self.client.aclose()
