"""Daily check of the NatCon Essays page for newly recommended articles.

Usage:
    python pipeline/detect.py                 # fetch the live page, update state, print a report
    python pipeline/detect.py --html FILE     # parse a saved copy instead of fetching

State lives in state/: seen.json (every URL ever listed) and queue.json
(new essays waiting to be translated, oldest first). Exit 0 = ok, 2 = alert (nothing queued).
"""
import argparse
import json
import pathlib
import re
import sys
from urllib.parse import urljoin, urlsplit, urlunsplit, parse_qsl, urlencode

import requests
from bs4 import BeautifulSoup

from common import BROWSER_UA, STATE as STATE_DIR, iso, load_json, save_json, utcnow
import firecrawl

ESSAYS_URL = "https://nationalconservatism.org/essays/"
SITE_HOST = "nationalconservatism.org"
# A run that finds fewer than this share of yesterday's items is treated as a page-layout change.
MIN_ITEM_RATIO = 0.5

TRACKING_PARAMS = re.compile(r"^(utm_|fbclid$|gclid$|mc_|ref$|si$)")


def normalize_url(href, base=ESSAYS_URL):
    """Canonical form used to decide whether an essay has been seen before."""
    href = href.strip()
    # The site sometimes writes off-site links without a scheme, e.g. "youtube.com/watch?...",
    # which browsers resolve to /media/youtube.com/... . Recover the intended host.
    m = re.match(r"^(?:https?://(?:www\.)?nationalconservatism\.org)?/(?:[\w-]+/)*((?:www\.)?[\w-]+\.(?:com|org|net|co\.uk|be|il)/.*)$", href)
    if m and SITE_HOST not in m.group(1):
        href = "https://" + m.group(1)
    elif re.match(r"^(?:www\.)?[\w-]+\.(?:com|org|net)/", href):
        href = "https://" + href
    url = urljoin(base, href)
    parts = urlsplit(url)
    query = urlencode([(k, v) for k, v in parse_qsl(parts.query) if not TRACKING_PARAMS.match(k)])
    host = parts.netloc.lower().removeprefix("www.")
    path = parts.path.rstrip("/") or "/"
    return urlunsplit(("https", host, path, query, ""))


def is_essay_link(url):
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https"):
        return False
    host = parts.netloc.lower().removeprefix("www.")
    if host != SITE_HOST:
        return True
    # Essays NatCon hosts itself (e.g. a WSJ piece) are uploaded PDFs.
    return "/wp-content/uploads/" in parts.path and parts.path.lower().endswith(".pdf")


def _split_label(label):
    """'Rupert Darwall, “America’s Net Zero Near Miss”' -> ('Rupert Darwall', 'America’s Net Zero Near Miss')."""
    m = re.match(r"^(.*?)\s*,\s*[“\"](.+?)[”\"]\s*$", label)
    return (m.group(1).strip(), m.group(2).strip()) if m else ("", label)


def _parse_essay_items(paras):
    """The live page lists each essay as <p class="essay-item"><a>Author, “Title”</a><br><em>Publication</em>, Date</p>."""
    items, seen = [], set()
    for p in paras:
        a = p.find("a", href=True)
        if not a:
            continue
        url = normalize_url(a["href"])
        if not is_essay_link(url) or url in seen:
            continue
        label = " ".join(a.get_text(" ", strip=True).split())
        author, title = _split_label(label)
        em = p.find("em")
        publication = " ".join(em.get_text(" ", strip=True).split()) if em else ""
        context = " ".join(p.get_text(" ", strip=True).split())
        tail = context.split(publication, 1)[-1] if publication else ""
        date = re.sub(r",\s*(\d{4})$", r", \1", tail.strip().lstrip(",").strip())
        seen.add(url)
        items.append({"url": url, "title": title, "author": author, "publication": publication,
                      "date": date, "context": context[:300]})
    return items


