#!/usr/bin/env python3
"""
ZoneWise Appraisal Demo
Demonstrates the Three Approaches to Value using real data

Usage:
    python demo_appraisal.py --parcel "26-37-35-77-00042.0"
    python demo_appraisal.py --address "200 Jason Ct, Satellite Beach, FL 32937"

© 2026 ZoneWise - Ariel Shapira
"""

import asyncio
import argparse
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger('ZoneWise')

# Import agents
from agents.appraisal_orchestrator import AppraisalOrchestrator
from agents.sales_comparison_agent import SalesComparisonAgent
from agents.cost_approach_agent import CostApproachAgent
from agents.income_approach_agent import IncomeApproachAgent
from data_sources.bcpao_client import BCPAOClient


async def demo_full_appraisal(parcel_id: str = None, address: str = None):
    """Run full Three Approaches appraisal."""
    
    print("\n" + "="*70)
    print("🏠 ZONEWISE PROPERTY APPRAISAL")
    print("   Three Approaches to Value")
    print("="*70 + "\n")
    
    orchestrator = AppraisalOrchestrator()
    
    try:
        # Run appraisal
        if parcel_id:
            print(f"📍 Analyzing parcel: {parcel_id}\n")
            result = await orchestrator.appraise(
                parcel_id,
                property_type="single_family_owner",
                store_results=False  # Demo mode - don't store
            )
        elif address:
            print(f"📍 Analyzing address: {address}\n")
            result = await orchestrator.appraise_by_address(
                address,
                property_type="single_family_owner",
                store_results=False
            )
        else:
            # Default demo property
            parcel_id = "26-37-35-77-00042.0"  # Sample Satellite Beach property
            print(f"📍 Demo property: {parcel_id}\n")
            result = await orchestrator.appraise(
                parcel_id,
                property_type="single_family_owner",
                store_results=False
            )
        
        # Display results
        print_appraisal_results(result)
        
        return result
        
    finally:
        await orchestrator.close()


async def demo_sales_comparison(parcel_id: str):
    """Demo just the Sales Comparison Approach."""
    
    print("\n" + "="*70)
    print("📊 SALES COMPARISON APPROACH")
    print("="*70 + "\n")
    
    agent = SalesComparisonAgent()
    
    try:
        result = await agent.analyze(parcel_id, store_results=False)
        
        print(f"Subject: {result.subject_property.get('address', parcel_id)}")
        print(f"Living Area: {result.subject_property.get('living_area_sf', 0):,} SF")
        print(f"Year Built: {result.subject_property.get('year_built', 'N/A')}")
        print()
        
        print("COMPARABLE SALES:")
        print("-" * 60)
        
        for comp in result.comparables:
            print(f"\nComp #{comp['comp_number']}: {comp['address']}")
            print(f"  Sale Price: ${comp['sale_price']:,.0f}")
            print(f"  Sale Date: {comp['sale_date']}")
            print(f"  Size: {comp['living_area_sf']:,} SF")
            print(f"  Adjustments: ${comp['adjustments']['total']:+,.0f}")
            print(f"  Adjusted Price: ${comp['adjusted_price']:,.0f}")
        
        print()
        print("=" * 60)
        print(f"INDICATED VALUE: ${result.indicated_value:,.0f}")
        print(f"Price/SF: ${result.price_per_sf:,.0f}")
        print(f"Confidence: {result.confidence}")
        print("=" * 60)
        
        return result
        
    finally:
        await agent.close()


async def demo_cost_approach(parcel_id: str):
    """Demo just the Cost Approach."""
    
    print("\n" + "="*70)
    print("🏗️ COST APPROACH")
    print("="*70 + "\n")
    
    bcpao = BCPAOClient()
    agent = CostApproachAgent()
    
    try:
        subject = await bcpao.get_property(parcel_id)
        if not subject:
            print(f"Property not found: {parcel_id}")
            return None
        
        result = await agent.analyze(subject, store_results=False)
        
        print(f"Subject: {subject.address}")
        print()
        
        print("LAND VALUE:")
        print(f"  Site Size: {subject.lot_size_sf:,.0f} SF")
        print(f"  Land Value: ${result.land_value:,.0f}")
        print(f"  Per SF: ${result.land_value_per_sf:.2f}")
        print()
        
        print("REPLACEMENT COST NEW:")
        print(f"  Building SF: {result.building_sf:,}")
        print(f"  Base Cost @ ${result.base_cost_per_sf}/SF: ${result.base_cost:,.0f}")
        print(f"  Quality Adjustments: ${result.quality_adjustment:,.0f}")
        print(f"  Soft Costs: ${result.soft_costs:,.0f}")
        print(f"  Entrepreneurial Profit: ${result.entrepreneurial_profit:,.0f}")
        print(f"  Total RCN: ${result.replacement_cost_new:,.0f}")
        print()
        
        print("DEPRECIATION:")
        print(f"  Physical ({result.physical_depreciation_pct:.1f}%): ${result.physical_depreciation:,.0f}")
        print(f"  Functional: ${result.functional_obsolescence:,.0f}")
        print(f"  External: ${result.external_obsolescence:,.0f}")
        print(f"  Total: ${result.total_depreciation:,.0f}")
        print()
        
        print("=" * 60)
        print(f"INDICATED VALUE: ${result.indicated_value:,.0f}")
        print(f"Confidence: {result.confidence}")
        print("=" * 60)
        
        return result
        
    finally:
        await bcpao.close()
        await agent.close()


