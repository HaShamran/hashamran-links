"""Fetch one recommended essay and pull out its text, images and embeds.

Usage:
    python pipeline/extract.py URL [--out FILE]

Firecrawl renders the page first (passes bot checks, handles PDFs); our own fetch is the fallback.

Prints (or writes) JSON: url, title, author, date, sitename, markdown body,
images, embeds, word_count and status ("ok", "paywalled", "too_short", "failed").
"""
import argparse
import io
import json
import re
import sys

import requests
import trafilatura

import detect
import firecrawl
from common import BROWSER_UA

MIN_WORDS = 350
PAYWALL_MARKERS = re.compile(
    r"subscribe to (continue|read)|to continue reading|already a subscriber|this article is for subscribers"
    r"|subscriber[- ]only|sign in to read|create a free account to continue|unlock this article",
    re.I,
)
EMBED_RE = re.compile(r'<iframe[^>]+src="([^"]+)"', re.I)
EMBED_HOSTS = ("youtube.com", "youtube-nocookie.com", "youtu.be", "vimeo.com", "rumble.com", "x.com", "twitter.com", "spotify.com")


BIO_SELECTOR = ('[class*="author-bio"], [class*="author-box"], [class*="about-author"], [class*="author-info"], '
                '[class*="author-card"], [class*="contributor-bio"], [class*="bio-box"], [class*="author__bio"], '
                '[class*="authorfootnote"], [class*="author-footnote"]')
ICON_RE = re.compile(r"icon|logo|standalone|twitter|xlogo|/x\.|\.svg|sprite|avatar-default", re.I)


def _img_src(img):
    for attr in ("data-src", "data-lazy-src", "data-original", "src"):
        v = img.get(attr, "")
        if v and not v.startswith("data:"):
            return v
    srcset = img.get("data-srcset") or img.get("srcset") or ""
    return srcset.split(",")[-1].strip().split(" ")[0] if srcset else ""


def author_bio(html, base_url, author=""):
    """The author box at the end of an essay, if the site has one: (bio text, photo URL)."""
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin
    soup = BeautifulSoup(html, "html.parser")
    for el in soup.select(BIO_SELECTOR):
        text = " ".join(el.get_text(" ", strip=True).split())
        if len(text) < 40 or len(text) > 2500:
            continue
        imgs = el.find_all("img") + (el.parent.find_all("img") if el.parent else [])
        photo = next((_img_src(i) for i in imgs if _img_src(i) and not ICON_RE.search(_img_src(i))), "")
        if not photo and author:
            # Some sites show the headshot next to the byline instead of in the bio box.
            img = soup.find("img", alt=lambda a: a and a.strip().lower() == author.lower())
            photo = _img_src(img) if img else ""
        photo = re.sub(r"\?w=\d+$", "", photo)
        return text, urljoin(base_url, photo) if photo else ""
    return "", ""


def fetch_any(url):
    """Return (content_type, bytes) for a page or PDF, using the browser only when needed."""
    try:
        r = requests.get(url, headers={"User-Agent": BROWSER_UA, "Accept-Language": "en-US,en"}, timeout=60)
        ctype = r.headers.get("content-type", "")
        if r.ok and ("pdf" in ctype or url.lower().endswith(".pdf")):
            return "pdf", r.content
        if r.ok and "Just a moment" not in r.text[:3000]:
            return "html", r.content
    except requests.RequestException:
        pass
    return "html", detect.fetch_browser(url).encode("utf-8")


def pdf_text(data):
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(data))
    pages = [p.extract_text() or "" for p in reader.pages]
    # Rejoin hyphenated line breaks and single newlines inside paragraphs.
    text = "\n".join(pages)
    text = re.sub(r"-\n(\w)", r"\1", text)
    text = re.sub(r"(?<![.!?:”\"])\n(?!\n)", " ", text)
    return text


def _article_text(html, url):
    opts = dict(url=url, include_images=True, include_tables=True, include_formatting=True, output_format="markdown")
    text = trafilatura.extract(html, favor_precision=True, **opts)
    if not text or len(text.split()) < MIN_WORDS:
        text = trafilatura.extract(html, favor_recall=True, **opts) or text
    return text


X_STATUS_RE = re.compile(r"^https?://(?:www\.|mobile\.)?(?:x|twitter)\.com/([^/]+)/status/(\d+)", re.I)
X_BLOCK_PREFIX = {"header-one": "## ", "header-two": "## ", "header-three": "### ", "blockquote": "> ",
                  "unordered-list-item": "- ", "ordered-list-item": "1. "}


