import json, pathlib, sys, tempfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import detect

FIXTURE = (pathlib.Path(__file__).parent / "fixture_essays.html").read_text(encoding="utf-8")


def test_parse_finds_essays_and_skips_navigation():
    urls = [i["url"] for i in detect.parse_essays(FIXTURE)]
    assert urls == [
        "https://americanmind.org/salvo/americas-net-zero-near-miss",
        "https://nationalconservatism.org/wp-content/uploads/2026/10/The-Pagan-Nationalism-of-Marco-Rubios-Athens-Speech-WSJ.pdf",
        "https://youtube.com/watch?v=beTQ02kBOc0",
        "https://firstthings.com/de-gaulle-triumphant",
    ]


def test_malformed_relative_link_recovered():
    assert detect.normalize_url("https://nationalconservatism.org/media/youtube.com/watch?si=abc&v=xyz") == "https://youtube.com/watch?v=xyz"


def test_first_run_baselines_then_detects_new():
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)
        r1 = detect.run(FIXTURE, d, now="t1")
        assert r1["status"] == "baseline" and r1["new"] == []
        newer = FIXTURE.replace("<ul>", '<ul><li><a href="https://unherd.com/2026/10/new-essay/">A New Essay</a> Someone</li>')
        r2 = detect.run(newer, d, now="t2")
        assert [n["url"] for n in r2["new"]] == ["https://unherd.com/2026/10/new-essay"]
        assert r2["queue_length"] == 1
        r3 = detect.run(newer, d, now="t3")
        assert r3["new"] == [] and r3["queue_length"] == 1


def test_layout_change_raises_alert_without_touching_queue():
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)
        detect.run(FIXTURE, d, now="t1")
        r = detect.run("<html><main><p>Maintenance</p></main></html>", d, now="t2")
        assert r["status"] == "layout_alert"
        assert json.loads((d / "queue.json").read_text()) == []


LIVE = (pathlib.Path(__file__).parent / "fixture_live.html").read_text(encoding="utf-8")


def test_live_layout_reads_essay_items_only():
    items = detect.parse_essays(LIVE)
    assert len(items) == 6
    assert not any("reclaimingconservatism" in i["url"] or "cookieadmin" in i["url"] for i in items)
    first = items[0]
    assert first["url"] == "https://americanmind.org/salvo/americas-net-zero-near-miss"
    assert first["author"] == "Rupert Darwall"
    assert first["title"] == "America’s Net Zero Near Miss"
    assert first["publication"] == "American Mind"
    assert first["date"] == "October 15, 2026"
    assert items[3]["date"] == "October 13, 2026"  # page writes "October 13,2026"


def test_x_article_markdown_keeps_text_and_images():
    import extract
    article = {"cover_media": {"media_info": {"original_img_url": "https://pbs.twimg.com/c.jpg"}},
               "media_entities": [{"media_id": "7", "media_info": {"original_img_url": "https://pbs.twimg.com/m.jpg"}}],
               "content": {"entityMap": [{"key": "0", "value": {"data": {"mediaItems": [{"mediaId": "7"}]}}}],
                           "blocks": [{"type": "header-two", "text": "Head", "entityRanges": []},
                                      {"type": "unstyled", "text": "Para", "entityRanges": []},
                                      {"type": "atomic", "text": " ", "entityRanges": [{"key": 0}]}]}}
    assert extract.x_article_markdown(article).split("\n\n") == [
        "![](https://pbs.twimg.com/c.jpg)", "## Head", "Para", "![](https://pbs.twimg.com/m.jpg)"]
