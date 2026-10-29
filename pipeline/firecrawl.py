"""Firecrawl (https://firecrawl.dev): the pipeline's first-choice fetcher for NatCon and essay pages.

NatCon sits behind a Cloudflare bot check that plain requests can't pass; Firecrawl renders the page for us.
Auth: in the Claude cloud environment the network proxy adds the key for api.firecrawl.dev, so no key is
needed in the container. Elsewhere set FIRECRAWL_API_KEY. Free plan: 1,000 credits a month; we stop at
MONTHLY_CAP (count kept in state/firecrawl_usage.json) and fall back to our own fetchers.
"""
import json
import os

import requests

from common import STATE, utcnow

API_URL = "https://api.firecrawl.dev/v2/scrape"
MONTHLY_CAP = 800
USAGE_FILE = STATE / "firecrawl_usage.json"


class FirecrawlError(RuntimeError):
    pass


_refused = False  # Firecrawl turned us away for lack of a key: skip it for the rest of the run


def _usage():
    try:
        return json.loads(USAGE_FILE.read_text())
    except (OSError, ValueError):
        return {}


def used_this_month():
    return _usage().get(utcnow().strftime("%Y-%m"), 0)


def available():
    return not _refused and used_this_month() < MONTHLY_CAP


def _record(credits):
    usage = _usage()
    month = utcnow().strftime("%Y-%m")
    usage[month] = usage.get(month, 0) + credits
    USAGE_FILE.write_text(json.dumps(usage, indent=2) + "\n")


def scrape(url, formats=("markdown",), main_only=True, timeout=120):
    """Firecrawl's data dict ({"markdown", "rawHtml", "metadata", ...}) for one URL."""
    global _refused
    if not available():
        raise FirecrawlError("Firecrawl unavailable (no key, or the monthly cap is reached)")
    key = os.environ.get("FIRECRAWL_API_KEY", "").strip()
    body = {"url": url, "formats": list(formats), "onlyMainContent": main_only, "timeout": timeout * 1000}
    r = requests.post(API_URL, json=body, timeout=timeout + 30,
                      headers={"Authorization": f"Bearer {key}"} if key else {})
    try:
        payload = r.json()
    except ValueError:
        payload = {}
    if r.status_code in (401, 402, 403):
        _refused = True
        raise FirecrawlError(f"Firecrawl refused the request (HTTP {r.status_code})")
    data = payload.get("data") or {}
    _record(int((data.get("metadata") or {}).get("creditsUsed") or 1))
    if not r.ok or not payload.get("success"):
        raise FirecrawlError(f"Firecrawl HTTP {r.status_code}: {str(payload.get('error') or r.text)[:200]}")
    return data