def x_article_markdown(article):
    """Markdown for an X long-form article (fxtwitter JSON): text blocks plus the article's own images."""
    media = {str(m.get("media_id")): (m.get("media_info") or {}).get("original_img_url")
             for m in article.get("media_entities") or []}
    entities = {str(e["key"]): e["value"] for e in (article["content"].get("entityMap") or [])}
    cover = ((article.get("cover_media") or {}).get("media_info") or {}).get("original_img_url")
    out = [f"![]({cover})"] if cover else []
    for b in article["content"]["blocks"]:
        if b.get("type") == "atomic":
            for r in b.get("entityRanges") or []:
                ent = entities.get(str(r["key"])) or {}
                for item in (ent.get("data") or {}).get("mediaItems") or []:
                    if media.get(str(item.get("mediaId"))):
                        out.append(f"![]({media[str(item['mediaId'])]})")
            continue
        text = (b.get("text") or "").strip()
        if text:
            out.append(X_BLOCK_PREFIX.get(b.get("type"), "") + text)
    return "\n\n".join(out)


def extract_x(url, out):
    """X (Twitter) posts need a login in a browser, so read them through the public fxtwitter API.
    An X long-form article becomes the post body; a tweet that only links to an essay elsewhere is
    followed to that essay; a long note tweet is used as the text itself."""
    user, status_id = X_STATUS_RE.match(url).groups()
    r = requests.get(f"https://api.fxtwitter.com/{user}/status/{status_id}", timeout=60)
    r.raise_for_status()
    t = r.json()["tweet"]
    author = t.get("author") or {}
    out["author"] = out["author"] or author.get("name", "")
    out["sitename"] = out["sitename"] or f"{author.get('name', user)} (X)"
    out["author_bio"] = author.get("description") or ""
    out["author_photo"] = (author.get("avatar_url") or "").replace("_200x200", "_400x400")
    out["source_format"] = "x"
    if t.get("article"):
        out["title"] = out["title"] or t["article"].get("title", "")
        out["markdown"] = x_article_markdown(t["article"])
    else:
        links = [f.get("replacement") for f in (t.get("raw_text") or {}).get("facets") or [] if f.get("type") == "url"]
        external = [l for l in links if l and not re.match(r"https?://(x|twitter)\.com/", l)]
        if external and len(re.findall(r"\w+", t.get("text", ""))) < MIN_WORDS:
            res = extract(external[0], {"title": out["title"], "author": out["author"], "date": out["date"],
                                        "publication": ""})
            res["via_x"] = url
            return res
        out["markdown"] = t.get("text", "")
        out["images"] = [m.get("url") for m in ((t.get("media") or {}).get("photos") or [])]
        out["markdown"] += "".join(f"\n\n![]({u})" for u in out["images"])
    if not out["images"]:
        out["images"] = re.findall(r"!\[[^\]]*\]\(([^)\s]+)", out["markdown"])
    out["embeds"] = [v.get("url") for v in ((t.get("media") or {}).get("videos") or []) if v.get("url")]
    out["word_count"] = len(re.findall(r"\w+", out["markdown"]))
    out["status"] = "ok" if out["word_count"] >= MIN_WORDS else "too_short"
    return out


def extract(url, item=None):
    if X_STATUS_RE.match(url):
        return _extract_local(url, item)
    out = _extract_firecrawl(url, item)
    if out["status"] in ("ok", "paywalled"):
        return out
    local = _extract_local(url, item)
    if local["status"] == "ok" or not out.get("markdown"):
        local.setdefault("firecrawl_error", out.get("error", ""))
        return local
    return out


