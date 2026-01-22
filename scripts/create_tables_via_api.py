#!/usr/bin/env python3
"""
Create tables in Supabase via the Management API or direct DB connection
"""

import os
import json
import httpx
from pathlib import Path

# Load credentials
env_path = Path(__file__).parent.parent / "agents" / "verify" / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

# Project reference from URL
PROJECT_REF = "mocerqjnksmhcjzxrewo"

def create_tables_via_postgrest():
    """Try to create tables by checking/using PostgREST schema introspection"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }

    client = httpx.Client(timeout=60)

    # Check if we can access the schema
    print("Checking Supabase connection...")
    try:
        resp = client.get(f"{SUPABASE_URL}/rest/v1/", headers=headers)
        print(f"Connection status: {resp.status_code}")

        # Try to get schema info
        resp = client.options(f"{SUPABASE_URL}/rest/v1/", headers=headers)
        print(f"Schema info: {resp.headers.get('Content-Profile', 'N/A')}")

    except Exception as e:
        print(f"Error: {e}")

    # Define minimal table creation via SQL
    # We'll try using the pg_dump RPC if available
    tables_sql = {
        "ordinances": """
            CREATE TABLE IF NOT EXISTS public.ordinances (
                id BIGSERIAL PRIMARY KEY,
                jurisdiction_id INTEGER NOT NULL,
                jurisdiction_name TEXT NOT NULL,
                ordinance_number TEXT NOT NULL,
                title TEXT,
                chapter TEXT,
                section TEXT,
                article TEXT,
                passed_date DATE,
                effective_date DATE,
                ordinance_type TEXT,
                summary TEXT,
                full_text TEXT,
                source_url TEXT,
                source_section TEXT,
                municode_node_id TEXT,
                content_hash TEXT,
                extraction_date TIMESTAMPTZ DEFAULT NOW(),
                extraction_confidence NUMERIC(3,2),
                verified BOOLEAN DEFAULT FALSE,
                notes TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW(),
                UNIQUE(jurisdiction_id, ordinance_number)
            );
        """,
        "development_bonuses": """
            CREATE TABLE IF NOT EXISTS public.development_bonuses (
                id BIGSERIAL PRIMARY KEY,
                jurisdiction_id INTEGER NOT NULL,
                jurisdiction_name TEXT NOT NULL,
                bonus_name TEXT NOT NULL,
                bonus_type TEXT,
                applicable_districts TEXT[],
                bonus_amount NUMERIC(6,2),
                bonus_unit TEXT,
                qualifying_criteria TEXT,
                requirements TEXT,
                ordinance_reference TEXT,
                ordinance_section TEXT,
                source_url TEXT,
                effective_date DATE,
                expiration_date DATE,
                content_hash TEXT,
                extraction_date TIMESTAMPTZ DEFAULT NOW(),
                extraction_confidence NUMERIC(3,2),
                verified BOOLEAN DEFAULT FALSE,
                notes TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW(),
                UNIQUE(jurisdiction_id, bonus_name, bonus_type)
            );
        """,
        "overlay_districts": """
            CREATE TABLE IF NOT EXISTS public.overlay_districts (
                id BIGSERIAL PRIMARY KEY,
                jurisdiction_id INTEGER NOT NULL,
                jurisdiction_name TEXT NOT NULL,
                overlay_code TEXT NOT NULL,
                overlay_name TEXT NOT NULL,
                overlay_type TEXT,
                purpose TEXT,
                applicable_base_districts TEXT[],
                additional_requirements TEXT,
                height_modifications TEXT,
                setback_modifications TEXT,
                use_restrictions TEXT,
                design_standards TEXT,
                review_requirements TEXT,
                ordinance_reference TEXT,
                ordinance_section TEXT,
                source_url TEXT,
                geographic_boundary TEXT,
                content_hash TEXT,
                extraction_date TIMESTAMPTZ DEFAULT NOW(),
                extraction_confidence NUMERIC(3,2),
                verified BOOLEAN DEFAULT FALSE,
                notes TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW(),
                UNIQUE(jurisdiction_id, overlay_code)
            );
        """,
        "conditional_uses": """
            CREATE TABLE IF NOT EXISTS public.conditional_uses (
                id BIGSERIAL PRIMARY KEY,
                jurisdiction_id INTEGER NOT NULL,
                jurisdiction_name TEXT NOT NULL,
                district_code TEXT NOT NULL,
                district_name TEXT,
                use_name TEXT NOT NULL,
                use_category TEXT,
                permit_type TEXT,
                approval_authority TEXT,
                conditions TEXT[],
                special_requirements TEXT,
                parking_requirements TEXT,
                setback_requirements TEXT,
                screening_requirements TEXT,
                hours_of_operation TEXT,
                noise_limitations TEXT,
                ordinance_reference TEXT,
                ordinance_section TEXT,
                source_url TEXT,
                content_hash TEXT,
                extraction_date TIMESTAMPTZ DEFAULT NOW(),
                extraction_confidence NUMERIC(3,2),
                verified BOOLEAN DEFAULT FALSE,
                notes TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW(),
                UNIQUE(jurisdiction_id, district_code, use_name)
            );
        """,
        "entitlement_timelines": """
            CREATE TABLE IF NOT EXISTS public.entitlement_timelines (
                id BIGSERIAL PRIMARY KEY,
                jurisdiction_id INTEGER NOT NULL,
                jurisdiction_name TEXT NOT NULL,
                entitlement_type TEXT NOT NULL,
                process_name TEXT,
                application_requirements TEXT,
                review_authority TEXT,
                public_hearing_required BOOLEAN,
                number_of_hearings INTEGER,
                estimated_days_minimum INTEGER,
                estimated_days_maximum INTEGER,
                estimated_days_typical INTEGER,
                application_fee TEXT,
                review_fee TEXT,
                appeal_process TEXT,
                ordinance_reference TEXT,
                ordinance_section TEXT,
                source_url TEXT,
                content_hash TEXT,
                extraction_date TIMESTAMPTZ DEFAULT NOW(),
                extraction_confidence NUMERIC(3,2),
                verified BOOLEAN DEFAULT FALSE,
                notes TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW(),
                UNIQUE(jurisdiction_id, entitlement_type)
            );
        """,
        "ordinance_changes": """
            CREATE TABLE IF NOT EXISTS public.ordinance_changes (
                id BIGSERIAL PRIMARY KEY,
                ordinance_id BIGINT,
                jurisdiction_id INTEGER NOT NULL,
                jurisdiction_name TEXT NOT NULL,
                original_ordinance TEXT,
                amending_ordinance TEXT,
                change_type TEXT,
                change_date DATE,
                effective_date DATE,
                change_summary TEXT,
                sections_affected TEXT[],
                previous_content TEXT,
                new_content TEXT,
                source_url TEXT,
                detected_date TIMESTAMPTZ DEFAULT NOW(),
                content_hash_before TEXT,
                content_hash_after TEXT,
                verified BOOLEAN DEFAULT FALSE,
                notes TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """,
        "municode_scrape_log": """
            CREATE TABLE IF NOT EXISTS public.municode_scrape_log (
                id BIGSERIAL PRIMARY KEY,
                run_id UUID DEFAULT gen_random_uuid(),
                jurisdiction_id INTEGER,
                jurisdiction_name TEXT,
                scrape_type TEXT,
                target_table TEXT,
                start_time TIMESTAMPTZ DEFAULT NOW(),
                end_time TIMESTAMPTZ,
                status TEXT,
                records_found INTEGER DEFAULT 0,
                records_inserted INTEGER DEFAULT 0,
                records_updated INTEGER DEFAULT 0,
                records_failed INTEGER DEFAULT 0,
                error_message TEXT,
                error_details JSONB,
                urls_scraped TEXT[],
                content_hashes JSONB,
                metadata JSONB,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """
    }

    # Output SQL for manual execution
    print("\n" + "="*60)
    print("SQL TO EXECUTE IN SUPABASE SQL EDITOR")
    print("="*60)
    print("\nGo to: https://supabase.com/dashboard/project/mocerqjnksmhcjzxrewo/sql/new")
    print("\nCopy and execute the following SQL:\n")

    full_sql = []
    for table, sql in tables_sql.items():
        full_sql.append(f"-- Table: {table}")
        full_sql.append(sql)

    # Add RLS policies
    full_sql.append("""
-- Enable RLS and create policies
ALTER TABLE public.ordinances ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.development_bonuses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.overlay_districts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.conditional_uses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ordinance_changes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.entitlement_timelines ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.municode_scrape_log ENABLE ROW LEVEL SECURITY;

-- Service role policies
CREATE POLICY "Allow all for service role" ON public.ordinances FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON public.development_bonuses FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON public.overlay_districts FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON public.conditional_uses FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON public.ordinance_changes FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON public.entitlement_timelines FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON public.municode_scrape_log FOR ALL USING (true);

-- Public read policies
CREATE POLICY "Public read" ON public.ordinances FOR SELECT USING (true);
CREATE POLICY "Public read" ON public.development_bonuses FOR SELECT USING (true);
CREATE POLICY "Public read" ON public.overlay_districts FOR SELECT USING (true);
CREATE POLICY "Public read" ON public.conditional_uses FOR SELECT USING (true);
CREATE POLICY "Public read" ON public.entitlement_timelines FOR SELECT USING (true);
""")

    combined_sql = '\n\n'.join(full_sql)
    print(combined_sql)

    # Save to file for easy copying
    output_path = Path(__file__).parent.parent / "sql" / "CREATE_TABLES.sql"
    with open(output_path, 'w') as f:
        f.write(combined_sql)
    print(f"\n\nSQL saved to: {output_path}")

    client.close()

if __name__ == "__main__":
    create_tables_via_postgrest()
