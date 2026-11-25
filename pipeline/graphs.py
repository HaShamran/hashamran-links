"""Graphs and charts in a source essay, and the check that holds a post whose graphs we could not get.

Hadar's rule (25 Nov 2026): never publish an article that has graphs or charts if the graph images can't be
fetched. Hold it instead.

Three places use this:
- extract.py records `graphs` (what looks like a chart in the source page) in its JSON output.
- finalize.py runs check() before marking a post ready. A post with a problem gets the status
  "held_missing_graphs" and a `hold_reason`, so the publisher on dud never sees it as ready.
- dud/publisher.py fetches every image before it builds the Substack draft and holds the post if one fails
  (substack_doc.py), so a chart that disappears between translation and publishing is caught too.

What counts as a graph:
- an <iframe> from a chart service (Datawrapper, Flourish, Infogram, Tableau, ...). These are interactive and
  never come through as an image, so a post that has one is always held.
- a chart drawn in the page itself (<svg> or <canvas> inside a <figure>, Highcharts and similar).
- an image whose alt text, caption, file name or neighbouring text says chart/graph/figure/data.
- a sentence that points at a chart ("the chart below", "see Figure 2") when no chart image was found at all.
"""
import re
from urllib.parse import urljoin

import requests

CHART_HOSTS = ("datawrapper.dwcdn.net", "datawrapper.de", "flourish.studio", "flo.uri.sh", "infogram.com",
               "e.infogram.com", "public.tableau.com", "tableau.com/views", "plotly.com", "chart-studio.plotly",
               "ourworldindata.org/grapher", "fred.stlouisfed.org/graph", "chartblocks", "everviz.com",
               "highcharts.com", "docs.google.com/spreadsheets", "app.powerbi.com", "observablehq.com/embed",
               "graphics.reuters.com", "statista.com/graph")
WORDS = r"(charts?|graphs?|figure\s*\d+|fig\.\s*\d+|infographic|data\s*viz|visuali[sz]ation|histogram|scatter\s*plot|bar\s*plot|line\s*plot|pie\s*chart|תרשים|גרף|איור\s*\d+)"
HINT_RE = re.compile(rf"(?<![a-z]){WORDS}(?![a-z])", re.I)
# A caption line under a chart usually names its data source: "Source: BLS", "Chart: The Economist".
CAPTION_RE = re.compile(r"^\s*[*_]*(source|sources|data|chart|graph|figure|fig\.)\s*[:.]", re.I)
# Text that points the reader at a chart.
# Not bare "the figure": "this figure is $2 trillion" is a number, not a picture.
REF_RE = re.compile(r"\b(the|this|that|these|following|above|below|next)\s+(chart|graph|infographic)s?\b"
                    r"|\b(see|in)\s+(figure|fig\.|chart|graph)\s*\d*\b"
                    r"|\b(chart|graph|figure)\s+(below|above)\b", re.I)
IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
IMG_EXT = re.compile(r"\.(png|jpe?g|gif|webp|svg|avif|heic)(\?|$)", re.I)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"


def _hint(*texts):
    return any(t and HINT_RE.search(t) for t in texts)


def from_html(html, base_url=""):
    """Charts we can see in the page's HTML: embeds, drawn charts, and images labelled as charts."""
    if not html:
        return []
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    out, seen = [], set()

    def add(kind, src, why):
        key = (kind, src)
        if key not in seen:
            seen.add(key)
            out.append({"kind": kind, "src": src, "why": why})

    for f in soup.find_all("iframe"):
        src = f.get("src") or f.get("data-src") or ""
        if any(h in src for h in CHART_HOSTS):
            add("embed", urljoin(base_url, src), "interactive chart embed")
    for el in soup.select('[class*="highcharts"], [class*="datawrapper"], [class*="flourish"], [class*="infogram"], '
                          '[data-datawrapper-height], div.tableauPlaceholder'):
        add("drawn", el.get("id") or el.name, "chart drawn by a script in the page")
    for fig in soup.find_all("figure"):
        cap = fig.find("figcaption")
        cap_text = cap.get_text(" ", strip=True) if cap else ""
        if (fig.find("svg") or fig.find("canvas")) and not fig.find("img") and (_hint(cap_text) or fig.find("canvas")):
            add("drawn", cap_text[:80] or "figure", "chart drawn in the page (svg/canvas)")
    for img in soup.find_all("img"):
        src = ""
        for attr in ("data-src", "data-lazy-src", "data-original", "src"):
            v = img.get(attr, "")
            if v and not v.startswith("data:"):
                src = v
                break
        if not src:
            continue
        fig = img.find_parent("figure")
        cap = fig.find("figcaption").get_text(" ", strip=True) if fig and fig.find("figcaption") else ""
        if _hint(img.get("alt"), img.get("title"), " ".join(img.get("class") or []), src.rsplit("/", 1)[-1], cap) \
                or CAPTION_RE.match(cap or "") and not re.search(r"getty|reuters|ap photo|shutterstock|photo", cap, re.I):
            add("image", urljoin(base_url, src), f"image labelled as a chart: {(img.get('alt') or cap or src)[:80]}")
    return out


