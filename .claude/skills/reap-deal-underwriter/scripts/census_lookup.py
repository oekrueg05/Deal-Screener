#!/usr/bin/env python3
"""
census_lookup.py -- verify location/market claims (claim-verification.md
category 5) against Census Bureau ACS data and BLS local-area unemployment
data, instead of trusting an OM's narrative demographic claims at face value.

Usage:
    python census_lookup.py --geo "Wauwatosa, WI" --metric median_income
    python census_lookup.py --geo "Fitchburg, WI" --metric population
    python census_lookup.py --geo "Fitchburg, WI" --metric population_growth
    python census_lookup.py --geo "Fitchburg, WI" --metric unemployment_rate

Metrics:
    population           latest ACS 5-year place-level population estimate
    median_income         latest ACS 5-year place-level median household income
    population_growth     % change in place-level population between the
                           latest ACS 5-year estimate and one ~5 years prior
    unemployment_rate      latest BLS LAUS county-level unemployment rate for
                           the county containing --geo (resolved via the
                           Census Geocoder)

ACS calls work without a key at low volume; set CENSUS_API_KEY (free,
https://api.census.gov/data/key_signup.html) to raise the rate limit.
BLS calls work unregistered (v2, limited daily quota); set BLS_API_KEY
(free, https://data.bls.gov/registrationEngine/) to raise it.

NOTE: employment_by_sector is not implemented yet -- ACS industry-by-sector
tables (e.g. S2403) are a reasonable follow-up but weren't needed for either
of the two deals this backlog was scoped against (Juniper, Sonne).
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _geo import parse_city_state, state_fips  # noqa: E402
from _http import VerificationError, emit, fail, get_json, now_iso  # noqa: E402

ACS_URL_TMPL = "https://api.census.gov/data/{year}/acs/acs5"
GEOCODER_URL = "https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress"
BLS_URL_TMPL = "https://api.bls.gov/publicAPI/v2/timeseries/data/{series_id}"

ACS_VARIABLES = {
    "population": "B01003_001E",
    "median_income": "B19013_001E",
}

MONTH_PERIODS = {f"M{i:02d}": i for i in range(1, 13)}


def _acs_place_row(city, state, year, api_key, variable):
    fips = state_fips(state)
    params = {"get": f"NAME,{variable}", "for": "place:*", "in": f"state:{fips}"}
    if api_key:
        params["key"] = api_key
    data = get_json(ACS_URL_TMPL.format(year=year), params=params)

    header, *rows = data
    name_idx = header.index("NAME")
    var_idx = header.index(variable)

    city_lower = city.strip().lower()
    for row in rows:
        place_name = row[name_idx].split(",")[0].strip().lower()
        # Census place names are e.g. "Wauwatosa city" / "Fitchburg city" / "Wauwatosa village"
        if place_name == city_lower or place_name.startswith(city_lower + " "):
            return row[name_idx], row[var_idx]

    raise VerificationError(
        f"no ACS {year} place-level match for '{city}, {state}' "
        f"(searched {len(rows)} places in state FIPS {fips})"
    )


def acs_metric(city, state, metric, year, api_key):
    variable = ACS_VARIABLES[metric]
    place_name, raw_value = _acs_place_row(city, state, year, api_key, variable)
    if raw_value in (None, "null"):
        raise VerificationError(f"ACS {year} returned no value for {metric} in {place_name}")
    return place_name, float(raw_value)


def population_growth(city, state, year, prior_year, api_key):
    place_name, current = acs_metric(city, state, "population", year, api_key)
    _, prior = acs_metric(city, state, "population", prior_year, api_key)
    if prior == 0:
        raise VerificationError(f"ACS {prior_year} population for {place_name} is 0; cannot compute growth")
    pct_change = (current - prior) / prior * 100
    return place_name, current, prior, pct_change


def resolve_county_fips(city, state):
    params = {
        "address": f"{city}, {state}",
        "benchmark": "Public_AR_Current",
        "vintage": "Current_Current",
        "layers": "Counties",
        "format": "json",
    }
    data = get_json(GEOCODER_URL, params=params)
    matches = data.get("result", {}).get("addressMatches") or []
    if not matches:
        raise VerificationError(f"Census Geocoder found no address match for '{city}, {state}'")
    counties = matches[0].get("geographies", {}).get("Counties") or []
    if not counties:
        raise VerificationError(f"Census Geocoder match for '{city}, {state}' has no county geography")
    geoid = counties[0]["GEOID"]
    county_name = counties[0].get("NAME", "")
    return geoid[:2], geoid[2:], county_name


def bls_unemployment_rate(state_fips_code, county_fips_code, api_key):
    series_id = f"LAUCN{state_fips_code}{county_fips_code}{'0' * 9}03"
    params = {"registrationkey": api_key} if api_key else {}
    data = get_json(BLS_URL_TMPL.format(series_id=series_id), params=params)

    if data.get("status") != "REQUEST_SUCCEEDED":
        messages = "; ".join(data.get("message", [])) or data.get("status", "unknown BLS error")
        raise VerificationError(f"BLS API error for series {series_id}: {messages}")

    series_list = data.get("Results", {}).get("series") or []
    if not series_list or not series_list[0].get("data"):
        raise VerificationError(f"BLS returned no data for series {series_id}")

    points = [d for d in series_list[0]["data"] if d.get("period") in MONTH_PERIODS]
    if not points:
        raise VerificationError(f"BLS series {series_id} has no monthly (non-annual) observations")

    latest = max(points, key=lambda d: (int(d["year"]), MONTH_PERIODS[d["period"]]))
    return series_id, latest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--geo", required=True, help='"City, ST", e.g. "Wauwatosa, WI"')
    parser.add_argument(
        "--metric",
        required=True,
        choices=["population", "median_income", "population_growth", "unemployment_rate"],
    )
    parser.add_argument("--year", type=int, default=2023, help="ACS 5-year vintage to query (default 2023)")
    parser.add_argument(
        "--prior-year",
        type=int,
        default=None,
        help="Prior ACS vintage for population_growth (default: --year minus 5)",
    )
    parser.add_argument("--census-api-key", default=os.environ.get("CENSUS_API_KEY"))
    parser.add_argument("--bls-api-key", default=os.environ.get("BLS_API_KEY"))
    args = parser.parse_args(argv)

    try:
        city, state = parse_city_state(args.geo)
    except ValueError as exc:
        fail(str(exc))
        return

    try:
        if args.metric in ("population", "median_income"):
            place_name, value = acs_metric(city, state, args.metric, args.year, args.census_api_key)
            result = {
                "geo": f"{city}, {state}",
                "matched_place": place_name,
                "metric": args.metric,
                "value": value,
                "acs_vintage": f"{args.year} ACS 5-Year Estimates",
                "source": "U.S. Census Bureau ACS",
                "source_url": "https://www.census.gov/programs-surveys/acs",
                "retrieved_at": now_iso(),
            }
        elif args.metric == "population_growth":
            prior_year = args.prior_year or (args.year - 5)
            place_name, current, prior, pct_change = population_growth(
                city, state, args.year, prior_year, args.census_api_key
            )
            result = {
                "geo": f"{city}, {state}",
                "matched_place": place_name,
                "metric": "population_growth",
                "current_population": current,
                "current_vintage": f"{args.year} ACS 5-Year Estimates",
                "prior_population": prior,
                "prior_vintage": f"{prior_year} ACS 5-Year Estimates",
                "pct_change": round(pct_change, 2),
                "source": "U.S. Census Bureau ACS",
                "source_url": "https://www.census.gov/programs-surveys/acs",
                "retrieved_at": now_iso(),
            }
        else:  # unemployment_rate
            st_fips, county_fips_code, county_name = resolve_county_fips(city, state)
            series_id, latest = bls_unemployment_rate(st_fips, county_fips_code, args.bls_api_key)
            result = {
                "geo": f"{city}, {state}",
                "matched_county": county_name,
                "metric": "unemployment_rate",
                "value_pct": float(latest["value"]),
                "as_of": f"{latest['periodName']} {latest['year']}",
                "bls_series_id": series_id,
                "source": "U.S. Bureau of Labor Statistics, Local Area Unemployment Statistics",
                "source_url": f"https://beta.bls.gov/dataViewer/view/timeseries/{series_id}",
                "retrieved_at": now_iso(),
            }
    except VerificationError as exc:
        fail(str(exc), geo=args.geo, metric=args.metric)
        return

    emit(result)


if __name__ == "__main__":
    main()
