# ZoneWise 12-Week Sprint Plan V3 (FINAL)
## AI Architect Recommendation | Data-First + Automation-Enhanced

**Created:** January 22, 2026  
**Target Completion:** April 16, 2026  
**Philosophy:** Data is the moat. Quality beats quantity. Automation is the multiplier.

---

## STRATEGIC CHANGES FROM V2

| Factor | V2 (8 Weeks) | V3 (12 Weeks) | Reason |
|--------|--------------|---------------|--------|
| Timeline | 8 weeks | **12 weeks** | Realistic for quality |
| Automation | None | **Week 1-2 investment** | 10x scraping speed |
| Quality Target | 67 counties any % | **Tiered: 95%/90%/85%** | Investor confidence |
| LLM Approach | Real-time | **Batch API (50% savings)** | Cost optimization |
| Validation | Week 8 only | **Daily pipeline** | Early error detection |
| Budget | ~$1,500 | **$1,500 (same, better ROI)** | Smart allocation |

---

## ANSWERS TO ADVISOR QUESTIONS

| Question | Answer |
|----------|--------|
| **GIS APIs access?** | YES - BCPAO, Miami-Dade, Orange, Hillsborough, Palm Beach all have ArcGIS REST APIs |
| **Phase 15 data exists?** | PARTIALLY - Statutory timelines exist, specific processing times require hybrid approach |
| **Compute/API budget?** | **$1,500 for 12 weeks** - detailed breakdown below |
| **Planning dept relationships?** | NO - 100% automated via CI V2 scraping methodology |

---

## 12-WEEK SPRINT SCHEDULE

### 🔵 SPRINT 1 (Weeks 1-3): FOUNDATION + AUTOMATION
**Jan 22 - Feb 11, 2026**

#### Week 1: Automation Infrastructure
| Day | Task | Deliverable |
|-----|------|-------------|
| 1 | Modal.com account setup | Parallel scraper ready |
| 2 | Template detector build | Classify ordinance structures |
| 3 | Claude Batch API setup | Overnight processing pipeline |
| 4 | Validation pipeline | GitHub Actions daily checks |
| 5 | Ground truth dataset | 50 Brevard districts manually verified |

#### Week 2: Brevard Phase 4 (Permitted Uses)
| Day | Task | Deliverable |
|-----|------|-------------|
| 1-2 | Structured output schema | JSON schema for use tables |
| 3-4 | Extract 5 pilot jurisdictions | Melbourne, Palm Bay, Titusville, Cocoa, Brevard County |
| 5 | QA and iterate | Fix extraction errors |

#### Week 3: Brevard Phases 7, 8 + Orange Pilot
| Day | Task | Deliverable |
|-----|------|-------------|
| 1-2 | Brevard overlays (Phase 7) | All 17 jurisdictions |
| 3-4 | Brevard bonuses (Phase 8) | Palm Bay Table 173-8 + others |
| 5 | Orange County Phases 2-3 | Base zoning + DIMS |

**Exit Criteria:**
- [ ] Automation tools: 4/4 built and tested
- [ ] Brevard: 14/20 phases at **95% accuracy**
- [ ] Orange: 6/20 phases at 90% accuracy
- [ ] Ground truth: 50 districts verified
- [ ] Cost: ≤$220

---

### 🟢 SPRINT 2 (Weeks 4-6): TIER 1 SCALE
**Feb 12 - Mar 4, 2026**

#### Week 4: Tier 1 Counties - Base Data
| Task | Counties | Phases |
|------|----------|--------|
| Parallel scrape (Modal) | Miami-Dade, Broward, Palm Beach, Hillsborough | 2, 3 |
| Extract with templates | Pinellas, Duval, Lee, Polk | 2, 3 |
| Validate daily | All 10 Tier 1 | Accuracy check |

#### Week 5: Tier 1 Counties - Permitted Uses
| Task | Counties | Phases |
|------|----------|--------|
| Batch extract uses | All 10 Tier 1 | 4 |
| Build use taxonomy | Standardize naming | - |
| QA sample | 100 random districts | Accuracy check |

#### Week 6: Tier 1 Counties - P1 Phases
| Task | Counties | Phases |
|------|----------|--------|
| Overlays | All 10 Tier 1 | 7 |
| Development bonuses | All 10 Tier 1 | 8 |
| P2 phases for Brevard | Brevard only | 5, 9, 10, 15, 16, 17 |

**Exit Criteria:**
- [ ] 10 Tier 1 counties: 12/20 phases at **90% accuracy**
- [ ] Brevard: 18/20 phases at **95% accuracy**
- [ ] ~10,000 districts in database
- [ ] Use taxonomy: 200+ standardized uses
- [ ] Cost: ≤$302

