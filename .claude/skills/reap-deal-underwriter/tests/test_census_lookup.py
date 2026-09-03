import json
import os

import pytest

import census_lookup
from _http import VerificationError
from _geo import parse_city_state

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def load_fixture(name):
    with open(os.path.join(FIXTURES, name)) as f:
        return json.load(f)


def test_parse_city_state():
    assert parse_city_state("Wauwatosa, WI") == ("Wauwatosa", "WI")
    with pytest.raises(ValueError):
        parse_city_state("Wauwatosa")


def test_acs_metric_matches_place_and_returns_value(monkeypatch):
    data = load_fixture("census_acs_population_2023.json")
    monkeypatch.setattr(census_lookup, "get_json", lambda url, params=None: data)
    place_name, value = census_lookup.acs_metric("Wauwatosa", "WI", "population", 2023, None)
    assert place_name == "Wauwatosa city, Wisconsin"
    assert value == 48219.0


def test_acs_metric_no_match_raises(monkeypatch):
    data = load_fixture("census_acs_population_2023.json")
    monkeypatch.setattr(census_lookup, "get_json", lambda url, params=None: data)
    with pytest.raises(VerificationError):
        census_lookup.acs_metric("Nowheresville", "WI", "population", 2023, None)


def test_population_growth_computes_pct_change(monkeypatch):
    current = load_fixture("census_acs_population_2023.json")
    prior = load_fixture("census_acs_population_2018.json")
    calls = {"n": 0}

    def fake_get_json(url, params=None):
        calls["n"] += 1
        return current if calls["n"] == 1 else prior

    monkeypatch.setattr(census_lookup, "get_json", fake_get_json)
    place_name, cur_val, prior_val, pct_change = census_lookup.population_growth(
        "Fitchburg", "WI", 2023, 2018, None
    )
    assert place_name == "Fitchburg city, Wisconsin"
    assert cur_val == 31647.0
    assert prior_val == 29284.0
    assert pct_change == pytest.approx((31647 - 29284) / 29284 * 100)


def test_resolve_county_fips(monkeypatch):
    data = load_fixture("census_geocode_wauwatosa.json")
    monkeypatch.setattr(census_lookup, "get_json", lambda url, params=None: data)
    st_fips, county_fips, county_name = census_lookup.resolve_county_fips("Wauwatosa", "WI")
    assert st_fips == "55"
    assert county_fips == "079"
    assert county_name == "Milwaukee County"


def test_resolve_county_fips_no_match_raises(monkeypatch):
    monkeypatch.setattr(census_lookup, "get_json", lambda url, params=None: {"result": {"addressMatches": []}})
    with pytest.raises(VerificationError):
        census_lookup.resolve_county_fips("Nowhere", "WI")


def test_bls_unemployment_rate_picks_latest_monthly_not_annual(monkeypatch):
    data = load_fixture("bls_milwaukee_county_unemployment.json")
    monkeypatch.setattr(census_lookup, "get_json", lambda url, params=None: data)
    series_id, latest = census_lookup.bls_unemployment_rate("55", "079", None)
    assert series_id == "LAUCN5507900000000003"
    assert latest["period"] == "M07"  # not the M13 annual-average row
    assert latest["value"] == "3.2"


def test_main_unemployment_rate_end_to_end(monkeypatch, capsys):
    geocode = load_fixture("census_geocode_wauwatosa.json")
    bls = load_fixture("bls_milwaukee_county_unemployment.json")
    urls_seen = []

    def fake_get_json(url, params=None):
        urls_seen.append(url)
        if "geocoding.geo.census.gov" in url:
            return geocode
        return bls

    monkeypatch.setattr(census_lookup, "get_json", fake_get_json)
    census_lookup.main(["--geo", "Wauwatosa, WI", "--metric", "unemployment_rate"])
    out = json.loads(capsys.readouterr().out)
    assert out["matched_county"] == "Milwaukee County"
    assert out["value_pct"] == 3.2
    assert out["as_of"] == "July 2026"
    assert len(urls_seen) == 2
