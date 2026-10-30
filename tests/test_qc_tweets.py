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
