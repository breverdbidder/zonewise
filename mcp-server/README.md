# ZoneWise MCP Server

FastAPI-based Zoning Intelligence API for Brevard County, Florida.

## Coverage

- **17 jurisdictions** (all of Brevard County)
- **273 zoning districts** with dimensional standards
- **100% verified** with source citations

## Deployment

### Render.com (Recommended)

1. Fork this repo or push to your GitHub
2. Connect to Render: https://render.com/deploy
3. Select "Blueprint" and point to this repo
4. Add environment variable:
   - `SUPABASE_KEY`: Your Supabase service role key

### Local Development

```bash
pip install -r requirements.txt
export SUPABASE_URL="https://mocerqjnksmhcjzxrewo.supabase.co"
export SUPABASE_KEY="your-key"
uvicorn main:app --reload
```

## API Endpoints

### Info & Health
- `GET /` - API info
- `GET /health` - Health check
- `GET /docs` - Swagger UI
- `GET /redoc` - ReDoc

### Jurisdictions
- `GET /jurisdictions` - List all 17 jurisdictions
- `GET /jurisdictions/{id}` - Get jurisdiction details

### Districts
- `GET /districts` - List districts (filterable)
- `GET /districts/{id}` - Get district details
- `GET /search?q=...` - Search districts

### Dimensional Standards
- `GET /dims/{jurisdiction}/{code}` - Get DIMS for specific district

### Use Type Lookups
- `GET /lookup/residential` - Find residential districts
- `GET /lookup/commercial` - Find commercial districts
- `GET /lookup/industrial` - Find industrial districts

### MCP Tool Interface
- `POST /mcp/tools/lookup_zoning` - MCP-compatible tool endpoint

## Examples

```bash
# Get all Melbourne districts
curl "https://zonewise-mcp.onrender.com/districts?jurisdiction_id=1"

# Get dimensional standards for R-1A in Melbourne
curl "https://zonewise-mcp.onrender.com/dims/Melbourne/R-1A"

# Search for single-family districts
curl "https://zonewise-mcp.onrender.com/search?q=single-family"

# Find high-density residential (10+ units/acre)
curl "https://zonewise-mcp.onrender.com/lookup/residential?min_density=10"
```

## MCP Integration (Claude Desktop)

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "zonewise": {
      "url": "https://zonewise-mcp.onrender.com",
      "tools": ["lookup_zoning"]
    }
  }
}
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SUPABASE_URL` | Yes | Supabase project URL |
| `SUPABASE_KEY` | Yes | Supabase service role key |
| `PORT` | No | Server port (default: 8000) |

---

Built by BidDeed.AI / Everest Capital USA
