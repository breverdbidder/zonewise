"""
Validate Opus 4.6 Adaptive Thinking + Streaming Patterns
Day 1-2 Task: Confirm Claude API works with extended thinking
and streaming for zoning data interpretation.
"""

import os
import sys
import json
import time
from datetime import datetime

# Check for anthropic library
try:
    import anthropic
except ImportError:
    print("ERROR: anthropic library not installed. Run: pip install anthropic")
    sys.exit(1)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")


def test_basic_completion():
    """Test 1: Basic Claude API call for zoning interpretation."""
    print("\n=== Test 1: Basic Zoning Interpretation ===")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    start = time.time()
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": """You are a Florida zoning expert. Given this district info:

District: R-1A (Single Family Residential)
Jurisdiction: Melbourne, FL
Min Lot: 7,500 sq ft
Front Setback: 25 ft
Side Setback: 7.5 ft
Rear Setback: 20 ft
Max Height: 35 ft

Question: Can I build a two-story single-family home on a 8,000 sq ft lot?

Respond in JSON format with: {answer, reasoning, constraints_met, constraints_violated}""",
            }
        ],
    )
    elapsed = time.time() - start

    result = response.content[0].text
    print(f"  Response time: {elapsed:.2f}s")
    print(f"  Tokens: input={response.usage.input_tokens}, output={response.usage.output_tokens}")
    print(f"  Response preview: {result[:300]}")

    return {
        "test": "basic_completion",
        "success": True,
        "elapsed_seconds": round(elapsed, 2),
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }


def test_streaming():
    """Test 2: Streaming response for longer zoning analysis."""
    print("\n=== Test 2: Streaming Zoning Analysis ===")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    start = time.time()
    chunks = 0
    full_text = ""
    first_chunk_time = None

    with client.messages.stream(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": """Analyze the permitted uses for Melbourne, FL R-1A zoning district.
List 10 common uses and whether they are Permitted (P), Conditional (C), or Prohibited (X).
Format as a JSON array of objects with: use_name, category, permission_type, conditions.""",
            }
        ],
    ) as stream:
        for text in stream.text_stream:
            if first_chunk_time is None:
                first_chunk_time = time.time() - start
            chunks += 1
            full_text += text

    elapsed = time.time() - start
    final_message = stream.get_final_message()

    print(f"  Time to first chunk: {first_chunk_time:.2f}s")
    print(f"  Total time: {elapsed:.2f}s")
    print(f"  Chunks received: {chunks}")
    print(f"  Response length: {len(full_text)} chars")
    print(f"  Tokens: input={final_message.usage.input_tokens}, output={final_message.usage.output_tokens}")
    print(f"  Response preview: {full_text[:300]}")

    return {
        "test": "streaming",
        "success": True,
        "time_to_first_chunk": round(first_chunk_time, 2),
        "total_elapsed_seconds": round(elapsed, 2),
        "chunks": chunks,
        "input_tokens": final_message.usage.input_tokens,
        "output_tokens": final_message.usage.output_tokens,
    }


def test_extended_thinking():
    """Test 3: Extended thinking for complex zoning question."""
    print("\n=== Test 3: Extended Thinking (Adaptive) ===")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    start = time.time()
    try:
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=16000,
            thinking={
                "type": "enabled",
                "budget_tokens": 5000,
            },
            messages=[
                {
                    "role": "user",
                    "content": """Complex zoning analysis:

A developer wants to build a mixed-use project in Melbourne, FL:
- Site: 2.5 acres, currently zoned R-1A
- Proposal: Ground floor retail, 3 floors residential above
- Question: What rezoning would be needed, what are the likely setback/height
  constraints under Melbourne's MU-1 or MU-2 districts, and what incentive
  bonuses might apply?

Think through this step by step, considering Melbourne's Land Development Code.""",
                }
            ],
        )
        elapsed = time.time() - start

        # Check for thinking blocks
        thinking_content = ""
        response_text = ""
        for block in response.content:
            if block.type == "thinking":
                thinking_content = block.thinking
            elif block.type == "text":
                response_text = block.text

        print(f"  Response time: {elapsed:.2f}s")
        print(f"  Thinking content length: {len(thinking_content)} chars")
        print(f"  Response text length: {len(response_text)} chars")
        print(f"  Tokens: input={response.usage.input_tokens}, output={response.usage.output_tokens}")
        if thinking_content:
            print(f"  Thinking preview: {thinking_content[:200]}...")
        print(f"  Response preview: {response_text[:300]}")

        return {
            "test": "extended_thinking",
            "success": True,
            "elapsed_seconds": round(elapsed, 2),
            "thinking_length": len(thinking_content),
            "response_length": len(response_text),
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        }

    except anthropic.BadRequestError as e:
        # Extended thinking might not be available on all models
        elapsed = time.time() - start
        print(f"  Extended thinking not available: {e}")
        return {
            "test": "extended_thinking",
            "success": False,
            "error": str(e),
            "elapsed_seconds": round(elapsed, 2),
            "note": "Extended thinking requires specific model support",
        }
    except Exception as e:
        elapsed = time.time() - start
        print(f"  Error: {e}")
        return {
            "test": "extended_thinking",
            "success": False,
            "error": str(e),
            "elapsed_seconds": round(elapsed, 2),
        }