def _extract_firecrawl(url, item=None):
    """Firecrawl gives us the rendered HTML; trafilatura turns it into clean Markdown with images."""
    item = item or {}
    out = {"url": url, "title": item.get("title", ""), "author": item.get("author", ""),
           "date": item.get("date", ""), "sitename": item.get("publication", ""),
           "markdown": "", "images": [], "embeds": [], "word_count": 0, "status": "failed"}
    try:
        data = firecrawl.scrape(url, formats=("markdown", "rawHtml"), main_only=False)
    except Exception as e:
        out["error"] = f"firecrawl: {e}"
        return out
    html = data.get("rawHtml") or ""
    meta = data.get("metadata") or {}
    text = _article_text(html, url) if html else ""
    if not text or len(re.findall(r"[^\W\d_]{2,}", text)) < MIN_WORDS:
        text = (data.get("markdown") or "").strip() or text
    out["markdown"] = text or ""
    out["fetched_with"] = "firecrawl"
    out["source_format"] = "pdf" if url.lower().endswith(".pdf") else "html"
    tmeta = trafilatura.extract_metadata(html, default_url=url) if html else None
    tmeta = tmeta.as_dict() if tmeta else {}
    out["title"] = out["title"] or tmeta.get("title") or meta.get("title") or ""
    out["author"] = out["author"] or tmeta.get("author") or meta.get("author") or ""
    out["date"] = out["date"] or tmeta.get("date") or ""
    out["sitename"] = out["sitename"] or tmeta.get("sitename") or meta.get("ogSiteName") or ""
    out["lead_image"] = tmeta.get("image") or meta.get("ogImage") or ""
    if html:
        out["author_bio"], out["author_photo"] = author_bio(html, url, out["author"])
        out["embeds"] = sorted({s for s in EMBED_RE.findall(html) if any(h in s for h in EMBED_HOSTS)})
    out["images"] = re.findall(r"!\[[^\]]*\]\(([^)\s]+)", out["markdown"])
    out["paywall_marker"] = bool(PAYWALL_MARKERS.search(html or out["markdown"]))
    out["word_count"] = len(re.findall(r"[^\W\d_]{2,}", out["markdown"]))
    if out["word_count"] >= MIN_WORDS:
        out["status"] = "ok"
    else:
        out["status"] = "paywalled" if out["paywall_marker"] else "too_short"
    return out


def _extract_local(url, item=None):
    item = item or {}
    out = {"url": url, "title": item.get("title", ""), "author": item.get("author", ""),
           "date": item.get("date", ""), "sitename": item.get("publication", ""),
           "markdown": "", "images": [], "embeds": [], "word_count": 0, "status": "failed"}
    if X_STATUS_RE.match(url):
        try:
            return extract_x(url, out)
        except Exception as e:
            out["error"] = f"{type(e).__name__}: {e}"
            return out
    try:
        kind, data = fetch_any(url)
    except Exception as e:  # network errors, bot checks
        out["error"] = f"{type(e).__name__}: {e}"
        return out
    if kind == "pdf":
        out["markdown"] = pdf_text(data)
        out["source_format"] = "pdf"
    else:
        html = data.decode("utf-8", errors="replace")
        text = _article_text(html, url)
        if not text or (len(text.split()) > 500 and text.count("\n\n") < 3):
            # Some sites only render the article body in a real browser.
            html = detect.fetch_browser(url)
            text = _article_text(html, url)
        if not text:
            out["error"] = "no article text found"
            return out
        meta = trafilatura.extract_metadata(html, default_url=url)
        meta = meta.as_dict() if meta else {}
        out["markdown"] = text
        for key in ("title", "author", "date", "sitename"):
            out[key] = out[key] or (meta.get(key) or "")
        out["lead_image"] = meta.get("image") or ""
        out["author_bio"], out["author_photo"] = author_bio(html, url, out["author"])
        out["images"] = re.findall(r"!\[[^\]]*\]\(([^)\s]+)", out["markdown"])
        out["embeds"] = sorted({s for s in EMBED_RE.findall(html) if any(h in s for h in EMBED_HOSTS)})
        out["paywall_marker"] = bool(PAYWALL_MARKERS.search(html))
        out["source_format"] = "html"
    out["word_count"] = len(re.findall(r"[^\W\d_]{2,}", out["markdown"]))
    if out.get("source_format") == "pdf" and out["word_count"] < MIN_WORDS:
        # A PDF without a text layer comes out as glyph codes ("/12/34/i255"). Find the essay's web page instead.
        out["status"] = "failed"
        out["error"] = "PDF has no readable text layer; look for the essay on the publication's own site"
    elif out["word_count"] < MIN_WORDS:
        out["status"] = "paywalled" if out.get("paywall_marker") else "too_short"
    else:
        out["status"] = "ok"
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--out")
    args = ap.parse_args(argv)
    url = detect.normalize_url(args.url)
    from common import STATE, load_json
    item = next((q for q in load_json(STATE / "queue.json", []) if q["url"] == url), None)
    result = extract(url, item)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        open(args.out, "w", encoding="utf-8").write(text)
    else:
        print(text)
    return 0 if result["status"] == "ok" else 2


if __name__ == "__main__":
    sys.exit(main())
