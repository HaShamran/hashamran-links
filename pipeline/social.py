"""Runs every 15 minutes in GitHub Actions: notices posts that went live on Substack, writes their relay
pages, sends tweets at the day's slots, and raises alerts. No Claude, no browser.

Usage:
    python pipeline/social.py              # live run (tweets need BUFFER_API_KEY; without it, a dry run)
    python pipeline/social.py --dry-run    # decide and print, send nothing

Tweet rules (Hadar, 2026-10-27/28): 3 a day around 11:00, 16:00 and 21:00 Israel time; only posts live less
than 48 hours, today's first; at most 3 tweets per post, never the same quote twice; 45 minutes apart.
"""
import argparse
import datetime as dt
import html
import json
import os
import re
import sys

import requests

import tweets
from common import (BROWSER_UA, ISRAEL, PAGES_URL, POSTS, PUBLICATION_URL, ROOT, STATE, iso, israel_date, load_json,
                    parse_iso, save_json, utcnow)

SLOTS = [(11, 0), (16, 0), (21, 0)]
SLOT_WINDOW = dt.timedelta(minutes=90)
MIN_GAP = dt.timedelta(minutes=45)
TWEET_WINDOW = dt.timedelta(hours=48)
MAX_PER_POST = 3
MAX_PER_DAY = 3
PUBLISH_OVERDUE = dt.timedelta(hours=26)


def norm(title):
    return re.sub(r"\s+", " ", title or "").strip()


def load_posts():
    posts = {}
    for f in sorted(POSTS.glob("*/post.json")):
        p = load_json(f)
        posts[p["slug"]] = p
    return posts


def substack_archive(limit=50):
    """Recent posts as [{title, slug, post_date, canonical_url, cover_image}]. Substack's JSON archive refuses
    some cloud IPs (GitHub Actions gets 403), so the RSS feed is the fallback. None when both fail."""
    headers = {"User-Agent": BROWSER_UA, "Accept-Language": "he,en;q=0.8"}
    try:
        r = requests.get(f"{PUBLICATION_URL}/api/v1/archive", params={"sort": "new", "limit": limit},
                         headers=headers, timeout=60)
        if r.ok:
            return r.json()
    except requests.RequestException:
        pass
    try:
        r = requests.get(f"{PUBLICATION_URL}/feed", headers=headers, timeout=60)
        if r.ok and "<rss" in r.text[:500]:
            return parse_feed(r.text)
    except requests.RequestException:
        pass
    return None


def parse_feed(xml):
    import email.utils
    import xml.etree.ElementTree as ET
    out = []
    for item in ET.fromstring(xml).iter("item"):
        link = (item.findtext("link") or "").strip()
        enc = item.find("enclosure")
        date = email.utils.parsedate_to_datetime(item.findtext("pubDate"))
        out.append({"title": item.findtext("title") or "", "slug": link.rstrip("/").rsplit("/", 1)[-1],
                    "post_date": iso(date), "canonical_url": link,
                    "cover_image": enc.get("url") if enc is not None else ""})
    return out


def match_live(posts, archive, live):
    """Record posts that now appear on Substack (matched by Hebrew title). Returns newly live slugs."""
    by_title = {norm(a["title"]): a for a in archive}
    new = []
    for slug, p in posts.items():
        if slug in live or p.get("status") not in ("ready", "published"):
            continue
        a = by_title.get(norm(p["title_he"]))
        if not a:
            continue
        live[slug] = {"url": a.get("canonical_url") or f"{PUBLICATION_URL}/p/{a['slug']}",
                      "live_at": iso(parse_iso(a["post_date"])),
                      "cover": a.get("cover_image") or p.get("cover_image") or ""}
        new.append(slug)
    return new


def relay_url(slug):
    return f"{PAGES_URL}/{slug}.html"


def relay_html(post, live):
    """A tiny page whose tags give X a large thumbnail (the article's own image, never the author photo),
    and which sends readers straight on to the Substack post."""
    e = lambda s: html.escape(s or "", quote=True)
    url, title = live["url"], post["title_he"]
    desc = post.get("subtitle_he") or post.get("byline_he", "")
    image = live.get("cover") or post.get("cover_image", "")
    if post.get("author_photo") and image == post["author_photo"]:
        image = post.get("cover_image", "")
    return f"""<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<title>{e(title)}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{e(desc)}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="השמרן">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{e(image)}">
<meta property="og:url" content="{e(url)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@HaShamran1948">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{e(image)}">
<link rel="canonical" href="{e(url)}">
<meta http-equiv="refresh" content="0; url={e(url)}">
</head>
<body><p><a href="{e(url)}">{e(title)}</a></p>
<script>location.replace({json.dumps(url)});</script></body>
</html>
"""


def write_relays(posts, live):
    written = []
    for slug, info in live.items():
        if slug not in posts:
            continue
        path = ROOT / f"{slug}.html"
        page = relay_html(posts[slug], info)
        if not path.exists() or path.read_text(encoding="utf-8") != page:
            path.write_text(page, encoding="utf-8")
            written.append(slug)
    return written


