# ZoneWise Appraisal Agents

> Professional property valuation using AI-powered Three Approaches to Value

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)

## Overview

ZoneWise implements the **Three Approaches to Value** used by professional appraisers (MAI standards), powered by real-time data integrations:

1. **Sales Comparison Approach** - Market value from comparable sales
2. **Cost Approach** - Replacement cost minus depreciation
3. **Income Approach** - Capitalized net operating income

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AppraisalOrchestrator                        │
│                     (LangGraph Pipeline)                        │
└─────────────────────────┬───────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│    Sales      │ │     Cost      │ │    Income     │
│  Comparison   │ │   Approach    │ │   Approach    │
│    Agent      │ │    Agent      │ │    Agent      │
└───────┬───────┘ └───────┬───────┘ └───────┬───────┘
        │                 │                 │
        └─────────────────┴─────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│    BCPAO      │ │    Census     │ │     MLS       │
│    Client     │ │    Client     │ │    Client     │
└───────────────┘ └───────────────┘ └───────────────┘
```

## Data Sources

| Source | Data Type | API |
|--------|-----------|-----|
| **BCPAO** | Property details, valuations, sales history | GIS REST API |
| **Census** | Demographics, income, vacancy rates | ACS 5-Year API |
| **MLS** | Comparable sales, active listings | Apify (Redfin/Zillow) |
| **Rental** | Rental comps, market rates | Apify + Rentometer |
| **Supabase** | Analysis storage, KPI tracking | PostgreSQL REST |

## Installation

```bash
# Clone the repository
git clone https://github.com/breverdbidder/zonewise.git
cd zonewise

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export CENSUS_API_KEY="your_census_key"
export APIFY_API_KEY="your_apify_key"
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_SERVICE_KEY="your_service_key"
```

## Quick Start

### Full Appraisal

```python
import asyncio
from zonewise_agents import AppraisalOrchestrator

async def main():
    orchestrator = AppraisalOrchestrator()
    
    # By parcel ID
    result = await orchestrator.appraise("26-37-35-77-00042.0")
    
    # Or by address
    result = await orchestrator.appraise_by_address(
        "200 Jason Ct, Satellite Beach, FL 32937"
    )
    
    print(f"Sales Comparison: ${result.sales_comparison_value:,.0f}")
    print(f"Cost Approach: ${result.cost_approach_value:,.0f}")
    print(f"Income Approach: ${result.income_approach_value:,.0f}")
    print(f"Final Value: ${result.final_value_opinion:,.0f}")
    print(f"Confidence: {result.confidence}")
    
    await orchestrator.close()

asyncio.run(main())
```

### Individual Approaches

```python
from zonewise_agents import SalesComparisonAgent, CostApproachAgent, IncomeApproachAgent
from zonewise_agents import BCPAOClient

async def sales_comparison_only():
    agent = SalesComparisonAgent()
    result = await agent.analyze("26-37-35-77-00042.0")
    
    print(f"Indicated Value: ${result.indicated_value:,.0f}")
    print(f"Comparables Used: {len(result.comparables)}")
    
    for comp in result.comparables:
        print(f"  {comp['address']}: ${comp['sale_price']:,.0f} → ${comp['adjusted_price']:,.0f}")
    
    await agent.close()

async def cost_approach_only():
    bcpao = BCPAOClient()
    agent = CostApproachAgent()
    
    subject = await bcpao.get_property("26-37-35-77-00042.0")
    result = await agent.analyze(subject)
    
    print(f"Land Value: ${result.land_value:,.0f}")
    print(f"RCN: ${result.replacement_cost_new:,.0f}")
    print(f"Depreciation: ${result.total_depreciation:,.0f}")
    print(f"Indicated Value: ${result.indicated_value:,.0f}")
    
    await bcpao.close()
    await agent.close()
```

## CLI Demo

```bash
# Full appraisal by parcel
python demo_appraisal.py --parcel "26-37-35-77-00042.0"

# Full appraisal by address
python demo_appraisal.py --address "200 Jason Ct, Satellite Beach, FL 32937"

# Individual approaches
python demo_appraisal.py --parcel "26-37-35-77-00042.0" --approach sales
python demo_appraisal.py --parcel "26-37-35-77-00042.0" --approach cost
python demo_appraisal.py --parcel "26-37-35-77-00042.0" --approach income

