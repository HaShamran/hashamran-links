"""Hebrew spelling check with Dicta's Nakdan: words its lexicon does not know (typos, invented words, odd spellings).

Usage:
    python3 pipeline/hebcheck.py posts/<slug>/post.json        # prints JSON: [{"word", "count", "context"}]

Nakdan (https://nakdan.dicta.org.il, free) vowelizes Hebrew and analyses each word. A word for which none of its
readings has a known lemma is not in its lexicon. Most hits are foreign names (טאקר, סולהיים), which are fine; the
rest are misspellings or made-up words, e.g. התלמידיים. The list goes to the reviewer (REVIEWER.md), who decides
which are errors. It never fails a post on its own, and a network error returns an empty list with a warning.
"""
import json
import re
import sys

import requests

NAKDAN = "https://nakdan-2-0.loadbalancer.dicta.org.il/api"
CHUNK = 4000  # characters per request
HEBREW_WORD = re.compile(r"[א-ת]")


def clean(text):
    """Hebrew prose only: no links, images, Latin words or markup."""
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)|\]\([^)]*\)|https?://\S+", " ", text or "")
    return re.sub(r"[A-Za-z*_#>|]+", " ", text)


def chunks(text):
    out, cur = [], ""
    for para in text.split("\n"):
        if cur and len(cur) + len(para) > CHUNK:
            out.append(cur); cur = ""
        cur += para + "\n"
    return out + [cur] if cur.strip() else out


def unknown(words):
    """Words from a Nakdan reply that have no reading with a known lemma."""
    out = []
    for w in words:
        if w.get("sep") or not HEBREW_WORD.search(w.get("word", "")):
            continue
        readings = [o for o in w.get("options") or [] if isinstance(o, list) and len(o) > 1]
        if readings and not any(lemma for o in readings for _, lemma, *_ in o[1]):
            out.append(w["word"].strip("׳״'\""))
    return out


def check(text):
    found = []
    for part in chunks(clean(text)):
        r = requests.post(NAKDAN, json={"task": "nakdan", "data": part, "genre": "modern", "addmorph": True,
                                        "keepqq": False, "nodageshdefmem": False, "patachma": False,
                                        "keepmetagim": True}, timeout=90)
        r.raise_for_status()
        found += unknown(r.json())
    out = []
    for word in dict.fromkeys(found):
        i = text.find(word)
        out.append({"word": word, "count": found.count(word), "context": text[max(0, i - 40):i + 40].replace("\n", " ")})
    return out


def post_text(post):
    return "\n".join([post.get("title_he", ""), post.get("subtitle_he", ""), post.get("body_he", ""),
                      post.get("author_bio_he", "")] + list(post.get("quotes_he") or []))


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    post = json.load(open(argv[0], encoding="utf-8"))
    try:
        result = check(post_text(post))
    except (requests.RequestException, ValueError) as e:
        print(f"warning: Dicta Nakdan unavailable ({e}); spelling not checked", file=sys.stderr)
        result = []
    print(json.dumps(result, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
