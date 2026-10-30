"""Third reference, for terminology only: English essays and published Hebrew translations of them, side by side.

48 pairs: 43 (2014–2025) from Commentary and National Review, translated and published by Mida (mida.org.il), and 5
(2014–2017) from First Things, American Affairs and the Washington Free Beacon, translated and published by השילוח
(index.csv column he_outlet). Use it to
see how a Hebrew right-of-centre outlet renders a current American or political term (deep state, swing voters,
woke, the squad). It never sets voice or style: תכלת (pipeline/azure/) stays primary, and השילוח
(pipeline/hashiloach/) is the second guide for Hebrew register. Mida's Hebrew is journalism, often abridged, and it
has mistakes (pair 9 moves Inauguration Day from January 20 to January 25), so check what you take from it.
The השילוח pairs are full, careful translations, and their translator's notes are in the glossary (little platoons,
government and administration).

The texts are the publishers' copyright: the permanent private copy is the project folder
/mnt/project-files/hashamran/translation-guide/mida/pairs/<dir>/{en,he}.md, never this public repo.

Usage:
    python3 pipeline/mida_corpus.py search "deep state"        # English hits, each with the Hebrew paragraph(s) at that point
    python3 pipeline/mida_corpus.py search --he "המדינה העמוקה"  # the other way round
    python3 pipeline/mida_corpus.py count "מצביעים מתנדנדים" "קולות צפים"
    python3 pipeline/mida_corpus.py show 12                     # one pair, paragraph by paragraph
"""
import argparse
import csv
import os
import pathlib
import re
import sys

INDEX = pathlib.Path(__file__).with_name("mida") / "index.csv"
STORE = pathlib.Path(os.environ.get("MIDA_STORE", "/mnt/project-files/hashamran/translation-guide/mida/pairs"))


def rows():
    with open(INDEX, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def paras(r, lang):
    p = STORE / r["dir"] / f"{lang}.md"
    if not p.exists():
        return []
    return [x.strip() for x in p.read_text(encoding="utf-8").split("\n\n") if x.strip() and not x.startswith("# ")]


def spans(ps):
    """Each paragraph's place in the essay as (start, end) fractions of its words."""
    total = sum(len(p.split()) for p in ps) or 1
    out, at = [], 0
    for p in ps:
        n = len(p.split())
        out.append((at / total, (at + n) / total)); at += n
    return out


def counterpart(src, dst, i):
    """Paragraphs of dst at the same place as paragraph i of src (translations keep the order; Mida may abridge)."""
    a, b = spans(src)[i]
    return [p for p, (c, d) in zip(dst, spans(dst)) if c < b and d > a][:2]


def pattern(term, hebrew):
    if hebrew:
        t = re.escape(term.replace("־", "-")).replace("\\-", "[-־ ]?")
        return re.compile(r"(?<![א-ת])[והבלמשכ]{0,2}" + t + r"(?![א-ת])")
    return re.compile(r"\b" + re.escape(term) + r"\b", re.I)


def search(term, hebrew=False, limit=6, width=160):
    pat, shown = pattern(term, hebrew), 0
    src_lang, dst_lang = ("he", "en") if hebrew else ("en", "he")
    for r in rows():
        src, dst = paras(r, src_lang), paras(r, dst_lang)
        for i, p in enumerate(src):
            m = pat.search(p)
            if not m:
                continue
            a = max(0, m.start() - width)
            print(f"[{r['n']} · {r['date']} · {r['title_en']}]")
            print(f"  {src_lang}: …{p[a:m.end() + width]}…")
            for q in counterpart(src, dst, i):
                print(f"  {dst_lang}: {q[:2 * width + 80]}")
            print()
            shown += 1
            break
        if shown >= limit:
            break
    if not shown:
        print("no match" if STORE.exists() else f"no pairs: {STORE} is missing")


def count(terms):
    corpus = "\n".join("\n".join(paras(r, "he") + paras(r, "en")) for r in rows())
    for term in terms:
        print(f"{term}: {len(pattern(term, bool(re.search('[א-ת]', term))).findall(corpus))}")


def show(n):
    r = next(x for x in rows() if x["n"] == str(n))
    print(f"{r['title_en']}  /  {r['title_he']}  ({r.get('publication') or 'Kohelet'}, {r['date']}){'  [abridged]' if r.get('abridged') == '1' else ''}\n")
    en, he = paras(r, "en"), paras(r, "he")
    for i, p in enumerate(en):
        print(f"EN {i + 1}: {p}")
        for q in counterpart(en, he, i):
            print(f"HE   : {q}")
        print()


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search"); s.add_argument("term"); s.add_argument("--he", action="store_true"); s.add_argument("-n", type=int, default=6)
    c = sub.add_parser("count"); c.add_argument("terms", nargs="+")
    w = sub.add_parser("show"); w.add_argument("n", type=int)
    a = ap.parse_args(argv)
    if a.cmd == "search":
        search(a.term, a.he, a.n)
    elif a.cmd == "count":
        count(a.terms)
    else:
        show(a.n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
