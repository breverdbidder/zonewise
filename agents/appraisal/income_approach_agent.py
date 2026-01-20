"""
ZoneWise Income Approach Agent
Performs professional income approach valuation

Methods:
1. Direct Capitalization: Value = NOI / Cap Rate
2. Gross Rent Multiplier: Value = Gross Rent × GRM

Best for:
- Investment properties
- Multi-family
- Commercial
- Single-family rentals

© 2026 ZoneWise - Ariel Shapira
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from ..data_sources.bcpao_client import BCPAOClient, BCPAOProperty
from ..data_sources.rental_client import RentalClient, RentalMarketData
from ..data_sources.census_client import CensusClient
from ..data_sources.supabase_client import SupabaseClient

logger = logging.getLogger(__name__)


@dataclass
class IncomeApproachResult:
    """Result of income approach analysis."""
    # Income
    monthly_rent: float
    annual_rent: float
    other_income: float
    potential_gross_income: float
    vacancy_rate: float
    vacancy_loss: float
    effective_gross_income: float
    
    # Expenses
    property_taxes: float
    insurance: float
    management_fee: float
    maintenance: float
    reserves: float
    hoa: float
    total_expenses: float
    expense_ratio: float
    
    # NOI
    net_operating_income: float
    
    # Capitalization
    cap_rate: float
    cap_rate_source: str
    indicated_value_direct_cap: float
    
    # GRM Method
    grm: float
    indicated_value_grm: float
    
    # Final
    indicated_value: float
    cash_on_cash: float
    dscr: float
    
    confidence: str
    narrative: str
    created_at: str


class IncomeApproachAgent:
    """
    Agent for Income Approach valuation.
    
    Usage:
        agent = IncomeApproachAgent()
        result = await agent.analyze(subject_property)
    """
    
    def __init__(self):
        self.bcpao = BCPAOClient()
        self.rental = RentalClient()
        self.census = CensusClient()
        self.supabase = SupabaseClient()
        
        # Market cap rates by property type (Brevard County 2025)
        self.cap_rates = {
            "single_family": 0.065,    # 6.5%
            "duplex": 0.070,           # 7.0%
            "triplex": 0.072,          # 7.2%
            "quad": 0.075,             # 7.5%
            "small_multi": 0.078,      # 7.8% (5-20 units)
            "large_multi": 0.060,      # 6.0% (20+ units)
            "retail": 0.080,           # 8.0%
            "office": 0.085,           # 8.5%
            "industrial": 0.075,       # 7.5%
        }
        
        # GRM by property type
        self.grm_rates = {
            "single_family": 130,
            "duplex": 115,
            "multi_family": 100,
        }
    
    async def analyze(
        self,
        subject: BCPAOProperty,
        analysis_id: str = None,
        store_results: bool = True,
        property_type: str = "single_family",
        known_rent: float = None
    ) -> IncomeApproachResult:
        """
        Perform income approach analysis.
        
        Args:
            subject: BCPAOProperty object
            analysis_id: Optional existing analysis ID
            store_results: Whether to store in Supabase
            property_type: Type for cap rate selection
            known_rent: Known actual rent (if available)
            
        Returns:
            IncomeApproachResult with complete analysis
        """
        logger.info(f"Starting Income Approach for {subject.address}")
        
        # 1. Get rental market data
        market = await self.rental.get_rental_market(
            subject.zip_code,
            bedrooms=subject.bedrooms or 3,
            property_type=property_type
        )
        
        # 2. Estimate rent
        if known_rent:
            monthly_rent = known_rent
        else:
            monthly_rent = await self._estimate_rent(subject, market)
        
        # 3. Calculate income
        income = self._calculate_income(monthly_rent, market.vacancy_rate)
        
        # 4. Calculate expenses
        expenses = self._calculate_expenses(
            subject,
            income["effective_gross_income"]
        )
        
        # 5. Calculate NOI
        noi = income["effective_gross_income"] - expenses["total"]
        
        # 6. Get cap rate
        cap_rate = self.cap_rates.get(property_type, 0.07)
        
        # 7. Direct Capitalization
        value_direct_cap = noi / cap_rate if cap_rate > 0 else 0
        
        # 8. GRM Method
        grm = self.grm_rates.get(property_type, 120)
        value_grm = monthly_rent * 12 * (grm / 12)  # Annual rent × annual GRM
        
        # 9. Reconcile (weight direct cap higher)
        indicated_value = (value_direct_cap * 0.70) + (value_grm * 0.30)
        indicated_value = round(indicated_value / 1000) * 1000
        
        # 10. Calculate investment metrics
        cash_on_cash = self._calculate_cash_on_cash(noi, indicated_value)
        dscr = self._calculate_dscr(noi, indicated_value)
        
        # 11. Determine confidence
        confidence = self._determine_confidence(subject, market, monthly_rent)
        
        # 12. Generate narrative
        narrative = self._generate_narrative(
            subject, monthly_rent, income, expenses, noi, 
            cap_rate, indicated_value, confidence
        )
        
        result = IncomeApproachResult(
            monthly_rent=monthly_rent,
            annual_rent=monthly_rent * 12,
            other_income=income["other_income"],
            potential_gross_income=income["pgi"],
            vacancy_rate=market.vacancy_rate,
            vacancy_loss=income["vacancy_loss"],
            effective_gross_income=income["effective_gross_income"],
            
            property_taxes=expenses["taxes"],
            insurance=expenses["insurance"],
            management_fee=expenses["management"],
            maintenance=expenses["maintenance"],
            reserves=expenses["reserves"],
            hoa=expenses.get("hoa", 0),
            total_expenses=expenses["total"],
            expense_ratio=expenses["ratio"],
            
            net_operating_income=noi,
            
            cap_rate=cap_rate,
            cap_rate_source="Market Survey",
            indicated_value_direct_cap=value_direct_cap,
            
            grm=grm,
            indicated_value_grm=value_grm,
            
            indicated_value=indicated_value,
            cash_on_cash=cash_on_cash,
            dscr=dscr,
            
            confidence=confidence,
            narrative=narrative,
            created_at=datetime.now().isoformat()
        )
        
        # Store results
        if store_results and analysis_id:
            await self._store_results(analysis_id, result)
        
        logger.info(f"Income Approach complete: ${indicated_value:,.0f} ({confidence} confidence)")
        
        return result
    
    async def _estimate_rent(
        self,
        subject: BCPAOProperty,
        market: RentalMarketData
    ) -> float:
        """Estimate market rent for subject property."""
        
        base_rent = market.median_rent
        
        # Adjust for size difference from typical
        typical_sf = 1500 + (subject.bedrooms or 3) * 200
        if subject.living_area_sf:
            size_ratio = subject.living_area_sf / typical_sf
            size_adj = (size_ratio - 1) * 0.3  # 30% of size diff
            base_rent *= (1 + size_adj)
        
        # Pool premium
        if subject.pool:
            base_rent *= 1.08
        
        # Waterfront premium
        if subject.waterfront:
            base_rent *= 1.25
        
        # Newer construction premium
        if subject.year_built and subject.year_built >= 2015:
            base_rent *= 1.10
        elif subject.year_built and subject.year_built >= 2000:
            base_rent *= 1.05
        elif subject.year_built and subject.year_built < 1980:
            base_rent *= 0.92
        
        # Garage premium
        if subject.garage_spaces and subject.garage_spaces >= 2:
            base_rent += 100
        
        return round(base_rent, 0)
    
    def _calculate_income(self, monthly_rent: float, vacancy_rate: float) -> Dict[str, float]:
        """Calculate income components."""
        annual_rent = monthly_rent * 12
        other_income = annual_rent * 0.02  # Pet fees, late fees, etc.
        
        pgi = annual_rent + other_income
        vacancy_loss = pgi * (vacancy_rate / 100)
        egi = pgi - vacancy_loss
        
        return {
            "monthly_rent": monthly_rent,
            "annual_rent": annual_rent,
            "other_income": round(other_income, 0),
            "pgi": round(pgi, 0),
            "vacancy_loss": round(vacancy_loss, 0),
            "effective_gross_income": round(egi, 0)
        }
    
    def _calculate_expenses(self, subject: BCPAOProperty, egi: float) -> Dict[str, float]:
        """Calculate operating expenses."""
        
        # Property taxes (use actual if available)
        if subject.taxable_value:
            taxes = subject.taxable_value * 0.018  # ~1.8% effective rate
        else:
            taxes = egi * 0.12  # Estimate 12% of EGI
        
        # Insurance (FL is expensive)
        insurance = egi * 0.08  # ~8% of EGI
        
        # Management (8%)
        management = egi * 0.08
        
        # Maintenance (5%)
        maintenance = egi * 0.05
        
        # Reserves (5%)
        reserves = egi * 0.05
        
        # HOA (would need actual data)
        hoa = 0
        
        total = taxes + insurance + management + maintenance + reserves + hoa
        ratio = (total / egi * 100) if egi > 0 else 0
        
        return {
            "taxes": round(taxes, 0),
            "insurance": round(insurance, 0),
            "management": round(management, 0),
            "maintenance": round(maintenance, 0),
            "reserves": round(reserves, 0),
            "hoa": round(hoa, 0),
            "total": round(total, 0),
            "ratio": round(ratio, 1)
        }
    
    def _calculate_cash_on_cash(self, noi: float, value: float, ltv: float = 0.75) -> float:
        """Calculate cash-on-cash return."""
        if value <= 0:
            return 0
        
        down_payment = value * (1 - ltv)
        
        # Estimate annual debt service
        loan_amount = value * ltv
        rate = 0.07  # 7% interest rate
        term = 30
        monthly_payment = loan_amount * (rate/12 * (1+rate/12)**(term*12)) / ((1+rate/12)**(term*12) - 1)
        annual_ds = monthly_payment * 12
        
        cash_flow = noi - annual_ds
        coc = (cash_flow / down_payment * 100) if down_payment > 0 else 0
        
        return round(coc, 2)
    
    def _calculate_dscr(self, noi: float, value: float, ltv: float = 0.75) -> float:
        """Calculate debt service coverage ratio."""
        if value <= 0:
            return 0
        
        loan_amount = value * ltv
        rate = 0.07
        term = 30
        monthly_payment = loan_amount * (rate/12 * (1+rate/12)**(term*12)) / ((1+rate/12)**(term*12) - 1)
        annual_ds = monthly_payment * 12
        
        dscr = noi / annual_ds if annual_ds > 0 else 0
        
        return round(dscr, 2)
    
    def _determine_confidence(
        self,
        subject: BCPAOProperty,
        market: RentalMarketData,
        estimated_rent: float
    ) -> str:
        """Determine confidence level."""
        
        # High confidence if:
        # - Market data is reliable
        # - Property is typical for rentals
        # - Rent estimate within market range
        
        if market.confidence == "HIGH":
            if market.rent_range_low <= estimated_rent <= market.rent_range_high:
                return "HIGH"
            return "MEDIUM"
        
        if market.confidence == "MEDIUM":
            return "MEDIUM"
        
        return "LOW"
    
    def _generate_narrative(
        self,
        subject: BCPAOProperty,
        rent: float,
        income: Dict,
        expenses: Dict,
        noi: float,
        cap_rate: float,
        value: float,
        confidence: str
    ) -> str:
        """Generate professional narrative."""
        
        narrative = f"""
