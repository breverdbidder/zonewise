#!/usr/bin/env python3
"""
PRD #11 — Playwright DOM table-wait fix for 17 remaining 0.35-confidence rows.
Root cause fix: wait_for_selector("table") + page.evaluate() instead of inner_text(body).
"""
import json, re, time, os, urllib.request
from playwright.sync_api import sync_playwright

MGMT  = os.environ["SUPABASE_MGMT_TOKEN"]
PROJ  = "mocerqjnksmhcjzxrewo"
SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_KEY"]

def sb_sql(sql):
    data = json.dumps({"query": sql}).encode()
    req = urllib.request.Request(
        f"https://api.supabase.com/v1/projects/{PROJ}/database/query",
        data=data,
        headers={"Authorization": f"Bearer {MGMT}", "Content-Type": "application/json", "User-Agent": "ZoneWise"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def clean(s):
    if not s:
        return None
    s = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', str(s))
    s = re.sub(r'\(\d+\)', '', s).strip()
    if s.lower() in ('none','na','n/a','-','no minimum','no max',''):
        return None
    m = re.search(r'[\d,]+(?:\.\d+)?', s)
    if m:
        try:
            v = float(m.group().replace(',',''))
            return v if v > 0 else None
        except:
            return None
    return None

def extract_fields(text, code):
    """Pull dimensional standards from rendered table text for a given district code."""
    tl = text.lower()
    # Find the block nearest to the district code mention
    code_lower = code.strip().lower()
    idx = tl.find(code_lower)
    if idx == -1:
        idx = tl.find(code_lower.replace('-', '').replace(' ', ''))
    if idx == -1:
        return {}
    # Use a broad window around the code mention
    block = text[max(0, idx-500): idx+8000]
    bl = block.lower()

    def find_ft(patterns):
        for pat in patterns:
            m = re.search(pat, bl, re.IGNORECASE)
            if m:
                v = clean(m.group(1))
                if v and 0 < v < 600:
                    return v
        return None

    def find_pct(patterns):
        for pat in patterns:
            m = re.search(pat, bl, re.IGNORECASE)
            if m:
                v = clean(m.group(1))
                if v and 0 < v <= 100:
                    return v
        return None

    def find_sqft(patterns):
        for pat in patterns:
            m = re.search(pat, bl, re.IGNORECASE)
            if m:
                s = m.group(1).replace(',', '')
                v = clean(s)
                if v and v > 100:
                    return v
        return None

    return {k: v for k, v in {
        "front_setback_ft":     find_ft([
            r'front[^.]{0,60}?(\d+(?:\.\d+)?)\s*(?:feet|ft|\')',
            r'front\s+yard[^.]{0,40}?(\d+(?:\.\d+)?)',
        ]),
        "rear_setback_ft":      find_ft([
            r'rear[^.]{0,60}?(\d+(?:\.\d+)?)\s*(?:feet|ft|\')',
            r'rear\s+yard[^.]{0,40}?(\d+(?:\.\d+)?)',
        ]),
        "side_setback_ft":      find_ft([
            r'(?<!\bcorner\b.{0,10})side[^.]{0,60}?(\d+(?:\.\d+)?)\s*(?:feet|ft|\')',
            r'side\s+yard[^.]{0,40}?(\d+(?:\.\d+)?)',
        ]),
        "max_height_ft":        find_ft([
            r'(?:max(?:imum)?\s+)?height[^.]{0,60}?(\d+(?:\.\d+)?)\s*(?:feet|ft)',
            r'not\s+exceed[^.]{0,30}?(\d+(?:\.\d+)?)\s*(?:feet|ft)',
            r'height\s*[:=]\s*(\d+(?:\.\d+)?)',
        ]),
        "min_lot_sqft":         find_sqft([
            r'lot\s+(?:area|size)[^.]{0,60}?([\d,]+)\s*(?:square\s+feet|sq\.?\s*ft)',
            r'minimum\s+(?:area|lot)[^.]{0,40}?([\d,]+)\s*(?:sq|square)',
        ]),
        "min_lot_width_ft":     find_ft([
            r'lot\s+width[^.]{0,50}?(\d+(?:\.\d+)?)\s*(?:feet|ft)',
            r'width[^.]{0,30}?minimum[^.]{0,20}?(\d+(?:\.\d+)?)\s*(?:feet|ft)',
        ]),
        "max_lot_coverage_pct": find_pct([
            r'(?:lot\s+|building\s+)?coverage[^.]{0,50}?(\d+(?:\.\d+)?)\s*(?:%|percent)',
            r'impervious[^.]{0,40}?(\d+(?:\.\d+)?)\s*(?:%|percent)',
        ]),
        "max_density_du_acre":  find_ft([
            r'(\d+(?:\.\d+)?)\s*(?:du|dwelling\s+units?)\s*(?:per|/)\s*acre',
            r'density[^.]{0,40}?(\d+(?:\.\d+)?)\s*(?:du|units)',
        ]),
    }.items() if v is not None}

# Per-jurisdiction chapter URLs to try — ordered best-to-fallback
# Key insight: use specific chapter nodeIds, not the landing page
JURISDICTION_CHAPTERS = {
    "Baldwin": [
        "https://library.municode.com/fl/baldwin/codes/code_of_ordinances?nodeId=PTIICOOR_CH86ZO_ARTIVDIRU",
        "https://library.municode.com/fl/baldwin/codes/code_of_ordinances?nodeId=PTIICOOR_CH86ZO_ARTIIIDI",
        "https://library.municode.com/fl/baldwin/codes/code_of_ordinances?nodeId=PTIICOOR_CH86ZO",
    ],
    "Callaway": [
        "https://library.municode.com/fl/callaway/codes/code_of_ordinances?nodeId=PTIICOOR_CH158ZO_ARTIVDIRE",
        "https://library.municode.com/fl/callaway/codes/code_of_ordinances?nodeId=PTIICOOR_CH158ZO_ARTIVDIST",
        "https://library.municode.com/fl/callaway/codes/code_of_ordinances?nodeId=PTIICOOR_CH158ZO",
    ],
    "Cedar Key": [
        "https://library.municode.com/fl/cedar_key/codes/code_of_ordinances?nodeId=PTIICOOR_CH110ZO_ARTIVDIST",
        "https://library.municode.com/fl/cedar_key/codes/code_of_ordinances?nodeId=PTIICOOR_CH110ZO_ARTIIIRE",
        "https://library.municode.com/fl/cedar_key/codes/code_of_ordinances?nodeId=PTIICOOR_CH110ZO",
    ],
    "DeFuniak Springs": [
        "https://library.municode.com/fl/defuniak_springs/codes/code_of_ordinances?nodeId=PTIICOOR_CH94ZO_ARTIVDIST",
        "https://library.municode.com/fl/defuniak_springs/codes/code_of_ordinances?nodeId=PTIICOOR_CH94ZO_ARTIIIDI",
        "https://library.municode.com/fl/defuniak_springs/codes/code_of_ordinances?nodeId=PTIICOOR_CH94ZO",
    ],
    "Delray Beach": [
        "https://library.municode.com/fl/delray_beach/codes/code_of_ordinances?nodeId=PTIICOOR_APXAZO_ARTIIISEDI_S4.3.4RLDIST",
        "https://library.municode.com/fl/delray_beach/codes/code_of_ordinances?nodeId=PTIICOOR_APXAZO_ARTIIISEDI",
        "https://library.municode.com/fl/delray_beach/codes/code_of_ordinances?nodeId=PTIICOOR_APXAZO",
    ],
    "Doral": [
        "https://library.municode.com/fl/doral/codes/code_of_ordinances?nodeId=PTIICOOR_CH7ZODERE_ARTIIIDI_DIV5MF4MURE",
        "https://library.municode.com/fl/doral/codes/code_of_ordinances?nodeId=PTIICOOR_CH7ZODERE_ARTIIIDI",
        "https://library.municode.com/fl/doral/codes/code_of_ordinances?nodeId=PTIICOOR_CH7ZODERE",
    ],
    "Key Colony Beach": [
        "https://library.municode.com/fl/key_colony_beach/codes/code_of_ordinances?nodeId=PTIICOOR_CH110ZO_ARTIIIRE",
        "https://library.municode.com/fl/key_colony_beach/codes/code_of_ordinances?nodeId=PTIICOOR_CH110ZO_ARTIVDIST",
        "https://library.municode.com/fl/key_colony_beach/codes/code_of_ordinances?nodeId=PTIICOOR_CH110ZO",
    ],
    "Macclenny": [
        "https://library.municode.com/fl/macclenny/codes/code_of_ordinances?nodeId=PTIICOOR_CH94ZO_ARTIVDIST",
        "https://library.municode.com/fl/macclenny/codes/code_of_ordinances?nodeId=PTIICOOR_CH94ZO_ARTIIIDI",
        "https://library.municode.com/fl/macclenny/codes/code_of_ordinances?nodeId=PTIICOOR_CH94ZO",
    ],
    "Mulberry": [
        "https://library.municode.com/fl/mulberry/codes/code_of_ordinances?nodeId=PTIICOOR_CH112ZO_ARTIVDIST",
        "https://library.municode.com/fl/mulberry/codes/code_of_ordinances?nodeId=PTIICOOR_CH112ZO_ARTIIIDI",
        "https://library.municode.com/fl/mulberry/codes/code_of_ordinances?nodeId=PTIICOOR_CH112ZO",
    ],
    "North Miami Beach": [
        "https://library.municode.com/fl/north_miami_beach/codes/code_of_ordinances?nodeId=PTIICOOR_CH24ZO_ARTIVDIST_DIVPUDI",
        "https://library.municode.com/fl/north_miami_beach/codes/code_of_ordinances?nodeId=PTIICOOR_CH24ZO_ARTIVDIST",
        "https://library.municode.com/fl/north_miami_beach/codes/code_of_ordinances?nodeId=PTIICOOR_CH24ZO",
    ],
    "Pensacola": [
        "https://library.municode.com/fl/pensacola/codes/code_of_ordinances?nodeId=PTIICOOR_APXBZO_ARTIIIOVDI_DIVENOEHCDI",
        "https://library.municode.com/fl/pensacola/codes/code_of_ordinances?nodeId=PTIICOOR_APXBZO_ARTIIIOVDI",
        "https://library.municode.com/fl/pensacola/codes/code_of_ordinances?nodeId=PTIICOOR_APXBZO",
        "https://library.municode.com/fl/pensacola/codes/code_of_ordinances?nodeId=PTIICOOR_CH42ZODERE",
    ],
    "Sanford": [
        # PRO = Professional Office district — look in Article II land use section
        "https://library.municode.com/fl/sanford/codes/code_of_ordinances?nodeId=PTIIILADERE_ARTIIZOUSREDI_S2.28PRDI",
        "https://library.municode.com/fl/sanford/codes/code_of_ordinances?nodeId=PTIIILADERE_SCHEDULE_CARDIRE",
        "https://library.municode.com/fl/sanford/codes/code_of_ordinances?nodeId=PTIIILADERE_ARTIIZOUSREDI",
    ],
}

def get_table_text_playwright(page, url):
    """Navigate to URL, wait for table DOM, return extracted table text."""
    try:
        page.goto(url, wait_until="networkidle", timeout=45000)
        # Wait for actual table element — the key fix
        try:
            page.wait_for_selector("table", timeout=20000)
        except:
            # No table found — try waiting longer then grab everything
            page.wait_for_timeout(5000)

        # Extract all table text via JS — gets the RENDERED content after AJAX
        table_text = page.evaluate("""
            () => {
                const tables = Array.from(document.querySelectorAll('table'));
                if (tables.length > 0) {
                    return tables.map(t => t.innerText).join('\\n\\n---TABLE---\\n\\n');
                }
                // Fallback: grab main content area
                const main = document.querySelector('.content-wrapper, main, #main-content, .section-content');
                return main ? main.innerText : document.body.innerText;
            }
        """)
        return table_text or ""
    except Exception as e:
        print(f"    ERROR: {e}")
        return ""

def main():
    # Load all 0.35 rows
    db_rows = sb_sql("""
        SELECT zs.id as sid, zd.code, j.name as jurisdiction
        FROM zone_standards zs
        JOIN zoning_districts zd ON zd.id=zs.zoning_district_id
        JOIN jurisdictions j ON j.id=zd.jurisdiction_id
        WHERE zs.confidence_score = 0.35
        ORDER BY j.name, zd.code
    """)

    by_j = {}
    for r in db_rows:
        by_j.setdefault(r['jurisdiction'], []).append(r)

    print(f"Target: {len(db_rows)} rows across {len(by_j)} jurisdictions\n")

    found_total   = 0
    updated_total = 0

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage",
                  "--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )

        for juris, rows in by_j.items():
            codes  = [r['code'] for r in rows]
            urls   = JURISDICTION_CHAPTERS.get(juris, [])
            print(f"\n{'='*55}")
            print(f"  {juris}: {codes}")

            best_text = ""
            best_url  = urls[0] if urls else ""
            best_score = 0

            for url in urls:
                page = context.new_page()
                try:
                    text = get_table_text_playwright(page, url)
                    # Score: how many zoning keywords?
                    kw_score = sum(1 for k in ['setback','front','rear','height','lot area','coverage'] if k in text.lower())
                    # Bonus for district code hits
                    code_hits = sum(1 for c in codes if c.strip().lower() in text.lower())
                    score = kw_score * 10 + code_hits * 5
                    print(f"    {url[-65:]}: {len(text):,}ch | kw={kw_score} code_hits={code_hits}")

                    if score > best_score:
                        best_score = score
                        best_text  = text
                        best_url   = url

                    # Stop if we have solid data
                    if kw_score >= 4 and code_hits >= 1:
                        page.close()
                        break
                except Exception as e:
                    print(f"    ERROR {url[-40:]}: {e}")
                finally:
                    try:
                        page.close()
                    except:
                        pass
                time.sleep(1.5)

            print(f"  Best: {len(best_text):,} chars | score={best_score}")

            for row in rows:
                code = row['code']
                sid  = row['sid']
                fields = extract_fields(best_text, code)
                n_key  = sum(1 for f in ['front_setback_ft','rear_setback_ft','side_setback_ft','max_height_ft','min_lot_sqft'] if f in fields)

                if fields and n_key >= 1:
                    conf = 0.70 if n_key >= 5 else (0.60 if n_key >= 3 else 0.45)
                    set_parts = [f"{k}={v}" for k, v in fields.items()]
                    set_parts += [f"confidence_score={conf}", f"source_url='{best_url}'", "scraped_at=NOW()"]
                    sb_sql(f"UPDATE zone_standards SET {','.join(set_parts)} WHERE id={sid} AND confidence_score<=0.35")
                    print(f"  ✅ {code}: {list(fields.keys())} conf={conf}")
                    found_total += 1
                else:
                    # 0.38 = table-wait attempted, no extractable data (likely image-based PDF)
                    sb_sql(f"UPDATE zone_standards SET confidence_score=0.38, source_url='{best_url}', scraped_at=NOW() WHERE id={sid} AND confidence_score=0.35")
                    print(f"  ⚠️  {code}: no data found → 0.38 (image/PDF source)")

                updated_total += 1
            time.sleep(2)

        context.close()
        browser.close()

    print(f"\n{'='*55}")
    print(f"Done: {found_total} with data / {updated_total} processed")
    dist = sb_sql("SELECT ROUND(confidence_score::numeric,2) as s, COUNT(*) c FROM zone_standards WHERE confidence_score IS NOT NULL GROUP BY 1 ORDER BY 1")
    print("Distribution:")
    for r in dist:
        print(f"  {r['s']} → {r['c']}")

if __name__ == "__main__":
    main()
