import qc
import tweets

GOOD = {"slug": "2026-10-29-murray-france", "source_url": "https://x", "author": "A", "author_he": "א",
        "publication": "P", "title_he": "צרפת", "byline_he": "מאת א",
        "title_options_he": ["צרפת", "צרפת על סף התהום", "התהום הצרפתית"],
        "body_he": "\n\n".join(["פסקה בעברית עם מספיק מילים כדי לעבור את הבדיקה " * 4] * 8),
        "quotes_he": ["ציטוט ראשון", "ציטוט שני", "ציטוט שלישי"]}


def test_good_post_passes():
    assert qc.check(GOOD)["pass"], qc.check(GOOD)["problems"]


def test_quotes_required_and_unique_and_short():
    assert not qc.check({**GOOD, "quotes_he": ["א", "א", "ב"]})["pass"]
    assert not qc.check({**GOOD, "quotes_he": ["א"]})["pass"]
    assert not qc.check({**GOOD, "quotes_he": ["א" * 300, "ב", "ג"]})["pass"]


def test_author_photo_not_in_body():
    bad = {**GOOD, "author_photo": "https://x/me.jpg", "body_he": "![](https://x/me.jpg)\n\n" + GOOD["body_he"]}
    assert any("author photo" in p for p in qc.check(bad)["problems"])


def test_link_counts_as_23():
    assert tweets.weighted_length("א" * 100) == 100 + 2 + 23


def test_title_pass_required():
    assert not qc.check({**GOOD, "title_options_he": []})["pass"]
    assert not qc.check({**GOOD, "title_options_he": ["א", "ב", "ג"]})["pass"]  # chosen title missing
    long_title = "א" * 90
    assert not qc.check({**GOOD, "title_he": long_title, "title_options_he": [long_title, "ב", "ג"]})["pass"]


def test_glossary_avoid_and_english_quotes():
    bad = {**GOOD, "body_he": GOOD["body_he"] + "\n\nהאבות המכוננים כתבו את החוקה האמריקנית."}
    assert any("glossary" in p for p in qc.check(bad)["problems"])
    quoted = {**GOOD, "body_he": GOOD["body_he"] + '\n\nהוא אמר "שלום" לכולם.'}
    assert any("quotation" in p for p in qc.check(quoted)["problems"])
    linked = {**GOOD, "body_he": GOOD["body_he"] + '\n\n[קישור](https://x/?q="a")'}
    assert qc.check(linked)["pass"], qc.check(linked)["problems"]


def test_azure_corpus_cleaner_and_alignment():
    import azure_corpus
    page = ('<div class="pages">(page 1 of 1)</div><p>First <em>para</em> of the essay, long enough to keep.</p>'
            '<p>Second para.<sup>1</sup></p><a href="include/print.php?id=1">Print</a>footer')
    assert azure_corpus.clean(page) == "First *para* of the essay, long enough to keep.\n\nSecond para."
    src, dst = ["a" * 10] * 10, ["b" * 10] * 5
    assert azure_corpus.aligned(src, dst, 9)[-1] == dst[-1]
    assert len(azure_corpus.rows()) == 224


def test_style_measures_against_tchelet():
    flat = " ".join(["המדינה של העם הזה היא המדינה של כולם והיא חשובה."] * 80)
    probs = qc.style_problems(qc.style(flat))
    assert any("connectives" in p for p in probs) and any("של" in p for p in probs)
    rich = " ".join(["ואולם הדבר אינו פשוט. אך יש בו אמת. ברם עלינו לזכור זאת, שהרי הוא חשוב. "
                     "זוהי אפוא שאלה קשה. יתר על כן היא דחופה. עם זאת אין לייאש. כלומר יש תקווה. "
                     "לפיכך נמשיך, שכן אין דרך אחרת. על כן נדבר. אמנם זה קשה, אלא שאין ברירה."] * 12)
    assert qc.style_problems(qc.style(rich)) == []
    assert qc.style_problems(qc.style("קצר מאוד.")) == []  # too short to measure


def test_lookup_text_helpers():
    import lookup
    assert lookup.hebrew_punct("ג'ון לוק, צה\"ל") == "ג׳ון לוק, צה״ל"
    raw = 'וְכׇל־הָעָ֖ם יִשְׁמְע֣וּ&nbsp;<span class="x">{ס}</span>'
    assert lookup.plain_hebrew(raw) == "וכל־העם ישמעו"
    assert lookup.plain_hebrew(raw, niqqud=True).startswith("וְכׇל־הָעָם")


