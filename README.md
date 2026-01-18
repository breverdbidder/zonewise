# ZoneWise - AI-Powered Zoning Compliance Platform

## Overview
ZoneWise provides instant zoning compliance checks for Brevard County, FL properties.

## Data Coverage
- **17 Jurisdictions**: All Brevard County municipalities
- **220 Zoning Districts**: Complete dimensional standards
- **335,578 Parcels**: Full county parcel database
- **99% Accuracy**: Validated against official GIS records

## Architecture
- **Database**: Supabase PostgreSQL
- **API**: FastAPI + Python
- **Frontend**: React + Tailwind
- **Deployment**: GitHub Actions + Cloudflare
- **AI**: Claude API via MCP

## Data Sources
- Brevard County Official GIS (gis.brevardfl.gov)
- Municipal Code Libraries (Municode, eLaws)
- BCPAO Property Records

## Validation
- 100 random parcels validated against official municipal records
- 99.0% accuracy (target: 95%)
- Cross-verified against Supabase ZoneWise database

## Quick Start
```bash
# Query zoning for a parcel
curl "https://mocerqjnksmhcjzxrewo.supabase.co/rest/v1/parcels?account=eq.2612345" \
  -H "apikey: YOUR_KEY"
```

---
*Built by Ariel Shapira | Everest Capital USA*
*Last Updated: 2026-01-18*
