#!/usr/bin/env python3
"""
PRD #8 — Playwright scraper for 61 NULL zone_standards rows
Fetches Municode with full JS rendering → navigates to zoning chapter →
extracts dimensional table → upserts to Supabase
"""
import json, re, time, os, sys
from playwright.sync_api import sync_playwright

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
MGMT_TOKEN   = os.environ.get("SUPABASE_MGMT_TOKEN", "")
PROJ_REF     = "mocerqjnksmhcjzxrewo"

import urllib.request

def sb_sql(sql):
    data = json.dumps({"query": sql}).encode()
    req = urllib.request.Request(
        f"https://api.supabase.com/v1/projects/{PROJ_REF}/database/query",
        data=data,
        headers={"Authorization": f"Bearer {MGMT_TOKEN}",
                 "Content-Type": "application/json",
                 "User-Agent": "ZoneWise-PRD8-Scraper"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def sb_rest(method, path, body=None):
    url = f"{SUPABASE_URL}/rest/v1/{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers={
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }, method=method)
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.status

def clean_num(s):
    try:
        return float(str(s).replace(",","").strip())
    except:
        return None

ZONING_KEYWORDS = [
    "zoning district", "zoning regulations", "dimensional requirements",
    "schedule of regulations", "district regulations", "area regulations",
    "development standards", "bulk regulations", "zoning schedule",
    "table of dimensional", "land development", "zoning ordinance"
]

SETBACK_KEYWORDS = [
    "front", "rear", "side", "setback", "yard", "height", "lot area",
    "lot width", "coverage", "density", "floor area ratio"
]

def find_zoning_chapter_link(page):
    """Find the best link to the zoning dimensional standards chapter."""
    links = page.query_selector_all("a")
    scored = []
    for link in links:
        try:
            text = (link.inner_text() or "").lower().strip()
            href = link.get_attribute("href") or ""
            if not href or href.startswith("#"):
                continue
            score = 0
            for kw in ZONING_KEYWORDS:
                if kw in text:
                    score += 3
            if "zoning" in href.lower():
                score += 2
            if score > 0:
                scored.append((score, text[:60], href))
        except:
            pass
    scored.sort(reverse=True)
    return scored[:5]

def extract_standards_from_text(text, code):
    """Extract dimensional standards for a district code from page text."""
    results = {}
    tl = text.lower()
    code_l = code.lower()

    # Find code location in text
    idx = tl.find(code_l)
    if idx == -1:
        # Try stripped version (R-1 → r1, C-2 → c2)
        code_stripped = re.sub(r'[^a-z0-9]', '', code_l)
        for m in re.finditer(re.escape(code_stripped), tl):
            idx = m.start()
            break
    if idx == -1:
        return {}

    block = text[max(0, idx-300):idx+5000]
    bl = block.lower()

    # Regex patterns: (value)(unit)
    def find_ft(patterns):
        for pat in patterns:
            m = re.search(pat, bl)
            if m:
                v = clean_num(m.group(1))
                if v and 0 < v < 600:
                    return v
        return None

    def find_pct(patterns):
        for pat in patterns:
            m = re.search(pat, bl)
            if m:
                v = clean_num(m.group(1))
                if v and 0 < v <= 100:
                    return v
        return None

    def find_sqft(patterns):
        for pat in patterns:
            m = re.search(pat, bl)
            if m:
                v = clean_num(m.group(1))
                if v and v > 100:
                    return v
        return None

    results["front_setback_ft"] = find_ft([
        r'front[^.]{0,40}?(\d+(?:\.\d+)?)\s*(?:feet|ft|\')',
        r'front\s+yard[^.]{0,30}?(\d+(?:\.\d+)?)',
    ])
    results["rear_setback_ft"] = find_ft([
        r'rear[^.]{0,40}?(\d+(?:\.\d+)?)\s*(?:feet|ft|\')',
        r'rear\s+yard[^.]{0,30}?(\d+(?:\.\d+)?)',
    ])
    results["side_setback_ft"] = find_ft([
        r'(?<!corner\s)side[^.]{0,40}?(\d+(?:\.\d+)?)\s*(?:feet|ft|\')',
        r'side\s+yard[^.]{0,30}?(\d+(?:\.\d+)?)',
    ])
    results["max_height_ft"] = find_ft([
        r'height[^.]{0,40}?(\d+(?:\.\d+)?)\s*(?:feet|ft|\')',
        r'not\s+exceed[^.]{0,20}?(\d+(?:\.\d+)?)\s*(?:feet|ft)',
    ])
    results["min_lot_sqft"] = find_sqft([
        r'lot\s+(?:area|size)[^.]{0,40}?([\d,]+)\s*(?:square\s+feet|sq\.?\s*ft)',
        r'([\d,]+)\s*(?:square\s+feet|sq\.?\s*ft)[^.]{0,30}?(?:minimum|lot)',
    ])
    results["min_lot_width_ft"] = find_ft([
        r'lot\s+width[^.]{0,40}?(\d+(?:\.\d+)?)\s*(?:feet|ft|\')',
    ])
    results["max_lot_coverage_pct"] = find_pct([
        r'(?:lot\s+)?(?:building\s+)?coverage[^.]{0,40}?(\d+(?:\.\d+)?)\s*(?:%|percent)',
        r'impervious[^.]{0,30}?(\d+(?:\.\d+)?)\s*(?:%|percent)',
    ])
    results["max_far"] = find_ft([
        r'floor\s+area\s+ratio[^.]{0,30}?(\d+\.\d+)',
        r'\bfar\b[^.]{0,20}?(\d+\.\d+)',
    ])
    results["max_density_du_acre"] = find_ft([
        r'(\d+(?:\.\d+)?)\s*(?:du|dwelling\s+units?)\s*(?:per|/)\s*acre',
        r'density[^.]{0,30}?(\d+(?:\.\d+)?)\s*(?:per|/)\s*acre',
    ])

    # Remove None values
    return {k: v for k, v in results.items() if v is not None}

