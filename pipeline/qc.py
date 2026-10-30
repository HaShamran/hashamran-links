"""Automatic quality checks for a translated post (see TRANSLATION.md).

Usage:
    python pipeline/qc.py posts/<slug>/post.json [/tmp/<slug>.src.json]   # report; exit 0 = pass, 2 = fail

With the extracted English (the second argument), it also checks fidelity: paragraph count, and every number
of two or more digits kept in the Hebrew (or listed in `fidelity_waivers` with the reason).
"""
import json
import pathlib
import re
import sys

import prepare
import tweets

GLOSSARY = pathlib.Path(__file__).with_name("glossary.json")

REQUIRED = ("slug", "source_url", "author", "author_he", "publication", "title_he", "byline_he", "body_he")
HEBREW = re.compile(r"[֐-׿]")
LATIN_WORD = re.compile(r"[A-Za-z]{2,}")
SLUG_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9-]+$")
URL = re.compile(r"\]\([^)]*\)|https?://\S+")
TITLE_MAX = 80  # characters; a Hebrew headline, not a sentence
TITLE_WORDS_WARN = 8  # TITLES.md: most תכלת titles are 2-6 words

# The תכלת voice, measured (pipeline/azure/STYLE.md). Limits sit near the 5th/95th percentile of the 224 תכלת
# essays, so real תכלת prose passes and flat, translated-sounding Hebrew does not.
CONNECTIVES = ("אלא", "אך", "אף", "אולם", "ואולם", "אפוא", "ברם", "שהרי", "הרי", "כלומר", "שכן", "לפיכך", "על כן",
               "יתר על כן", "עם זאת", "ואמנם", "אמנם", "דהיינו", "לכן", "ממילא", "זאת ועוד", "לא זו בלבד",
               "מכל מקום", "כאמור")
CONNECTIVES_MIN = 5.0    # per 1,000 words (תכלת median 11)
SHEL_MAX = 4.2           # "של" per 100 words (תכלת median 3.1); more reads as translationese
SENTENCE_MAX = 30        # average words per sentence (תכלת 20)
STYLE_MIN_WORDS = 600    # shorter pieces are too small to measure

# English idioms translated word for word (STYLE.md section 9); none of them occurs in תכלת as our prose would use it.
CALQUES = {"בסופו של יום": "בסופו של דבר", "לשחק תפקיד": "למלא תפקיד", "לשחק את התפקיד": "למלא את התפקיד",
           "לעשות שכל": "הגיוני, מתקבל על הדעת", "עושה שכל": "הגיוני, מתקבל על הדעת", "לעשות הבדל": "לשנות, להשפיע",
           "על בסיס יומי": "מדי יום"}
JARGON = {"נרטיב": "סיפור, תפיסה", "אג'נדה": "סדר יום", "אג׳נדה": "סדר יום", "קונספט": "מושג, רעיון",
          "דיסקורס": "שיח", "פרובלמטי": "בעייתי", "פרקטי": "מעשי"}
# Where our drafts drift from תכלת (STYLE.md section 18): warnings, at the 5th/95th percentile of the 224 essays.
DRIFT = {"veulam_max": 1.5, "neg_min": 2.5, "ki_min": 1.4, "beyoter_max": 3.0, "atzmo_max": 4.2, "spread_min": 8.9}
NEGATION = re.compile(r"(?<![א-ת])[וש]?(אינו|אינה|אינם|אינן|איני|אינני|איננו|אין)(?![א-ת])")
ATZMO = re.compile(r"(?<![א-ת])[מבול]?עצמ(ו|ה|ם|ן)(?![א-ת])")


def word(w):
    return re.compile(r"(?<![א-ת])" + w + r"(?![א-ת])")


def style(text):
    """Style measures of a Hebrew text, compared with תכלת in STYLE.md."""
    words = len(re.findall(r"[א-ת]+", text)) or 1
    hits = {c: len(word(c).findall(text)) for c in CONNECTIVES}
    sentences = [x for x in re.split(r"[.?!]\s", text) if len(x.split()) > 2] or [text]
    lengths = [len(x.split()) for x in sentences]
    mean = sum(lengths) / len(lengths)
    per1000 = lambda n: round(n * 1000 / words, 2)
    return {"words": words,
            "connectives_per_1000": round(sum(hits.values()) * 1000 / words, 1),
            "distinct_connectives": sum(1 for v in hits.values() if v),
            "shel_per_100": round(len(word("של").findall(text)) * 100 / words, 2),
            "sentence_words": round(mean, 1),
            "sentence_spread": round((sum((n - mean) ** 2 for n in lengths) / len(lengths)) ** 0.5, 1),
            "veulam_per_1000": per1000(len(word("ואולם").findall(text))),
            "negation_per_1000": per1000(len(NEGATION.findall(text))),
            "ki_per_1000": per1000(len(word("[וש]?כי").findall(text))),
            "beyoter_per_1000": per1000(len(word("ביותר").findall(text))),
            "atzmo_per_1000": per1000(len(ATZMO.findall(text)))}


