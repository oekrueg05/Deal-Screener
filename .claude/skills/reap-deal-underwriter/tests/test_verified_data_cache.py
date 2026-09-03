import json
import os

import pytest

import verified_data_cache as vdc


def cache_file(tmp_path):
    return str(tmp_path / "cache.json")


def test_make_key_normalizes():
    assert vdc.make_key("Cap_Rate", "Milwaukee", "Suburban Class A") == vdc.make_key(
        "cap_rate", " milwaukee ", "SUBURBAN CLASS A"
    )


def test_set_then_get_round_trip(tmp_path, capsys):
    cf = cache_file(tmp_path)
    vdc.main(
        [
            "--cache-file", cf, "set",
            "--category", "cap_rate", "--market", "Milwaukee", "--asset-tier", "suburban Class A",
            "--value", "5.4", "--source", "Marcus & Millichap 2025 Forecast",
            "--source-url", "https://example.com/report.pdf", "--as-of", "2025-06-01",
        ]
    )
    capsys.readouterr()  # discard set output

    vdc.main(
        [
            "--cache-file", cf, "get",
            "--category", "cap_rate", "--market", "Milwaukee", "--asset-tier", "suburban Class A",
        ]
    )
    out = json.loads(capsys.readouterr().out)
    assert out["value"] == "5.4"
    assert out["source"] == "Marcus & Millichap 2025 Forecast"
    assert out["age_days"] == 0


def test_get_miss_fails_loudly(tmp_path, capsys):
    cf = cache_file(tmp_path)
    with pytest.raises(SystemExit) as exc_info:
        vdc.main(["--cache-file", cf, "get", "--category", "cap_rate", "--market", "Nowhere"])
    assert exc_info.value.code == 1
    err = json.loads(capsys.readouterr().err)
    assert "no cached entry" in err["error"]


def test_get_stale_entry_fails_loudly(tmp_path, capsys, monkeypatch):
    cf = cache_file(tmp_path)
    vdc.main(
        [
            "--cache-file", cf, "set",
            "--category", "cap_rate", "--market", "Milwaukee", "--asset-tier", "",
            "--value", "5.4", "--source", "src", "--as-of", "2025-06-01",
        ]
    )
    capsys.readouterr()

    # backdate retrieved_at so the entry is stale
    data = vdc.load(cf)
    key = vdc.make_key("cap_rate", "Milwaukee", "")
    data[key]["retrieved_at"] = "2000-01-01T00:00:00Z"
    vdc.save(cf, data)

    with pytest.raises(SystemExit) as exc_info:
        vdc.main(["--cache-file", cf, "get", "--category", "cap_rate", "--market", "Milwaukee", "--max-age-days", "90"])
    assert exc_info.value.code == 1
    err = json.loads(capsys.readouterr().err)
    assert "stale" in err["error"] or "older than" in err["error"]


def test_list_filters_by_category_and_market(tmp_path, capsys):
    cf = cache_file(tmp_path)
    vdc.main(["--cache-file", cf, "set", "--category", "cap_rate", "--market", "Milwaukee",
              "--value", "5.4", "--source", "s", "--as-of", "2025-06-01"])
    capsys.readouterr()
    vdc.main(["--cache-file", cf, "set", "--category", "cap_rate", "--market", "Madison",
              "--value", "5.1", "--source", "s", "--as-of", "2025-06-01"])
    capsys.readouterr()
    vdc.main(["--cache-file", cf, "set", "--category", "financing_rate", "--market", "Milwaukee",
              "--value", "4.1", "--source", "s", "--as-of", "2025-06-01"])
    capsys.readouterr()

    vdc.main(["--cache-file", cf, "list", "--category", "cap_rate"])
    out = json.loads(capsys.readouterr().out)
    assert out["count"] == 2
    assert {e["market"] for e in out["entries"]} == {"Milwaukee", "Madison"}


def test_prune_removes_stale_entries(tmp_path, capsys):
    cf = cache_file(tmp_path)
    vdc.main(["--cache-file", cf, "set", "--category", "cap_rate", "--market", "Milwaukee",
              "--value", "5.4", "--source", "s", "--as-of", "2025-06-01"])
    capsys.readouterr()

    data = vdc.load(cf)
    key = vdc.make_key("cap_rate", "Milwaukee", "")
    data[key]["retrieved_at"] = "2000-01-01T00:00:00Z"
    vdc.save(cf, data)

    vdc.main(["--cache-file", cf, "prune", "--max-age-days", "90"])
    out = json.loads(capsys.readouterr().out)
    assert out["removed_count"] == 1
    assert out["remaining_count"] == 0
