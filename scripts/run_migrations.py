"""Run SQL migrations against Supabase via REST API."""

import httpx
import sys
import os
from pathlib import Path

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", os.environ.get("SUPABASE_SERVICE_KEY", ""))

def run_sql(sql: str, description: str = "") -> dict:
    """Execute SQL via Supabase REST API (rpc endpoint for raw SQL)."""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    # Use the Supabase SQL endpoint (PostgREST doesn't support raw SQL,
    # so we use the management API or pg_net extension)
    # Alternative: use the /rest/v1/rpc endpoint with a helper function
    # Most reliable: use the Supabase Management API
    url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"

    # First try: use a custom exec_sql function if it exists
    response = httpx.post(
        url,
        headers=headers,
        json={"query": sql},
        timeout=60.0
    )

    if response.status_code == 404:
        # Function doesn't exist, create it first
        print("  Creating exec_sql helper function...")
        create_fn_sql = """
        CREATE OR REPLACE FUNCTION exec_sql(query text)
        RETURNS json
        LANGUAGE plpgsql
        SECURITY DEFINER
        AS $$
        DECLARE
            result json;
        BEGIN
            EXECUTE query;
            RETURN json_build_object('success', true, 'message', 'SQL executed successfully');
        EXCEPTION WHEN OTHERS THEN
            RETURN json_build_object('success', false, 'error', SQLERRM, 'detail', SQLSTATE);
        END;
        $$;
        """
        # We need another way to bootstrap... let's try the management API
        # Actually, let's split the SQL and run via individual REST calls where possible
        return {"error": "exec_sql not available", "status": 404}

    return {"status": response.status_code, "data": response.text}


def run_migration_via_management_api(sql: str, description: str = "") -> dict:
    """Execute SQL via Supabase database query endpoint."""
    # The Supabase project ref from URL
    project_ref = SUPABASE_URL.split("//")[1].split(".")[0]

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }

    # Try using the pg_graphql or direct SQL endpoint
    url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"

    response = httpx.post(
        url,
        headers=headers,
        json={"query": sql},
        timeout=120.0
    )

    return {"status": response.status_code, "body": response.text[:500]}


def split_and_run_migration(filepath: str) -> bool:
    """Read a migration file and execute it statement by statement."""
    print(f"\n{'='*60}")
    print(f"Running migration: {filepath}")
    print(f"{'='*60}")

    sql = Path(filepath).read_text(encoding='utf-8')

    # Try running the whole file at once first
    result = run_migration_via_management_api(sql, filepath)
    print(f"  Status: {result['status']}")
    print(f"  Response: {result['body'][:200]}")

    if result['status'] in (200, 201):
        print(f"  Migration {filepath} completed successfully!")
        return True
    else:
        print(f"  Full migration failed, trying statement-by-statement...")
        return run_statements(sql)


def run_statements(sql: str) -> bool:
    """Split SQL into statements and run individually."""
    # Split on semicolons, but be careful with functions
    statements = []
    current = []
    in_function = False

    for line in sql.split('\n'):
        stripped = line.strip()

        # Skip comments
        if stripped.startswith('--') and not in_function:
            continue

        if '$$' in stripped:
            in_function = not in_function

        current.append(line)

        if not in_function and stripped.endswith(';'):
            stmt = '\n'.join(current).strip()
            if stmt and stmt != ';':
                statements.append(stmt)
            current = []

    if current:
        stmt = '\n'.join(current).strip()
        if stmt:
            statements.append(stmt)

    success_count = 0
    fail_count = 0

    for i, stmt in enumerate(statements):
        if not stmt.strip() or stmt.strip() == ';':
            continue

        result = run_migration_via_management_api(stmt, f"Statement {i+1}")
        status = result['status']

        if status in (200, 201):
            success_count += 1
            # Only print first 60 chars of statement
            preview = stmt.replace('\n', ' ')[:60]
            print(f"  [{i+1}/{len(statements)}] OK: {preview}...")
        else:
            fail_count += 1
            preview = stmt.replace('\n', ' ')[:60]
            print(f"  [{i+1}/{len(statements)}] FAIL ({status}): {preview}...")
            print(f"    Response: {result['body'][:150]}")

    print(f"\n  Results: {success_count} succeeded, {fail_count} failed")
    return fail_count == 0


def verify_tables() -> dict:
    """Verify that tables were created correctly."""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }

    results = {}

    # Check zone_standards table
    for table in ["zone_standards", "permitted_uses", "permission_types", "use_categories"]:
        response = httpx.get(
            f"{SUPABASE_URL}/rest/v1/{table}",
            headers={**headers, "Prefer": "count=exact"},
            params={"select": "*", "limit": "1"},
            timeout=30.0
        )
        results[table] = {
            "status": response.status_code,
            "exists": response.status_code == 200,
            "count": response.headers.get("content-range", "unknown"),
        }
        print(f"  {table}: status={response.status_code}, range={results[table]['count']}")

    return results


if __name__ == "__main__":
    if not SUPABASE_KEY:
        print("ERROR: SUPABASE_KEY not set")
        sys.exit(1)

    migrations_dir = Path(__file__).parent.parent / "migrations"

    # Run migration 005
    m005 = migrations_dir / "005_zone_standards.sql"
    if m005.exists():
        split_and_run_migration(str(m005))

    # Run migration 006
    m006 = migrations_dir / "006_permitted_uses.sql"
    if m006.exists():
        split_and_run_migration(str(m006))

    # Verify
    print(f"\n{'='*60}")
    print("Verifying tables...")
    print(f"{'='*60}")
    verify_tables()
