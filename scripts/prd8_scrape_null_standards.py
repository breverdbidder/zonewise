#!/usr/bin/env python3
"""
PRD #9 Path B — Playwright deep nav for 24 remaining 0.30 rows
Targets specific Municode chapter/article nodeIds discovered via web search
"""
import json, re, time, os, sys, urllib.request
from playwright.sync_api import sync_playwright

MGMT_TOKEN = os.environ["SUPABASE_MGMT_TOKEN"]
PROJ_REF   = "mocerqjnksmhcjzxrewo"
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

def sb_sql(sql):
    data = json.dumps({"query": sql}).encode()
    req = urllib.request.Request(
        f"https://api.supabase.com/v1/projects/{PROJ_REF}/database/query",
        data=data,
        headers={"Authorization": f"Bearer {MGMT_TOKEN}",
                 "Content-Type": "application/json",
                 "User-Agent": "ZoneWise-PRD9"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def clean(s):
    s = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', str(s))
    s = re.sub(r'\(\d+\)', '', s).strip()
    if s.lower() in ('none','','-','n/a'):
        return None
    m = re.search(r'[\d,]+(?:\.\d+)?', s)
    if m:
        try:
            return float(m.group().replace(',',''))
        except:
            return None
    return None

def extract(text, code):
    """Extract dimensional standards from text for a given district code."""
    tl = text.lower()
    idx = tl.find(code.lower())
    if idx == -1:
        # Try without hyphens
        idx = tl.find(code.replace('-','').lower())
    if idx == -1:
        return {}

    block = text[max(0, idx-300):idx+5000]
    bl    = block.lower()

    def find_ft(pats):
        for pat in pats:
            m = re.search(pat, bl)
            if m:
                v = clean(m.group(1))
                if v and 0 < v < 600:
                    return v
        return None

    def find_pct(pats):
        for pat in pats:
            m = re.search(pat, bl)
            if m:
                v = clean(m.group(1))
                if v and 0 < v <= 100:
                    return v
        return None

    def find_sqft(pats):
        for pat in pats:
            m = re.search(pat, bl)
            if m:
                v = clean(m.group(1))
                if v and v > 100:
                    return v
        return None

    return {k: v for k, v in {
        "front_setback_ft":       find_ft([r'front[^.]{0,50}?(\d+(?:\.\d+)?)\s*(?:feet|ft|\')', r'front\s+yard[^.]{0,30}?(\d+(?:\.\d+)?)']),
        "rear_setback_ft":        find_ft([r'rear[^.]{0,50}?(\d+(?:\.\d+)?)\s*(?:feet|ft|\')',  r'rear\s+yard[^.]{0,30}?(\d+(?:\.\d+)?)']),
        "side_setback_ft":        find_ft([r'(?<!corner\s)side[^.]{0,50}?(\d+(?:\.\d+)?)\s*(?:feet|ft|\')', r'side\s+yard[^.]{0,30}?(\d+(?:\.\d+)?)']),
        "max_height_ft":          find_ft([r'height[^.]{0,50}?(\d+(?:\.\d+)?)\s*(?:feet|ft|\')', r'not\s+exceed[^.]{0,20}?(\d+(?:\.\d+)?)\s*(?:feet|ft)']),
        "min_lot_sqft":           find_sqft([r'lot\s+(?:area|size)[^.]{0,40}?([\d,]+)\s*(?:square\s+feet|sq\.?\s*ft)', r'([\d,]+)\s*(?:sq\.?\s*ft|square\s+feet)[^.]{0,30}?(?:minimum|lot)']),
        "min_lot_width_ft":       find_ft([r'lot\s+width[^.]{0,40}?(\d+(?:\.\d+)?)\s*(?:feet|ft|\')']),
        "max_lot_coverage_pct":   find_pct([r'(?:lot\s+)?(?:building\s+)?coverage[^.]{0,40}?(\d+(?:\.\d+)?)\s*(?:%|percent)', r'impervious[^.]{0,30}?(\d+(?:\.\d+)?)\s*(?:%|percent)']),
        "max_density_du_acre":    find_ft([r'(\d+(?:\.\d+)?)\s*(?:du|dwelling\s+units?)\s*(?:per|/)\s*acre']),
    }.items() if v is not None}

# Deep chapter URLs to try per jurisdiction (discovered via web search + Municode structure)
JURISDICTION_URLS = {
    "Fort Walton Beach": [
        "https://library.municode.com/fl/fort_walton_beach/codes/code_of_ordinances?nodeId=PTIICOOR_CH159ZORE",
        "https://library.municode.com/fl/fort_walton_beach/codes/code_of_ordinances?nodeId=PTIICOOR_CH159ZORE_ARTIVDI",
        "https://library.municode.com/fl/fort_walton_beach/codes/code_of_ordinances?nodeId=PTIICOOR_CH159ZORE_ARTVDI",
        "https://library.municode.com/fl/fort_walton_beach/codes/code_of_ordinances?nodeId=PTIICOOR_CH159ZORE_ARTIVDIST_DIVIRE",
        "https://library.municode.com/fl/fort_walton_beach/codes/code_of_ordinances",
        "https://library.municode.com/fl/fort_walton_beach/codes/land_development_code",
    ],
    "Baldwin": [
        "https://library.municode.com/fl/baldwin/codes/code_of_ordinances?nodeId=PTIICOOR_CH86ZO",
        "https://library.municode.com/fl/baldwin/codes/code_of_ordinances?nodeId=PTIICOOR_CH86ZO_ARTIVDIST",
        "https://library.municode.com/fl/baldwin/codes/code_of_ordinances",
    ],
    "Callaway": [
        "https://library.municode.com/fl/callaway/codes/code_of_ordinances?nodeId=PTIICOOR_CH158ZO",
        "https://library.municode.com/fl/callaway/codes/code_of_ordinances?nodeId=PTIICOOR_CH158ZO_ARTIVDI",
        "https://library.municode.com/fl/callaway/codes/code_of_ordinances",
    ],
    "Cedar Key": [
        "https://library.municode.com/fl/cedar_key/codes/code_of_ordinances?nodeId=PTIICOOR_CH110ZO",
        "https://library.municode.com/fl/cedar_key/codes/code_of_ordinances?nodeId=PTIICOOR_CH110ZO_ARTIVDIST",
        "https://library.municode.com/fl/cedar_key/codes/code_of_ordinances",
    ],
    "Pensacola": [
        "https://library.municode.com/fl/pensacola/codes/code_of_ordinances?nodeId=PTIICOOR_CH42ZODERE",
        "https://library.municode.com/fl/pensacola/codes/code_of_ordinances?nodeId=PTIICOOR_CH42ZODERE_ARTVIOVDI",
        "https://library.municode.com/fl/pensacola/codes/code_of_ordinances",
    ],
    "DeFuniak Springs": [
        "https://library.municode.com/fl/defuniak_springs/codes/code_of_ordinances?nodeId=PTIICOOR_CH94ZO",
        "https://library.municode.com/fl/defuniak_springs/codes/code_of_ordinances",
    ],
    "Delray Beach": [
        "https://library.municode.com/fl/delray_beach/codes/code_of_ordinances?nodeId=PTIICOOR_CH4.4.2ZO_ARTIVDIST",
        "https://library.municode.com/fl/delray_beach/codes/code_of_ordinances?nodeId=PTIICOOR_APXAZO",
        "https://library.municode.com/fl/delray_beach/codes/code_of_ordinances",
    ],
    "Doral": [
        "https://library.municode.com/fl/doral/codes/code_of_ordinances?nodeId=PTIICOOR_CH7ZODERE",
        "https://library.municode.com/fl/doral/codes/code_of_ordinances?nodeId=PTIICOOR_CH7ZODERE_ARTIVDIST",
        "https://library.municode.com/fl/doral/codes/code_of_ordinances",
    ],
    "Key Colony Beach": [
        "https://library.municode.com/fl/key_colony_beach/codes/code_of_ordinances?nodeId=PTIICOOR_CH110ZO",
        "https://library.municode.com/fl/key_colony_beach/codes/code_of_ordinances",
    ],
    "Macclenny": [
        "https://library.municode.com/fl/macclenny/codes/code_of_ordinances?nodeId=PTIICOOR_CH94ZO",
        "https://library.municode.com/fl/macclenny/codes/code_of_ordinances",
    ],
    "Mulberry": [
        "https://library.municode.com/fl/mulberry/codes/code_of_ordinances?nodeId=PTIICOOR_CH112ZO",
        "https://library.municode.com/fl/mulberry/codes/code_of_ordinances",
    ],
    "North Miami Beach": [
        "https://library.municode.com/fl/north_miami_beach/codes/code_of_ordinances?nodeId=PTIICOOR_CH24ZO",
        "https://library.municode.com/fl/north_miami_beach/codes/code_of_ordinances?nodeId=PTIICOOR_CH24ZO_ARTIVDIST",
        "https://library.municode.com/fl/north_miami_beach/codes/code_of_ordinances",
    ],
    "Sanford": [  # PRO only
        "https://library.municode.com/fl/sanford/codes/code_of_ordinances?nodeId=PTIIILADERE_SCHEDULE_CARDIRE",
        "https://library.municode.com/fl/sanford/codes/code_of_ordinances?nodeId=PTIIILADERE_ARTIIZOUSREDI_S2.28PRDI",
    ],
    "Palatka": [
        "https://library.municode.com/fl/palatka/codes/code_of_ordinances?nodeId=PTIICOOR_CH98ZO",
        "https://library.municode.com/fl/palatka/codes/code_of_ordinances",
    ],
    "Oakland Park": [
        "https://library.municode.com/fl/oakland_park/codes/code_of_ordinances?nodeId=PTIICOOR_CH155ZO",
        "https://library.municode.com/fl/oakland_park/codes/code_of_ordinances",
    ],
    "New Smyrna Beach": [
        "https://library.municode.com/fl/new_smyrna_beach/codes/code_of_ordinances?nodeId=PTIICOOR_CH94ZO",
        "https://library.municode.com/fl/new_smyrna_beach/codes/code_of_ordinances",
    ],
}

def best_text_for_jurisdiction(browser, juris_name, urls):
    """Try each URL, return the longest text containing zoning keywords."""
    ZONING_KW = ['setback','front yard','rear yard','height','lot area','lot width','coverage']
    best = ""
    best_url = urls[0]
    for url in urls:
        page = browser.new_page()
        try:
            page.goto(url, wait_until="networkidle", timeout=40000)
            page.wait_for_timeout(3000)
            text = page.inner_text("body")
            has_data = sum(1 for kw in ZONING_KW if kw in text.lower())
            print(f"    {url[-60:]}: {len(text):,} chars | {has_data} kw")
            if has_data >= 2 and len(text) > len(best):
                best = text
                best_url = url
            # If we have good data, stop trying more URLs
            if has_data >= 4:
                page.close()
                break
        except Exception as e:
            print(f"    {url[-50:]}: ERROR {e}")
        finally:
            try:
                page.close()
            except:
                pass
        time.sleep(1)
    return best, best_url

def main():
    # Load remaining 0.30 rows
    rows = sb_sql("""
        SELECT zs.id as sid, zd.code, j.name as jurisdiction, j.municode_url
        FROM zone_standards zs
        JOIN zoning_districts zd ON zd.id=zs.zoning_district_id
        JOIN jurisdictions j ON j.id=zd.jurisdiction_id
        WHERE zs.confidence_score = 0.30
        ORDER BY j.name, zd.code
    """)
    print(f"Target: {len(rows)} rows")

    by_j = {}
    for r in rows:
        by_j.setdefault(r['jurisdiction'], []).append(r)

    updated_total = 0
    found_total   = 0

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=["--no-sandbox","--disable-dev-shm-usage"])

        for juris, juris_rows in by_j.items():
            codes = [r['code'] for r in juris_rows]
            print(f"\n{'='*55}")
            print(f"  {juris}: {codes}")

            urls = JURISDICTION_URLS.get(juris, [juris_rows[0]['municode_url']])
            text, src_url = best_text_for_jurisdiction(browser, juris, urls)
            print(f"  Best text: {len(text):,} chars from {src_url[-60:]}")

            for row in juris_rows:
                code = row['code']
                sid  = row['sid']

                extracted = extract(text, code)
                n_key = sum(1 for f in ['front_setback_ft','rear_setback_ft','side_setback_ft',
                                        'max_height_ft','min_lot_sqft'] if f in extracted)

                if extracted and n_key >= 1:
                    conf = 0.70 if n_key >= 5 else (0.60 if n_key >= 3 else 0.45)
                    set_parts = [f"{k}={v}" for k,v in extracted.items()]
                    set_parts += [f"confidence_score={conf}", f"source_url='{src_url}'", "scraped_at=NOW()"]
                    sb_sql(f"UPDATE zone_standards SET {','.join(set_parts)} WHERE id={sid} AND confidence_score<=0.30")
                    print(f"  ✅ {code}: {list(extracted.keys())} conf={conf}")
                    found_total   += 1
                else:
                    # Mark 0.35 = attempted deep nav, still not found (honest)
                    sb_sql(f"UPDATE zone_standards SET confidence_score=0.35, source_url='{src_url}', scraped_at=NOW() WHERE id={sid} AND confidence_score=0.30")
                    print(f"  ⚠️  {code}: not found → 0.35")
                updated_total += 1

            time.sleep(2)

        browser.close()

    print(f"\n{'='*55}")
    print(f"Done: {found_total} with data / {updated_total} total processed")
    r = sb_sql("SELECT ROUND(confidence_score::numeric,2) as s, COUNT(*) c FROM zone_standards WHERE confidence_score IS NOT NULL GROUP BY 1 ORDER BY 1")
    print(f"Distribution: {r}")

if __name__ == "__main__":
    main()
