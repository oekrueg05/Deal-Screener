import json
import os

import pytest

import fred_rate
from _http import VerificationError

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def load_fixture(name):
    with open(os.path.join(FIXTURES, name)) as f:
        return json.load(f)


def test_latest_observation_skips_unpublished_dot_value(monkeypatch):
    data = load_fixture("fred_dgs7.json")
    monkeypatch.setattr(fred_rate, "get_json", lambda url, params=None: data)
    obs = fred_rate.latest_observation("DGS7", "fake-key")
    assert obs["date"] == "2026-09-01"
    assert obs["value"] == "4.12"


def test_latest_observation_raises_when_all_unpublished(monkeypatch):
    data = {"observations": [{"date": "2026-09-02", "value": "."}]}
    monkeypatch.setattr(fred_rate, "get_json", lambda url, params=None: data)
    with pytest.raises(VerificationError):
        fred_rate.latest_observation("DGS7", "fake-key")


def test_build_result_applies_spread():
    obs = {"date": "2026-09-01", "value": "4.12"}
    result = fred_rate.build_result("DGS7", obs, spread_bps=140)
    assert result["value_pct"] == 4.12
    assert result["all_in_rate_pct"] == pytest.approx(5.52)
    assert result["source_url"] == "https://fred.stlouisfed.org/series/DGS7"


def test_main_fails_loudly_without_api_key(monkeypatch, capsys):
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    with pytest.raises(SystemExit) as exc_info:
        fred_rate.main(["--series", "DGS7"])
    assert exc_info.value.code == 1
    err = json.loads(capsys.readouterr().err)
    assert "FRED_API_KEY" in err["fix"]


def test_main_end_to_end(monkeypatch, capsys):
    data = load_fixture("fred_dgs7.json")
    monkeypatch.setattr(fred_rate, "get_json", lambda url, params=None: data)
    fred_rate.main(["--series", "DGS7", "--api-key", "fake-key", "--spread-bps", "140"])
    out = json.loads(capsys.readouterr().out)
    assert out["value_pct"] == 4.12
    assert out["all_in_rate_pct"] == pytest.approx(5.52)
    assert out["as_of"] == "2026-09-01"
