# ZoneWise Database Migrations

SQL migration files for ZoneWise database schema with zonewize skill integration.

## Files

- **001_initial_schema.sql** - All tables, indexes, views, RLS policies
- **002_seed_jurisdictions.sql** - 17 Brevard County jurisdictions

## Quick Start

```bash
# Local development
supabase start
psql postgresql://postgres:postgres@localhost:54322/postgres -f migrations/001_initial_schema.sql
psql postgresql://postgres:postgres@localhost:54322/postgres -f migrations/002_seed_jurisdictions.sql

# Production
export DATABASE_URL="postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres"
psql $DATABASE_URL -f migrations/001_initial_schema.sql
psql $DATABASE_URL -f migrations/002_seed_jurisdictions.sql
```

## Verification

```sql
SELECT COUNT(*) FROM jurisdictions;  -- Should return 17
SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';  -- Should return 10
SELECT COUNT(*) FROM information_schema.views WHERE table_schema = 'public';  -- Should return 4
```

See full documentation: [SUPABASE_INTEGRATION.md](../docs/SUPABASE_INTEGRATION.md)
