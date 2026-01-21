# CMA Market Analysis Summarizer v2.0

> **BidDeed.AI | Agentic Comparative Market Analysis**
> 
> Transform raw comps data into actionable valuation intelligence in under 5 minutes.
> 
> **Used by:** BidDeed.AI (foreclosure max bid calculations) | ZoneWise (zoning + valuation)

---

## Quick Start

Copy the prompt template below into Claude, ChatGPT, or Gemini along with your property data.

---

## AI Prompt Template

```
You are a professional real estate market analyst specializing in residential property valuation. Create a comprehensive, client-ready CMA summary from the provided comparable sales data.

CRITICAL INSTRUCTIONS:
- Calculate price/sqft for every property
- Identify the most comparable property (closest match in size, condition, features)
- Provide specific dollar adjustments with clear rationale
- Include confidence level (High/Medium/Low) based on comp quality
- Format for immediate client presentation

OUTPUT FORMAT:

## 1. EXECUTIVE SUMMARY
[3-4 sentences: market position, key advantages, timing recommendation]

## 2. PRICING RECOMMENDATION
**Suggested List Price:** $XXX,XXX
**Price Range:** $XXX,XXX - $XXX,XXX
**Confidence Level:** [High/Medium/Low]
**Strategy:** [Aggressive/Competitive/Quick Sale]

## 3. COMPARABLE SALES ANALYSIS
[Table with: Address | Price | Bed/Bath | Sqft | $/Sqft | DOM | Sold Date | Condition]
[Include price/sqft average and subject property target range]

## 4. ACTIVE COMPETITION
[Table with: Address | List Price | Bed/Bath | Sqft | $/Sqft | DOM | Analysis]
[Note overpriced listings, direct competitors, and market gaps]

## 5. MARKET CONDITIONS
- Market Type: [Seller's/Buyer's/Balanced]
- Inventory Level: [X months supply]
- Average DOM: [X days]
- Price Trend: [Direction + % over 90 days]
- Offer Activity: [Multiple offers common/Single offers typical/Negotiation expected]

## 6. ADJUSTMENT ANALYSIS
[Table with: Feature | Adjustment | Rationale]
[Show total adjustments and final adjusted value]

## 7. PRICING STRATEGY
- Recommended Price: $XXX,XXX
- Positioning rationale
- Expected timeline
- Best/Likely/Worst case outcomes

## 8. NEXT STEPS
[5-6 actionable items for listing preparation]

---

SUBJECT PROPERTY:
[ADDRESS]
[BEDS/BATHS/SQFT/LOT SIZE/YEAR BUILT]
[KEY FEATURES AND CONDITION]
[RECENT UPGRADES WITH DATES]

COMPARABLE SALES (CLOSED):
1. [Address] - $XXX,XXX, X/X bed/bath, X,XXX sqft, X.XX acre, sold [DATE], [X] DOM, [CONDITION], [KEY FEATURES]
2. [Continue for 3-6 comps]

ACTIVE LISTINGS (COMPETITION):
1. [Address] - $XXX,XXX, X/X bed/bath, X,XXX sqft, [X] DOM, [CONDITION]
2. [Continue for 2-4 active listings]

MARKET CONTEXT (Optional):
[Inventory levels, DOM trends, recent market activity]
```

---

## Example: Complete CMA

### Input Data

**SUBJECT PROPERTY:**
456 Maple Avenue, Satellite Beach, FL 32937
4 bed, 2.5 bath, 2,200 sqft, 0.25 acre lot, built 2015
Excellent condition, updated kitchen (2024), new HVAC (2023), hardwood floors, corner lot

**COMPARABLE SALES:**
1. 123 Oak St - $485,000, 4/2, 2,100 sqft, 0.20 acre, sold Dec 15 2025, 18 DOM, average condition, original kitchen
2. 789 Elm Dr - $510,000, 4/2.5, 2,300 sqft, 0.22 acre, sold Nov 22 2025, 12 DOM, fully renovated 2024
3. 321 Pine Ln - $472,000, 3/2, 2,000 sqft, 0.18 acre, sold Jan 8 2026, 31 DOM, needs updates
4. 555 Birch Way - $498,000, 4/2.5, 2,150 sqft, 0.23 acre, sold Dec 28 2025, 15 DOM, good condition