def from_markdown(md):
    """Charts we can see in the extracted Markdown: images whose alt text, caption line or neighbouring sentence
    names a chart, and sentences that point at a chart."""
    if not md:
        return []
    out = []
    blocks = [b.strip() for b in re.split(r"\n\s*\n", md)]
    for i, b in enumerate(blocks):
        for m in IMG_RE.finditer(b):
            alt, src = m.group(1), m.group(2)
            nxt = blocks[i + 1] if i + 1 < len(blocks) else ""
            prev = blocks[i - 1] if i else ""
            caption = nxt if len(nxt) < 300 and not IMG_RE.search(nxt) else ""
            if _hint(alt, src.rsplit("/", 1)[-1]) or CAPTION_RE.match(caption) \
                    or REF_RE.search(prev) or REF_RE.search(caption):
                out.append({"kind": "image", "src": src, "why": f"image presented as a chart: {(alt or caption or src)[:80]}"})
    refs = [m.group(0) for m in REF_RE.finditer(re.sub(r"!\[[^\]]*\]\([^)]*\)", "", md))]
    if refs:
        out.append({"kind": "reference", "src": "", "why": f"the text points at a chart ({refs[0]!r})"})
    return out


def find(html, markdown, base_url=""):
    """Everything that looks like a graph in the source, deduplicated by image URL."""
    items, seen = [], set()
    for g in from_html(html, base_url) + from_markdown(markdown):
        key = (g["kind"], g["src"])
        if key in seen:
            continue
        seen.add(key)
        items.append(g)
    return items


def fetch_ok(url, timeout=30):
    """True when the URL answers with an image (the same two tries the publisher's downloader makes)."""
    if not url.startswith("http"):
        return False
    for ua in (UA, "Mozilla/5.0"):
        try:
            r = requests.get(url, headers={"User-Agent": ua}, timeout=timeout)
        except requests.RequestException:
            continue
        ctype = r.headers.get("content-type", "")
        if r.ok and r.content and (ctype.startswith("image/") or (not ctype.startswith("text/") and IMG_EXT.search(url))):
            return True
    return False


def _same_image(a, b):
    """Two URLs for the same picture: equal, or one is a CDN wrapper around the other (substackcdn /fetch/)."""
    from urllib.parse import unquote
    a, b = unquote(a), unquote(b)
    return a == b or a.endswith(b) or b.endswith(a) or a.rsplit("/", 1)[-1].split("?")[0] == b.rsplit("/", 1)[-1].split("?")[0]


def check(post, src, fetch=fetch_ok):
    """Problems that must hold the post (empty list = fine). `src` is extract.py's JSON for the essay."""
    graphs = src.get("graphs")
    if graphs is None:  # extracted before 25 Nov 2026: work it out from the Markdown we have
        graphs = from_markdown(src.get("markdown", ""))
    problems = []
    body = post.get("body_he", "")
    body_imgs = [m.group(2) for m in IMG_RE.finditer(body)]
    images = [g for g in graphs if g["kind"] == "image"]
    for g in graphs:
        if g["kind"] in ("embed", "drawn"):
            problems.append(f"the source has a chart we cannot copy as an image ({g['why']}: {g['src'][:100]})")
    if any(g["kind"] == "reference" for g in graphs) and not images and not body_imgs:
        ref = next(g for g in graphs if g["kind"] == "reference")
        problems.append(f"{ref['why']} but no chart image was extracted")
    for g in images:
        url = next((u for u in body_imgs if _same_image(g["src"], u)), None)
        if not url:
            problems.append(f"chart image missing from the Hebrew body: {g['src'][:120]}")
        elif not fetch(url):
            problems.append(f"chart image cannot be downloaded: {g['src'][:120]}")
    return problems