Income Approach Analysis for {subject.address}

INCOME ANALYSIS:
Monthly Market Rent: ${rent:,.0f}
Annual Rent: ${rent * 12:,.0f}
Other Income: ${income['other_income']:,.0f}
Potential Gross Income: ${income['pgi']:,.0f}
Less: Vacancy ({expenses.get('vacancy_rate', 5):.1f}%): (${income['vacancy_loss']:,.0f})
Effective Gross Income: ${income['effective_gross_income']:,.0f}

OPERATING EXPENSES:
Property Taxes: ${expenses['taxes']:,.0f}
Insurance: ${expenses['insurance']:,.0f}
Management (8%): ${expenses['management']:,.0f}
Maintenance (5%): ${expenses['maintenance']:,.0f}
Reserves (5%): ${expenses['reserves']:,.0f}
Total Operating Expenses: ${expenses['total']:,.0f}
Expense Ratio: {expenses['ratio']:.1f}%

NET OPERATING INCOME: ${noi:,.0f}

DIRECT CAPITALIZATION:
Cap Rate: {cap_rate * 100:.2f}%
Value = NOI / Cap Rate
Value = ${noi:,.0f} / {cap_rate:.4f}
Indicated Value: ${value:,.0f}

The cap rate is derived from market survey of similar investment 
properties in the {subject.zip_code} market area.

