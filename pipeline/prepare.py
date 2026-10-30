"""Prepare an extracted essay for translation: numbered paragraphs, sections, a brief and a memory file.

Usage:
    python3 pipeline/prepare.py /tmp/<slug>.src.json /tmp/<slug>/

Writes into the work folder (never into the repo; the English is the publisher's copyright):
    section-01.en.md, section-02.en.md ...  the essay in sections of about 1,400 words, paragraphs numbered [P1], [P2]...
    memory.md                               running list of names and terms decided; read before and update after each section
    brief.md                                the translation brief to fill in before translating
and prints the paragraph count and the numbers that the Hebrew must keep (qc.py checks them).
"""
import json
import pathlib
import re
import sys

SECTION_WORDS = 1400


def is_media(p):
    return p.startswith("![") or re.fullmatch(r"https?://\S+", p) is not None


def paragraphs(markdown):
    return [p.strip() for p in re.split(r"\n\s*\n", markdown or "") if p.strip()]


# Where the essay ends and the page goes on: reader comments, polls, print-edition notes, publisher boilerplate.
# Found by testing the published posts (2026-10-30): WORLD and UnHerd pages came back with hundreds of comments.
END_MARKERS = re.compile(
    r"^(#+ *Comments\b|Please wait while we load the latest comments|#+ *Do you agree with this article|"
    r"\*?Appeared in the .{0,80}print edition|The American Mind is a publication of the Claremont Institute|"
    r"Please register, subscribe, or log in to comment)", re.I | re.M)
BOILERPLATE = re.compile(r"^(This copy is for your personal, non-commercial use only\..*|"
                         r"\**[A-Z][a-z]{2}\.? \d{1,2}, \d{4},? \d{1,2}:\d{2} [ap]m [A-Z]{2,3}\**)$", re.M)  # + datelines


def essay(markdown):
    """The essay alone: everything before the first end-of-essay marker, without reprint boilerplate."""
    markdown = BOILERPLATE.sub("", markdown or "")
    m = END_MARKERS.search(markdown)
    return markdown[:m.start()] if m else markdown


def text_paragraphs(markdown):
    """Paragraphs that carry text (not images, embeds or one-word leftovers)."""
    return [p for p in paragraphs(essay(markdown)) if not is_media(p) and len(p) > 30]


NUM = re.compile(r"(?<![\w.])\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?")


def numbers(text):
    """Numbers of two or more digits, without URLs and image links; 1,000 → 1000."""
    text = re.sub(r"\]\([^)]*\)|https?://\S+", " ", text)
    return sorted({n.replace(",", "") for n in NUM.findall(text) if len(n.replace(",", "").split(".")[0]) >= 2})


def sections(paras):
    out, cur, words = [], [], 0
    for i, p in enumerate(paras, 1):
        n = len(p.split())
        if cur and words + n > SECTION_WORDS:
            out.append(cur); cur, words = [], 0
        cur.append(f"[P{i}] {p}"); words += n
    if cur:
        out.append(cur)
    return out


BRIEF = """# Translation brief: {title}

Fill this in before translating. It goes into post.json as `brief`.
- tone: the author's voice in a few words (polemical, ironic, scholarly, personal...)
- audience_gap: what an Israeli reader will not know that the essay assumes
- allusions: American or pop-culture references to localize, and how (see US-POLITICS.md, TITLES.md)
- hard_terms: terms to settle before starting (glossary, US-POLITICS.md, the two corpora)
- names: people and institutions, with the Hebrew spelling (lookup.py name)
"""
MEMORY = """# Names and terms decided for: {title}

Read before every section. Add each name and term the first time you settle it, then never vary it.
| English | Hebrew | first in |
|---|---|---|
"""


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    src = json.load(open(argv[0], encoding="utf-8"))
    work = pathlib.Path(argv[1]); work.mkdir(parents=True, exist_ok=True)
    paras = text_paragraphs(src.get("markdown", ""))
    secs = sections(paras)
    for k, s in enumerate(secs, 1):
        (work / f"section-{k:02d}.en.md").write_text("\n\n".join(s) + "\n", encoding="utf-8")
    title = src.get("title", "")
    for name, tpl in (("brief.md", BRIEF), ("memory.md", MEMORY)):
        if not (work / name).exists():
            (work / name).write_text(tpl.format(title=title), encoding="utf-8")
    print(json.dumps({"paragraphs": len(paras), "sections": len(secs), "numbers": numbers(src.get("markdown", "")),
                      "work": str(work)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
