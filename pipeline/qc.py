"""Automatic quality checks for a translated post (see TRANSLATION.md).

Usage:
    python pipeline/qc.py posts/<slug>/post.json      # prints a report, exit 0 = pass, 2 = fail
"""
import json
import pathlib
import re
import sys

import tweets

GLOSSARY = pathlib.Path(__file__).with_name("glossary.json")

REQUIRED = ("slug", "source_url", "author", "author_he", "publication", "title_he", "byline_he", "body_he")
HEBREW = re.compile(r"[֐-׿]")
LATIN_WORD = re.compile(r"[A-Za-z]{2,}")
SLUG_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9-]+$")
URL = re.compile(r"\]\([^)]*\)|https?://\S+")
TITLE_MAX = 80  # characters; a Hebrew headline, not a sentence


def load_glossary():
    try:
        return json.loads(GLOSSARY.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []


def glossary_problems(text, glossary):
    """House terms used in a variant the glossary lists under "avoid" (pass 2b, glossary consistency)."""
    out = []
    for entry in glossary:
        for bad in entry.get("avoid", []):
            if bad and bad in text:
                out.append(f"glossary: use {entry['he']!r} for {entry['en']!r}, not {bad!r}")
    return out


def paragraphs(md):
    return [p.strip() for p in re.split(r"\n\s*\n", md) if p.strip()]


def is_media(p):
    return p.startswith("![") or re.fullmatch(r"https?://\S+", p) is not None


def check(post):
    problems = []
    for key in REQUIRED:
        if not str(post.get(key, "")).strip():
            problems.append(f"missing field: {key}")
    if post.get("slug") and not SLUG_RE.match(post["slug"]):
        problems.append("slug must look like YYYY-MM-DD-surname-title-words (lowercase ASCII)")
    body = post.get("body_he", "")
    paras = [p for p in paragraphs(body) if not is_media(p)]
    title = post.get("title_he", "")
    if not HEBREW.search(title):
        problems.append("title is not in Hebrew")
    if len(title) > TITLE_MAX:
        problems.append(f"title is {len(title)} characters; keep it under {TITLE_MAX} (pass 3)")
    options = [t for t in post.get("title_options_he") or [] if str(t).strip()]
    if len(options) < 3 or title not in options:
        problems.append("title_options_he needs at least 3 candidate titles including the chosen title_he (pass 3)")
    texts = [title, post.get("subtitle_he", ""), body, post.get("author_bio_he", "")] + list(post.get("quotes_he") or [])
    plain = URL.sub("", "\n".join(texts))
    if '"' in plain:
        problems.append('English quotation marks (") in the Hebrew text; use ״ ״')
    problems += glossary_problems(plain, load_glossary())
    # A paragraph that is mostly Latin script was probably left untranslated.
    for i, p in enumerate(paras, 1):
        heb = len(HEBREW.findall(p))
        lat = sum(len(w) for w in LATIN_WORD.findall(re.sub(r"\(https?://[^)]+\)", "", p)))
        if lat > heb:
            problems.append(f"paragraph {i} looks untranslated: {p[:60]!r}")
    src = post.get("source_paragraphs") or 0
    if src and not (0.8 * src <= len(paras) <= 1.25 * src):
        problems.append(f"paragraph count {len(paras)} is far from the source's {src}: something may be missing")
    words = len(re.findall(r"\w+", body))
    if words < 250:
        problems.append(f"body is only {words} words")
    for marker in ("subscribe", "Subscriber Agreement", "djreprints", "Sign up", "newsletter"):
        if marker.lower() in body.lower():
            problems.append(f"source clutter left in body: {marker!r}")
    photo = post.get("author_photo")
    if photo and photo in body:
        problems.append("the author photo appears in the body; it belongs only in the bio at the bottom")
    quotes = post.get("quotes_he") or []
    if len(quotes) != 3:
        problems.append(f"need exactly 3 tweet quotes, found {len(quotes)}")
    if len(set(quotes)) != len(quotes):
        problems.append("tweet quotes repeat")
    for i, q in enumerate(quotes, 1):
        if not HEBREW.search(q):
            problems.append(f"quote {i} is not in Hebrew")
        if not tweets.fits(q):
            n = tweets.weighted_length(q)
            problems.append(f"quote {i} is too long for a tweet with its link ({n} of 280 weighted chars)")
    return {"pass": not problems, "problems": problems, "he_paragraphs": len(paras), "words": words}


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    post = json.load(open(argv[0], encoding="utf-8"))
    report = check(post)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["pass"] else 2


if __name__ == "__main__":
    sys.exit(main())
