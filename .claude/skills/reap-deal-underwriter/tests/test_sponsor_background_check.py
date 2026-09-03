import json
import os

import sponsor_background_check as sbc

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def load_bytes(name):
    with open(os.path.join(FIXTURES, name), "rb") as f:
        return f.read()


def test_find_hits_flags_name_near_risk_term():
    text = "A lawsuit was filed against JJH3 Group alleging breach of contract."
    hits = sbc.find_hits(text, ["JJH3 Group"])
    assert len(hits) == 1
    assert "lawsuit" in hits[0]["matched_terms"]


def test_find_hits_no_match_returns_empty():
    text = "Wangard Partners announced a new groundbreaking today."
    hits = sbc.find_hits(text, ["Wangard Partners"])
    assert hits == []


def test_process_url_clean_page_reports_no_hits(monkeypatch):
    monkeypatch.setattr(sbc, "get_bytes", lambda url: load_bytes("sponsor_clean_page.html"))
    result = sbc.process_url("https://example.com/news", ["Wangard Partners"])
    assert result["hits"] == []
    assert "no sponsor" in result["note"]


def test_process_url_litigation_page_flags_hit(monkeypatch):
    monkeypatch.setattr(sbc, "get_bytes", lambda url: load_bytes("sponsor_litigation_page.html"))
    result = sbc.process_url("https://example.com/legal-roundup", ["JJH3 Group"])
    assert len(result["hits"]) == 1
    assert "lawsuit" in result["hits"][0]["matched_terms"]


def test_main_nothing_found_discloses_absence_of_evidence(monkeypatch, capsys):
    monkeypatch.setattr(sbc, "get_bytes", lambda url: load_bytes("sponsor_clean_page.html"))
    sbc.main(["--sponsor", "Wangard Partners", "--url", "https://example.com/news"])
    out = json.loads(capsys.readouterr().out)
    assert out["outcome"] == "nothing_found"
    assert "absence-of-evidence" in out["disclosure"]


def test_main_found_sets_outcome_found(monkeypatch, capsys):
    monkeypatch.setattr(sbc, "get_bytes", lambda url: load_bytes("sponsor_litigation_page.html"))
    sbc.main(["--sponsor", "JJH3 Group", "--url", "https://example.com/legal-roundup"])
    out = json.loads(capsys.readouterr().out)
    assert out["outcome"] == "found"
    assert out["flags_found"] == 1
    assert "disclosure" not in out