def style_problems(m):
    if m["words"] < STYLE_MIN_WORDS:
        return []
    out = []
    if m["connectives_per_1000"] < CONNECTIVES_MIN:
        out.append(f"style: {m['connectives_per_1000']} argument connectives per 1,000 words, תכלת has at least "
                   f"{CONNECTIVES_MIN} (rebuild the joints of the argument: ואולם, ברם, אפוא, שהרי, יתר על כן...)")
    need = min(8, m["words"] // 200)
    if m["distinct_connectives"] < need:
        out.append(f"style: only {m['distinct_connectives']} different connectives; use at least {need}")
    if m["shel_per_100"] > SHEL_MAX:
        out.append(f"style: {m['shel_per_100']} \"של\" per 100 words, over {SHEL_MAX}; use construct forms and "
                   "possessive suffixes (הוצאותיה, not ההוצאות שלה)")
    if m["sentence_words"] > SENTENCE_MAX:
        out.append(f"style: sentences average {m['sentence_words']} words; split them (תכלת averages 20)")
    return out


def style_warnings(m):
    """Drift from תכלת that is worth a second look but can be right for a given essay (STYLE.md section 18)."""
    if m["words"] < STYLE_MIN_WORDS:
        return []
    d, out = DRIFT, []
    if m["veulam_per_1000"] > d["veulam_max"]:
        out.append(f"style: ״ואולם״ {m['veulam_per_1000']} per 1,000 words (תכלת median 0.37); vary the contrast: "
                   "אבל, אך, אולם, ברם, עם זאת, ואילו")
    if m["negation_per_1000"] < d["neg_min"]:
        out.append(f"style: ״אין/אינו״ only {m['negation_per_1000']} per 1,000 words (תכלת median 5.9); "
                   "present-tense negation is ״אינו״, not ״לא״ (STYLE.md section 7)")
    if m["ki_per_1000"] < d["ki_min"]:
        out.append(f"style: ״כי״ only {m['ki_per_1000']} per 1,000 words (תכלת median 3.8); alternate ״כי״ with ״ש״ "
                   "after verbs of saying, above all where ״ש״ would stack")
    if m["beyoter_per_1000"] > d["beyoter_max"]:
        out.append(f"style: ״ביותר״ {m['beyoter_per_1000']} per 1,000 words (תכלת median 1.3); not every \"most\" is "
                   "a superlative")
    if m["atzmo_per_1000"] > d["atzmo_max"]:
        out.append(f"style: ״עצמו״ forms {m['atzmo_per_1000']} per 1,000 words (תכלת median 1.9); drop emphatic "
                   "\"himself\"")
    if m["sentence_spread"] < d["spread_min"]:
        out.append(f"style: sentence lengths too even (deviation {m['sentence_spread']} words, תכלת median 11.9); let "
                   "some sentences run and some stop short")
    return out


def calque_problems(text):
    return [f"calque: ״{c}״ reads as translated English; write ״{fix}״ (STYLE.md section 9)"
            for c, fix in CALQUES.items() if word(c).search(text)]


def jargon_warnings(text):
    return [f"loanword: ״{j}״; תכלת writes ״{fix}״ unless the author uses it as a term (STYLE.md section 9)"
            for j, fix in JARGON.items() if re.search(r"(?<![א-ת])[הבלמוש]?" + j + r"(ים|ות|ית|יים|יות)?(?![א-ת])", text)]


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


def process_problems(post):
    """The brief, the independent review and the blind back-translation (TRANSLATION.md, REVIEWER.md)."""
    out = []
    if not post.get("brief"):
        out.append("missing translation brief (brief): write it before translating")
    review = post.get("review") or {}
    if not review.get("independent"):
        out.append("missing independent review (review.independent): run the reviewer in REVIEWER.md")
    elif review.get("fixed", 0) + len(review.get("not_fixed") or []) < review.get("findings", 0):
        out.append("review findings left open: fix each one or list it in review.not_fixed with the reason")
    bt = post.get("back_translation") or {}
    if not (bt.get("title") and len(bt.get("quotes") or []) == 3):
        out.append("missing blind back-translation of the title and the 3 quotes (back_translation)")
    elif bt.get("meaning_kept") is not True:
        out.append("back-translation shows a shift in meaning: fix it, then set back_translation.meaning_kept")
    current = {"title": post.get("title_he", ""), "subtitle": post.get("subtitle_he", ""),
               "quotes": list(post.get("quotes_he") or [])}
    if bt and bt.get("source") != current:
        out.append("back-translation is stale or unrecorded: back_translation.source must hold the exact Hebrew title, "
                   "subtitle and quotes it was made from; rerun the blind back-translator after any change (REVIEWER.md)")
    return out


UNITS = {"אחד": 1, "אחת": 1, "שניים": 2, "שתיים": 2, "שני": 2, "שתי": 2, "שלושה": 3, "שלוש": 3, "ארבעה": 4,
         "ארבע": 4, "חמישה": 5, "חמש": 5, "שישה": 6, "שש": 6, "שבעה": 7, "שבע": 7, "שמונה": 8, "תשעה": 9, "תשע": 9}
TENS = {"עשרים": 20, "שלושים": 30, "ארבעים": 40, "חמישים": 50, "שישים": 60, "שבעים": 70, "שמונים": 80, "תשעים": 90}
BIG = {"מאה": 100, "מאתיים": 200, "אלף": 1000, "אלפיים": 2000}


def _word_value(w):
    """(word, kind) for a Hebrew number word, with or without a one-letter prefix (ו, ה, ב...)."""
    for cand in (w, w[1:]) if len(w) > 2 and w[0] in "ובהלמשכ" else (w,):
        for kind, table in (("unit", UNITS), ("tens", TENS), ("big", BIG)):
            if cand in table:
                return table[cand], kind
        if cand in ("עשר", "עשרה"):
            return 10, "teen"
        if cand in ("מאות", "אלפים"):
            return (100 if cand == "מאות" else 1000), "mult"
    return None, None


def _spoken(words):
    """Every partial value of each run of number words: עשרים וחמש מאות → 20, 25, 2500."""
    out, total = set(), None
    for w in words:
        n, kind = _word_value(w)
        if kind is None:
            total = None
            continue
        if kind == "mult" or (kind == "big" and n == 1000 and total and total < 1000):
            total = total * n if total else None
        else:
            total = (total or 0) + n
        if total and total >= 10:
            out.add(str(total))
    return out


def hebrew_numbers(text):
    """Numbers written in Hebrew words (שלושה עשר, עשרים וחמש, שלוש מאות, שנות השלושים), as digit strings.

    Loose on purpose: every partial value of a number phrase counts, so the check flags only numbers that are
    truly absent.
    """
    out = set()
    for m in re.finditer(r"שנות ה([א-ת]+)((?:\s+וה[א-ת]+)*)", text):  # שנות השלושים והארבעים = the 1930s and 1940s
        for decade in [m.group(1)] + re.findall(r"וה([א-ת]+)", m.group(2)):
            if decade in TENS:
                out |= {str(c + TENS[decade]) for c in (1800, 1900, 2000)}
            elif decade == "אלפיים":
                out.add("2000")
            elif decade == "עשרה":
                out |= {"1910", "2010"}
    for m in re.finditer(r"מאה ה([א-ת]+(?:\s+ו?[א-ת]+)?)", text):  # המאה התשע עשרה = the 19th century
        out |= _spoken(m.group(1).split())
    for clause in re.split(r"[^\sא-ת]+", text):  # punctuation ends a number phrase
        out |= _spoken(clause.split())
    return out


def fidelity_problems(post, source_markdown):
    """Mechanical comparison with the English: nothing dropped in bulk, every number kept."""
    out = []
    src_paras = len(prepare.text_paragraphs(source_markdown))
    he = [p for p in paragraphs(post.get("body_he", "")) if not is_media(p)]
    if src_paras and not (0.8 * src_paras <= len(he) <= 1.25 * src_paras):
        out.append(f"fidelity: {len(he)} Hebrew paragraphs for {src_paras} in the English: something may be missing")
    he_text = "\n".join([post.get("body_he", ""), post.get("subtitle_he", ""), post.get("title_he", "")])
    he_nums = set(prepare.numbers(he_text)) | {n.replace(",", "") for n in re.findall(r"\d[\d,.]*", he_text)}
    he_nums |= hebrew_numbers(he_text)
    waived = {str(w.get("number")) for w in post.get("fidelity_waivers") or [] if w.get("reason")}
    missing = [n for n in prepare.numbers(prepare.essay(source_markdown)) if n not in he_nums and n not in waived]
    if missing:
        out.append(f"fidelity: numbers in the English missing from the Hebrew: {', '.join(missing[:12])} "
                   "(restore them, or add each to fidelity_waivers with the reason, e.g. 1960s → שנות השישים)")
    return out


def check(post, source_markdown=None):
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
    problems += calque_problems(plain)
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
    measures = style("\n\n".join(paras))
    problems += style_problems(measures)
    if source_markdown is not None:
        problems += process_problems(post) + fidelity_problems(post, source_markdown)
    warnings = []
    if len(title.split()) > TITLE_WORDS_WARN:
        warnings.append(f"title has {len(title.split())} words; תכלת titles are mostly 2-6 (TITLES.md)")
    warnings += style_warnings(measures) + jargon_warnings(plain)
    return {"pass": not problems, "problems": problems, "warnings": warnings, "he_paragraphs": len(paras),
            "words": words, "style": measures}


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    post = json.load(open(argv[0], encoding="utf-8"))
    source = json.load(open(argv[1], encoding="utf-8")).get("markdown", "") if len(argv) > 1 else None
    report = check(post, source)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["pass"] else 2


if __name__ == "__main__":
    sys.exit(main())
