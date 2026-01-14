"""
ZoneWise Ingestion Pipeline
Main orchestrator for scraping, parsing, and storing zoning data

Usage:
    python run_ingestion.py                    # Scrape all jurisdictions
    python run_ingestion.py indian_harbour_beach  # Scrape specific jurisdiction
    python run_ingestion.py --test             # Test with IHB only
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

from firecrawl_scraper import scrape_jurisdiction, scrape_all_jurisdictions, JURISDICTIONS
from ordinance_parser import parse_ordinance

# Supabase configuration
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://mocerqjnksmhcjzxrewo.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1vY2VycWpua3NtaGNqenhyZXdvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDUzMjUyNiwiZXhwIjoyMDgwMTA4NTI2fQ.fL255mO0V8-rrU0Il3L41cIdQXUau-HRQXiamTqp9nE')

# Jurisdiction ID mapping (name to Supabase ID)
JURISDICTION_IDS = {
    'melbourne': 1,
    'palm_bay': 2,
    'indian_harbour_beach': 3,
    'cocoa': 4,
    'cocoa_beach': 5,
    'rockledge': 6,
    'titusville': 7,
    'satellite_beach': 8,
    'west_melbourne': 9,
    'cape_canaveral': 10,
    'malabar': 11,
    'grant_valkaria': 12,
    'indialantic': 13,
    'melbourne_beach': 14,
    'melbourne_village': 15,
    'palm_shores': 16,
    'brevard_county': 17
}


def get_supabase_client():
    """Get Supabase client"""
    try:
        from supabase import create_client
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except ImportError:
        print("⚠️ supabase package not installed. Run: pip install supabase")
        return None


def get_category(code: str) -> str:
    """Map district code to category"""
    if code.startswith('R-'):
        return 'Residential'
    elif code in ['C-P', 'C-1', 'C-2'] or code.startswith('C-'):
        return 'Commercial'
    elif code.startswith('B-'):
        return 'Commercial'
    elif code.startswith(('M-', 'I-')):
        return 'Industrial'
    elif code.startswith('P-'):
        return 'Institutional'
    elif code in ['PUD', 'MU', 'MXD']:
        return 'Mixed-Use'
    return 'Other'


async def process_jurisdiction(
    jurisdiction_id: str,
    save_raw: bool = True,
    store_supabase: bool = True
) -> Dict[str, Any]:
    """
    Process a single jurisdiction: scrape, parse, store
    
    Args:
        jurisdiction_id: Jurisdiction identifier
        save_raw: Save raw content to file
        store_supabase: Store results in Supabase
        
    Returns:
        Processing result with status and metrics
    """
    start_time = datetime.now()
    result = {
        'jurisdiction_id': jurisdiction_id,
        'success': False,
        'steps': {}
    }
    
    # Step 1: Scrape
    print(f"\n{'='*60}")
    print(f"📄 Processing: {jurisdiction_id}")
    print('='*60)
    
    scrape_result = await scrape_jurisdiction(jurisdiction_id)
    result['steps']['scrape'] = {
        'success': scrape_result.get('success', False),
        'content_length': scrape_result.get('content_length', 0)
    }
    
    if not scrape_result.get('success'):
        result['error'] = f"Scrape failed: {scrape_result.get('error', 'Unknown')}"
        return result
    
    content = scrape_result['content']
    
    # Save raw content
    if save_raw:
        raw_dir = 'data/raw'
        os.makedirs(raw_dir, exist_ok=True)
        raw_path = f"{raw_dir}/{jurisdiction_id}_ordinance.md"
        with open(raw_path, 'w') as f:
            f.write(content)
        print(f"   💾 Saved raw: {raw_path}")
    
    # Step 2: Parse
    print(f"   🔍 Parsing content ({len(content):,} chars)...")
    
    jurisdiction_name = JURISDICTIONS.get(jurisdiction_id, {}).get('full_name', jurisdiction_id)
    parse_result = parse_ordinance(content, jurisdiction_id, jurisdiction_name)
    
    result['steps']['parse'] = {
        'success': True,
        'districts_found': len(parse_result.get('districts', [])),
        'confidence': parse_result.get('confidence', 0),
        'method': parse_result.get('parse_method', 'unknown')
    }
    
    districts = parse_result.get('districts', [])
    print(f"   📊 Found {len(districts)} districts (confidence: {parse_result.get('confidence', 0):.0%})")
    
    # Save parsed data
    parsed_dir = 'data/parsed'
    os.makedirs(parsed_dir, exist_ok=True)
    parsed_path = f"{parsed_dir}/{jurisdiction_id}_zoning.json"
    with open(parsed_path, 'w') as f:
        json.dump({
            'jurisdiction_id': jurisdiction_id,
            'jurisdiction_name': jurisdiction_name,
            'scraped_at': scrape_result.get('scraped_at'),
            'ordinance_url': scrape_result.get('ordinance_url'),
            'districts': districts,
            'setbacks': parse_result.get('setbacks', {}),
            'dimensions': parse_result.get('dimensions', {}),
            'parse_confidence': parse_result.get('confidence', 0)
        }, f, indent=2)
    print(f"   💾 Saved parsed: {parsed_path}")
    
    # Step 3: Store in Supabase
    if store_supabase:
        supabase = get_supabase_client()
        
        if supabase:
            db_jurisdiction_id = JURISDICTION_IDS.get(jurisdiction_id)
            
            if db_jurisdiction_id:
                stored = 0
                updated = 0
                
                # Get existing districts
                existing = supabase.table('zoning_districts').select('code').eq('jurisdiction_id', db_jurisdiction_id).execute()
                existing_codes = [d['code'] for d in existing.data]
                
                for district in districts:
                    code = district.get('district_code', district.get('code', ''))
                    if not code:
                        continue
                    
                    district_data = {
                        'jurisdiction_id': db_jurisdiction_id,
                        'code': code,
                        'name': district.get('name', district.get('district_name', f'{code} District')),
                        'category': district.get('category', get_category(code)),
                        'description': str(district.get('allowed_uses', []))[:500] if district.get('allowed_uses') else None,
                        'ordinance_section': district.get('ordinance_section', ''),
                        'effective_date': '2024-01-01'
                    }
                    
                    try:
                        if code in existing_codes:
                            supabase.table('zoning_districts').update(district_data).eq('jurisdiction_id', db_jurisdiction_id).eq('code', code).execute()
                            updated += 1
                        else:
                            supabase.table('zoning_districts').insert(district_data).execute()
                            stored += 1
                    except Exception as e:
                        print(f"      ⚠️ DB error for {code}: {str(e)[:50]}")
                
                result['steps']['store'] = {
                    'success': True,
                    'stored': stored,
                    'updated': updated
                }
                print(f"   💾 Supabase: {stored} created, {updated} updated")
            else:
                result['steps']['store'] = {
                    'success': False,
                    'error': f'Unknown jurisdiction ID mapping for {jurisdiction_id}'
                }
        else:
            result['steps']['store'] = {
                'success': False,
                'error': 'Supabase client not available'
            }
    
    # Calculate metrics
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    result['success'] = True
    result['duration_seconds'] = duration
    result['metrics'] = {
        'content_length': len(content),
        'districts_found': len(districts),
        'parse_confidence': parse_result.get('confidence', 0)
    }
    
    print(f"   ✅ Completed in {duration:.1f}s")
    
    return result


async def run_full_ingestion(
    jurisdictions: Optional[List[str]] = None,
    parallel: bool = False
) -> Dict[str, Any]:
    """
    Run full ingestion pipeline for multiple jurisdictions
    
    Args:
        jurisdictions: List of jurisdiction IDs (default: all 17)
        parallel: Run in parallel (faster but may hit rate limits)
        
    Returns:
        Summary of all results
    """
    if jurisdictions is None:
        jurisdictions = list(JURISDICTIONS.keys())
    
    start_time = datetime.now()
    results = {}
    
    print("\n" + "="*60)
    print("🏛️ ZONEWISE INGESTION PIPELINE")
    print("="*60)
    print(f"📅 Started: {start_time.isoformat()}")
    print(f"🎯 Jurisdictions: {len(jurisdictions)}")
    print("="*60)
    
    if parallel:
        # Run all in parallel
        tasks = [process_jurisdiction(jid) for jid in jurisdictions]
        task_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for jid, result in zip(jurisdictions, task_results):
            if isinstance(result, Exception):
                results[jid] = {'success': False, 'error': str(result)}
            else:
                results[jid] = result
    else:
        # Run sequentially with rate limiting
        for jid in jurisdictions:
            results[jid] = await process_jurisdiction(jid)
            await asyncio.sleep(3)  # Rate limit between jurisdictions
    
    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    successful = sum(1 for r in results.values() if r.get('success'))
    total_districts = sum(r.get('metrics', {}).get('districts_found', 0) for r in results.values())
    
    summary = {
        'success': True,
        'started_at': start_time.isoformat(),
        'completed_at': end_time.isoformat(),
        'duration_seconds': duration,
        'total_jurisdictions': len(jurisdictions),
        'successful': successful,
        'failed': len(jurisdictions) - successful,
        'total_districts_found': total_districts,
        'results': results
    }
    
    # Save summary
    os.makedirs('data', exist_ok=True)
    summary_path = f"data/ingestion_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("\n" + "="*60)
    print("📊 INGESTION COMPLETE")
    print("="*60)
    print(f"✅ Successful: {successful}/{len(jurisdictions)}")
    print(f"📋 Districts found: {total_districts}")
    print(f"⏱️ Duration: {duration:.1f}s ({duration/len(jurisdictions):.1f}s per jurisdiction)")
    print(f"💾 Summary: {summary_path}")
    print("="*60)
    
    return summary


# CLI interface
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        if arg == '--test':
            # Test mode: just IHB
            result = asyncio.run(process_jurisdiction('indian_harbour_beach'))
            print(json.dumps({k: v for k, v in result.items() if k != 'content'}, indent=2))
            
        elif arg == '--all':
            # Full ingestion
            summary = asyncio.run(run_full_ingestion())
            
        elif arg in JURISDICTIONS:
            # Specific jurisdiction
            result = asyncio.run(process_jurisdiction(arg))
            print(json.dumps({k: v for k, v in result.items() if k != 'content'}, indent=2))
            
        else:
            print(f"Unknown argument: {arg}")
            print("Usage:")
            print("  python run_ingestion.py              # Interactive")
            print("  python run_ingestion.py --test       # Test with IHB")
            print("  python run_ingestion.py --all        # All jurisdictions")
            print("  python run_ingestion.py <jurisdiction_id>")
    else:
        # Default: test mode
        print("Running test with Indian Harbour Beach...")
        result = asyncio.run(process_jurisdiction('indian_harbour_beach'))
        print("\n" + json.dumps({k: v for k, v in result.items() if k != 'content'}, indent=2))
