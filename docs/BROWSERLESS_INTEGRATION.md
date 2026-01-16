# ZoneWise: Browserless Integration Findings

## Session Date: January 16, 2026

## Key Discovery: Browserless is the Solution for Municode

### What Works
1. **Browserless /content endpoint** - Returns full JS-rendered HTML
   - Titusville main page: 139K chars (vs 1K from Jina/Firecrawl)
   
2. **Browserless /pdf endpoint** - Generates PDFs of JS-rendered pages
   - Successfully generated PDF from Municode

3. **Browserless is already integrated** in BidDeed.AI
   - API Key: `2TVXSZeWLkFYROe996214181c88dd919e5d58160ed3416448`
   - Cost: $35/mo for 20,000 units

### What Doesn't Work (Yet)
1. **Municode deep links** return "Content Not Found"
   - URLs with nodeId parameters don't resolve directly
   - Need to navigate through TOC structure first
   
2. **AMLegal (Palm Bay)** - CAPTCHA persists even with:
   - Browserless standard mode
   - Browserless + residential proxy

### Solution Architecture

```
┌─────────────────────────────────────────────────────┐
│           ZoneWise Extraction Pipeline              │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Layer 1: Direct Fetch (FREE)                       │
│  ├─ eLaws sites (when operational)                  │
│  ├─ City PDFs (westmelbourne.gov, etc.)             │
│  └─ Jina Reader for simple pages                    │
│                                                     │
│  Layer 2: Browserless ($35/mo)                      │
│  ├─ Municode JS-rendered pages                      │
│  ├─ Navigate TOC → Chapter → Section                │
│  └─ Generate PDFs for archival                      │
│                                                     │
│  Layer 3: Manual/PDF Fallback                       │
│  ├─ Contact planning departments                    │
│  ├─ Download ordinance PDFs                         │
│  └─ OCR extraction if needed                        │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Recommended Next Steps

1. **Create Browserless Navigator Script**
   - Start from main Municode URL
   - Extract TOC links from rendered page
   - Navigate to zoning chapter
   - Extract dimensional standards tables

2. **Implement for Each Jurisdiction**:
   | Jurisdiction | Platform | Strategy |
   |--------------|----------|----------|
   | Titusville | Municode LDR | Browserless navigation |
   | Rockledge | Municode LDC | Browserless navigation |
   | West Melbourne | Municode | Browserless navigation |
   | Cape Canaveral | Municode | Browserless navigation |
   | Cocoa Beach | Municode LDC | Browserless navigation |
   | Palm Bay | AMLegal | City PDF fallback |
   | Brevard County | eLaws | Wait for recovery |

3. **Cost Estimate**
   - 5 jurisdictions × ~20 page loads = 100 units
   - Well within free tier equivalent
   - Monthly cost impact: ~$0.50

### GitHub Integration

Add to `.github/workflows/zonewise_extraction.yml`:
```yaml
env:
  BROWSERLESS_API_KEY: ${{ secrets.BROWSERLESS_API_KEY }}
```

### API Reference

```python
# Browserless Content API
response = httpx.post(
    f"https://chrome.browserless.io/content?token={API_KEY}",
    json={
        "url": url,
        "gotoOptions": {"waitUntil": "networkidle2", "timeout": 60000}
    },
    timeout=120
)

# Browserless PDF API
response = httpx.post(
    f"https://chrome.browserless.io/pdf?token={API_KEY}",
    json={
        "url": url,
        "options": {"printBackground": True, "format": "A4"},
        "gotoOptions": {"waitUntil": "networkidle2", "timeout": 90000}
    },
    timeout=180
)
```

---
*Validated: January 16, 2026*
