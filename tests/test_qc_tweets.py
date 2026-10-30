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
    assert len(azure_corpus.rows()) == 100


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
