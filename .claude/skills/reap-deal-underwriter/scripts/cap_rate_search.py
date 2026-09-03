#!/usr/bin/env python3
"""
cap_rate_search.py -- extract a market/tier-specific cap rate figure out of
one or more candidate source pages (screening-benchmarks.md's cap-rate-
verification step; the same logic also applies to claim-verification.md
category 2, "yield / cap rate").

This script does NOT search the web itself -- the calling assistant already
has a WebSearch tool and should use it first to find candidate report URLs
for the deal's actual named market (see screening-benchmarks.md: search the
market by name before falling back to a proxy, prefer tiered sources over
blended national headlines). Pass those candidate URLs here; this script
fetches each one, extracts text (HTML or PDF), and scores every percentage
figure it finds by whether it's near "cap rate" language and the market/
tier keywords you're looking for -- so you get ranked, sourced candidates
instead of having to eyeball a whole report by hand.

Usage:
    python cap_rate_search.py --url "https://example.com/milwaukee-report" \\
        --market Milwaukee --asset-tier "suburban Class A"

    python cap_rate_search.py --url "https://example.com/report.pdf" \\
        --market Milwaukee --asset-tier "value-add"

If the best a PDF source offers is a chart with no text match, this script
says so explicitly (per screening-benchmarks.md: "a report existing doesn't
mean its number is extractable") and points at pdf_chart_extract.py rather
than silently returning nothing or blending in a proxy number.
"""
import argparse
import re
import sys

sys.path.insert(0, __import__("os").path.dirname(__file__))
from _http import VerificationError, emit, fail, get_bytes, now_iso  # noqa: E402
from _pdf import page_texts  # noqa: E402

PCT_RE = re.compile(r"(\d{1,2}(?:\.\d{1,2})?)\s*%")
CAP_RATE_TERMS = ("cap rate", "capitalization rate", "going-in yield", "exit cap")
CONTEXT_CHARS = 180


def sniff_kind(content):
    return "pdf" if content[:4] == b"%PDF" else "html"


def html_to_text(html_bytes):
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html_bytes, "html.parser")
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()
    return soup.get_text(separator=" ")


def score_match(context_lower, market, asset_tier):
    has_cap_rate = any(term in context_lower for term in CAP_RATE_TERMS)
    has_market = market.lower() in context_lower
    has_tier = bool(asset_tier) and asset_tier.lower() in context_lower
    score = int(has_cap_rate) * 2 + int(has_market) * 2 + int(has_tier)
    return score, has_cap_rate, has_market, has_tier


def find_candidates(text, market, asset_tier, page=None):
    """
    Score every percentage in text by proximity to cap-rate/market/tier
    language. A dense rate-survey table can pack a dozen '%' signs within a
    couple hundred characters (e.g. "Milwaukee 4.75% - 5.25% ... 5.5% - 5.75%
    ..."), and each one's context window would otherwise re-capture the same
    table row -- so matches whose windows overlap a previously *kept* match
    collapse into that one candidate instead of spawning a near-duplicate
    per number.
    """
    candidates = []
    last_kept_end = -CONTEXT_CHARS  # sentinel so the first match is never skipped
    for m in PCT_RE.finditer(text):
        if m.start() - last_kept_end < CONTEXT_CHARS:
            continue  # overlaps the previously kept match's context window
        start = max(0, m.start() - CONTEXT_CHARS)
        end = min(len(text), m.end() + CONTEXT_CHARS)
        snippet = " ".join(text[start:end].split())
        score, has_cap_rate, has_market, has_tier = score_match(snippet.lower(), market, asset_tier)
        if score == 0:
            continue  # a bare percentage with no cap-rate/market/tier context isn't useful
        last_kept_end = m.end()
        candidates.append(
            {
                "value_pct": float(m.group(1)),
                "snippet": snippet,
                "page": page,
                "score": score,
                "mentions_cap_rate_language": has_cap_rate,
                "mentions_market": has_market,
                "mentions_asset_tier": has_tier,
            }
        )
    return candidates


MAX_CANDIDATES = 20


def _rank_and_cap(candidates, max_candidates=MAX_CANDIDATES):
    """Best matches first (market-mentioning ties broken above generic ones); cap the list length
    so a multi-asset-type survey (apartment/office/retail/industrial/hotel tables all in one PDF)
    doesn't dump dozens of candidates the caller has to scroll through by hand."""
    ranked = sorted(candidates, key=lambda c: (-c["score"], -int(c["mentions_market"])))
    truncated = len(ranked) > max_candidates
    return ranked[:max_candidates], truncated, len(ranked)


def process_url(url, market, asset_tier):
    content = get_bytes(url)
    kind = sniff_kind(content)

    if kind == "pdf":
        candidates = []
        for page_num, text in page_texts(content):
            candidates.extend(find_candidates(text, market, asset_tier, page=page_num))
        kept, truncated, total = _rank_and_cap(candidates)
        result = {"url": url, "kind": "pdf", "candidates": kept}
        if not candidates:
            result["note"] = (
                "no percentage in this PDF's extractable text was near cap-rate/market/tier "
                "language. If the report covers this market, the figure may live in a chart "
                "image rather than text -- run pdf_chart_extract.py on this URL and Read() the "
                "extracted images rather than assuming the number isn't there."
            )
        elif truncated:
            result["note"] = (
                f"{total} candidates matched cap-rate/market/tier language; showing the "
                f"top {MAX_CANDIDATES} by relevance (market-mentioning ranked first)."
            )
        return result

    text = html_to_text(content)
    candidates = find_candidates(text, market, asset_tier)
    kept, truncated, total = _rank_and_cap(candidates)
    result = {"url": url, "kind": "html", "candidates": kept}
    if not candidates:
        result["note"] = "no percentage on this page was near cap-rate/market/tier language."
    elif truncated:
        result["note"] = (
            f"{total} candidates matched cap-rate/market/tier language; showing the "
            f"top {MAX_CANDIDATES} by relevance (market-mentioning ranked first)."
        )
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--url", action="append", required=True, dest="urls", help="Candidate source URL (repeatable)")
    parser.add_argument("--market", required=True, help='e.g. "Milwaukee"')
    parser.add_argument("--asset-tier", default=None, help='e.g. "suburban Class A", "value-add"')
    args = parser.parse_args(argv)

    results = []
    for url in args.urls:
        try:
            results.append(process_url(url, args.market, args.asset_tier))
        except VerificationError as exc:
            results.append({"url": url, "error": str(exc)})

    if all("error" in r for r in results):
        fail("every candidate URL failed to fetch", results=results)
        return

    emit(
        {
            "market": args.market,
            "asset_tier": args.asset_tier,
            "retrieved_at": now_iso(),
            "results": results,
        }
    )


if __name__ == "__main__":
    main()
