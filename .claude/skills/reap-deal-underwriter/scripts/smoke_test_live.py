#!/usr/bin/env python3
"""
smoke_test_live.py -- exercise every claim-verification script against real
public sources, not fixtures. Intended to run from an environment with real
outbound internet (e.g. the GitHub Actions workflow in
.github/workflows/scripts-smoke-test.yml), NOT from inside a sandboxed
Claude Code session whose egress is restricted to an allowlist -- running
this there just reports every check broken regardless of whether anything
actually is, since the sandbox itself blocks the calls.

Distinguishes "the script crashed or a source is unreachable" (a real
failure -- APIs and URLs drift, as FEMA's REST host path did mid-semester)
from "the script ran cleanly and legitimately found nothing" (not a
failure -- see e.g. cap_rate_search.py's designed behavior when a source
has no cap rate data). Exits non-zero only on the former, so a scheduled
CI run stays a meaningful signal instead of a monthly false alarm.

Requires FRED_API_KEY and CENSUS_API_KEY in the environment (get free keys:
https://fred.stlouisfed.org/docs/api/api_key.html,
https://api.census.gov/data/key_signup.html). BLS_API_KEY is optional.

Usage:
    python smoke_test_live.py
"""
import json
import os
import subprocess
import sys

SCRIPTS_DIR = os.path.dirname(__file__)

# A stable, publicly reachable multi-market cap rate PDF -- not a Milwaukee-
# or Dallas-specific choice, just a known-good fixture for exercising the
# fetch/extract/render pipeline live.
CBRE_CAP_RATE_PDF = (
    "https://www.cbre-ea.com/docs/default-source/default-document-library/"
    "cbre-u-s-cap-rate-survey-h2-2021-(1).pdf?sfvrsn=2"
)
STABLE_ADDRESS = "1600 Pennsylvania Avenue NW, Washington, DC"
STABLE_GEO = "Milwaukee, WI"
STABLE_SPONSOR_URL = "https://en.wikipedia.org/wiki/CBRE_Group"


def run(*args, timeout=60):
    proc = subprocess.run(
        [sys.executable, *args],
        cwd=SCRIPTS_DIR,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return proc.returncode, proc.stdout, proc.stderr


def check(name, fn):
    try:
        ok, detail = fn()
    except Exception as exc:  # noqa: BLE001 - a check crashing is itself a failure to report
        ok, detail = False, f"raised {type(exc).__name__}: {exc}"
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name}: {detail}")
    return ok


def check_fred():
    if not os.environ.get("FRED_API_KEY"):
        return False, "FRED_API_KEY not set"
    code, out, err = run("fred_rate.py", "--series", "DGS7")
    if code != 0:
        return False, f"exit {code}: {err.strip()[:200]}"
    data = json.loads(out)
    return True, f"DGS7 = {data['value_pct']}% as of {data['as_of']}"


def check_census():
    if not os.environ.get("CENSUS_API_KEY"):
        return False, "CENSUS_API_KEY not set"
    code, out, err = run("census_lookup.py", "--geo", STABLE_GEO, "--metric", "population")
    if code != 0:
        return False, f"exit {code}: {err.strip()[:200]}"
    data = json.loads(out)
    return True, f"{data['matched_place']} population = {data['value']:.0f}"


def check_fema():
    code, out, err = run("fema_flood_check.py", "--address", STABLE_ADDRESS)
    if code != 0:
        return False, f"exit {code}: {err.strip()[:200]}"
    data = json.loads(out)
    return True, f"flood_zone = {data.get('flood_zone')}, sfha = {data.get('sfha')}"


def check_cache():
    code, out, err = run(
        "verified_data_cache.py",
        "--cache-file", "/tmp/smoke_test_cache.json",
        "set", "--category", "smoke_test", "--market", "Test", "--value", "1",
        "--source", "smoke_test_live.py", "--as-of", "2026-01-01",
    )
    if code != 0:
        return False, f"set failed, exit {code}: {err.strip()[:200]}"
    code, out, err = run(
        "verified_data_cache.py",
        "--cache-file", "/tmp/smoke_test_cache.json",
        "get", "--category", "smoke_test", "--market", "Test",
    )
    if code != 0:
        return False, f"get failed, exit {code}: {err.strip()[:200]}"
    return True, "set/get round-trip ok"


def check_cap_rate_search():
    code, out, err = run(
        "cap_rate_search.py", "--url", CBRE_CAP_RATE_PDF, "--market", "Milwaukee",
        timeout=90,
    )
    if code != 0:
        return False, f"exit {code}: {err.strip()[:200]}"
    data = json.loads(out)
    result = data["results"][0]
    if "error" in result:
        return False, f"fetch error: {result['error'][:200]}"
    return True, f"{len(result['candidates'])} candidates returned (kind={result['kind']})"


def check_pdf_chart_extract():
    code, out, err = run(
        "pdf_chart_extract.py", "--url", CBRE_CAP_RATE_PDF, "--out-dir", "/tmp/smoke_test_charts",
        timeout=90,
    )
    if code != 0:
        return False, f"exit {code}: {err.strip()[:200]}"
    data = json.loads(out)
    return True, f"{data['page_count']} pages, {len(data['embedded_images_extracted'])} images extracted"


def check_sponsor_background_check():
    code, out, err = run(
        "sponsor_background_check.py", "--sponsor", "CBRE", "--url", STABLE_SPONSOR_URL,
    )
    if code != 0:
        return False, f"exit {code}: {err.strip()[:200]}"
    data = json.loads(out)
    return True, f"outcome={data['outcome']}, sources_failed_to_fetch={data['sources_failed_to_fetch']}"


def main():
    checks = [
        ("fred_rate.py", check_fred),
        ("census_lookup.py", check_census),
        ("fema_flood_check.py", check_fema),
        ("verified_data_cache.py", check_cache),
        ("cap_rate_search.py", check_cap_rate_search),
        ("pdf_chart_extract.py", check_pdf_chart_extract),
        ("sponsor_background_check.py", check_sponsor_background_check),
    ]
    results = [check(name, fn) for name, fn in checks]
    failed = results.count(False)
    print(f"\n{len(results) - failed}/{len(results)} checks passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
