# ZoneWise Municode Pipeline

Automated scraping and ingestion of zoning ordinances from all 17 Brevard County jurisdictions.

## Quick Start

```bash
cd pipeline

# Set environment variables
export SUPABASE_SERVICE_KEY="your_key"
export FIRECRAWL_API_KEY="your_key"  # Optional - falls back to httpx

# Run full pipeline
python run_pipeline.py --all

# Or test with single jurisdiction
python run_pipeline.py --jurisdiction 2  # Palm Bay
```

## Pipeline Stages

1. **Scrape**: Fetch zoning ordinances from Municode/eLaws using Firecrawl
2. **Parse**: Extract district codes, names, categories, development standards
3. **Ingest**: Batch insert to Supabase zoning_districts table

## Files

- `config/jurisdictions.json` - 17 Brevard jurisdictions with Municode URLs
- `src/municode_scraper.py` - Firecrawl/httpx scraper
- `src/zoning_parser.py` - Regex parser for district extraction  
- `src/supabase_ingest.py` - Supabase batch insert
- `run_pipeline.py` - Main orchestrator

## Status

| Status | Count |
|--------|-------|
| ✅ Complete | 1 (Satellite Beach) |
| ⚠️ Placeholder | 16 |

Run pipeline to complete remaining jurisdictions.
