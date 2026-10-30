"""Lookups for the translator: established Hebrew names and titles, and the original Hebrew of Jewish sources.

Usage:
    python3 pipeline/lookup.py name "John Locke" "The Federalist Papers" "Heritage Foundation"
        Hebrew Wikipedia title (via English Wikipedia's language links, then Wikidata's Hebrew label).
        Prints "-" when Hebrew Wikipedia has no article: then transliterate, and log the choice.
    python3 pipeline/lookup.py source "Deuteronomy 17:13" "Berakhot 58a:5" [--niqqud]
        Original Hebrew text from Sefaria, without cantillation (and without niqqud unless --niqqud).
"""
import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

UA = "HaShamranTranslationBot/1.0 (https://hashamran.substack.com)"  # Wikimedia asks for a descriptive agent


def get_json(url, tries=5):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    for i in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code != 429 or i == tries - 1:
                raise
            time.sleep(int(e.headers.get("Retry-After") or 0) or 2 ** (i + 1))  # Wikimedia rate limit


def hebrew_punct(text):
    """Wikipedia writes ג'ון and צה"ל with ASCII marks; we print the Hebrew geresh and gershayim."""
    return text.replace("'", "׳").replace('"', "״")


def hebrew_name(english):
    """Hebrew Wikipedia's title for an English Wikipedia subject, or None."""
    q = urllib.parse.urlencode({"action": "query", "titles": english, "prop": "langlinks", "lllang": "he",
                                "redirects": 1, "format": "json"})
    pages = get_json("https://en.wikipedia.org/w/api.php?" + q).get("query", {}).get("pages", {})
    for page in pages.values():
        for link in page.get("langlinks", []):
            return hebrew_punct(link["*"])
    q = urllib.parse.urlencode({"action": "wbgetentities", "sites": "enwiki", "titles": english, "props": "labels",
                                "languages": "he", "format": "json"})
    for entity in get_json("https://www.wikidata.org/w/api.php?" + q).get("entities", {}).values():
        label = entity.get("labels", {}).get("he", {}).get("value")
        if label and re.search(r"[א-ת]", label):
            return hebrew_punct(label)
    return None


CANTILLATION = re.compile(r"[֑-֯׀׃]")
NIQQUD = re.compile(r"[\u05b0-\u05bd\u05bf\u05c1\u05c2\u05c4\u05c5\u05c7]")  # keeps the maqaf (U+05BE)


def plain_hebrew(text, niqqud=False):
    text = re.sub(r'<sup[^>]*>.*?</sup>|<i class="footnote">.*?</i>', "", text, flags=re.S)  # Sefaria footnotes
    text = re.sub(r"<br\s*/?>", " ", text)
    text = re.sub(r"<[^>]+>|\{[^}]*\}", "", html.unescape(text)).replace("\xa0", " ")
    text = CANTILLATION.sub("", text)
    if not niqqud:
        text = NIQQUD.sub("", text)
    return re.sub(r"\s+", " ", text).strip()


def source(ref, niqqud=False):
    """(Hebrew reference, Hebrew text, English text) from Sefaria for a reference like "Deuteronomy 17:13"."""
    d = get_json("https://www.sefaria.org/api/texts/" + urllib.parse.quote(ref) + "?context=0&commentary=0")
    if "error" in d:
        raise ValueError(d["error"])
    flat = lambda x: " ".join(flat(i) for i in x) if isinstance(x, list) else (x or "")
    return d.get("heRef", ""), plain_hebrew(flat(d.get("he")), niqqud), plain_hebrew(flat(d.get("text")), True)


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("name"); n.add_argument("terms", nargs="+")
    s = sub.add_parser("source"); s.add_argument("refs", nargs="+"); s.add_argument("--niqqud", action="store_true")
    a = ap.parse_args(argv)
    for item in (a.terms if a.cmd == "name" else a.refs):
        try:
            if a.cmd == "name":
                time.sleep(1)  # stay well inside Wikimedia's rate limit
                print(f"{item} → {hebrew_name(item) or '-'}")
            else:
                he_ref, he, en = source(item, a.niqqud)
                print(f"{item} ({he_ref}): {he}\n    EN: {en}")
        except Exception as e:  # one bad lookup should not stop the rest
            print(f"{item} → error: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
