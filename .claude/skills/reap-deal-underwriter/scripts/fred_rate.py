#!/usr/bin/env python3
"""
fred_rate.py -- verify a financing-rate/index claim (claim-verification.md
category 1) against FRED (Federal Reserve Economic Data), a primary source,
instead of a news article's restated figure.

Usage:
    python fred_rate.py --series DGS7
    python fred_rate.py --series SOFR --spread-bps 140

Requires a free FRED API key (instant signup, no cost:
https://fred.stlouisfed.org/docs/api/api_key.html), passed via --api-key or
the FRED_API_KEY environment variable.

Common series for CRE financing claims:
    DGS7    7-Year Treasury Constant Maturity Rate
    DGS10   10-Year Treasury Constant Maturity Rate
    DGS5    5-Year Treasury Constant Maturity Rate
    SOFR    Secured Overnight Financing Rate (daily)
Any other FRED series ID also works -- https://fred.stlouisfed.org/tags/series
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _http import VerificationError, emit, fail, get_json, now_iso  # noqa: E402

FRED_OBSERVATIONS_URL = "https://api.stlouisfed.org/fred/series/observations"

KNOWN_SERIES = {
    "DGS7": "7-Year Treasury Constant Maturity Rate",
    "DGS10": "10-Year Treasury Constant Maturity Rate",
    "DGS5": "5-Year Treasury Constant Maturity Rate",
    "SOFR": "Secured Overnight Financing Rate",
}


def latest_observation(series_id, api_key):
    """Return the most recent *published* observation for a FRED series.

    FRED sometimes reports the newest date(s) as '.' (not yet published) --
    pull a small window and skip those rather than trusting the first row.
    """
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "sort_order": "desc",
        "limit": 5,
    }
    data = get_json(FRED_OBSERVATIONS_URL, params=params)

    if "error_message" in data:
        raise VerificationError(f"FRED API error for series '{series_id}': {data['error_message']}")

    observations = data.get("observations") or []
    for obs in observations:
        if obs.get("value") not in (None, ".", ""):
            return obs

    raise VerificationError(f"FRED returned no published observations for series '{series_id}'")


def build_result(series_id, obs, spread_bps=None):
    value = float(obs["value"])
    result = {
        "series": series_id,
        "series_label": KNOWN_SERIES.get(series_id, series_id),
        "value_pct": value,
        "as_of": obs["date"],
        "retrieved_at": now_iso(),
        "source": "FRED (Federal Reserve Bank of St. Louis)",
        "source_url": f"https://fred.stlouisfed.org/series/{series_id}",
    }
    if spread_bps is not None:
        result["spread_bps"] = spread_bps
        result["all_in_rate_pct"] = round(value + spread_bps / 100.0, 4)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--series", required=True, help="FRED series ID, e.g. DGS7, DGS10, SOFR")
    parser.add_argument(
        "--spread-bps",
        type=float,
        default=None,
        help="Optional spread in basis points to add to the index, e.g. an OM's '7Y Treasury + 140 bps' -> --spread-bps 140",
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("FRED_API_KEY"),
        help="FRED API key; defaults to $FRED_API_KEY",
    )
    args = parser.parse_args(argv)

    if not args.api_key:
        fail(
            "no FRED API key configured",
            fix="sign up for a free key at https://fred.stlouisfed.org/docs/api/api_key.html "
            "and pass it via --api-key or the FRED_API_KEY env var",
        )
        return

    try:
        obs = latest_observation(args.series, args.api_key)
    except VerificationError as exc:
        fail(str(exc), series=args.series)
        return

    emit(build_result(args.series, obs, args.spread_bps))


if __name__ == "__main__":
    main()
