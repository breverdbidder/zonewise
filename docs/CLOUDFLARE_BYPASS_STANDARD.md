# ZoneWise Cloudflare Bypass Standard

## HARDCODED METHOD - USE FOR ALL MUNICODE SCRAPING

This document defines the **canonical method** for scraping Municode data across all 67 Florida counties.

## The Problem

Municode uses Cloudflare protection that blocks direct HTTP requests and standard web scrapers.

## The Solution

**Firecrawl with `waitFor` parameter** - allows Cloudflare challenge to complete before extracting content.

## Hardcoded Configuration

```python
FIRECRAWL_KEY = "fc-fa112951a2564765a2d146302774ac9b"
FIRECRAWL_URL = "https://api.firecrawl.dev/v1/scrape"

# CRITICAL SETTINGS - DO NOT CHANGE
CLOUDFLARE_WAIT_MS = 12000      # 12 seconds minimum
CLOUDFLARE_RETRY_WAIT_MS = 15000  # 15 seconds on retry
REQUEST_TIMEOUT = 120           # 2 minutes max
RATE_LIMIT_DELAY = 3.0          # 3 seconds between requests
```

## Standard API Call

```python
payload = {
    "url": municode_url,
    "formats": ["markdown"],
    "onlyMainContent": True,
    "waitFor": 12000,  # CRITICAL: 12 seconds for Cloudflare
    "timeout": 90000,
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
}

response = requests.post(
    FIRECRAWL_URL,
    json=payload,
    headers={"Authorization": f"Bearer {FIRECRAWL_KEY}"}
)
```

## Validation Checks

After scraping, verify Cloudflare was bypassed:

1. **Content length > 2000 chars** - short content = challenge page
2. **No Cloudflare indicators** in content:
   - "enable javascript"
   - "just a moment"
   - "checking your browser"
   - "ray id"

## Retry Logic

If first attempt fails:
1. Wait 2 seconds
2. Retry with `waitFor: 15000` (15 seconds)
3. If still fails, log error and continue

## Proven Results

| County | Sections | Chars | Zones | Success |
|--------|----------|-------|-------|---------|
| Brevard | 4/4 | 317,786 | 43 | 100% |

## File Locations

| File | Purpose |
|------|---------|
| `scripts/municode_multi_county_scraper.py` | Canonical scraper |
| `scripts/cloudflare_bypass_scraper.py` | Utility scraper |
| `data/municode_scraped_raw.json` | Raw scraped content |

## Usage

```bash
# Scrape single county
python scripts/municode_multi_county_scraper.py brevard_county

# Scrape all configured counties
python scripts/municode_multi_county_scraper.py --all
```

## Adding New Counties

1. Find Municode URL: `https://library.municode.com/fl/{county_slug}`
2. Navigate to zoning chapter
3. Copy nodeId from URL
4. Add to `FLORIDA_COUNTIES` dict in scraper

## Cost Analysis

- Firecrawl: ~$0.001 per page
- 67 counties × 5 pages avg = ~$0.34/run
- Daily scraping = ~$10/month

## Critical Rules

1. **ALWAYS use waitFor=12000ms** - less will fail
2. **ALWAYS check content length** - verify bypass worked
3. **ALWAYS rate limit** - 3 seconds between requests
4. **NEVER use direct HTTP** - will be blocked

---

**This is the ONLY supported method for Municode scraping in ZoneWise.**

Last Updated: 2026-01-25
