"""Secondary Hebrew reference: 100 recent essays from השילוח (2017–2026), for political terms תכלת never needed.

תכלת (pipeline/azure/) stays the primary guide for voice and style. Use this one to see how today's Hebrew
conservative writing names new things: woke, populism, DEI, the deep state, the judicial overhaul.

The texts are השילוח's copyright: the permanent private copy is the project folder
/mnt/project-files/hashamran/translation-guide/hashiloach/essays/, never this public repo. Where that folder is
missing, `fetch` downloads them from the magazine's public site into a local cache.

Usage:
    python3 pipeline/hashiloach_corpus.py fetch                 # no-op when the project folder is there
    python3 pipeline/hashiloach_corpus.py search "פופוליזם"     # each use in context, with the essay
    python3 pipeline/hashiloach_corpus.py count ווק ווֹק וואוק    # which spelling השילוח uses
"""
import argparse
import csv
import html
import json
import os
import pathlib
import re
import sys
import urllib.request

INDEX = pathlib.Path(__file__).with_name("hashiloach") / "index.csv"
STORE = pathlib.Path(os.environ.get("HASHILOACH_STORE", "/mnt/project-files/hashamran/translation-guide/hashiloach/essays"))
CACHE = pathlib.Path(os.environ.get("HASHILOACH_CACHE", "/tmp/hashiloach-corpus"))
API = "https://hashiloach.org.il/wp-json/wp/v2/posts/{}?_fields=content"


def rows():
    with open(INDEX, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def clean(h):
    h = re.sub(r"<script.*?</script>|<style.*?</style>|<figure.*?</figure>|<sup[^>]*>.*?</sup>", "", h, flags=re.S)
    h = re.sub(r"</p>|<br\s*/?>|</h\d>|</li>|</blockquote>", "\n", h)
    t = html.unescape(re.sub(r"<[^>]+>", "", h)).replace("\xa0", " ")
    return "\n\n".join(line.strip() for line in t.split("\n") if line.strip())


def text(r):
    p = STORE / r["file"]
    if p.exists():
        return p.read_text(encoding="utf-8").split("\n---\n", 1)[-1]
    c = CACHE / r["file"]
    return c.read_text(encoding="utf-8") if c.exists() else ""


def fetch():
    if all((STORE / r["file"]).exists() for r in rows()):
        print(f"all {len(rows())} essays already stored in {STORE}")
        return 0
    CACHE.mkdir(parents=True, exist_ok=True)
    for r in rows():
        if not text(r):
            try:
                req = urllib.request.Request(API.format(r["wp_id"]), headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=60) as resp:
                    (CACHE / r["file"]).write_text(clean(json.loads(resp.read())["content"]["rendered"]), encoding="utf-8")
            except OSError:
                pass
    have = sum(1 for r in rows() if text(r))
    print(f"{have} of {len(rows())} essays available")
    return 0 if have else 2


def pattern(term):
    """The term with or without a one-letter prefix (ו, ה, ב, ל, מ, ש, כ), maqaf and hyphen treated alike."""
    t = re.escape(term.replace("־", "-")).replace("\\-", "[-־ ]?")
    return re.compile(r"(?<![א-ת])[והבלמשכ]{0,2}" + t + r"(?![א-ת])")


def search(term, limit=8, width=110):
    pat, shown = pattern(term), 0
    for r in rows():
        t = text(r)
        for m in pat.finditer(t):
            a, b = max(0, m.start() - width), m.end() + width
            print(f"[{r['date']} · {r['title']}] …{t[a:b].replace(chr(10), ' ')}…")
            shown += 1
            break
        if shown >= limit:
            break
    if not shown:
        print("no match")


def count(terms):
    corpus = "\n".join(text(r) for r in rows())
    for term in terms:
        print(f"{term}: {len(pattern(term).findall(corpus))}")


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("fetch")
    s = sub.add_parser("search"); s.add_argument("term"); s.add_argument("-n", type=int, default=8)
    c = sub.add_parser("count"); c.add_argument("terms", nargs="+")
    a = ap.parse_args(argv)
    if a.cmd == "fetch":
        return fetch()
    search(a.term, a.n) if a.cmd == "search" else count(a.terms)
    return 0


if __name__ == "__main__":
    sys.exit(main())