**ACTIVE LISTINGS:**
1. 888 Cedar Ct - $519,000, 4/2.5, 2,250 sqft, 22 DOM, good condition
2. 999 Willow Rd - $489,000, 4/2, 2,100 sqft, 45 DOM, average condition
3. 111 Spruce Ave - $535,000, 4/3, 2,400 sqft, 8 DOM, luxury finishes

**MARKET CONTEXT:**
Low inventory (2.1 months supply), average DOM trending down to 19 days, seller's market with multiple offers common

---

### Output Example

# CMA Summary: 456 Maple Avenue, Satellite Beach

**Prepared for:** [Client Name]  
**Date:** January 2026  
**Platform:** BidDeed.AI

---

## 1. Executive Summary

Your property at 456 Maple Avenue is exceptionally well-positioned in the current Brevard County seller's market. The 2024 kitchen renovation, new HVAC system, and premium corner lot location place it in the top tier of available inventory. With only 2.1 months of supply and declining days on market, this home should attract multiple offers within the first two weeks if priced strategically.

---

## 2. Pricing Recommendation

| Metric | Value |
|--------|-------|
| **Suggested List Price** | $509,000 |
| **Price Range** | $500,000 - $520,000 |
| **Confidence Level** | High |
| **Strategy** | Competitive |

**Rationale:** Positioned to attract maximum buyer interest while capturing full value based on superior updates and condition.

---

## 3. Comparable Sales Analysis

| Address | Price | Bed/Bath | Sqft | $/Sqft | DOM | Sold | Condition |
|---------|-------|----------|------|--------|-----|------|-----------|
| 123 Oak St | $485,000 | 4/2 | 2,100 | $231 | 18 | Dec 15 '25 | Average |
| 789 Elm Dr | $510,000 | 4/2.5 | 2,300 | $222 | 12 | Nov 22 '25 | Renovated |
| 321 Pine Ln | $472,000 | 3/2 | 2,000 | $236 | 31 | Jan 8 '26 | Below Avg |
| 555 Birch Way | $498,000 | 4/2.5 | 2,150 | $232 | 15 | Dec 28 '25 | Good |

**Average Sold $/Sqft:** $230  
**Subject Property Target:** $228-$236/sqft = **$502,000 - $519,000**

**Most Comparable:** 555 Birch Way - similar bed/bath config, lot size, and DOM. Subject property commands premium due to recent kitchen renovation.

---

## 4. Active Competition

| Address | List Price | Bed/Bath | Sqft | $/Sqft | DOM | Status |
|---------|------------|----------|------|--------|-----|--------|
| 888 Cedar Ct | $519,000 | 4/2.5 | 2,250 | $231 | 22 | Direct Comp |
| 999 Willow Rd | $489,000 | 4/2 | 2,100 | $233 | 45 | Overpriced |
| 111 Spruce Ave | $535,000 | 4/3 | 2,400 | $223 | 8 | Premium Tier |

**Analysis:**
- 999 Willow Rd at 45 DOM indicates market resistance at that price/condition combo
- 888 Cedar Ct is our direct competition - we can undercut while offering superior updates
- 111 Spruce Ave targets a higher segment; not our competition

---

## 5. Market Conditions

| Indicator | Status | Interpretation |
|-----------|--------|----------------|
| **Market Type** | Seller's Market | Favors aggressive pricing |
| **Inventory** | 2.1 months | Low (balanced is 4-6 months) |
| **Average DOM** | 19 days | Decreasing - strong demand |
| **Price Trend** | +2% (90 days) | Stable to increasing |
| **Offer Activity** | Multiple offers common | Price competitively to generate bidding |

**Bottom Line:** Current conditions favor sellers. Well-priced, updated homes receiving multiple offers within 10-14 days.

---

## 6. Adjustment Analysis

| Feature | Adjustment | Rationale |
|---------|------------|-----------|
| Updated Kitchen (2024) | +$15,000 | Recent renovation vs. original kitchens in comps |
| New HVAC (2023) | +$8,000 | Major system replacement reduces buyer concerns |
| Corner Lot (0.25 acre) | +$10,000 | Premium location with extra yard/privacy |
| Hardwood Floors | +$5,000 | Desirable feature vs. carpet in some comps |
| 2.5 Bath vs 2 Bath | +$7,000 | Extra half bath valuable for 4BR homes |
| Excellent Condition | +$5,000 | Move-in ready vs. homes needing updates |
| **Total Adjustments** | **+$50,000** | |

**Base Comp Average:** $488,000  
**Adjusted Value:** $538,000  
**Market-Adjusted Range:** $500,000 - $520,000 (accounts for negotiation)

