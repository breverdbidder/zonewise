"""
zonewize/scraper.py
Ordinance scraping via Firecrawl API with caching.

Responsibilities:
- Scrape jurisdiction ordinance pages
- Manage 7-day cache in Supabase
- Handle Firecrawl API errors gracefully
"""

import httpx
from typing import Dict, Optional, Any
from datetime import datetime, timedelta


async def scrape_ordinance(
    ordinance_url: str,
    firecrawl_client: Optional[Any] = None,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    Scrape ordinance page using Firecrawl API.
    
    Args:
        ordinance_url: URL of the ordinance page to scrape
        firecrawl_client: Optional Firecrawl client (uses default if None)
        timeout: Request timeout in seconds
    
    Returns:
        Dict with keys:
        - success (bool): Whether scrape succeeded
        - content (str): HTML content of ordinance page
        - metadata (dict): Additional metadata from Firecrawl
    
    Raises:
        httpx.HTTPError: If Firecrawl API fails
        httpx.TimeoutException: If request times out
    """
    # Note: In production, use actual Firecrawl MCP client
    # For now, mock the scraping behavior
    
    if firecrawl_client:
        # Use provided Firecrawl client
        try:
            result = await firecrawl_client.scrape(ordinance_url)
            return {
                'success': True,
                'content': result['markdown'],  # or 'html' depending on format
                'metadata': result.get('metadata', {})
            }
        except Exception as e:
            raise httpx.HTTPError(f"Firecrawl scrape failed: {str(e)}")
    
    # Mock implementation for development/testing
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.get(ordinance_url)
            response.raise_for_status()
            
            return {
                'success': True,
                'content': response.text,
                'metadata': {
                    'url': ordinance_url,
                    'status_code': response.status_code,
                    'scraped_at': datetime.now().isoformat()
                }
            }
        
        except httpx.TimeoutException:
            raise httpx.TimeoutException(
                f"Firecrawl timeout after {timeout}s for {ordinance_url}"
            )
        
        except httpx.HTTPStatusError as e:
            raise httpx.HTTPError(
                f"Firecrawl HTTP error {e.response.status_code} for {ordinance_url}"
            )


def get_cached_ordinance(
    jurisdiction: str,
    supabase_client: Optional[Any] = None
) -> Optional[Dict[str, Any]]:
    """
    Retrieve cached ordinance from Supabase.
    
    Args:
        jurisdiction: Jurisdiction identifier
        supabase_client: Supabase client for database access
    
    Returns:
        Dict with cached ordinance data if found, None otherwise:
        - data (str): Cached ordinance content
        - last_updated (str): ISO timestamp of when cached
        - age_days (int): How many days old the cache is
    """
    if not supabase_client:
        # No Supabase client - return None (cache miss)
        return None
    
    try:
        result = supabase_client.table('ordinance_cache').select('*').eq(
            'jurisdiction', jurisdiction
        ).maybe_single().execute()
        
        if not result.data:
            return None
        
        # Calculate cache age
        last_updated = datetime.fromisoformat(result.data['last_updated'])
        age = datetime.now() - last_updated
        age_days = age.days
        
        return {
            'data': result.data['content'],
            'last_updated': result.data['last_updated'],
            'age_days': age_days
        }
    
    except Exception as e:
        print(f"[WARNING] Cache lookup failed: {str(e)}")
        return None


def cache_ordinance(
    jurisdiction: str,
    content: str,
    supabase_client: Optional[Any] = None,
    correlation_id: Optional[str] = None
) -> bool:
    """
    Cache ordinance data in Supabase.
    
    Args:
        jurisdiction: Jurisdiction identifier
        content: Ordinance HTML/text content
        supabase_client: Supabase client for database access
        correlation_id: Correlation ID for tracing
    
    Returns:
        True if cache write succeeded, False otherwise
    """
    if not supabase_client:
        return False
    
    try:
        supabase_client.table('ordinance_cache').upsert({
            'jurisdiction': jurisdiction,
            'content': content,
            'last_updated': datetime.now().isoformat(),
            'correlation_id': correlation_id
        }).execute()
        
        return True
    
    except Exception as e:
        print(f"[WARNING] Cache write failed: {str(e)}")
        return False
