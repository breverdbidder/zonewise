"""
ZoneWise V3 - Supabase Client
Database client for PostgreSQL + PostGIS operations.
"""

import os
from typing import Optional
from supabase import create_client, Client
import structlog

logger = structlog.get_logger()

_supabase_client: Optional[Client] = None


def get_supabase() -> Client:
    """Get or create Supabase client singleton."""
    global _supabase_client
    
    if _supabase_client is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        
        if not url or not key:
            raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set")
        
        _supabase_client = create_client(url, key)
        logger.info("Supabase client initialized")
    
    return _supabase_client