def test_hashiloach_pattern_and_index():
    import hashiloach_corpus as h
    p = h.pattern("דיפ־סטייט")
    assert p.search("מה שמכונה ״הדיפ סטייט״ בוושינגטון") and p.search("ובדיפ-סטייט")
    assert not h.pattern("ווק").search("הווקאלי")
    assert len(h.rows()) == 100


def test_prepare_sections_and_numbers(tmp_path):
    import json
    import prepare
    md = "\n\n".join([f"Paragraph {i} says that in 1,250 cases out of 57 percent of {i * 10} things happened." * 3
                      for i in range(1, 41)] + ["![](https://x/img.png)", "https://youtu.be/abc"])
    src = tmp_path / "src.json"
    src.write_text(json.dumps({"title": "T", "markdown": md}))
    assert prepare.main([str(src), str(tmp_path / "w")]) == 0
    secs = sorted((tmp_path / "w").glob("section-*.en.md"))
    assert len(secs) >= 2 and "[P1]" in secs[0].read_text() and (tmp_path / "w" / "brief.md").exists()
    assert "1250" in prepare.numbers(md) and "57" in prepare.numbers(md) and "5" not in prepare.numbers(md)
    assert len(prepare.text_paragraphs(md)) == 40


def test_fidelity_and_process_checks():
    process = {"brief": {"tone": "polemical"},
               "review": {"independent": True, "findings": 2, "major": 1, "fixed": 2, "not_fixed": []},
               "back_translation": {"title": "t", "subtitle": "s", "quotes": ["a", "b", "c"], "meaning_kept": True}}
    source = "\n\n".join(["In 1977 the debt reached 115 percent of output and kept rising for years after that."] * 8)
    body = "\n\n".join(["בשנת 1977 הגיע החוב ל־115 אחוזים מן התוצר והמשיך לעלות שנים רבות לאחר מכן."] * 8)
    good = {**GOOD, **process, "body_he": body}
    assert not [p for p in qc.check(good, source)["problems"] if "fidelity" in p or "review" in p or "brief" in p]
    dropped = {**good, "body_he": body.replace("115", "")}
    assert any("115" in p for p in qc.check(dropped, source)["problems"])
    waived = {**dropped, "fidelity_waivers": [{"number": "115", "reason": "test"}]}
    assert not any("115" in p for p in qc.check(waived, source)["problems"])
    assert any("independent review" in p for p in qc.check({**good, "review": {}}, source)["problems"])
    assert any("meaning" in p for p in qc.check(
        {**good, "back_translation": {**process["back_translation"], "meaning_kept": False}}, source)["problems"])
    assert any("paragraphs" in p for p in qc.check({**good, "body_he": body.split("\n\n")[0]}, source)["problems"])


def test_essay_trim_and_hebrew_number_words():
    import prepare
    body = "\n\n".join(["The essay itself, which runs on for a while about 1968 and other matters of note."] * 5)
    page = ("This copy is for your personal, non-commercial use only. Distribution is governed by law.\n\n"
            "**Oct. 13, 2026 12:36 pm ET**\n\n" + body +
            "\n\n## Comments\n\n" + "\n\n".join(["A reader writes at length about 2024 and 77 other things."] * 30))
    assert len(prepare.text_paragraphs(page)) == 5
    assert prepare.numbers(prepare.essay(page)) == ["1968"]
    words = qc.hebrew_numbers("פי שלושה עשר, עשרים וחמש מאות שנה, שלוש מאות הספרטנים, בשנות השלושים והארבעים, "
                              "במאה העשרים, מאה ועשרים אלף")
    assert {"13", "25", "300", "1930", "1940", "20", "120000"} <= words
    assert "77" not in words


def test_hebcheck_unknown_words():
    import hebcheck
    reply = [{"word": "התלמידיים", "sep": False, "options": [["הַ|תַּלְמִידִיִּים", [["1", "", False]]]]},
             {"word": " ", "sep": True, "options": []},
             {"word": "הלכו", "sep": False, "options": [["הָלְכוּ", [["2", "הלך", False]]]]}]
    assert hebcheck.unknown(reply) == ["התלמידיים"]
    assert "http" not in hebcheck.clean("ראו ![תמונה](https://x/y.png) וגם https://a.b Trump")
    assert "Trump" not in hebcheck.clean("Trump אמר")