def scrape_jurisdiction(browser, juris_name, municode_url, target_rows):
    """Full Playwright scrape for one jurisdiction."""
    found_data = {}
    page = browser.new_page()
    codes = [r["district_code"] for r in target_rows]

    try:
        print(f"\n  Loading: {municode_url}")
        page.goto(municode_url, wait_until="networkidle", timeout=45000)
        page.wait_for_timeout(3000)

        # Try to find and navigate to zoning chapter
        zoning_links = find_zoning_chapter_link(page)
        print(f"  Zoning links found: {[(s, t) for s,t,h in zoning_links[:3]]}")

        best_text = page.inner_text("body")
        best_url  = municode_url

        # If we have a good zoning link, navigate to it
        if zoning_links and zoning_links[0][0] >= 3:
            target_href = zoning_links[0][2]
            if not target_href.startswith("http"):
                target_href = "https://library.municode.com" + target_href
            print(f"  Navigating to zoning chapter: {target_href[:80]}")
            try:
                page.goto(target_href, wait_until="networkidle", timeout=45000)
                page.wait_for_timeout(4000)
                chapter_text = page.inner_text("body")
                if len(chapter_text) > len(best_text):
                    best_text = chapter_text
                    best_url  = target_href
            except Exception as e:
                print(f"  Chapter nav failed: {e}")

        print(f"  Got {len(best_text):,} chars from {best_url[:60]}")

        # Check if we have any setback-related content
        has_zoning_data = any(kw in best_text.lower() for kw in SETBACK_KEYWORDS)
        print(f"  Has zoning data: {has_zoning_data}")

        if has_zoning_data:
            for row in target_rows:
                code = row["district_code"]
                extracted = extract_standards_from_text(best_text, code)
                found_data[row["standards_id"]] = (code, extracted, best_url)
        else:
            # Text doesn't have dimensional data — mark all 0.30
            for row in target_rows:
                found_data[row["standards_id"]] = (row["district_code"], {}, best_url)

    except Exception as e:
        print(f"  ERROR: {e}")
        for row in target_rows:
            found_data[row["standards_id"]] = (row["district_code"], {}, municode_url)
    finally:
        page.close()

    return found_data

def main():
    # Load 61 target rows
    rows = sb_sql("""
        SELECT
          zs.id as standards_id,
          zd.code as district_code,
          j.name as jurisdiction_name,
          j.municode_url
        FROM zone_standards zs
        JOIN zoning_districts zd ON zd.id = zs.zoning_district_id
        JOIN jurisdictions j ON j.id = zd.jurisdiction_id
        WHERE zs.confidence_score <= 0.30
        ORDER BY j.name, zd.code
    """)

    print(f"Target rows: {len(rows)}")

    # Group by jurisdiction
    by_juris = {}
    for row in rows:
        jname = row["jurisdiction_name"]
        by_juris.setdefault(jname, {"url": row["municode_url"], "rows": []})
        by_juris[jname]["rows"].append(row)

    print(f"Jurisdictions: {len(by_juris)}")

    total_updated = 0
    total_found   = 0
    total_not_found = 0

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])

        for juris_name, data in by_juris.items():
            print(f"\n{'='*55}")
            print(f"Scraping: {juris_name} ({len(data['rows'])} districts)")
            codes = [r["district_code"] for r in data["rows"]]
            print(f"  Districts: {', '.join(codes)}")

            found = scrape_jurisdiction(browser, juris_name, data["url"], data["rows"])

            for sid, (code, extracted, src_url) in found.items():
                key_fields = ["front_setback_ft","rear_setback_ft","side_setback_ft",
                              "max_height_ft","min_lot_sqft","max_lot_coverage_pct"]
                n_key = sum(1 for f in key_fields if f in extracted)

                if extracted:
                    confidence = 0.70 if n_key >= 5 else (0.60 if n_key >= 3 else 0.45)
                    set_parts = [f"{k} = {v}" for k,v in extracted.items()]
                    set_parts += [f"confidence_score = {confidence}",
                                  f"source_url = '{src_url}'",
                                  "scraped_at = NOW()"]
                    sb_sql(f"UPDATE zone_standards SET {', '.join(set_parts)} WHERE id = {sid} AND confidence_score <= 0.30")
                    print(f"  ✅ {code:12} → {list(extracted.keys())} (conf={confidence})")
                    total_found += 1
                else:
                    sb_sql(f"UPDATE zone_standards SET confidence_score = 0.30, source_url = '{src_url}', scraped_at = NOW() WHERE id = {sid} AND confidence_score IS NULL OR confidence_score <= 0.30")
                    print(f"  ❌ {code:12} → not found (0.30)")
                    total_not_found += 1
                total_updated += 1

            time.sleep(2)

        browser.close()

    print(f"\n{'='*55}")
    print(f"COMPLETE: {total_found} extracted / {total_not_found} not found / {total_updated} total")

    # Verify
    remaining = sb_sql("SELECT COUNT(*) as c FROM zone_standards WHERE confidence_score IS NULL")
    print(f"NULL confidence remaining: {remaining[0]['c']} (want 0)")
    dist = sb_sql("SELECT ROUND(confidence_score::numeric,2) as s, COUNT(*) c FROM zone_standards WHERE confidence_score IS NOT NULL GROUP BY 1 ORDER BY 1")
    print(f"Distribution: {dist}")

if __name__ == "__main__":
    main()