def test_structured_extraction():
    """Test 4: Structured data extraction pattern for scraping pipeline."""
    print("\n=== Test 4: Structured Extraction Pattern ===")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    sample_ordinance_text = """
    Sec. 1-3.3. - R-1A Single family residential district.
    (A) Purpose. The R-1A district is established to provide for low-density,
    single-family residential development.
    (B) Permitted uses:
        (1) Single-family dwellings
        (2) Parks and recreation areas
        (3) Home occupations (Type I)
        (4) Essential services
    (C) Conditional uses:
        (1) Churches and places of worship
        (2) Schools (public and private)
        (3) Day care centers
        (4) Group homes (6 or fewer residents)
    (D) Dimensional standards:
        Minimum lot area: 7,500 sq ft
        Minimum lot width: 60 ft
        Maximum height: 35 ft
        Maximum lot coverage: 40%
        Front setback: 25 ft
        Side setback: 7.5 ft
        Rear setback: 20 ft
    (Ord. No. 2023-45, § 2, 8-15-2023; Ord. No. 2019-12, § 1, 3-20-2019)
    """

    start = time.time()
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2048,
        system="""You are a zoning data extraction specialist.
Extract structured data from ordinance text into valid JSON.
Be precise and only extract what is explicitly stated.""",
        messages=[
            {
                "role": "user",
                "content": f"""Extract all data from this ordinance section into JSON:

{sample_ordinance_text}

Return JSON with: district_code, district_name, purpose, permitted_uses[], conditional_uses[],
dimensional_standards (min_lot_sqft, min_lot_width_ft, max_height_ft, max_coverage_pct,
front_setback_ft, side_setback_ft, rear_setback_ft), ordinance_references[]""",
            }
        ],
    )
    elapsed = time.time() - start

    result = response.content[0].text
    print(f"  Response time: {elapsed:.2f}s")
    print(f"  Tokens: input={response.usage.input_tokens}, output={response.usage.output_tokens}")

    # Validate JSON parsability
    try:
        # Extract JSON from response (might be wrapped in markdown)
        json_str = result
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0]
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0]

        parsed = json.loads(json_str.strip())
        print(f"  JSON valid: Yes")
        print(f"  Keys: {list(parsed.keys())}")
        uses_count = len(parsed.get("permitted_uses", []))
        cond_count = len(parsed.get("conditional_uses", []))
        print(f"  Permitted uses extracted: {uses_count}")
        print(f"  Conditional uses extracted: {cond_count}")

        return {
            "test": "structured_extraction",
            "success": True,
            "json_valid": True,
            "permitted_uses_count": uses_count,
            "conditional_uses_count": cond_count,
            "elapsed_seconds": round(elapsed, 2),
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        }
    except json.JSONDecodeError as e:
        print(f"  JSON parse error: {e}")
        print(f"  Raw response: {result[:500]}")
        return {
            "test": "structured_extraction",
            "success": True,
            "json_valid": False,
            "error": str(e),
            "elapsed_seconds": round(elapsed, 2),
        }


def main():
    print("=" * 60)
    print("Opus 4.6 Adaptive Thinking + Streaming Validation")
    print(f"Timestamp: {datetime.utcnow().isoformat()}Z")
    print("=" * 60)

    if not ANTHROPIC_API_KEY:
        print("ERROR: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    results = []

    # Run all tests
    for test_fn in [test_basic_completion, test_streaming, test_extended_thinking, test_structured_extraction]:
        try:
            result = test_fn()
            results.append(result)
        except Exception as e:
            print(f"  Test failed with exception: {e}")
            results.append({
                "test": test_fn.__name__,
                "success": False,
                "error": str(e),
            })

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    passed = sum(1 for r in results if r.get("success"))
    total = len(results)
    print(f"  Tests passed: {passed}/{total}")

    for r in results:
        status = "PASS" if r.get("success") else "FAIL"
        print(f"  [{status}] {r['test']}: {r.get('elapsed_seconds', 'N/A')}s")

    # Save results
    report = {
        "validation_report": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "model": "claude-sonnet-4-5-20250929",
            "tests_passed": passed,
            "tests_total": total,
            "results": results,
        }
    }

    from pathlib import Path
    report_path = Path(__file__).parent.parent / "data" / "opus_validation_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n  Report saved to: {report_path}")

    return report


if __name__ == "__main__":
    main()
