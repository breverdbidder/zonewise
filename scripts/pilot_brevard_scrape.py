"""
Brevard County Pilot Scrape - Day 1-2 Task
Tests AgentQL Pro + Playwright against 1 Brevard jurisdiction (Melbourne)
to validate the scraping pipeline works end-to-end.
"""

import os
import sys
import json
import re
import httpx
from datetime import datetime
from pathlib import Path

# Configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
AGENTQL_API_KEY = os.environ.get("AGENTQL_API_KEY", "")

# Target: Melbourne, FL (jurisdiction_id=1)
PILOT_JURISDICTION = {
    "id": 1,
    "name": "Melbourne",
    "municode_slug": "melbourne",
    "municode_url": "https://library.municode.com/fl/melbourne/codes/code_of_ordinances",
}


def get_supabase_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


def verify_existing_data():
    """Step 1: Verify existing Melbourne data in Supabase."""
    print("\n=== Step 1: Verifying existing Melbourne data ===")
    headers = get_supabase_headers()

    # Check jurisdictions
    r = httpx.get(
        f"{SUPABASE_URL}/rest/v1/jurisdictions",
        headers={**headers, "Prefer": "count=exact"},
        params={"select": "id,name,state,county", "name": "eq.Melbourne", "limit": "5"},
        timeout=30.0,
    )
    jurisdictions = r.json()
    print(f"  Melbourne jurisdictions found: {len(jurisdictions)}")
    for j in jurisdictions:
        print(f"    - id={j['id']}, name={j['name']}, state={j.get('state', 'N/A')}")

    # Check zoning districts for Melbourne
    r = httpx.get(
        f"{SUPABASE_URL}/rest/v1/zoning_districts",
        headers={**headers, "Prefer": "count=exact"},
        params={"select": "id,code,name,category", "jurisdiction_id": "eq.1", "limit": "10"},
        timeout=30.0,
    )
    districts = r.json()
    count = r.headers.get("content-range", "?")
    print(f"  Melbourne districts: {count}")
    for d in districts[:5]:
        print(f"    - {d['code']}: {d.get('name', 'N/A')}")

    # Check dimensional standards for Melbourne districts
    r = httpx.get(
        f"{SUPABASE_URL}/rest/v1/dimensional_standards",
        headers={**headers, "Prefer": "count=exact"},
        params={"select": "*", "limit": "5"},
        timeout=30.0,
    )
    dims = r.json()
    dims_count = r.headers.get("content-range", "?")
    print(f"  Dimensional standards: {dims_count}")

    # Check ordinances for Melbourne
    r = httpx.get(
        f"{SUPABASE_URL}/rest/v1/ordinances",
        headers={**headers, "Prefer": "count=exact"},
        params={"select": "id,ordinance_number,title", "jurisdiction_id": "eq.1", "limit": "5"},
        timeout=30.0,
    )
    ords = r.json()
    ords_count = r.headers.get("content-range", "?")
    print(f"  Melbourne ordinances: {ords_count}")
    for o in ords[:3]:
        print(f"    - {o.get('ordinance_number', 'N/A')}: {(o.get('title', 'N/A') or 'N/A')[:60]}")

    return {
        "jurisdictions": len(jurisdictions),
        "districts": count,
        "dimensional_standards": dims_count,
        "ordinances": ords_count,
    }


