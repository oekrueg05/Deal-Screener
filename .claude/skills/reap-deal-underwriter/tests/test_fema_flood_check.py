import json
import os

import pytest

import fema_flood_check
from _http import VerificationError

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def load_fixture(name):
    with open(os.path.join(FIXTURES, name)) as f:
        return json.load(f)


def test_geocode_returns_lat_lon(monkeypatch):
    data = load_fixture("census_geocode_locations_sonne.json")
    monkeypatch.setattr(fema_flood_check, "get_json", lambda url, params=None: data)
    lat, lon, matched = fema_flood_check.geocode("7746 Menomonee River Parkway, Wauwatosa, WI")
    assert lat == 43.0642
    assert lon == -88.0201
    assert "MENOMONEE" in matched


def test_geocode_no_match_raises(monkeypatch):
    monkeypatch.setattr(fema_flood_check, "get_json", lambda url, params=None: {"result": {"addressMatches": []}})
    with pytest.raises(VerificationError):
        fema_flood_check.geocode("nonsense address")


def test_query_flood_zone_sfha(monkeypatch):
    data = load_fixture("fema_nfhl_sfha.json")
    monkeypatch.setattr(fema_flood_check, "get_json", lambda url, params=None: data)
    features = fema_flood_check.query_flood_zone(43.0642, -88.0201)
    assert features[0]["attributes"]["SFHA_TF"] == "T"


def test_main_end_to_end_sfha_hit(monkeypatch, capsys):
    geocode_data = load_fixture("census_geocode_locations_sonne.json")
    nfhl_data = load_fixture("fema_nfhl_sfha.json")

    def fake_get_json(url, params=None):
        if "geocoding" in url:
            return geocode_data
        return nfhl_data

    monkeypatch.setattr(fema_flood_check, "get_json", fake_get_json)
    fema_flood_check.main(["--address", "7746 Menomonee River Parkway, Wauwatosa, WI"])
    out = json.loads(capsys.readouterr().out)
    assert out["sfha"] is True
    assert out["flood_zone"] == "AE"
    assert "Special Flood Hazard Area" in out["note"]


def test_main_end_to_end_no_features_explains_ambiguity(monkeypatch, capsys):
    monkeypatch.setattr(fema_flood_check, "get_json", lambda url, params=None: load_fixture("fema_nfhl_no_features.json"))
    fema_flood_check.main(["--lat", "43.0", "--lon", "-88.0"])
    out = json.loads(capsys.readouterr().out)
    assert out["sfha"] is None
    assert "gap in NFHL" in out["note"]


def test_main_requires_address_or_latlon(capsys):
    with pytest.raises(SystemExit) as exc_info:
        fema_flood_check.main([])
    assert exc_info.value.code == 1