def parse_essays(html):
    """Return [{url, title, context, ...}] in page order, one entry per essay link."""
    soup = BeautifulSoup(html, "html.parser")
    paras = soup.select("p.essay-item")
    if paras:
        return _parse_essay_items(paras)
    # Fallback for a changed layout: every off-site link in the main content.
    for tag in soup.select("header, footer, nav, script, style, form, aside"):
        tag.decompose()
    root = soup.select_one("main") or soup.select_one("article") or soup.select_one(".entry-content") or soup.body or soup
    items, seen = [], set()
    for a in root.find_all("a", href=True):
        raw = a["href"]
        if raw.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        url = normalize_url(raw)
        if not is_essay_link(url) or url in seen:
            continue
        title = " ".join(a.get_text(" ", strip=True).split())
        if len(title) < 3 or title.lower() in {"read more", "link", "pdf", "here"}:
            continue
        block = a.find_parent(["li", "article", "p", "div", "tr"]) or a.parent
        context = " ".join(block.get_text(" ", strip=True).split())[:300]
        seen.add(url)
        items.append({"url": url, "title": title, "context": context})
    return items


def run(html, state_dir=STATE_DIR, now=None):
    now = now or iso(utcnow())
    seen = load_json(state_dir / "seen.json", None)
    queue = load_json(state_dir / "queue.json", [])
    meta = load_json(state_dir / "meta.json", {})
    items = parse_essays(html)

    report = {"checked_at": now, "items_on_page": len(items), "new": [], "status": "ok"}
    last_count = meta.get("last_item_count")
    if not items or (last_count and len(items) < last_count * MIN_ITEM_RATIO):
        report["status"] = "layout_alert"
        report["message"] = f"Found {len(items)} essays, previously {last_count}. The page layout may have changed; nothing was queued."
        return report

    if seen is None:
        seen = {it["url"]: {"title": it["title"], "first_seen": now, "status": "baseline"} for it in items}
        report["status"] = "baseline"
        report["message"] = f"First run: recorded {len(items)} existing essays as already seen."
    else:
        for it in items:
            if it["url"] in seen:
                continue
            seen[it["url"]] = {"title": it["title"], "first_seen": now, "status": "queued"}
            queue.append({**it, "first_seen": now, "status": "queued"})
            report["new"].append(it)

    meta["last_item_count"] = len(items)
    meta["last_checked_at"] = now
    save_json(state_dir / "seen.json", seen)
    save_json(state_dir / "queue.json", queue)
    save_json(state_dir / "meta.json", meta)
    report["queue_length"] = sum(1 for q in queue if q["status"] == "queued")
    return report


def fetch(url=ESSAYS_URL):
    """Firecrawl first (it passes NatCon's Cloudflare check), then a plain request, then headless Chromium."""
    errors = []
    try:
        html = firecrawl.scrape(url, formats=("rawHtml",), main_only=False).get("rawHtml") or ""
        if "essay-item" in html or len(html) > 20000:
            return html
        errors.append(f"firecrawl: thin page ({len(html)} bytes)")
    except Exception as e:
        errors.append(f"firecrawl: {e}")
    try:
        r = requests.get(url, headers={"User-Agent": BROWSER_UA}, timeout=60)
        if r.ok and "Just a moment" not in r.text[:2000]:
            return r.text
        errors.append(f"requests: HTTP {r.status_code}")
    except requests.RequestException as e:
        errors.append(f"requests: {e}")
    try:
        return fetch_browser(url)
    except Exception as e:
        errors.append(f"browser: {e}")
    raise RuntimeError("Could not fetch the Essays page. " + "; ".join(errors))


def fetch_browser(url):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        exe = pathlib.Path("/opt/pw-browsers/chromium")
        kw = {"executable_path": str(exe)} if exe.is_file() else {}
        browser = pw.chromium.launch(args=["--disable-blink-features=AutomationControlled"], **kw)
        page = browser.new_page(user_agent=BROWSER_UA)
        page.goto(url, wait_until="domcontentloaded", timeout=90000)
        for _ in range(30):
            if "Just a moment" not in page.title():
                break
            page.wait_for_timeout(1500)
        html = page.content()
        browser.close()
    if "Just a moment" in html[:3000]:
        raise RuntimeError("Blocked by the site's bot check (Cloudflare challenge did not clear).")
    return html


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", help="parse this saved HTML file instead of fetching")
    ap.add_argument("--state-dir", default=str(STATE_DIR))
    args = ap.parse_args(argv)
    try:
        html = pathlib.Path(args.html).read_text(encoding="utf-8") if args.html else fetch()
    except RuntimeError as e:
        print(json.dumps({"status": "fetch_failed", "message": str(e)}, ensure_ascii=False, indent=2))
        return 2
    report = run(html, pathlib.Path(args.state_dir))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] in ("ok", "baseline") else 2


if __name__ == "__main__":
    sys.exit(main())
