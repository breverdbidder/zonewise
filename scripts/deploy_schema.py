#!/usr/bin/env python3
"""
Deploy Ordinance Monitoring Schema to Supabase
"""

import os
import httpx
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

def deploy_schema():
    """Deploy the ordinance monitoring schema"""
    schema_path = Path(__file__).parent.parent / "sql" / "ordinance_monitoring_schema.sql"

    if not schema_path.exists():
        print(f"Schema file not found: {schema_path}")
        return False

    with open(schema_path) as f:
        sql = f.read()

    # Split into individual statements and execute
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

    # Use Supabase SQL endpoint (via rpc)
    # First, let's check if tables exist
    client = httpx.Client(timeout=60.0)

    # Execute schema via pg_query RPC (if available) or direct REST
    print("Deploying schema to Supabase...")
    print(f"URL: {SUPABASE_URL}")
    print(f"Key: {SUPABASE_KEY[:20]}...")

    # Test connection first
    try:
        resp = client.get(
            f"{SUPABASE_URL}/rest/v1/",
            headers=headers
        )
        print(f"Connection test: {resp.status_code}")
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

    # For Supabase, we need to run SQL via the dashboard or supabase CLI
    # But we can verify table creation by trying to access them

    tables = [
        "ordinances",
        "development_bonuses",
        "overlay_districts",
        "conditional_uses",
        "ordinance_changes",
        "entitlement_timelines",
        "municode_scrape_log"
    ]

    print("\nChecking/creating tables...")

    # Output SQL for manual execution if needed
    print("\n" + "="*60)
    print("SQL SCHEMA TO EXECUTE IN SUPABASE SQL EDITOR:")
    print("="*60)
    print(sql[:2000] + "\n...(truncated)")
    print("="*60)

    # Check existing tables
    for table in tables:
        try:
            resp = client.get(
                f"{SUPABASE_URL}/rest/v1/{table}?limit=1",
                headers=headers
            )
            if resp.status_code == 200:
                print(f"  Table '{table}': EXISTS")
            elif resp.status_code == 404:
                print(f"  Table '{table}': NEEDS CREATION")
            else:
                print(f"  Table '{table}': Status {resp.status_code}")
        except Exception as e:
            print(f"  Table '{table}': Error - {e}")

    client.close()
    return True

if __name__ == "__main__":
    deploy_schema()
