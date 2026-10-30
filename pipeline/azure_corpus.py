"""Parallel reference corpus: 100 essays that appeared in both Azure (English) and תכלת (Hebrew), Shalem Press.

The texts are not stored in this public repo (they are Shalem Press's copyright). `fetch` downloads them from
azure.org.il and tchelet.org.il into a local cache; `search` shows how תכלת rendered an English word or phrase.

Usage:
    python3 pipeline/azure_corpus.py fetch                  # ~1 min, cache in /tmp/azure-corpus
    python3 pipeline/azure_corpus.py search "sovereignty"   # English paragraph + matching Hebrew paragraphs
    python3 pipeline/azure_corpus.py search "ריבונות" --he  # search the Hebrew side instead
    python3 pipeline/azure_corpus.py show 17                # print pair 17 (see pipeline/azure/index.csv)
"""
import argparse
import concurrent.futures as cf
import csv
import html
import os
import pathlib
import re
import sys
import urllib.request

INDEX = pathlib.Path(__file__).with_name("azure") / "index.csv"
CACHE = pathlib.Path(os.environ.get("AZURE_CORPUS", "/tmp/azure-corpus"))


def rows():
    with open(INDEX, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def clean(page):
    """Article body from an azure.org.il / tchelet.org.il article page, one paragraph per blank-line block."""
    s = page[page.find("</div>", page.find('class="pages"')):]
    ends = [m.start() for m in re.finditer(r"include/print\.php", s)]
    if ends:
        s = s[:ends[-1]]
    s = re.sub(r"<script.*?</script>|<style.*?</style>|<sup[^>]*>.*?</sup>", "", s, flags=re.S)
    s = re.sub(r"<br\s*/?>|</p>|</h\d>|</div>|</li>|</blockquote>", "\n", s, flags=re.I)
    s = re.sub(r"<(em|i)>(.*?)</\1>", r"*\2*", s, flags=re.S | re.I)
    s = html.unescape(re.sub(r"<[^>]+>", "", s)).replace("﻿", "")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in s.split("\n")]
    s = "\n\n".join(l for l in lines if l and l not in ("Print", "PDF Format", "הדפסה", "גרסת PDF"))
    return re.sub(r'<a href="?\s*$', "", s).strip()


def get(url):
    req = urllib.request.Request(url + "&page=all", headers={"User-Agent": "Mozilla/5.0 (HaShamran translation reference)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "ignore")


def fetch():
    CACHE.mkdir(parents=True, exist_ok=True)

    def one(r):
        for lang, key in (("en", "azure_url"), ("he", "tchelet_url")):
            out = CACHE / f"{int(r['n']):03d}.{lang}.txt"
            if out.exists() and out.stat().st_size > 1000:
                continue
            for _ in range(3):
                try:
                    out.write_text(clean(get(r[key])), encoding="utf-8")
                    break
                except OSError:
                    pass

    with cf.ThreadPoolExecutor(6) as ex:
        list(ex.map(one, rows()))
    have = len(list(CACHE.glob("*.txt")))
    print(f"{have} of {2 * len(rows())} texts in {CACHE}")
    return 0 if have else 2


def paras(n, lang):
    p = CACHE / f"{n:03d}.{lang}.txt"
    return [x for x in p.read_text(encoding="utf-8").split("\n\n") if len(x) > 40] if p.exists() else []


def aligned(src, dst, i):
    """Paragraphs of dst at the same relative position as src[i] (the editions were edited, so ±1)."""
    pos = sum(len(x) for x in src[:i]) / max(1, sum(len(x) for x in src))
    total, acc = sum(len(x) for x in dst), 0
    for j, x in enumerate(dst):
        acc += len(x)
        if acc / max(1, total) >= pos:
            return dst[max(0, j - 1): j + 2]
    return dst[-2:]


def search(term, hebrew=False, limit=6):
    pat = re.compile(re.escape(term) if hebrew else r"\b" + re.escape(term) + r"\b", re.I)
    shown = 0
    for r in rows():
        n = int(r["n"])
        en, he = paras(n, "en"), paras(n, "he")
        src, dst = (he, en) if hebrew else (en, he)
        for i, p in enumerate(src):
            if pat.search(p):
                print(f"=== {n}: {r['title_en']} / {r['title_he']}")
                print(("HE: " if hebrew else "EN: ") + p)
                for q in aligned(src, dst, i):
                    print(("  EN: " if hebrew else "  HE: ") + q)
                print()
                shown += 1
                break
        if shown >= limit:
            break
    if not shown:
        print("no match (did you run fetch?)")


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("fetch")
    s = sub.add_parser("search"); s.add_argument("term"); s.add_argument("--he", action="store_true"); s.add_argument("-n", type=int, default=6)
    sh = sub.add_parser("show"); sh.add_argument("n", type=int)
    a = ap.parse_args(argv)
    if a.cmd == "fetch":
        return fetch()
    if a.cmd == "search":
        search(a.term, a.he, a.n)
    else:
        for lang in ("en", "he"):
            print("\n\n".join(paras(a.n, lang)), "\n\n" + "=" * 40 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
