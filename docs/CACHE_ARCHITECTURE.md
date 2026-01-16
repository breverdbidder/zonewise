# ZoneWise Cache Architecture V1.0

## Overview

Three-layer caching system optimized for Firecrawl cost reduction while maintaining data freshness for zoning lookups.

**Target Performance:**
- Cache hit rate: 70%+
- Alpha cost: $20-40/month
- Beta cost (50 users): $50-83/month
- Annual savings vs. Zoneomics: $1,100-3,800

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ZoneWise Query                              │
│                    (Parcel ID or Jurisdiction)                      │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     L1: Jurisdiction Codes                          │
│              zonewise_jurisdiction_codes table                      │
│                    (30-day TTL, 17 jurisdictions)                   │
│                                                                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │ Satellite   │ │   Indian    │ │  Melbourne  │ │   Palm Bay  │   │
│  │   Beach     │ │   Harbour   │ │             │ │             │   │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │
│                        ... 13 more ...                              │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                   HIT                    MISS
                    │                       │
                    ▼                       ▼
            ┌───────────────┐   ┌─────────────────────────────────────┐
            │ Return cached │   │         L2: Parcel Cache            │
            │ jurisdiction  │   │      zonewise_parcel_cache table    │
            │    data       │   │           (90-day TTL)              │
            └───────────────┘   │                                     │
                                │  Lookup by: parcel_id, account_num  │
                                └───────────────────┬─────────────────┘
                                                    │
                                        ┌───────────┴───────────┐
                                        │                       │
                                       HIT                    MISS
                                        │                       │
                                        ▼                       ▼
                                ┌───────────────┐   ┌─────────────────┐
                                │ Return cached │   │  L3: Firecrawl  │
                                │  parcel data  │   │   Live Lookup   │
                                └───────────────┘   │                 │
                                                    │  1. BCPAO API   │
                                                    │  2. Jurisdiction│
                                                    │     website     │
                                                    │  3. Parse data  │
                                                    │  4. Store in L2 │
                                                    └─────────────────┘
```

## Database Tables

### L1: `zonewise_jurisdiction_codes`
Static zoning code definitions per jurisdiction.

| Column | Type | Description |
|--------|------|-------------|
| jurisdiction_id | VARCHAR(50) | PK, e.g., "satellite_beach" |
| jurisdiction_name | VARCHAR(100) | Display name |
| districts | JSONB | Array of zoning districts |
| code_document | TEXT | Full zoning code text |
| permitted_uses | JSONB | Use matrix by district |
| dimensional_standards | JSONB | Setbacks, heights, etc. |
| expires_at | TIMESTAMPTZ | Cache expiration |
| cache_hits | INTEGER | Analytics counter |

**Refresh:** Monthly (codes rarely change)

### L2: `zonewise_parcel_cache`
Parcel-to-zoning mappings after first lookup.

| Column | Type | Description |
|--------|------|-------------|
| parcel_id | VARCHAR(50) | PK, BCPAO parcel number |
| jurisdiction_id | VARCHAR(50) | FK to L1 |
| zoning_code | VARCHAR(20) | e.g., "R-1", "C-2" |
| dimensional requirements | INTEGER | All setback/height fields |
| permitted_uses | JSONB | Resolved uses for parcel |
| expires_at | TIMESTAMPTZ | 90-day cache expiration |
| is_stale | BOOLEAN | Manual invalidation flag |

**Refresh:** 90 days or on-demand

### `zonewise_lookup_log`
Audit trail for all lookups (analytics + cost tracking).

| Column | Type | Description |
|--------|------|-------------|
| lookup_type | VARCHAR(20) | parcel, jurisdiction, bulk |
| cache_hit | BOOLEAN | Was it served from cache? |
| cache_layer | VARCHAR(10) | L1, L2, or MISS |
| firecrawl_cost_estimate | DECIMAL | Cost if cache miss |
| user_id | VARCHAR(100) | For Beta multi-user |
| source | VARCHAR(50) | api, biddeed, spd, web |

### `zonewise_daily_metrics`
Aggregated daily statistics for monitoring.

## Cost Model

### Firecrawl Pricing (Hobby Plan)
- $16/month for 3,000 pages
- $0.0053 per page

### Alpha Phase (100 lookups/month)
| Scenario | Cache Hit Rate | Live Lookups | Pages | Cost |
|----------|---------------|--------------|-------|------|
| Cold start | 0% | 100 | 300 | $15.90 |
| Warm cache | 70% | 30 | 90 | $4.77 |
| Optimized | 85% | 15 | 45 | $2.39 |

**Target:** $20-40/month with Standard plan headroom

### Beta Phase (545 lookups/month, 50 users)
| Scenario | Cache Hit Rate | Live Lookups | Pages | Cost |
|----------|---------------|--------------|-------|------|
| Cold start | 0% | 545 | 1,635 | $86.66 |
| Warm cache | 70% | 164 | 492 | $26.08 |
| Optimized | 85% | 82 | 246 | $13.04 |

**Target:** $50-83/month with Standard plan

## Integration Points

### BidDeed.AI Integration
```python
from zonewise.cache_service import lookup_parcel_zoning

