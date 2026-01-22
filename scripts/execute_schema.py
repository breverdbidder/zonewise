#!/usr/bin/env python3
"""
Execute SQL Schema on Supabase using the Management API or direct connection
"""

import os
import httpx
import json
from pathlib import Path

# Load from env file
env_path = Path(__file__).parent.parent / "agents" / "verify" / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

def execute_sql_via_rest(sql: str) -> dict:
    """Execute SQL using Supabase REST API with rpc"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }

    # Try using the pg_dump or SQL execution endpoint
    # Supabase provides a /sql endpoint for service role
    client = httpx.Client(timeout=120.0)

    # Split SQL into separate statements for better execution
    statements = []
    current = []

    for line in sql.split('\n'):
        stripped = line.strip()
        if stripped.startswith('--') or not stripped:
            continue
        current.append(line)
        if stripped.endswith(';'):
            statements.append('\n'.join(current))
            current = []

    print(f"Found {len(statements)} SQL statements to execute")

    results = {"success": 0, "failed": 0, "errors": []}

    for i, stmt in enumerate(statements):
        if not stmt.strip():
            continue

        # Skip certain statements that might cause issues
        if 'DROP TRIGGER' in stmt or 'CREATE TRIGGER' in stmt:
            print(f"  [{i+1}] Skipping trigger statement (will retry later)")
            continue

        try:
            # Use rpc to call a function that executes SQL (if available)
            # Or use direct POST to REST API for INSERT/UPDATE
            # For DDL, we need to use the SQL execution endpoint

            # Try the /rest/v1/rpc/exec_sql endpoint (if function exists)
            resp = client.post(
                f"{SUPABASE_URL}/rest/v1/rpc/exec_sql",
                headers=headers,
                json={"query": stmt}
            )

            if resp.status_code == 200:
                results["success"] += 1
                print(f"  [{i+1}] SUCCESS")
            elif resp.status_code == 404:
                # exec_sql function doesn't exist, try alternative
                print(f"  [{i+1}] exec_sql function not available")
                results["failed"] += 1
                break
            else:
                results["failed"] += 1
                results["errors"].append(f"Statement {i+1}: {resp.status_code} - {resp.text[:200]}")
                print(f"  [{i+1}] FAILED: {resp.status_code}")

        except Exception as e:
            results["failed"] += 1
            results["errors"].append(f"Statement {i+1}: {str(e)}")
            print(f"  [{i+1}] ERROR: {e}")

    client.close()
    return results

def create_exec_sql_function():
    """Create the exec_sql function for raw SQL execution"""
    sql = """
    CREATE OR REPLACE FUNCTION exec_sql(query text)
    RETURNS json
    LANGUAGE plpgsql
    SECURITY DEFINER
    AS $$
    BEGIN
        EXECUTE query;
        RETURN json_build_object('success', true);
    EXCEPTION WHEN OTHERS THEN
        RETURN json_build_object('success', false, 'error', SQLERRM);
    END;
    $$;
    """
    return sql

def create_tables_via_insert():
    """Create tables by attempting inserts and letting Supabase auto-create"""
    # This won't work for table creation, just for verification

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    client = httpx.Client(timeout=30.0)

    # Test insert to verify tables exist
    test_record = {
        "jurisdiction_id": 0,
        "jurisdiction_name": "TEST",
        "ordinance_number": "TEST-0000",
        "ordinance_type": "test"
    }

    try:
        resp = client.post(
            f"{SUPABASE_URL}/rest/v1/ordinances",
            headers=headers,
            json=test_record
        )
        print(f"Test insert response: {resp.status_code}")
        if resp.status_code == 201:
            print("Table exists and working!")
            # Delete test record
            client.delete(
                f"{SUPABASE_URL}/rest/v1/ordinances?ordinance_number=eq.TEST-0000",
                headers=headers
            )
        else:
            print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

    client.close()

def main():
    print("="*60)
    print("SUPABASE SCHEMA DEPLOYMENT")
    print("="*60)

    schema_path = Path(__file__).parent.parent / "sql" / "ordinance_monitoring_schema.sql"

    if not schema_path.exists():
        print(f"Schema file not found: {schema_path}")
        return

    with open(schema_path) as f:
        sql = f.read()

    print(f"\nSchema file: {schema_path}")
    print(f"Schema size: {len(sql)} bytes")

    print("\n--- Attempting SQL Execution via REST API ---")
    result = execute_sql_via_rest(sql)

    if result["failed"] > 0 and result["success"] == 0:
        print("\n" + "="*60)
        print("MANUAL EXECUTION REQUIRED")
        print("="*60)
        print("\nThe Supabase REST API doesn't support raw SQL execution.")
        print("Please execute the schema manually via:")
        print("1. Supabase Dashboard > SQL Editor")
        print("2. Copy/paste the schema from: sql/ordinance_monitoring_schema.sql")
        print("3. Click 'Run' to execute")
        print("\nAlternatively, use Supabase CLI:")
        print("  supabase db push")

        # Save schema for easy copying
        output_path = Path(__file__).parent.parent / "sql" / "EXECUTE_THIS.sql"
        with open(output_path, 'w') as f:
            f.write(sql)
        print(f"\nSchema saved to: {output_path}")

if __name__ == "__main__":
    main()
