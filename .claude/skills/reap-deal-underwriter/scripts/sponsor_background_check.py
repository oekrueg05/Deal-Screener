#!/usr/bin/env python3
"""
sponsor_background_check.py -- basic news/litigation scan on a sponsor
entity and its named principals (claim-verification.md category 9), which
the skill previously did not cover for any deal.

Like cap_rate_search.py, this does not search the web itself: use
WebSearch first for e.g. '"<sponsor entity>" lawsuit OR litigation OR SEC
OR bankruptcy' and '"<principal name>" lawsuit OR litigation', then pass
the resulting candidate URLs here. This script fetches each page and flags
snippets where the sponsor/principal name appears near risk-flag language,
so you get ranked candidates to actually read instead of eyeballing search
result summaries.

Usage:
    python sponsor_background_check.py --sponsor "Wangard Partners" \\
        --principal "Stewart Wangard" \\
        --url "https://..." --url "https://..."

Always reports one of two outcomes per source, never a silent third:
"found" (with cited snippet) or "nothing found" (which is a limitation to
disclose, not a clean bill of health) -- see claim-verification.md's
discipline section.
"""
import argparse
import re
import sys

sys.path.insert(0, __import__("os").path.dirname(__file__))
from _http import VerificationError, emit, fail, get_bytes, now_iso  # noqa: E402

RISK_TERMS = (
    "lawsuit", "litigation", "sec ", "complaint", "bankruptcy", "fraud",
    "default", "foreclosure", "indictment", "settlement", "class action",
    "cease and desist", "receivership",
)
CONTEXT_CHARS = 200


def html_to_text(content):
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(content, "html.parser")
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()
    return soup.get_text(separator=" ")


def find_hits(text, names):
    text_lower = text.lower()
    hits = []
    for name in names:
        name_lower = name.lower()
        for m in re.finditer(re.escape(name_lower), text_lower):
            start = max(0, m.start() - CONTEXT_CHARS)
            end = min(len(text), m.end() + CONTEXT_CHARS)
            snippet = " ".join(text[start:end].split())
            snippet_lower = snippet.lower()
            matched_terms = [term.strip() for term in RISK_TERMS if term in snippet_lower]
            if matched_terms:
                hits.append({"name": name, "matched_terms": matched_terms, "snippet": snippet})
    return hits


def process_url(url, names):
    content = get_bytes(url)
    text = content.decode("utf-8", errors="ignore") if content[:4] != b"%PDF" else None
    if text is None:
        from _pdf import page_texts

        text = "\n".join(t for _, t in page_texts(content))
    else:
        text = html_to_text(content)

    hits = find_hits(text, names)
    result = {"url": url, "hits": hits}
    if not hits:
        result["note"] = "no sponsor/principal name found near risk-flag language on this page."
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sponsor", required=True, help="Sponsor entity name")
    parser.add_argument("--principal", action="append", default=[], dest="principals", help="Named principal (repeatable)")
    parser.add_argument("--url", action="append", required=True, dest="urls", help="Candidate source URL (repeatable)")
    args = parser.parse_args(argv)

    names = [args.sponsor] + args.principals
    results = []
    for url in args.urls:
        try:
            results.append(process_url(url, names))
        except VerificationError as exc:
            results.append({"url": url, "error": str(exc)})

    fetch_failures = [r for r in results if "error" in r]
    total_hits = sum(len(r.get("hits", [])) for r in results)

    summary = {
        "sponsor": args.sponsor,
        "principals": args.principals,
        "sources_checked": len(args.urls),
        "sources_failed_to_fetch": len(fetch_failures),
        "flags_found": total_hits,
        "outcome": "found" if total_hits else "nothing_found",
        "retrieved_at": now_iso(),
        "results": results,
    }
    if not total_hits:
        summary["disclosure"] = (
            f"No litigation/regulatory/bankruptcy flags found across {len(args.urls)} source(s) "
            "checked. This is an absence-of-evidence result, not a confirmed clean record -- "
            "note it in Unknowns as 'no adverse findings in sources checked' rather than as a "
            "verified clean background."
        )

    if fetch_failures and len(fetch_failures) == len(results):
        fail("every candidate URL failed to fetch", results=results)
        return

    emit(summary)


if __name__ == "__main__":
    main()
