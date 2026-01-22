---
name: everest-supabase-operations
description: Supabase database operations for Everest Capital projects (BidDeed.AI, ZoneWise, Life OS). Includes query building, checkpoint management, insights logging, and table schemas. Connection to mocerqjnksmhcjzxrewo.supabase.co. Handles RLS policies, migrations, and error recovery. Triggers on: Supabase query, database, checkpoint, save state, insights, table schema, RLS policy.
---

# Everest Supabase Operations

## Connection

**Project**: mocerqjnksmhcjzxrewo.supabase.co
**Region**: us-east-1

```python
from supabase import create_client

SUPABASE_URL = "https://mocerqjnksmhcjzxrewo.supabase.co"
SUPABASE_KEY = os.environ["SUPABASE_KEY"]  # Service role key

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
```

## Key Tables

### BidDeed.AI Tables

| Table | Purpose | Rows |
|-------|---------|------|
| `historical_auctions` | Past auction data for ML | 1,393+ |
| `multi_county_auctions` | Current auction listings | Dynamic |
| `daily_metrics` | Pipeline performance | Daily |
| `insights` | System logs, decisions | Append-only |
| `activities` | User/system activities | 12+ |

### ZoneWise Tables

| Table | Purpose |
|-------|---------|
| `districts` | 273 zoning districts |
| `jurisdictions` | 17 Florida jurisdictions |
| `mcp_requests` | MCP server logs |

### Life OS Tables

| Table | Purpose |
|-------|---------|
| `tasks` | ADHD task tracking |
| `sprint_tasks` | Ralph Wiggum queue |
| `tax_records` | Tax optimization data |

### Shared Tables

| Table | Purpose |
|-------|---------|
| `claude_context_checkpoints` | Conversation state |
| `api_usage` | API cost tracking |

## Query Patterns

### Safe Query Building
```python
from scripts.query_builder import QueryBuilder

qb = QueryBuilder("historical_auctions")

# Select with filters
result = qb.select(
    columns=["case_number", "judgment_amount", "sale_price"],
    filters={"zip_code": "32937", "year": 2025},
    order_by="auction_date",
    limit=100
).execute()
```

### Insert with Validation
```python
from scripts.query_builder import safe_insert

# Validates against schema before insert
result = safe_insert(
    table="multi_county_auctions",
    data={
        "case_number": "05-2024-CA-012345",
        "parcel_id": "12345678",
        "judgment_amount": 150000,
        "auction_date": "2026-01-21"
    }
)
```

### Upsert Pattern
```python
result = supabase.table("multi_county_auctions").upsert(
    data,
    on_conflict="case_number"
).execute()
```

## Checkpoint Management

### Save Checkpoint
```python
from scripts.checkpoint_manager import save_checkpoint

save_checkpoint(
    conversation_id="conv_123",
    state={
        "current_task": "foreclosure_analysis",
        "properties_processed": 15,
        "pending_properties": ["12345678", "87654321"],
        "context_summary": "Analyzing Dec 3 auction..."
    },
    token_count=150000
)
```

### Load Checkpoint
```python
from scripts.checkpoint_manager import load_checkpoint

checkpoint = load_checkpoint(conversation_id="conv_123")
if checkpoint:
    state = checkpoint["state"]
    # Resume from saved state
```

### Auto-Checkpoint Trigger
```python
TOKEN_THRESHOLD = 150000  # 75% of 200K limit

def check_checkpoint_needed(current_tokens: int) -> bool:
    return current_tokens >= TOKEN_THRESHOLD
```

## Insights Logging

### Log Insight
```python
from scripts.insights_logger import log_insight

log_insight(
    category="ml_prediction",
    message="Third-party probability: 72%",
    data={
        "parcel_id": "12345678",
        "probability": 0.72,
        "confidence": "high"
    },
    level="info"
)
```

### Log Categories
- `pipeline`: Scraper/workflow events
- `ml_prediction`: Model predictions
- `decision`: BID/REVIEW/SKIP decisions
- `error`: Errors and failures
- `performance`: Timing and metrics
- `audit`: Security/compliance events

### Query Insights
```python
# Get recent errors
errors = supabase.table("insights")\
    .select("*")\
    .eq("level", "error")\
    .gte("created_at", "2026-01-20")\
    .execute()
```

## Table Schemas

### historical_auctions
```sql
CREATE TABLE historical_auctions (
    id SERIAL PRIMARY KEY,
    case_number TEXT UNIQUE NOT NULL,
    parcel_id TEXT,
    address TEXT,
    zip_code TEXT,
    judgment_amount NUMERIC,
    opening_bid NUMERIC,
    sale_price NUMERIC,
    sold_to_third_party BOOLEAN,
    plaintiff TEXT,
    plaintiff_category TEXT,
    auction_date DATE,
    property_type TEXT,
    assessed_value NUMERIC,
    bedrooms INT,
    bathrooms NUMERIC,
    building_sf INT,
    lot_sf INT,
    year_built INT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### claude_context_checkpoints
```sql
CREATE TABLE claude_context_checkpoints (
    id SERIAL PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    state JSONB NOT NULL,
    token_count INT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '7 days')
);

CREATE INDEX idx_checkpoints_conv ON claude_context_checkpoints(conversation_id);
```

### insights
```sql
CREATE TABLE insights (
    id SERIAL PRIMARY KEY,
    category TEXT NOT NULL,
    level TEXT DEFAULT 'info',
    message TEXT NOT NULL,
    data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_insights_category ON insights(category);
CREATE INDEX idx_insights_created ON insights(created_at DESC);
```

## RLS Policies

### Service Role (Full Access)
```sql
-- Used by backend/scripts
CREATE POLICY "Service role full access" ON historical_auctions
    FOR ALL USING (auth.role() = 'service_role');
```

### Anon Role (Read Only)
```sql
-- Used by public API
CREATE POLICY "Anon read access" ON districts
    FOR SELECT USING (true);
```

## Error Recovery

### Retry Pattern
```python
from scripts.query_builder import with_retry

@with_retry(max_attempts=3, backoff=2.0)
async def fetch_with_retry(table: str, filters: dict):
    return supabase.table(table).select("*").match(filters).execute()
```

### Connection Recovery
```python
from scripts.connection_manager import get_client

# Auto-reconnects on failure
client = get_client()  # Cached, reconnects if stale
```

## Migrations

### Run Migration
```bash
# Using Supabase CLI
supabase db push

# Or direct SQL
psql $DATABASE_URL -f migrations/001_add_column.sql
```

### Migration Naming
```
migrations/
├── 001_initial_schema.sql
├── 002_add_ml_features.sql
├── 003_add_checkpoints.sql
└── 004_add_indexes.sql
```

## Performance Tips

1. **Use indexes** for filtered columns
2. **Limit results** - never `SELECT *` without LIMIT
3. **Use RPC** for complex queries
4. **Batch inserts** - use `upsert` with arrays
5. **Cache lookups** - districts change rarely

## Integration

- **BidDeed.AI**: Historical data, predictions, reports
- **ZoneWise**: District data, MCP logs
- **Life OS**: Task tracking, tax records
- **Claude Sessions**: Context checkpoints
