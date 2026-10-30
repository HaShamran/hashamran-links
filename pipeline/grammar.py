"""Optional extra layer: gender and number agreement in the Hebrew, checked with Dicta's DictaBERT parser.

Usage:
    pip install -q torch --index-url https://download.pytorch.org/whl/cpu && pip install -q transformers
    python3 pipeline/grammar.py posts/<slug>/post.json      # prints JSON: [{"rule", "words", "sentence"}]

It adds findings for the reviewer (REVIEWER.md) and replaces nothing. If the libraries, the model download or the
run fail, it prints a warning, returns an empty list and exits 0, and the workflow goes on as before.

Rules (only where the parser gives both words a single gender or number):
- adjective and its noun (amod):            ״החלטה חשוב״
- subject and its verb or predicate (nsubj): ״הממשלה החליטו״; a subject joined by ו (conj) is skipped
- numeral and its noun (nummod):           ״שלוש ספרים״

The model is Dicta's dictabert-joint (CC BY 4.0), pinned to REVISION. Its code was read at that revision before use
(it imports only torch and transformers and does no file, network or shell access). To move to a newer revision,
read that revision's BertFor*.py files first, then change REVISION.
"""
import json
import re
import sys

MODEL = "dicta-il/dictabert-joint"
REVISION = "7b1256fc0846e22d1af431eae299e2dcecee2778"  # 2026-09-30
BATCH = 8
SENTENCE = re.compile(r"(?<=[.!?])\s+")
# Numerals whose form shows gender (שלוש ספרים is wrong); עשרות, מאה, אלפי and the like have one form for both.
UNIT_NUMERALS = {"שניים", "שתיים", "שני", "שתי", "שלושה", "שלוש", "ארבעה", "ארבע", "חמישה", "חמש", "שישה", "שש",
                 "שבעה", "שבע", "שמונה", "תשעה", "תשע", "עשרה", "עשר"}


def sentences(post):
    text = "\n".join([post.get("title_he", ""), post.get("subtitle_he", ""), post.get("body_he", ""),
                      post.get("author_bio_he", "")] + list(post.get("quotes_he") or []))
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)|\]\([^)]*\)|https?://\S+|[*_#>\[\]]", " ", text)
    out = []
    for line in text.split("\n"):
        for s in SENTENCE.split(line):
            s = " ".join(s.split())
            if len(re.findall(r"[א-ת]+", s)) >= 3:
                out.append(s[:600])
    return out


def numeral(token):
    """A unit numeral, with or without a prefix (ו, ה, ב, ל, מ, ש). By the word itself, not its lemma: עשרות has lemma עשר."""
    return token in UNIT_NUMERALS or (len(token) > 2 and token[0] in "והבלמש" and token[1:] in UNIT_NUMERALS)


def single(feats, key):
    v = (feats or {}).get(key)
    return v if v in ("Masc", "Fem", "Sing", "Plur") else None


def clash(a, b, keys):
    """The first feature on which two tokens both have a single value and differ."""
    for k in keys:
        x, y = single(a["morph"]["feats"], k), single(b["morph"]["feats"], k)
        if x and y and x != y:
            return f"{k}: {a['token']} {x}, {b['token']} {y}"
    return None


def agreement(parsed):
    """Agreement findings in one parsed sentence (DictaBERT's json output).

    Kept narrow on purpose, because a parser error is a false alarm: the two words must stand close together, and
    coordination (ו), construct chains (סמיכות) and gender-neutral numerals (עשרות, מאה, אלפי) are skipped.
    """
    toks, out = parsed["tokens"], []
    in_conj = {t["syntax"]["dep_head_idx"] for t in toks if t["syntax"]["dep_func"] == "conj"}
    in_conj |= {i for i, t in enumerate(toks) if t["syntax"]["dep_func"] == "conj"}
    for i, t in enumerate(toks):
        h = t["syntax"]["dep_head_idx"]
        if not 0 <= h < len(toks) or h == i or i in in_conj or h in in_conj:
            continue
        head, func, pos, hpos = toks[h], t["syntax"]["dep_func"], t["morph"]["pos"], toks[h]["morph"]["pos"]
        found = None
        if func == "amod" and pos == "ADJ" and hpos == "NOUN" and h == i - 1 \
                and not head["syntax"]["dep_func"].startswith("compound"):
            found = ("adjective-noun", clash(t, head, ("Gender", "Number")))
        elif func == "nummod" and pos == "NUM" and hpos == "NOUN" and numeral(t["token"]) and 0 < h - i <= 2:
            found = ("numeral-noun", clash(t, head, ("Gender",)))
        elif func == "nsubj" and pos in ("NOUN", "PROPN", "PRON") and hpos in ("VERB", "ADJ") and abs(h - i) <= 3:
            if head["morph"]["feats"].get("Person") in (None, "3"):
                found = ("subject-verb", clash(t, head, ("Number", "Gender")))
        if found and found[1]:
            out.append({"rule": found[0], "words": found[1], "sentence": parsed["text"]})
    return out


def check(post):
    from transformers import AutoModel, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(MODEL, revision=REVISION)
    model = AutoModel.from_pretrained(MODEL, revision=REVISION, trust_remote_code=True, use_safetensors=True)
    model.eval()
    sents, out = sentences(post), []
    for k in range(0, len(sents), BATCH):
        for parsed in model.predict(sents[k:k + BATCH], tok, output_style="json"):
            out += agreement(parsed)
    return out


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    post = json.load(open(argv[0], encoding="utf-8"))
    try:
        result = check(post)
    except Exception as e:  # an optional layer: never stop the run
        print(f"warning: grammar check skipped ({type(e).__name__}: {e})", file=sys.stderr)
        result = []
    print(json.dumps(result, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