def relay_is_up(slug):
    """True once GitHub Pages serves the relay page with its thumbnail tag."""
    try:
        r = requests.get(relay_url(slug), timeout=30)
        return r.ok and "twitter:image" in r.text
    except requests.RequestException:
        return False


def current_slot(now):
    local = now.astimezone(ISRAEL)
    for i, (h, m) in enumerate(SLOTS):
        start = local.replace(hour=h, minute=m, second=0, microsecond=0)
        if start <= local < start + SLOT_WINDOW:
            return f"{local.date().isoformat()}#{i}"
    return None


def choose(posts, live, log, now):
    """The (slug, quote index) to tweet now, or None. Today's posts first, then the newest."""
    today = israel_date(now)
    used = {}
    for t in log:
        used.setdefault(t["slug"], set()).add(t["quote"])
    candidates = []
    for slug, info in live.items():
        p = posts.get(slug)
        if not p:
            continue
        live_at = parse_iso(info["live_at"])
        if now - live_at > TWEET_WINDOW:
            continue
        done = used.get(slug, set())
        if len(done) >= MAX_PER_POST:
            continue
        free = [i for i in range(len(p.get("quotes_he") or [])) if i not in done]
        if not free:
            continue
        candidates.append((israel_date(live_at) == today, len(done) == 0, live_at, slug, free[0]))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][3], candidates[0][4]


def tweet_due(log, now):
    """The slot key if a tweet is owed now, else None."""
    slot = current_slot(now)
    if not slot or any(t.get("slot") == slot for t in log):
        return None
    today = israel_date(now)
    if sum(1 for t in log if israel_date(parse_iso(t["at"])) == today) >= MAX_PER_DAY:
        return None
    if log and now - max(parse_iso(t["at"]) for t in log) < MIN_GAP:
        return None
    return slot


def alerts(posts, live, now):
    out = []
    for slug, p in posts.items():
        if p.get("status") == "ready" and slug not in live and p.get("ready_at"):
            waited = now - parse_iso(p["ready_at"])
            if waited > PUBLISH_OVERDUE:
                out.append(f"{slug} has waited {waited.days}d {waited.seconds // 3600}h to be published: "
                           "check that dud is on and signed in to Substack (run login.cmd)")
        if p.get("status") == "draft_failed_qc":
            out.append(f"{slug} failed the quality check and was not published")
    return out


def run(dry_run=False, now=None, archive=None):
    now = now or utcnow()
    posts = load_posts()
    live = load_json(STATE / "live.json", {})
    # dud reports each post it sees live (Substack refuses GitHub Actions); those records win.
    for f in sorted((STATE / "live").glob("*.json")):
        live.setdefault(f.stem, load_json(f))
    log = load_json(STATE / "tweets.json", [])
    report = {"at": iso(now), "newly_live": [], "relays_written": [], "tweet": None, "alerts": []}

    archive = archive if archive is not None else substack_archive()
    if archive is None:
        report["substack_unreachable"] = True
        archive = []
    report["newly_live"] = match_live(posts, archive, live)
    report["relays_written"] = write_relays(posts, live)
    save_json(STATE / "live.json", live)

    slot = tweet_due(log, now)
    pick = choose(posts, live, log, now) if slot else None
    if pick:
        slug, qi = pick
        post = posts[slug]
        text = tweets.compose(post["quotes_he"][qi], relay_url(slug))
        entry = {"slot": slot, "slug": slug, "quote": qi, "text": text, "at": iso(now)}
        if slug in report["relays_written"] or not relay_is_up(slug):
            report["tweet"] = {"waiting_for_relay_page": slug}
        elif dry_run or not os.environ.get("BUFFER_API_KEY"):
            report["tweet"] = {**entry, "dry_run": True}
        else:
            buf = tweets.Buffer()
            entry["buffer_id"] = buf.post_now(buf.x_channel_id(), text)
            log.append(entry)
            save_json(STATE / "tweets.json", log)
            report["tweet"] = entry
    # Substack usually refuses GitHub Actions; that is expected, since dud reports live posts (state/live/).
    report["alerts"] = alerts(posts, live, now)
    # No timestamp in the saved copy, so the file (and the repo) only changes when something happens.
    save_json(STATE / "social-status.json", {k: v for k, v in report.items() if k != "at"})
    return report


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--check-buffer", action="store_true", help="only check the Buffer key and the X channel")
    args = ap.parse_args(argv)
    if args.check_buffer:
        try:
            print(json.dumps({"buffer": "ok", "x_channel_id": tweets.Buffer().x_channel_id()}))
            return 0
        except tweets.BufferError as e:
            print(json.dumps({"buffer": "error", "error": str(e)}, ensure_ascii=False))
            return 3
    try:
        report = run(dry_run=args.dry_run)
    except tweets.BufferError as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        return 3
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
