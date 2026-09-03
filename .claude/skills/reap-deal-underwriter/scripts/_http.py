"""
Shared HTTP + output helpers for the reap-deal-underwriter verification scripts.

Every script in this directory follows the same contract (see CLAUDE.md):
  1. Take clear CLI args.
  2. Hit a real public API or a well-defined fetch target.
  3. Print structured JSON to stdout on success (figure, source, as-of date).
  4. Fail loudly and specifically on stderr + a non-zero exit code when it
     can't find something -- never print a silent empty/placeholder result.
"""
import datetime as dt
import json
import sys

import requests

DEFAULT_TIMEOUT = 15
USER_AGENT = "reap-deal-underwriter-skill/1.0 (Marquette REAP; educational use)"


class VerificationError(Exception):
    """Raised when a script cannot produce a verified, sourced figure."""


def _headers(extra=None):
    headers = {"User-Agent": USER_AGENT}
    if extra:
        headers.update(extra)
    return headers


def get_json(url, params=None, headers=None, timeout=DEFAULT_TIMEOUT):
    resp = _get(url, params=params, headers=headers, timeout=timeout)
    try:
        return resp.json()
    except ValueError as exc:
        raise VerificationError(
            f"{url} did not return valid JSON (got: {resp.text[:300]!r})"
        ) from exc


def get_text(url, params=None, headers=None, timeout=DEFAULT_TIMEOUT):
    resp = _get(url, params=params, headers=headers, timeout=timeout)
    return resp.text


def get_bytes(url, params=None, headers=None, timeout=30):
    resp = _get(url, params=params, headers=headers, timeout=timeout)
    return resp.content


def _get(url, params=None, headers=None, timeout=DEFAULT_TIMEOUT):
    try:
        resp = requests.get(url, params=params, headers=_headers(headers), timeout=timeout)
    except requests.RequestException as exc:
        raise VerificationError(f"request to {url} failed: {exc}") from exc
    if resp.status_code != 200:
        raise VerificationError(
            f"{url} returned HTTP {resp.status_code}: {resp.text[:300]!r}"
        )
    return resp


def now_iso():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def emit(result):
    """Print a successful, structured result to stdout as JSON."""
    print(json.dumps(result, indent=2, default=str))


def fail(message, **extra):
    """Fail loudly: structured error to stderr, exit 1. Never return a fake result."""
    payload = {"error": message}
    payload.update(extra)
    print(json.dumps(payload, indent=2, default=str), file=sys.stderr)
    sys.exit(1)