---

## 7. Pricing Strategy

### Recommended: $509,000

**Why This Price:**
- Positioned between direct comp 555 Birch Way ($498K) and premium 789 Elm Dr ($510K)
- Psychology: $509K feels significantly better than $510K+ while capturing value
- Undercuts direct competitor 888 Cedar Ct ($519K) while offering superior updates
- Allows $4-9K negotiation room while staying above psychological $500K floor

### Expected Outcomes

| Scenario | Timeline | Sale Price | % of List |
|----------|----------|------------|-----------|
| **Best Case** | 7-10 days | $510K-$515K | 100-101% |
| **Likely Case** | 10-14 days | $505K-$510K | 99-100% |
| **Worst Case** | 21-30 days | $500K-$505K | 98-99% |

### Alternative Strategies

| Strategy | List Price | Timeline | Risk/Reward |
|----------|------------|----------|-------------|
| Aggressive | $519,000 | 30+ days | Test ceiling, may need reduction |
| Quick Sale | $499,000 | 7-10 days | Generate bidding war, likely sell $510K+ |

---

## 8. Next Steps

1. **Professional Photography** - Schedule shoot highlighting kitchen renovation and corner lot landscaping
2. **Pre-Listing Inspection** - Address any issues proactively to avoid contract negotiations
3. **Staging Consultation** - Emphasize open floor plan and natural light
4. **List Thursday/Friday** - Maximize weekend showing traffic
5. **Review Deadline** - Set Tuesday evening for offer review after first weekend
6. **Pricing Adjustment Trigger** - If no offers after 14 days, reassess at $499,000

---

*This analysis based on current market data as of January 2026. Market conditions change rapidly. BidDeed.AI updates valuations daily from MLS, BCPAO, and county records.*

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | Jan 2026 | Enhanced format, added market condition indicators, confidence levels |
| 1.0 | Dec 2025 | Initial release |

---

## Tips for Best Results

### Data Collection

1. **Comps Selection:**
   - Same subdivision or within 0.5 miles
   - Sold within 90 days (6 months max for slow markets)
   - Within 10% of subject sqft
   - Same bed/bath configuration preferred

2. **Adjustment Values (Brevard County 2026):**
   - Bedroom: +/- $10,000-15,000
   - Full Bath: +/- $8,000-12,000
   - Half Bath: +/- $5,000-7,000
   - Pool: +$15,000-25,000 (market dependent)
   - Renovated Kitchen: +$15,000-30,000
   - New Roof: +$10,000-15,000
   - Sqft: $100-150/sqft (varies by area)

3. **Local Market Resources:**
   - MLS (primary source)
   - BCPAO (Brevard County Property Appraiser)
   - Realtor.com/Zillow (active listings)
   - Property360 market reports

---

## License

BidDeed.AI - Everest Capital USA
Internal Tool | Also powers ZoneWise valuations
Contact: ariel@biddeed.ai

---

## BidDeed.AI Integration

### Max Bid Formula
This CMA feeds directly into BidDeed.AI's max bid calculation:

```
Max Bid = (ARV × 70%) - Repairs - $10K - MIN($25K, 15% × ARV)
```

Where **ARV (After Repair Value)** = CMA Adjusted Value

### Decision Thresholds
| Bid/Judgment Ratio | Recommendation |
|--------------------|----------------|
| ≥ 75% | **BID** - Strong opportunity |
| 60-74% | **REVIEW** - Manual analysis needed |
| < 60% | **SKIP** - Insufficient margin |

### Pipeline Stage
CMA runs at **Stage 7 (ML Score)** in the 12-stage pipeline:
1. Discovery → 2. Scraping → 3. Title Search → 4. Lien Priority → 5. Tax Certs → 6. Demographics → **7. ML Score (CMA)** → 8. Max Bid → 9. Decision Log → 10. Report → 11. Disposition → 12. Archive

---

## ZoneWise Integration

CMA provides the **valuation layer** for ZoneWise's zoning analysis:

| ZoneWise Component | CMA Contribution |
|--------------------|------------------|
| Site Feasibility | ARV establishes project ceiling |
| Development Pro Forma | $/sqft benchmarks for new construction |
| Highest & Best Use | Comparable analysis validates use case |
| Entitlement ROI | Before/after valuation delta |

### API Endpoint (Future)
```
POST /api/v1/cma/analyze
{
  "subject_property": {...},
  "comparables": [...],
  "active_listings": [...],
  "market_context": {...}
}
```
