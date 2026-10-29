import datetime as dt

import publisher
import substack_doc

ISR = publisher.ISRAEL


def now(h, day=29):
    return dt.datetime(2026, 10, day, h, tzinfo=ISR).astimezone(dt.timezone.utc)


def idx(n):
    return [{"slug": f"s{i}", "title_he": f"כותרת {i}", "status": "ready", "ready_at": f"2026-10-2{i}"} for i in range(n)]


def arch_today(k):
    return [{"title": f"פורסם {i}", "slug": f"p{i}", "post_date": "2026-10-29T05:00:00Z"} for i in range(k)]


def test_hours_and_pace():
    assert publisher.due_post(now(5), [], idx(1), {})[0] is None
    assert publisher.due_post(now(7), [], idx(1), {})[0]["slug"] == "s0"
    assert publisher.due_post(now(13), arch_today(1), idx(3), {})[0] is None      # 1 a day
    assert publisher.due_post(now(10), arch_today(1), idx(7), {})[0] is None      # 2nd waits for noon
    assert publisher.due_post(now(13), arch_today(1), idx(7), {})[0]["slug"] == "s0"
    assert publisher.due_post(now(13), arch_today(2), idx(7), {})[0] is None


def test_skips_live_and_published():
    arch = [{"title": "כותרת 0", "slug": "x", "post_date": "2026-10-28T05:00:00Z"}]
    assert publisher.due_post(now(7), arch, idx(2), {})[0]["slug"] == "s1"
    assert publisher.due_post(now(7), [], idx(2), {"s0": {"published": True}})[0]["slug"] == "s1"


def test_substack_markdown_puts_author_photo_last_and_brand_cover_first():
    post = {"byline_he": "מאת א", "title_he": "כ", "body_he": "פסקה\n\n![כיתוב](https://x/a.jpg)", "author": "A",
            "author_photo": "https://x/me.jpg", "author_bio_he": "ביו", "publication": "P", "source_url": "https://s",
            "brand_cover": True, "cover_image": "https://x/cover.png"}
    md = substack_doc.substack_markdown(post)
    assert md.index("cover.png") < md.index("a.jpg") < md.index("me.jpg") < md.index("למאמר המקורי")


def test_fix_images_shrinks_author_photo_and_never_uses_it_as_cover():
    body = {"type": "doc", "content": [{"type": "image2", "attrs": {"src": "art"}},
                                       {"type": "image2", "attrs": {"src": "me"}}]}
    out, cover = substack_doc.fix_images(body, True)
    assert cover == "art" and out["content"][1]["attrs"]["resizeWidth"] == 120