Confidence Level: {confidence}
"""
        return narrative.strip()
    
    async def _store_results(self, analysis_id: str, result: IncomeApproachResult):
        """Store results in Supabase."""
        try:
            income_data = {
                "monthly_rent": result.monthly_rent,
                "potential_gross_income": result.potential_gross_income,
                "other_income": result.other_income,
                "vacancy_rate": result.vacancy_rate,
                "vacancy_loss": result.vacancy_loss,
                "effective_gross_income": result.effective_gross_income,
                "property_taxes": result.property_taxes,
                "insurance": result.insurance,
                "management_fee_pct": 8.0,
                "management_fee": result.management_fee,
                "maintenance": result.maintenance,
                "reserves": result.reserves,
                "hoa": result.hoa,
                "total_operating_expenses": result.total_expenses,
                "expense_ratio": result.expense_ratio,
                "net_operating_income": result.net_operating_income,
                "cap_rate_source": result.cap_rate_source,
                "cap_rate": result.cap_rate,
                "indicated_value": result.indicated_value,
                "grm": result.grm,
                "grm_value": result.indicated_value_grm,
                "confidence": result.confidence,
                "narrative": result.narrative
            }
            
            await self.supabase.store_income_approach(analysis_id, income_data)
            
        except Exception as e:
            logger.error(f"Error storing income approach: {e}")
    
    async def close(self):
        await self.bcpao.close()
        await self.rental.close()
        await self.census.close()
        await self.supabase.close()
