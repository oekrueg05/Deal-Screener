#!/usr/bin/env python3
"""
verified_data_cache.py -- local cache of previously-verified claim-check
figures, keyed by (category, market, asset_tier), so a repeat market
(Milwaukee will come up again this semester) doesn't need a fresh
from-scratch search every time a new deal comes in.

No network calls -- pure local JSON store. Cache file defaults to
<this skill dir>/.cache/verified_data.json; override with --cache-file or
$REAP_CACHE_FILE so it can be shared across script invocations/deals.

Usage:
    # after verifying a figure some other way (e.g. cap_rate_search.py):
    python verified_data_cache.py set --category cap_rate --market Milwaukee \\
        --asset-tier "suburban Class A" --value 5.4 \\
        --source "Marcus & Millichap 2025 Multifamily Investment Forecast" \\
        --source-url "https://..." --as-of 2025-06-01

    # on the next deal in the same market, check the cache before searching:
    python verified_data_cache.py get --category cap_rate --market Milwaukee \\
        --asset-tier "suburban Class A" --max-age-days 90

    python verified_data_cache.py list
    python verified_data_cache.py prune --max-age-days 90
"""
import argparse
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _http import emit, fail, now_iso  # noqa: E402

DEFAULT_CACHE_FILE = os.path.join(os.path.dirname(__file__), "..", ".cache", "verified_data.json")
DEFAULT_MAX_AGE_DAYS = 90


def cache_path(args_cache_file):
    return args_cache_file or os.environ.get("REAP_CACHE_FILE") or DEFAULT_CACHE_FILE


def make_key(category, market, asset_tier):
    norm = lambda s: (s or "").strip().lower()  # noqa: E731
    return "|".join([norm(category), norm(market), norm(asset_tier)])


def load(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)


def save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, sort_keys=True)


def age_days(retrieved_at):
    retrieved = dt.datetime.strptime(retrieved_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
    return (dt.datetime.now(dt.timezone.utc) - retrieved).days


def cmd_set(args):
    path = cache_path(args.cache_file)
    data = load(path)
    key = make_key(args.category, args.market, args.asset_tier)
    entry = {
        "category": args.category,
        "market": args.market,
        "asset_tier": args.asset_tier,
        "value": args.value,
        "source": args.source,
        "source_url": args.source_url,
        "as_of": args.as_of,
        "retrieved_at": now_iso(),
    }
    data[key] = entry
    save(path, data)
    emit({"cached": entry, "cache_file": path})


def cmd_get(args):
    path = cache_path(args.cache_file)
    data = load(path)
    key = make_key(args.category, args.market, args.asset_tier)
    entry = data.get(key)
    if entry is None:
        fail(
            "no cached entry for this (category, market, asset_tier)",
            category=args.category, market=args.market, asset_tier=args.asset_tier,
        )
        return
    days_old = age_days(entry["retrieved_at"])
    if days_old > args.max_age_days:
        fail(
            f"cached entry is {days_old} days old, older than --max-age-days {args.max_age_days} "
            "-- re-verify rather than trusting a stale figure",
            stale_entry=entry,
        )
        return
    entry_with_age = dict(entry, age_days=days_old)
    emit(entry_with_age)


def cmd_list(args):
    path = cache_path(args.cache_file)
    data = load(path)
    entries = []
    for entry in data.values():
        if args.category and entry["category"].lower() != args.category.lower():
            continue
        if args.market and entry["market"].lower() != args.market.lower():
            continue
        entries.append(dict(entry, age_days=age_days(entry["retrieved_at"])))
    entries.sort(key=lambda e: e["age_days"])
    emit({"cache_file": path, "count": len(entries), "entries": entries})


def cmd_prune(args):
    path = cache_path(args.cache_file)
    data = load(path)
    kept, removed = {}, []
    for key, entry in data.items():
        if age_days(entry["retrieved_at"]) > args.max_age_days:
            removed.append(entry)
        else:
            kept[key] = entry
    save(path, kept)
    emit({"cache_file": path, "removed_count": len(removed), "removed": removed, "remaining_count": len(kept)})


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--cache-file", default=None, help="Override cache file path (default: skill_dir/.cache/verified_data.json, or $REAP_CACHE_FILE)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_set = sub.add_parser("set", help="Store a verified figure")
    p_set.add_argument("--category", required=True, help='e.g. "cap_rate", "financing_rate", "growth_rate"')
    p_set.add_argument("--market", required=True)
    p_set.add_argument("--asset-tier", default="")
    p_set.add_argument("--value", required=True)
    p_set.add_argument("--source", required=True)
    p_set.add_argument("--source-url", default=None)
    p_set.add_argument("--as-of", required=True, help="Date the source figure itself is as-of, e.g. 2025-06-01")
    p_set.set_defaults(func=cmd_set)

    p_get = sub.add_parser("get", help="Look up a cached figure")
    p_get.add_argument("--category", required=True)
    p_get.add_argument("--market", required=True)
    p_get.add_argument("--asset-tier", default="")
    p_get.add_argument("--max-age-days", type=int, default=DEFAULT_MAX_AGE_DAYS)
    p_get.set_defaults(func=cmd_get)

    p_list = sub.add_parser("list", help="List cached entries")
    p_list.add_argument("--category", default=None)
    p_list.add_argument("--market", default=None)
    p_list.set_defaults(func=cmd_list)

    p_prune = sub.add_parser("prune", help="Remove entries older than --max-age-days")
    p_prune.add_argument("--max-age-days", type=int, default=DEFAULT_MAX_AGE_DAYS)
    p_prune.set_defaults(func=cmd_prune)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
