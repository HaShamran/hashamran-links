"""Sweep one translation mistake across everything we have (MISTAKE-PROTOCOL.md, step 2).

    python3 pipeline/mistake_sweep.py --he '<Hebrew regex>' [--en '<English regex>'] [--qc double_possessive]

Counts the pattern in our own posts (posts/*/post.json) and in the Hebrew side of every reference bank in the
project folder (תכלת, השילוח, Mida, Kohelet, Misgav, JISS, INSS, Israel Hayom), with examples. With --qc, a match
counts only when the named qc.py check (qc.<name>_problems) also flags it. With --en, it also counts how often the
English side of the paired banks has the trigger, so the Hebrew of those pairs shows how professional
translators rendered it. Output: a JSON summary on stdout.
"""
import argparse
import glob
import json
import os
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import qc  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
GUIDE = os.environ.get("HASHAMRAN_GUIDE", "/mnt/project-files/hashamran/translation-guide")
BANKS = {"tchelet": "pairs/*/", "hashiloach": "hashiloach/essays/*.md", "mida": "mida/pairs/*/",
         "kohelet": "kohelet/pairs/*/", "misgav": "misgav/pairs/*/", "jiss": "jiss/pairs/*/",
         "inss": "inss/pairs/*/", "israelhayom": "israelhayom/pairs/*/"}


def _read(path):
    try:
        return open(path, encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _post_text(p):
    return "\n".join([str(p.get(k, "")) for k in ("title_he", "subtitle_he", "body_he", "author_bio_he")]
                     + list(p.get("quotes_he") or []))


def sweep(he, en=None, check=None, examples=15):
    pat = re.compile(he)
    en_pat = re.compile(en, re.I) if en else None
    flag = getattr(qc, f"{check}_problems") if check else None

    def hits(text):
        return [m for m in pat.finditer(text) if not flag or flag(m.group(0))]

    def ctx(text, m):
        return text[max(0, m.start() - 50):m.end() + 30].replace("\n", " ")

    out = {"ours": {"posts": 0, "hits": 0, "posts_with": 0, "examples": []}, "banks": {}}
    for f in sorted(glob.glob(str(ROOT / "posts/*/post.json"))):
        t = _post_text(json.loads(_read(f) or "{}"))
        h = hits(t)
        out["ours"]["posts"] += 1
        out["ours"]["hits"] += len(h)
        out["ours"]["posts_with"] += bool(h)
        out["ours"]["examples"] += [f"{pathlib.Path(f).parent.name}: {ctx(t, m)}" for m in h]
    for bank, rel in BANKS.items():
        entries = sorted(glob.glob(os.path.join(GUIDE, rel)))
        b = {"essays": len(entries), "hebrew_words": 0, "hits": 0, "essays_with": 0, "en_trigger": 0, "examples": []}
        for e in entries:
            t = _read(e if e.endswith(".md") else os.path.join(e, "he.md"))
            b["hebrew_words"] += len(re.findall(r"[א-ת]+", t))
            h = hits(t)
            b["hits"] += len(h)
            b["essays_with"] += bool(h)
            if len(b["examples"]) < examples:
                b["examples"] += [f"{pathlib.Path(e).name}: {ctx(t, m)}" for m in h][:examples - len(b["examples"])]
            if en_pat and not e.endswith(".md"):
                b["en_trigger"] += len(en_pat.findall(_read(os.path.join(e, "en.md"))))
        out["banks"][bank] = b
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--he", required=True, help="Hebrew regex for the mistake")
    ap.add_argument("--en", help="English regex for what triggers it (counted in the paired banks)")
    ap.add_argument("--qc", help="name of a qc.py check that must also flag the match, e.g. double_possessive")
    ap.add_argument("--examples", type=int, default=15)
    a = ap.parse_args(argv)
    print(json.dumps(sweep(a.he, a.en, a.qc, a.examples), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
