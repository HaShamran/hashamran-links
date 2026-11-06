"""Top up the translation queue from older essays on the NatCon Essays page.

Hadar's rule (6 Nov 2026): at least two articles go live every day. The page adds new essays more slowly than
that, so when fewer than --min essays are queued, this promotes the newest essays that were already listed when
detection started ("baseline" in state/seen.json, in page order, newest first) into state/queue.json.
New essays found by detect.py still come first: backfill only fills the gap.

Usage:
    python pipeline/backfill.py            # top up to 3 queued
    python pipeline/backfill.py --min 4
"""
import argparse
import json

from common import STATE, iso, load_json, save_json, utcnow


def run(min_queued=3, state_dir=STATE, now=None):
    now = now or iso(utcnow())
    seen = load_json(state_dir / "seen.json", {})
    queue = load_json(state_dir / "queue.json", [])
    queued = sum(1 for q in queue if q["status"] == "queued")
    in_queue = {q["url"] for q in queue}
    added = []
    for url, entry in seen.items():  # dict order = page order at baseline, newest first
        if queued + len(added) >= min_queued:
            break
        if entry.get("status") != "baseline" or url in in_queue:
            continue
        entry["status"] = "queued"
        entry["backfilled_at"] = now
        item = {"url": url, "title": entry["title"], "first_seen": entry.get("first_seen", now),
                "status": "queued", "source": "backfill"}
        queue.append(item)
        added.append(item)
    if added:
        save_json(state_dir / "seen.json", seen)
        save_json(state_dir / "queue.json", queue)
    return {"queued_before": queued, "added": [{"url": a["url"], "title": a["title"]} for a in added]}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--min", type=int, default=3)
    args = ap.parse_args(argv)
    print(json.dumps(run(args.min), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