async def demo_income_approach(parcel_id: str):
    """Demo just the Income Approach."""
    
    print("\n" + "="*70)
    print("💰 INCOME APPROACH")
    print("="*70 + "\n")
    
    bcpao = BCPAOClient()
    agent = IncomeApproachAgent()
    
    try:
        subject = await bcpao.get_property(parcel_id)
        if not subject:
            print(f"Property not found: {parcel_id}")
            return None
        
        result = await agent.analyze(subject, store_results=False)
        
        print(f"Subject: {subject.address}")
        print(f"Bedrooms: {subject.bedrooms} | Bathrooms: {subject.bathrooms}")
        print()
        
        print("INCOME:")
        print(f"  Monthly Rent: ${result.monthly_rent:,.0f}")
        print(f"  Annual Rent: ${result.annual_rent:,.0f}")
        print(f"  Other Income: ${result.other_income:,.0f}")
        print(f"  Potential Gross Income: ${result.potential_gross_income:,.0f}")
        print(f"  Vacancy Loss ({result.vacancy_rate:.1f}%): (${result.vacancy_loss:,.0f})")
        print(f"  Effective Gross Income: ${result.effective_gross_income:,.0f}")
        print()
        
        print("EXPENSES:")
        print(f"  Property Taxes: ${result.property_taxes:,.0f}")
        print(f"  Insurance: ${result.insurance:,.0f}")
        print(f"  Management: ${result.management_fee:,.0f}")
        print(f"  Maintenance: ${result.maintenance:,.0f}")
        print(f"  Reserves: ${result.reserves:,.0f}")
        print(f"  Total Expenses: ${result.total_expenses:,.0f}")
        print(f"  Expense Ratio: {result.expense_ratio:.1f}%")
        print()
        
        print(f"NET OPERATING INCOME: ${result.net_operating_income:,.0f}")
        print()
        
        print("CAPITALIZATION:")
        print(f"  Cap Rate: {result.cap_rate * 100:.2f}%")
        print(f"  Direct Cap Value: ${result.indicated_value_direct_cap:,.0f}")
        print(f"  GRM ({result.grm}) Value: ${result.indicated_value_grm:,.0f}")
        print()
        
        print("INVESTMENT METRICS:")
        print(f"  Cash-on-Cash Return: {result.cash_on_cash:.2f}%")
        print(f"  DSCR: {result.dscr:.2f}")
        print()
        
        print("=" * 60)
        print(f"INDICATED VALUE: ${result.indicated_value:,.0f}")
        print(f"Confidence: {result.confidence}")
        print("=" * 60)
        
        return result
        
    finally:
        await bcpao.close()
        await agent.close()


def print_appraisal_results(result):
    """Print formatted appraisal results."""
    
    print("PROPERTY INFORMATION:")
    print(f"  Address: {result.address}")
    print(f"  Parcel ID: {result.parcel_id}")
    print()
    
    print("THREE APPROACHES TO VALUE:")
    print("-" * 60)
    print(f"  1. Sales Comparison: ${result.sales_comparison_value:>12,.0f}  (Weight: {result.sales_weight}%)")
    print(f"  2. Cost Approach:    ${result.cost_approach_value:>12,.0f}  (Weight: {result.cost_weight}%)")
    print(f"  3. Income Approach:  ${result.income_approach_value:>12,.0f}  (Weight: {result.income_weight}%)")
    print("-" * 60)
    print()
    
    print("RECONCILIATION:")
    print(f"  Value Range: ${result.value_range_low:,.0f} - ${result.value_range_high:,.0f}")
    print(f"  Most Applicable Approach: {result.most_applicable}")
    print()
    
    print("=" * 60)
    print(f"  FINAL VALUE OPINION: ${result.final_value_opinion:>15,.0f}")
    print("=" * 60)
    print()
    
    print(f"Recommendation: {result.recommendation}")
    print(f"Confidence: {result.confidence}")
    if result.max_bid:
        print(f"Max Bid (Foreclosure): ${result.max_bid:,.0f}")
    print(f"Processing Time: {result.processing_time_seconds:.1f} seconds")
    print(f"Stages Completed: {', '.join(result.stages_completed)}")
    print()


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='ZoneWise Property Appraisal Demo')
    parser.add_argument('--parcel', type=str, help='BCPAO parcel ID')
    parser.add_argument('--address', type=str, help='Property address')
    parser.add_argument('--approach', type=str, choices=['all', 'sales', 'cost', 'income'],
                        default='all', help='Which approach to demo')
    parser.add_argument('--output', type=str, help='Output JSON file')
    
    args = parser.parse_args()
    
    # Default demo parcel
    parcel_id = args.parcel or "26-37-35-77-00042.0"
    
    if args.approach == 'all':
        result = await demo_full_appraisal(parcel_id=args.parcel, address=args.address)
    elif args.approach == 'sales':
        result = await demo_sales_comparison(parcel_id)
    elif args.approach == 'cost':
        result = await demo_cost_approach(parcel_id)
    elif args.approach == 'income':
        result = await demo_income_approach(parcel_id)
    
    # Save output if requested
    if args.output and result:
        from dataclasses import asdict
        with open(args.output, 'w') as f:
            json.dump(asdict(result), f, indent=2, default=str)
        print(f"\n📄 Results saved to: {args.output}")


if __name__ == "__main__":
    asyncio.run(main())
