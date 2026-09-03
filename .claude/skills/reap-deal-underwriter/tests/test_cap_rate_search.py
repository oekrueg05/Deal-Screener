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


def test_dense_survey_table_collapses_to_one_candidate_per_row():
    # Mirrors a real CBRE Cap Rate Survey table row: many '%' signs packed
    # within a couple hundred characters, with a neighboring market's own
    # figures sitting close enough to fall inside Milwaukee's naive context
    # window. Before the market-anchored pass this produced ~15 near-
    # duplicate candidates for one row, then still mislabeled Kansas City's
    # own numbers as a Milwaukee match.
    row = (
        "Kansas City 4.25% - 4.5% 4% - 4.5% 4.75% - 5.25% 4.25% - 4.75% "
        "Milwaukee 4.75% - 5.25% 4.5% - 5% 5.5% - 5.75% 4.75% - 5.5% "
        "Minneapolis/St. Paul 4.25% - 4.5% 4% - 4.25% 4.75% - 5% 4.5% - 4.75%"
    )
    candidates = cap_rate_search.find_candidates(row, "Milwaukee", None, page=21)
    assert len(candidates) == 1, f"expected exactly one Milwaukee candidate, got {len(candidates)}"
    assert candidates[0]["mentions_market"] is True
    assert candidates[0]["value_pct"] == 4.75
    assert "Milwaukee 4.75% - 5.25%" in candidates[0]["snippet"]


def test_neighboring_market_not_mislabeled_when_cap_rate_language_present():
    # Same shape as the real CBRE PDF: "cap rate" language sits near the top
    # of the table, close enough to fall in a neighboring city's own context
    # window -- that city's numbers are a legitimate generic-pass candidate,
    # but must NOT be flagged as a Milwaukee match just because "Milwaukee"
    # happens to be within reading distance on the page.
    text = (
        "United States Cap Rate Survey H2 2021 | Report Apartment Stabilized Market "
        "Kansas City 4.25% - 4.5% 4% - 4.5% Milwaukee 4.75% - 5.25% 4.5% - 5%"
    )
    candidates = cap_rate_search.find_candidates(text, "Milwaukee", None, page=21)
    milwaukee_hit = next(c for c in candidates if "4.75% - 5.25%" in c["snippet"] and c["value_pct"] == 4.75)
    assert milwaukee_hit["mentions_market"] is True

    kansas_city_hits = [c for c in candidates if c is not milwaukee_hit]
    assert kansas_city_hits, "expected Kansas City's own figures to still surface as a candidate"
    assert all(c["mentions_market"] is False for c in kansas_city_hits)


def test_rank_and_cap_truncates_and_prioritizes_market_matches():
    candidates = [{"value_pct": float(i), "snippet": "s", "page": 1, "score": 2, "mentions_market": False} for i in range(30)]
    candidates.append({"value_pct": 99.0, "snippet": "milwaukee row", "page": 1, "score": 2, "mentions_market": True})

    kept, truncated, total = cap_rate_search._rank_and_cap(candidates)

    assert total == 31
    assert truncated is True
    assert len(kept) == cap_rate_search.MAX_CANDIDATES
    assert kept[0]["mentions_market"] is True  # market match ranked first despite tied score


def test_main_end_to_end(monkeypatch, capsys):
    html_bytes = load_bytes("cap_rate_page.html")
    monkeypatch.setattr(cap_rate_search, "get_bytes", lambda url: html_bytes)

    cap_rate_search.main(["--url", "https://example.com/milwaukee-report", "--market", "Milwaukee"])
    out = json.loads(capsys.readouterr().out)
    assert out["market"] == "Milwaukee"
    assert out["results"][0]["candidates"][0]["value_pct"] == 5.35
