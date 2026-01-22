#!/usr/bin/env python3
"""
Direct database setup using psycopg2 via Supabase pooler
"""

import os
from pathlib import Path

# Load credentials
env_path = Path(__file__).parent.parent / "agents" / "verify" / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
PROJECT_REF = "mocerqjnksmhcjzxrewo"

# Build connection string using pooler
# Format: postgresql://postgres.[project-ref]:[password]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
# The password is the database password, not the JWT

# Try different connection approaches
def try_connect():
    try:
        import psycopg2

        # Connection strings to try
        connections = [
            # Direct connection (requires DB password)
            # f"postgresql://postgres:{SUPABASE_KEY}@db.{PROJECT_REF}.supabase.co:5432/postgres",
            # Pooler connection with JWT (usually doesn't work for DDL)
            f"postgresql://postgres.{PROJECT_REF}:{SUPABASE_KEY}@aws-0-us-east-1.pooler.supabase.com:5432/postgres?sslmode=require",
        ]

        for conn_str in connections:
            try:
                print(f"Trying: {conn_str[:50]}...")
                conn = psycopg2.connect(conn_str)
                print("Connected!")

                # Try to execute a simple query
                cur = conn.cursor()
                cur.execute("SELECT current_database(), current_user")
                result = cur.fetchone()
                print(f"Database: {result[0]}, User: {result[1]}")

                # Now execute schema
                schema_path = Path(__file__).parent.parent / "sql" / "CREATE_TABLES.sql"
                if schema_path.exists():
                    with open(schema_path) as f:
                        sql = f.read()

                    print("Executing schema...")
                    cur.execute(sql)
                    conn.commit()
                    print("Schema executed successfully!")

                cur.close()
                conn.close()
                return True

            except Exception as e:
                print(f"Failed: {e}")
                continue

        return False

    except ImportError:
        print("psycopg2 not installed")
        return False

if __name__ == "__main__":
    if not try_connect():
        print("\n" + "="*60)
        print("MANUAL SCHEMA DEPLOYMENT REQUIRED")
        print("="*60)
        print("\nPlease execute the SQL in Supabase SQL Editor:")
        print(f"https://supabase.com/dashboard/project/{PROJECT_REF}/sql/new")
        print("\nSQL file: zonewise/sql/CREATE_TABLES.sql")
