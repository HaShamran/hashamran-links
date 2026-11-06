import json

import backfill


def write(d, name, data):
    (d / name).write_text(json.dumps(data), encoding="utf-8")


def test_tops_up_in_page_order_and_keeps_new_first(tmp_path):
    write(tmp_path, "seen.json", {
        "https://a.com/new": {"title": "New", "status": "queued"},
        "https://a.com/1": {"title": "One", "status": "baseline"},
        "https://a.com/2": {"title": "Two", "status": "baseline"},
        "https://a.com/3": {"title": "Three", "status": "baseline"},
    })
    write(tmp_path, "queue.json", [{"url": "https://a.com/new", "title": "New", "status": "queued"}])
    r = backfill.run(3, state_dir=tmp_path, now="2026-11-06T00:00:00+00:00")
    assert [a["title"] for a in r["added"]] == ["One", "Two"]
    q = json.loads((tmp_path / "queue.json").read_text())
    assert [x["title"] for x in q] == ["New", "One", "Two"]
    assert json.loads((tmp_path / "seen.json").read_text())["https://a.com/3"]["status"] == "baseline"
    assert backfill.run(3, state_dir=tmp_path)["added"] == []
