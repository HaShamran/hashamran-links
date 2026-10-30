"""Last step of the daily cloud run for each translated post: quality check, cover choice, mark ready.

Usage:
    python pipeline/finalize.py posts/<slug>/post.json /tmp/<slug>.src.json

The second argument is extract.py's output for the essay: the quality check compares the Hebrew with it.

Passing posts become status "ready" and appear in posts/index.json, which the publisher on dud reads.
Failing posts become "draft_failed_qc" (never published; the morning report and the Action raise an alert).
Exit 0 = ready, 2 = failed the check.
"""
import html
import json
import pathlib
import re
import sys

import qc
from common import BRAND, PAGES_URL, POSTS, STATE, iso, load_json, save_json, utcnow


def substack_slug(slug):
    """2026-10-20-murray-france-stares-down → murray-france-stares-down (Substack URL /p/<this>)."""
    return re.sub(r"^\d{4}-\d{2}-\d{2}-", "", slug)[:80].strip("-")


def first_article_image(post):
    for m in re.finditer(r"!\[[^\]]*\]\(([^)\s]+)\)", post.get("body_he", "")):
        if m.group(1) != post.get("author_photo"):
            return m.group(1)
    return ""


def render_cover(post, out_path):
    """Brand-kit cover (navy, Frank Ruhl Libre, logo) for posts with no image of their own."""
    from playwright.sync_api import sync_playwright
    tpl = (BRAND / "post-cover.html").read_text(encoding="utf-8")
    page_html = (tpl.replace("{{TITLE}}", html.escape(post["title_he"]))
                    .replace("{{AUTHOR}}", html.escape(post.get("author_he") or post["author"]))
                    .replace("{{SOURCE}}", html.escape(post["publication"]))
                    .replace("../logo.svg", "logo.svg"))
    tmp = BRAND / f".render-{post['slug']}.html"
    tmp.write_text(page_html, encoding="utf-8")
    try:
        with sync_playwright() as pw:
            exe = pathlib.Path("/opt/pw-browsers/chromium")
            browser = pw.chromium.launch(**({"executable_path": str(exe)} if exe.is_file() else {}))
            page = browser.new_page(viewport={"width": 1200, "height": 630})
            page.goto(tmp.as_uri(), wait_until="networkidle")
            page.evaluate("document.fonts.ready")
            page.evaluate("""() => { const h = document.querySelector('.h'); let s = 96;
                while (document.querySelector('.w').scrollHeight > 630 && s > 48) { s -= 4; h.style.fontSize = s + 'px'; } }""")
            page.screenshot(path=str(out_path), clip={"x": 0, "y": 0, "width": 1200, "height": 630})
            browser.close()
    finally:
        tmp.unlink(missing_ok=True)


def rebuild_index():
    """posts/index.json: the short list the publisher on dud reads."""
    index = []
    for f in sorted(POSTS.glob("*/post.json")):
        p = load_json(f)
        index.append({k: p.get(k) for k in ("slug", "title_he", "status", "ready_at", "substack_slug", "substack_draft_id")})
    save_json(POSTS / "index.json", index)
    return index


def finalize(path, source_markdown, render=True):
    path = pathlib.Path(path)
    post = load_json(path)
    report = qc.check(post, source_markdown)
    post["style"] = report["style"]
    if not report["pass"]:
        post["status"] = "draft_failed_qc"
        post["qc_problems"] = report["problems"]
    else:
        image = first_article_image(post)
        if image:
            post.update(cover_image=image, brand_cover=False)
        elif render:
            render_cover(post, path.parent / "cover.png")
            post.update(cover_image=f"{PAGES_URL}/posts/{post['slug']}/cover.png", brand_cover=True)
        post.setdefault("substack_slug", substack_slug(post["slug"]))
        post["status"] = "ready"
        post.setdefault("ready_at", iso(utcnow()))
        post.pop("qc_problems", None)
    save_json(path, post)
    queue = load_json(STATE / "queue.json", [])
    for q in queue:
        if q["url"] == post.get("source_url") or q["url"] == post.get("queue_url"):
            q["status"] = "translated" if post["status"] == "ready" else "failed_qc"
            q["post"] = f"posts/{post['slug']}/post.json"
    save_json(STATE / "queue.json", queue)
    rebuild_index()
    return post["status"], report


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) < 2:
        print("usage: finalize.py posts/<slug>/post.json /tmp/<slug>.src.json (the English is required)")
        return 2
    source = load_json(pathlib.Path(argv[1])).get("markdown", "")
    status, report = finalize(argv[0], source)
    print(json.dumps({"status": status, **report}, ensure_ascii=False, indent=2))
    return 0 if status == "ready" else 2


if __name__ == "__main__":
    sys.exit(main())
