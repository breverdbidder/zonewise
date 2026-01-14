# ZoneWise API - Render Deployment

**Deployed:** January 2025  
**Status:** ✅ LIVE  
**URL:** https://zonewise-api-v2.onrender.com

---

## Service Configuration

| Setting | Value |
|---------|-------|
| Service Name | `zonewise-api-v2` |
| Plan | Starter ($7/month) |
| Region | Oregon (US West) |
| Build Command | `pip install fastapi uvicorn httpx supabase pydantic python-dotenv` |
| Start Command | `uvicorn zonewise_api:app --host 0.0.0.0 --port $PORT` |
| Auto-Deploy | ✅ Enabled (main branch) |

---

## API Endpoints

| Endpoint | Method | URL |
|----------|--------|-----|
| Root | GET | https://zonewise-api-v2.onrender.com/ |
| Health | GET | https://zonewise-api-v2.onrender.com/health |
| Docs | GET | https://zonewise-api-v2.onrender.com/docs |
| Analyze | POST | https://zonewise-api-v2.onrender.com/api/v1/analyze |
| Jurisdictions | GET | https://zonewise-api-v2.onrender.com/api/v1/jurisdictions |

---

## Cold Start Behavior

Render Starter tier has cold starts after 15 minutes of inactivity:

- **First request:** 30-90 seconds
- **Subsequent requests:** <2 seconds

This is expected behavior, not an error.

---

## Quick Test Commands

```bash
# Health check
curl https://zonewise-api-v2.onrender.com/health

# Property analysis
curl -X POST https://zonewise-api-v2.onrender.com/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"address": "798 Ocean Dr, Satellite Beach, FL"}'
```

---

## Environment Variables

Configured in Render dashboard (not in code):

- `SUPABASE_URL` - ZoneWise Supabase project URL
- `SUPABASE_SERVICE_KEY` - Service role key for database access

---

## Database

- **Provider:** Supabase
- **Table:** `zoning_requirements`
- **Records:** 21 zoning districts
- **Jurisdictions:** Satellite Beach, Indian Harbour Beach, Melbourne

---

## Monthly Costs

| Service | Cost |
|---------|------|
| Render Starter | $7 |
| Supabase Free | $0 |
| BCPAO API | $0 |
| **Total** | **$7/month** |

---

## Deployment History

### Initial Deployment (Failed)
- Complex requirements.txt caused build failures
- render.yaml configuration conflicts
- Multiple rebuild attempts unsuccessful

### Working Solution
- Deleted original service
- Created new service with inline build command
- Bypasses requirements.txt parsing issues
- Fresh service = no cached artifacts

### Key Learning
For simple FastAPI apps, inline build commands are more reliable than requirements.txt on Render.

---

## Remaining Work

### Coverage Gap (80% remaining)
14 jurisdictions still needed:
- Titusville
- Cocoa / Cocoa Beach
- Cape Canaveral
- Palm Bay
- Rockledge
- West Melbourne
- Merritt Island
- Brevard County (unincorporated)
- Others

### Future Enhancements
- [ ] API key authentication
- [ ] Rate limiting
- [ ] CORS restriction
- [ ] Setback violation detection
- [ ] Height restriction checks
- [ ] Automated ordinance updates

---

## Links

- **Render Dashboard:** https://dashboard.render.com/
- **Supabase Dashboard:** https://supabase.com/dashboard/project/mocerqjnksmhcjzxrewo
- **GitHub Repo:** https://github.com/breverdbidder/zonewise
- **Swagger Docs:** https://zonewise-api-v2.onrender.com/docs