# Save results to JSON
python demo_appraisal.py --parcel "26-37-35-77-00042.0" --output result.json
```

## Appraisal Methodology

### Sales Comparison Approach

1. **Subject Analysis**: Get property data from BCPAO
2. **Comp Search**: Find sales in BCPAO + MLS within:
   - 1.5 miles radius
   - 12 months recency
   - ±30% size
   - Same property type
3. **Adjustments**: Calculate $ adjustments for:
   - Living area ($100/SF)
   - Lot size ($5/SF)
   - Age ($500/year)
   - Bedrooms ($10,000 each)
   - Bathrooms ($7,500 each)
   - Garage ($15,000/space)
   - Pool ($25,000)
4. **Reconciliation**: Weight-based average of adjusted prices

### Cost Approach

1. **Land Value**: Sales comparison of vacant land by ZIP
2. **Replacement Cost New**:
   - Base cost/SF by quality tier
   - Construction type multiplier
   - Quality adjustments (pool, garage, etc.)
   - Soft costs (15%)
   - Entrepreneurial profit (10%)
3. **Depreciation**:
   - Physical: Age-life method
   - Functional: Layout/feature obsolescence
   - External: Market/location factors
4. **Indicated Value**: Land + (RCN - Depreciation)

### Income Approach

1. **Market Rent**: From rental comps + market data
2. **Income Analysis**:
   - Potential Gross Income
   - Vacancy & Credit Loss
   - Effective Gross Income
3. **Expenses**: Taxes, insurance, management, maintenance, reserves
4. **NOI**: EGI - Operating Expenses
5. **Capitalization**:
   - Direct Cap: NOI / Cap Rate
   - GRM: Rent × Gross Rent Multiplier
6. **Reconciliation**: 70% Direct Cap + 30% GRM

### Final Reconciliation

Weights by property type:
| Type | Sales | Cost | Income |
|------|-------|------|--------|
| Single Family (Owner) | 60% | 25% | 15% |
| Single Family (Rental) | 40% | 20% | 40% |
| Multi-Family | 30% | 20% | 50% |
| New Construction | 30% | 50% | 20% |

## Database Schema

The system stores results in Supabase:

```sql
-- Main analysis record
CREATE TABLE property_analyses (
    id UUID PRIMARY KEY,
    parcel_id TEXT,
    address TEXT,
    analysis_date TIMESTAMP,
    zonewise_score FLOAT,
    recommendation TEXT,
    confidence_level FLOAT
);

-- Comparable sales
CREATE TABLE comparable_sales (
    id UUID PRIMARY KEY,
    analysis_id UUID REFERENCES property_analyses(id),
    comp_number INTEGER,
    address TEXT,
    sale_price FLOAT,
    adjusted_price FLOAT,
    -- ... more fields
);

-- Each approach gets its own table
CREATE TABLE sales_comparison_conclusions (...);
CREATE TABLE cost_approach_analyses (...);
CREATE TABLE income_approach_analyses (...);
CREATE TABLE appraisal_reconciliation (...);
```

## Configuration

### Environment Variables

```bash
# Required
CENSUS_API_KEY=your_census_api_key
APIFY_API_KEY=apify_api_8J7Mo...

# Optional (for storage)
SUPABASE_URL=https://mocerqjnksmhcjzxrewo.supabase.co
SUPABASE_SERVICE_KEY=eyJ...
```

### Adjustment Rates

Customize in `SalesComparisonAgent.__init__`:

```python
self.adjustment_rates = {
    "living_area_per_sf": 100,
    "lot_size_per_sf": 5,
    "age_per_year": 500,
    "bedroom": 10000,
    "bathroom": 7500,
    "garage_space": 15000,
    "pool": 25000,
}
```

## Testing

```bash
# Run all tests
pytest tests/

# Test individual components
pytest tests/test_bcpao_client.py
pytest tests/test_sales_comparison.py
```

## File Structure

```
zonewise_agents/
├── __init__.py                    # Package exports
├── requirements.txt               # Dependencies
├── demo_appraisal.py             # CLI demo
├── README.md                      # This file
│
├── data_sources/                  # Data integrations
│   ├── __init__.py
│   ├── bcpao_client.py           # BCPAO property data
│   ├── census_client.py          # Census demographics
│   ├── mls_client.py             # MLS comparable sales
│   ├── rental_client.py          # Rental market data
│   └── supabase_client.py        # Database operations
│
└── agents/                        # Appraisal agents
    ├── __init__.py
    ├── sales_comparison_agent.py # Sales Comparison Approach
    ├── cost_approach_agent.py    # Cost Approach
    ├── income_approach_agent.py  # Income Approach
    └── appraisal_orchestrator.py # LangGraph orchestration
```

## License

Proprietary - © 2026 ZoneWise / ZoneWise.AI

---

Built with ❤️ by the ZoneWise team