---

### 🟡 SPRINT 3 (Weeks 7-10): TIER 2 + DESIGN PARTNERS
**Mar 5 - Apr 1, 2026**

#### Week 7: Tier 1 Depth
| Task | Counties | Phases |
|------|----------|--------|
| P2 phases | All 10 Tier 1 | 5, 9, 10, 15 |
| Ordinance library | All 10 Tier 1 | 16 |
| Change detection | All 10 Tier 1 | 17 |

#### Week 8: Tier 2 Start
| Task | Counties | Phases |
|------|----------|--------|
| Parallel scrape | Volusia, Pasco, Seminole, Sarasota, Manatee | 2, 3, 4 |
| Parallel scrape | Lake, Osceola, Marion, Collier, St. Johns | 2, 3, 4 |

#### Week 9: Design Partner Testing
| Task | Target | Deliverable |
|------|--------|-------------|
| Recruit 5 Brevard builders | Space Coast HBCA members | Contact list |
| Onboard 3 design partners | API access + training | Active users |
| Collect feedback | Bug reports, feature requests | Prioritized backlog |

#### Week 10: Accuracy Audit
| Task | Scope | Target |
|------|-------|--------|
| Full Tier 1 audit | 10 counties × 100 districts | 95% accuracy |
| Fix identified errors | All flagged districts | 0 critical errors |
| Design partner testimonials | 3 written statements | Investor materials |

**Exit Criteria:**
- [ ] 10 Tier 1 counties: **18/20 phases at 95% accuracy**
- [ ] 10 Tier 2 counties: 6/20 phases at 85% accuracy
- [ ] 3 design partners active with testimonials
- [ ] ~15,000 districts in database
- [ ] Cost: ≤$284

---

### 🔴 SPRINT 4 (Weeks 11-12): TIER 3 + INVESTOR READY
**Apr 2 - Apr 16, 2026**

#### Week 11: Complete 67 Counties
| Task | Counties | Phases |
|------|----------|--------|
| Tier 2 remainder | 10 more counties | 2, 3, 4 |
| Tier 3 all | 37 remaining counties | 2, 3, 4 |
| P2 phases for Tier 2 | 20 Tier 2 counties | 5, 7, 8 |

#### Week 12: Investor Ready
| Task | Deliverable |
|------|-------------|
| API documentation | Swagger/OpenAPI spec |
| Data room | Metrics, validation reports, testimonials |
| Pitch deck data | Screenshots, accuracy stats |
| Final validation | Random 500-district audit |

**Exit Criteria:**
- [ ] **67/67 FL counties with data**
- [ ] Tier 1 (10): 18/20 phases at 95% accuracy
- [ ] Tier 2 (20): 12/20 phases at 90% accuracy
- [ ] Tier 3 (37): 6/20 phases at 85% accuracy
- [ ] ~20,000 districts in database
- [ ] 5 design partners (3 with testimonials)
- [ ] Investor data room complete
- [ ] Cost: ≤$275

---

## BUDGET SUMMARY

| Sprint | Weeks | Budget | Cumulative |
|--------|-------|--------|------------|
| 1 | 1-3 | $220 | $220 |
| 2 | 4-6 | $302 | $522 |
| 3 | 7-10 | $284 | $806 |
| 4 | 11-12 | $275 | $1,081 |
| Contingency | - | $300 | **$1,381** |

**Buffer remaining:** $119 (within $1,500 budget)

---

## AUTOMATION TOOLS TO BUILD (Week 1)

### 1. Parallel Scraper (Modal.com)
```python
# modal_scraper.py
import modal

stub = modal.Stub("zonewise-scraper")
image = modal.Image.debian_slim().pip_install("playwright", "beautifulsoup4")

@stub.function(image=image, concurrency_limit=10, timeout=300)
async def scrape_jurisdiction(url: str) -> dict:
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        content = await page.content()
        await browser.close()
    return {"url": url, "html": content}

# Process 670 jurisdictions in parallel
@stub.local_entrypoint()
def main():
    urls = load_jurisdiction_urls()  # From Supabase
    results = list(scrape_jurisdiction.map(urls))
    save_to_supabase(results)
```

### 2. Template Detector
```python
# template_detector.py
def detect_ordinance_template(toc_html: str) -> str:
    """Classify ordinance structure into known templates."""
    
    TEMPLATE_PATTERNS = {
        "template_a": ["Article IV - Zoning Districts", "Article V - Use Regulations"],
        "template_b": ["Chapter 62 - Land Development", "Division 2 - Zoning"],
        "template_c": ["Part III - Land Development Code", "Chapter 34 - Zoning"],
    }
    
    for template, patterns in TEMPLATE_PATTERNS.items():
        if all(p in toc_html for p in patterns):
            return template
    
    return "custom"  # Manual review needed
```