def test_agentql_scrape():
    """Step 2: Test AgentQL Pro scraping on Melbourne Municode page."""
    print("\n=== Step 2: Testing AgentQL Pro Scraping ===")

    if not AGENTQL_API_KEY:
        print("  WARNING: AGENTQL_API_KEY not set, skipping AgentQL test")
        return test_playwright_fallback()

    try:
        import agentql
        agentql.configure(api_key=AGENTQL_API_KEY)
        print("  AgentQL configured successfully")
    except Exception as e:
        print(f"  AgentQL configuration failed: {e}")
        return test_playwright_fallback()

    # Test with Playwright + AgentQL
    try:
        from playwright.sync_api import sync_playwright
        print("  Playwright available")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = agentql.wrap(browser.new_page())

            url = PILOT_JURISDICTION["municode_url"]
            print(f"  Navigating to: {url}")
            page.goto(url, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(3000)

            # Get page content size
            content = page.content()
            print(f"  Page content size: {len(content):,} bytes")

            if len(content) < 10000:
                print("  WARNING: Content too small - JS may not have rendered")
            else:
                print("  Content size OK - JS rendered properly")

            # Try AgentQL query for zoning chapters
            try:
                query = """
                {
                    zoning_chapters[] {
                        title
                        link
                    }
                }
                """
                result = page.query_data(query)
                print(f"  AgentQL query result: {json.dumps(result, indent=2)[:500]}")
            except Exception as e:
                print(f"  AgentQL query failed (expected on complex pages): {e}")

            # Extract text content for ordinance patterns
            text = page.inner_text("body")
            print(f"  Text content size: {len(text):,} chars")

            # Search for ordinance references
            ord_pattern = r'\(Ord\.?\s*(?:No\.?)?\s*(\d{2,4}[-–]\d+)'
            matches = re.findall(ord_pattern, text)
            print(f"  Ordinance references found: {len(matches)}")
            if matches:
                print(f"    Examples: {matches[:5]}")

            # Look for zoning-related links
            links = page.query_selector_all("a[href*='nodeId']")
            print(f"  Municode section links found: {len(links)}")

            browser.close()

            return {
                "success": True,
                "content_size": len(content),
                "text_size": len(text),
                "ordinance_refs": len(matches),
                "section_links": len(links),
                "method": "agentql+playwright",
            }

    except ImportError:
        print("  Playwright not installed, trying fallback...")
        return test_httpx_fallback()
    except Exception as e:
        print(f"  AgentQL scrape error: {e}")
        return test_httpx_fallback()


def test_playwright_fallback():
    """Fallback: Test with plain Playwright (no AgentQL)."""
    print("\n  --- Playwright Fallback ---")
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            url = PILOT_JURISDICTION["municode_url"]
            print(f"  Navigating to: {url}")
            page.goto(url, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(3000)

            content = page.content()
            text = page.inner_text("body")
            print(f"  Content: {len(content):,} bytes, Text: {len(text):,} chars")

            # Extract ordinance references
            ord_pattern = r'\(Ord\.?\s*(?:No\.?)?\s*(\d{2,4}[-–]\d+)'
            matches = re.findall(ord_pattern, text)
            print(f"  Ordinance references: {len(matches)}")

            browser.close()
            return {
                "success": True,
                "content_size": len(content),
                "text_size": len(text),
                "ordinance_refs": len(matches),
                "method": "playwright",
            }
    except Exception as e:
        print(f"  Playwright fallback failed: {e}")
        return test_httpx_fallback()


def test_httpx_fallback():
    """Final fallback: Test with httpx (no JS rendering)."""
    print("\n  --- HTTPX Fallback (no JS) ---")
    url = PILOT_JURISDICTION["municode_url"]
    try:
        r = httpx.get(url, follow_redirects=True, timeout=30.0)
        print(f"  HTTP status: {r.status_code}")
        print(f"  Content size: {len(r.text):,} chars")
        print(f"  NOTE: Without JS rendering, Municode content will be minimal")
        return {
            "success": True,
            "content_size": len(r.text),
            "method": "httpx",
            "note": "No JS rendering - limited content",
        }
    except Exception as e:
        print(f"  HTTPX fallback failed: {e}")
        return {"success": False, "error": str(e), "method": "httpx"}


def insert_test_data():
    """Step 3: Test inserting data to Supabase allowed_uses table."""
    print("\n=== Step 3: Testing Data Insert to allowed_uses ===")
    headers = get_supabase_headers()

    # First get a Melbourne district ID
    r = httpx.get(
        f"{SUPABASE_URL}/rest/v1/zoning_districts",
        headers=headers,
        params={"select": "id,code", "jurisdiction_id": "eq.1", "limit": "1"},
        timeout=30.0,
    )
    districts = r.json()
    if not districts:
        print("  No Melbourne districts found - skipping insert test")
        return {"success": False, "reason": "no_districts"}

    district_id = districts[0]["id"]
    district_code = districts[0]["code"]
    print(f"  Using district: {district_code} (id={district_id})")

    # Test insert into allowed_uses
    # Valid use_type values: 'by-right', 'conditional', 'prohibited'
    test_use = {
        "zoning_district_id": district_id,
        "use_name": "Single-family residential (pilot test)",
        "use_type": "by-right",
        "conditions": "By-right use, no special approval needed",
        "ordinance_section": "Pilot scrape test - Day 1-2",
    }

    r = httpx.post(
        f"{SUPABASE_URL}/rest/v1/allowed_uses",
        headers=headers,
        json=test_use,
        timeout=30.0,
    )
    print(f"  Insert status: {r.status_code}")
    if r.status_code in (200, 201):
        result = r.json()
        print(f"  Inserted: {json.dumps(result[0] if isinstance(result, list) else result, indent=2)[:300]}")

        # Clean up test data
        if isinstance(result, list) and result:
            test_id = result[0]["id"]
            r2 = httpx.delete(
                f"{SUPABASE_URL}/rest/v1/allowed_uses",
                headers=headers,
                params={"id": f"eq.{test_id}"},
                timeout=30.0,
            )
            print(f"  Cleanup status: {r2.status_code} (removed test record)")

        return {"success": True, "method": "rest_api"}
    else:
        print(f"  Insert failed: {r.text[:200]}")
        return {"success": False, "error": r.text[:200]}


def generate_report(existing_data, scrape_result, insert_result):
    """Step 4: Generate pilot scrape report."""
    print("\n=== Step 4: Generating Report ===")

    report = {
        "pilot_scrape_report": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "jurisdiction": PILOT_JURISDICTION["name"],
            "jurisdiction_id": PILOT_JURISDICTION["id"],
            "existing_data": existing_data,
            "scrape_test": scrape_result,
            "insert_test": insert_result,
            "status": "PASS" if (scrape_result.get("success") and insert_result.get("success")) else "PARTIAL",
            "next_steps": [
                "Deploy zone_standards and permitted_uses migrations via GitHub Actions",
                "Scale scraping to all 17 Brevard jurisdictions",
                "Enable AgentQL Pro for intelligent data extraction",
                "Set up overnight batch processing with Claude API",
            ],
        }
    }

    # Save report
    report_path = Path(__file__).parent.parent / "data" / "pilot_scrape_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"  Report saved to: {report_path}")
    print(f"  Status: {report['pilot_scrape_report']['status']}")

    return report


def main():
    print("=" * 60)
    print("ZoneWise Brevard County Pilot Scrape")
    print(f"Target: {PILOT_JURISDICTION['name']} (ID: {PILOT_JURISDICTION['id']})")
    print(f"Timestamp: {datetime.utcnow().isoformat()}Z")
    print("=" * 60)

    if not SUPABASE_KEY:
        print("ERROR: SUPABASE_KEY not set")
        sys.exit(1)

    # Step 1: Verify existing data
    existing_data = verify_existing_data()

    # Step 2: Test scraping
    scrape_result = test_agentql_scrape()

    # Step 3: Test data insert
    insert_result = insert_test_data()

    # Step 4: Generate report
    report = generate_report(existing_data, scrape_result, insert_result)

    print("\n" + "=" * 60)
    print("PILOT SCRAPE COMPLETE")
    print("=" * 60)

    return report


if __name__ == "__main__":
    main()