def test_mida_corpus_alignment(tmp_path, monkeypatch, capsys):
    import mida_corpus
    d = tmp_path / "001-1"; d.mkdir()
    (d / "en.md").write_text("# T\n\nThe deep state is real.\n\nSecond paragraph is here now.\n", encoding="utf-8")
    (d / "he.md").write_text("# ת\n\nהמדינה העמוקה קיימת באמת היום.\n\nפסקה שנייה נמצאת כאן עכשיו.\n", encoding="utf-8")
    idx = tmp_path / "index.csv"
    idx.write_text("n,dir,title_he,title_en,date,publication,mida_url,en_url,abridged,words_he,words_en\n"
                   "1,001-1,ת,T,2025-01-01,Commentary,u,v,0,6,8\n", encoding="utf-8")
    monkeypatch.setattr(mida_corpus, "STORE", tmp_path); monkeypatch.setattr(mida_corpus, "INDEX", idx)
    mida_corpus.search("deep state")
    out = capsys.readouterr().out
    assert "המדינה העמוקה" in out and "פסקה שנייה" not in out
    mida_corpus.count(["המדינה העמוקה"])
    assert "המדינה העמוקה: 1" in capsys.readouterr().out


def test_grammar_agreement_rules():
    import grammar

    def tok(token, pos, func, head, **feats):
        return {"token": token, "morph": {"pos": pos, "feats": feats}, "syntax": {"dep_func": func, "dep_head_idx": head}}

    def parse(*toks):
        return {"text": " ".join(t["token"] for t in toks), "tokens": list(toks)}

    bad_adj = parse(tok("החלטה", "NOUN", "root", -1, Gender="Fem", Number="Sing"),
                    tok("חשוב", "ADJ", "amod", 0, Gender="Masc", Number="Sing"))
    assert [f["rule"] for f in grammar.agreement(bad_adj)] == ["adjective-noun"]
    good_adj = parse(tok("החלטה", "NOUN", "root", -1, Gender="Fem", Number="Sing"),
                     tok("חשובה", "ADJ", "amod", 0, Gender="Fem", Number="Sing"))
    assert grammar.agreement(good_adj) == []
    bad_subj = parse(tok("הממשלה", "NOUN", "nsubj", 1, Gender="Fem", Number="Sing"),
                     tok("החליטו", "VERB", "root", -1, Number="Plur", Person="3"))
    assert [f["rule"] for f in grammar.agreement(bad_subj)] == ["subject-verb"]
    bad_num = parse(tok("שלוש", "NUM", "nummod", 1, Gender="Fem"), tok("ספרים", "NOUN", "root", -1, Gender="Masc"))
    assert [f["rule"] for f in grammar.agreement(bad_num)] == ["numeral-noun"]
    tens = parse(tok("עשרות", "NUM", "nummod", 1, Gender="Fem"), tok("ספרים", "NOUN", "root", -1, Gender="Masc"))
    assert grammar.agreement(tens) == []
    # a subject joined by ו is skipped: the parser gives only one of its parts
    conj = parse(tok("הממשלה", "NOUN", "nsubj", 3, Gender="Fem", Number="Sing"), tok("ו", "CCONJ", "cc", 2),
                 tok("הכנסת", "NOUN", "conj", 0, Gender="Fem", Number="Sing"),
                 tok("החליטו", "VERB", "root", -1, Number="Plur", Person="3"))
    assert grammar.agreement(conj) == []


def test_kohelet_index():
    import kohelet_corpus, mida_corpus
    rows = mida_corpus.rows()
    assert len(rows) == 72 and {"original", "he_url", "en_url"} <= set(rows[0])
    assert {r["original"] for r in rows} <= {"he", "en", ""}
    assert kohelet_corpus.mida_corpus.INDEX.name == "index.csv"


def test_policy_corpus_banks(capsys):
    import policy_corpus
    assert policy_corpus.use("misgav") and policy_corpus.use("jiss") and policy_corpus.use("inss")
    import mida_corpus
    assert len(list(mida_corpus.rows())) == 1201
    policy_corpus.main(["--bank", "jiss", "count", "deterrence"])
    assert capsys.readouterr().out.startswith("deterrence: ")
