import json
import os

import cap_rate_search

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def load_bytes(name):
    with open(os.path.join(FIXTURES, name), "rb") as f:
        return f.read()


def test_sniff_kind():
    assert cap_rate_search.sniff_kind(b"%PDF-1.4 rest") == "pdf"
    assert cap_rate_search.sniff_kind(b"<html></html>") == "html"


def test_html_finds_market_and_tier_scoped_cap_rate(monkeypatch):
    html_bytes = load_bytes("cap_rate_page.html")
    monkeypatch.setattr(cap_rate_search, "get_bytes", lambda url: html_bytes)

    result = cap_rate_search.process_url(
        "https://example.com/milwaukee-report", "Milwaukee", "suburban Class A"
    )

    assert result["kind"] == "html"
    assert result["candidates"], "expected at least one scored candidate"
    top = result["candidates"][0]
    assert top["value_pct"] == 5.35
    assert top["mentions_cap_rate_language"] is True
    assert top["mentions_market"] is True
    # the unrelated vacancy figure should not outrank the cap rate figure
    assert all(c["value_pct"] != 4.1 or c["score"] < top["score"] for c in result["candidates"])


def test_pdf_text_extraction_finds_cap_rate(monkeypatch):
    pdf_bytes = load_bytes("cap_rate_text.pdf")
    monkeypatch.setattr(cap_rate_search, "get_bytes", lambda url: pdf_bytes)

    result = cap_rate_search.process_url("https://example.com/report.pdf", "Milwaukee", None)

    assert result["kind"] == "pdf"
    assert result["candidates"]
    assert result["candidates"][0]["value_pct"] == 5.40
    assert result["candidates"][0]["page"] == 1


def test_pdf_chart_only_reports_no_text_match_and_points_at_chart_extract(monkeypatch):
    pdf_bytes = load_bytes("cap_rate_chart_only.pdf")
    monkeypatch.setattr(cap_rate_search, "get_bytes", lambda url: pdf_bytes)

    result = cap_rate_search.process_url("https://example.com/chart-report.pdf", "Milwaukee", None)

    assert result["kind"] == "pdf"
    assert result["candidates"] == []
    assert "pdf_chart_extract.py" in result["note"]


def test_main_end_to_end(monkeypatch, capsys):
    html_bytes = load_bytes("cap_rate_page.html")
    monkeypatch.setattr(cap_rate_search, "get_bytes", lambda url: html_bytes)

    cap_rate_search.main(["--url", "https://example.com/milwaukee-report", "--market", "Milwaukee"])
    out = json.loads(capsys.readouterr().out)
    assert out["market"] == "Milwaukee"
    assert out["results"][0]["candidates"][0]["value_pct"] == 5.35