### 3. Validation Pipeline
```yaml
# .github/workflows/validate.yml
name: Daily Data Validation
on:
  schedule:
    - cron: '0 6 * * *'  # 6 AM UTC daily

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Sample 50 random districts
        run: python scripts/sample_districts.py
        
      - name: Validate against ground truth
        run: python scripts/validate_accuracy.py
        
      - name: Create issues for errors
        if: failure()
        run: python scripts/create_issues.py
        
      - name: Update accuracy dashboard
        run: python scripts/update_metrics.py
```

### 4. Claude Batch Processor
```python
# batch_processor.py
import anthropic

client = anthropic.Anthropic()

def process_batch(requests: list[dict]) -> str:
    """Submit batch for overnight processing (50% cheaper)."""
    
    batch = client.batches.create(
        requests=[
            {
                "custom_id": f"district-{r['id']}",
                "params": {
                    "model": "claude-sonnet-4-5-20250929",
                    "max_tokens": 4096,
                    "messages": [{"role": "user", "content": r['prompt']}]
                }
            }
            for r in requests
        ]
    )
    
    return batch.id  # Poll for results next morning
```

---

## QUALITY GATES

| Gate | When | Criteria | Action if Fail |
|------|------|----------|----------------|
| G1 | Week 2 | Brevard Phase 4 accuracy ≥90% | Pause, fix extraction logic |
| G2 | Week 4 | Template detector accuracy ≥85% | Add more patterns |
| G3 | Week 6 | Tier 1 base data accuracy ≥85% | Reduce scope to 5 counties |
| G4 | Week 10 | Tier 1 full accuracy ≥95% | Extend Sprint 3 by 1 week |
| G5 | Week 12 | 67 counties with data | Acceptable at 60 counties minimum |

---

## RISK REGISTER

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Municode rate limiting | 30% | HIGH | Implement delays, rotate IPs |
| Phase 15 data doesn't exist | 50% | MEDIUM | Pivot to "estimated timelines" |
| Design partners don't respond | 40% | MEDIUM | Offer 6 months free, expand outreach |
| Budget overrun | 20% | LOW | $300 contingency, reduce Tier 3 scope |
| Quality <90% at Week 10 | 25% | HIGH | Extend to 14 weeks, focus on Tier 1 |

---

## INVESTOR-READY DELIVERABLES (Week 12)

| Deliverable | Content |
|-------------|---------|
| **Data Coverage Proof** | SQL query showing 67 counties, 20K districts |
| **Accuracy Report** | Random sample validation: 95% Tier 1, 90% Tier 2 |
| **Unique Features Demo** | Phases 8, 15, 17 live demonstration |
| **Design Partner Testimonials** | 3 written statements from Brevard builders |
| **Competitive Comparison** | ZoneWise 18/20 vs Gridics 16/20 vs Zoneomics 10/20 |
| **API Documentation** | Swagger spec + example queries |
| **Cost Analysis** | $1,500 investment → $300-400K annual value |

---

## FINAL RECOMMENDATION

### ✅ APPROVED PLAN: 12 Weeks, $1,500 Budget

**Key Decisions:**
1. **Timeline:** Extend to 12 weeks for quality (not 8)
2. **Automation:** Invest Week 1-2 in tooling (10x ROI)
3. **Quality:** Tiered accuracy targets (95%/90%/85%)
4. **Budget:** $1,500 total, front-loaded for automation
5. **Validation:** Daily pipeline, not end-of-project

**Expected Outcome:**
- 67 FL counties with quality-tiered data
- 10 counties at investor-grade 95% accuracy
- 3-5 design partners with testimonials
- Ready for pre-seed by April 16, 2026
- Positioned before July 1 HB 267 deadline

---

## IMMEDIATE NEXT ACTIONS

### Today (Jan 22):
1. [ ] Create Modal.com account (free tier)
2. [ ] Apply for Claude Batch API access
3. [ ] Push V3 plan to GitHub

### Tomorrow (Jan 23):
4. [ ] Build parallel scraper prototype
5. [ ] Create 50-district ground truth dataset
6. [ ] Set up validation GitHub Action

### Day 3 (Jan 24):
7. [ ] Test parallel scraping on 5 Brevard jurisdictions
8. [ ] Build template detector v1
9. [ ] Start Brevard Phase 4 extraction

---

*Version: 3.0 (Final)*
*Created: January 22, 2026*
*AI Architect: Claude*
*Project: ZoneWise*
*Owner: Ariel Shapira / Everest Capital USA*
