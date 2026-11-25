import datetime as dt
import json

import finalize
import graphs
import publisher

CHART = "https://cdn.example.com/uploads/unemployment-chart.png"
PHOTO = "https://cdn.example.com/uploads/senate-floor.jpg"


def test_finds_embeds_drawn_and_labelled_charts_in_html():
    html = f"""<article>
      <iframe src="https://datawrapper.dwcdn.net/AbC12/3/"></iframe>
      <figure><img src="{CHART}" alt="Unemployment rate"><figcaption>Source: BLS</figcaption></figure>
      <figure><img src="{PHOTO}" alt="The Senate"><figcaption>Photo: Getty Images</figcaption></figure>
      <figure><svg></svg><figcaption>Figure 2: GDP growth</figcaption></figure>
    </article>"""
    found = graphs.from_html(html, "https://example.com/a")
    kinds = sorted(g["kind"] for g in found)
    assert kinds == ["drawn", "embed", "image"]
    assert next(g for g in found if g["kind"] == "image")["src"] == CHART


def test_markdown_charts_and_references():
    md = (f"Look at the chart below.\n\n![]({CHART})\n\n*Source: Census Bureau*\n\n"
          f"![The Capitol]({PHOTO})\n\nThis figure is $2 trillion, a public figure said.")
    found = graphs.from_markdown(md)
    assert [g["src"] for g in found if g["kind"] == "image"] == [CHART]
    assert any(g["kind"] == "reference" for g in found)
    assert graphs.from_markdown("This figure is $2 trillion. He charted a new course.") == []


def post(body):
    return {"body_he": body}


def test_check_holds_missing_unfetchable_and_embedded_charts():
    src = {"graphs": [{"kind": "image", "src": CHART, "why": "x"}]}
    ok = lambda url: True
    bad = lambda url: False
    assert graphs.check(post(f"פסקה\n\n![גרף]({CHART})"), src, ok) == []
    assert "cannot be downloaded" in graphs.check(post(f"![גרף]({CHART})"), src, bad)[0]
    assert "missing from the Hebrew" in graphs.check(post("פסקה בלי תמונה"), src, ok)[0]
    wrapped = "https://substackcdn.com/image/fetch/w_1456/" + CHART.replace("/", "%2F").replace(":", "%3A")
    assert graphs.check(post(f"![]({wrapped})"), src, ok) == []
    embed = {"graphs": [{"kind": "embed", "src": "https://datawrapper.dwcdn.net/x/", "why": "interactive chart embed"}]}
    assert "cannot copy" in graphs.check(post("טקסט"), embed, ok)[0]
    ref = {"graphs": [{"kind": "reference", "src": "", "why": "the text points at a chart ('the chart below')"}]}
    assert "no chart image" in graphs.check(post("טקסט"), ref, ok)[0]
    assert graphs.check(post("טקסט"), {"graphs": []}, bad) == []


def test_finalize_holds_post_with_missing_graph(tmp_path, monkeypatch):
    monkeypatch.setattr(finalize, "STATE", tmp_path)
    monkeypatch.setattr(finalize, "POSTS", tmp_path)
    monkeypatch.setattr(finalize.qc, "check", lambda p, s: {"pass": True, "problems": [], "style": {}})
    d = tmp_path / "2026-11-25-x-y"
    d.mkdir()
    (d / "post.json").write_text(json.dumps({"slug": "2026-11-25-x-y", "title_he": "כ", "source_url": "u",
                                             "body_he": f"![גרף]({CHART})"}), encoding="utf-8")
    (tmp_path / "queue.json").write_text(json.dumps([{"url": "u", "status": "queued"}]), encoding="utf-8")
    src = {"markdown": "", "graphs": [{"kind": "image", "src": CHART, "why": "x"}]}
    status, report = finalize.finalize(d / "post.json", src, render=False, fetch=lambda u: False)
    assert status == "held_missing_graphs"
    saved = json.loads((d / "post.json").read_text(encoding="utf-8"))
    assert "cannot be downloaded" in saved["hold_reason"]
    assert json.loads((tmp_path / "queue.json").read_text(encoding="utf-8"))[0]["status"] == "held"
    status, _ = finalize.finalize(d / "post.json", src, render=False, fetch=lambda u: True)
    assert status == "ready"


def test_publisher_holds_post_when_an_image_will_not_download(tmp_path, monkeypatch):
    class R:
        def __init__(self, code, ctype="image/png"):
            self.status_code, self.ok, self.content = code, code == 200, b"x"
            self.headers = {"content-type": ctype}
    monkeypatch.setattr(publisher.requests, "get", lambda url, **k: R(404 if "chart" in url else 200))
    fetch = publisher._downloader(str(tmp_path))
    assert fetch(PHOTO).startswith(str(tmp_path))
    try:
        fetch(CHART)
        assert False, "should have raised"
    except publisher.ImageUnavailable:
        pass
    # a held post waits HOLD_RETRY before it is tried again; the next post goes ahead meanwhile
    at = dt.datetime(2026, 11, 25, 5, tzinfo=dt.timezone.utc)
    index = [{"slug": "a", "title_he": "א", "status": "ready", "ready_at": "1"},
             {"slug": "b", "title_he": "ב", "status": "ready", "ready_at": "2"}]
    state = {"a": {"held": "chart", "held_at": at.isoformat()}}
    assert publisher.due_post(at + dt.timedelta(hours=1), [], index, state)[0]["slug"] == "b"
    assert publisher.due_post(at + dt.timedelta(hours=13), [], index, state)[0]["slug"] == "a"