async def check_foreclosure_zoning(parcel_id: str):
    result = await lookup_parcel_zoning(
        parcel_id,
        source="biddeed_integration"
    )
    return result.data
```

### SPD Site Plan Integration
```python
from zonewise.cache_service import lookup_parcel_zoning

async def check_site_feasibility(parcel_id: str):
    result = await lookup_parcel_zoning(
        parcel_id,
        source="spd_integration"
    )
    
    if result.success:
        return {
            "zoning": result.data.get("zoning_code"),
            "max_height": result.data.get("max_height"),
            "setbacks": {
                "front": result.data.get("front_setback"),
                "rear": result.data.get("rear_setback"),
                "side": result.data.get("side_setback")
            }
        }
```

## Cache Warming Strategy

### Initial Deployment (One-Time)
```bash
# Warm L1 cache for all 17 jurisdictions
python -m zonewise.scripts.warm_jurisdiction_cache

# Pre-populate common parcels (foreclosure history)
python -m zonewise.scripts.warm_parcel_cache --source=historical_auctions
```

### Nightly Maintenance
```yaml
# GitHub Actions: .github/workflows/cache_maintenance.yml
- name: Mark stale entries
  run: python -m zonewise.scripts.mark_stale_parcels

- name: Cleanup old logs
  run: python -m zonewise.scripts.cleanup_logs --days=365
```

## Monitoring

### Cache Stats View
```sql
SELECT * FROM zonewise_cache_stats;
```
Returns:
- L1/L2 entry counts
- 30-day cache hit rate
- 30-day Firecrawl cost
- Today's lookup count

### Cost Alert Threshold
Set up Supabase webhook when:
```sql
SELECT firecrawl_cost_30d > 75  -- Alert at 75% of budget
FROM zonewise_cache_stats;
```

## Environment Variables

```bash
# Supabase (ZoneWise-specific instance)
ZONEWISE_SUPABASE_URL=https://[project].supabase.co
ZONEWISE_SUPABASE_KEY=eyJ...

# Firecrawl
FIRECRAWL_API_KEY=fc-...

# Optional: BidDeed.AI integration
BIDDEED_SUPABASE_URL=https://mocerqjnksmhcjzxrewo.supabase.co
```

## Files Structure

```
zonewise/
├── database/
│   ├── seed_requirements.sql      # Existing dimensional data
│   └── cache_schema.sql           # NEW: Cache tables
├── src/
│   ├── cache_service.py           # NEW: Cache service
│   ├── scrapers/
│   │   └── firecrawl_adapter.py   # Firecrawl integration
│   └── api/
│       └── zoning_endpoints.py    # API routes
├── scripts/
│   ├── warm_jurisdiction_cache.py
│   ├── warm_parcel_cache.py
│   └── cleanup_logs.py
└── tests/
    └── test_cache_service.py
```

## Comparison: Zoneomics vs. ZoneWise Cache

| Metric | Zoneomics API | ZoneWise + Firecrawl |
|--------|--------------|---------------------|
| Alpha cost | $89/month | $20-40/month |
| Beta cost | $189-489/month | $50-83/month |
| Annual cost | $1,968-5,868 | $510-867 |
| Data freshness | Weekly | On-demand |
| Brevard coverage | Generic | Tailored to 17 jurisdictions |
| Customization | Limited schemas | Full control |
| Setup effort | Low | Medium (one-time) |

**Decision:** Build ZoneWise cache for Alpha/Beta. Revisit Zoneomics when expanding beyond Brevard County.

---

*Last Updated: January 15, 2026*
*Author: Claude AI Architect*
