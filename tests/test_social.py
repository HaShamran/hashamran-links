import datetime as dt

import social
from common import ISRAEL, iso

POST = {"slug": "2026-10-29-a-title", "title_he": "כותרת", "status": "ready", "byline_he": "מאת א",
        "quotes_he": ["ציטוט א", "ציטוט ב", "ציטוט ג"], "ready_at": "2026-10-29T03:00:00+00:00"}


def at(h, m=0, day=29):
    return dt.datetime(2026, 10, day, h, m, tzinfo=ISRAEL).astimezone(dt.timezone.utc)


def test_slots_are_israel_time_windows():
    assert social.current_slot(at(11, 5)) == "2026-10-29#0"
    assert social.current_slot(at(12, 29)) == "2026-10-29#0"
    assert social.current_slot(at(12, 31)) is None
    assert social.current_slot(at(21, 0)) == "2026-10-29#2"
    assert social.current_slot(at(9, 0)) is None


def test_one_tweet_per_slot_and_45_minute_gap():
    log = [{"slot": "2026-10-29#0", "slug": "x", "quote": 0, "at": iso(at(11, 0))}]
    assert social.tweet_due(log, at(11, 30)) is None
    assert social.tweet_due(log, at(16, 0)) == "2026-10-29#1"
    log2 = [{"slot": "2026-10-29#0", "slug": "x", "quote": 0, "at": iso(at(15, 40))}]
    assert social.tweet_due(log2, at(16, 0)) is None


def test_max_three_a_day():
    log = [{"slot": f"other#{i}", "slug": "x", "quote": i, "at": iso(at(8 + i))} for i in range(3)]
    assert social.tweet_due(log, at(16, 0)) is None


def test_choose_prefers_today_and_skips_old_and_used():
    posts = {"old": {**POST, "slug": "old"}, "today": {**POST, "slug": "today"}, "stale": {**POST, "slug": "stale"}}
    live = {"old": {"live_at": iso(at(7, day=28))}, "today": {"live_at": iso(at(7))},
            "stale": {"live_at": iso(at(7, day=26))}}
    assert social.choose(posts, live, [], at(11)) == ("today", 0)
    log = [{"slug": "today", "quote": q, "at": iso(at(8))} for q in range(3)]
    assert social.choose(posts, live, log, at(16)) == ("old", 0)
    log += [{"slug": "old", "quote": 0, "at": iso(at(8))}]
    assert social.choose(posts, live, log, at(21)) == ("old", 1)
    assert social.choose(posts, live, [], at(12, day=31)) is None  # nothing live in the last 48 hours


def test_match_live_by_title_and_relay_page_never_uses_author_photo():
    posts = {POST["slug"]: {**POST, "author_photo": "https://x/author.jpg", "cover_image": "https://x/art.jpg"}}
    live = {}
    arch = [{"title": " כותרת ", "slug": "abc", "post_date": "2026-10-29T05:00:00.000Z",
             "canonical_url": "https://hashamran.substack.com/p/abc", "cover_image": "https://x/author.jpg"}]
    assert social.match_live(posts, arch, live) == [POST["slug"]]
    page = social.relay_html(posts[POST["slug"]], live[POST["slug"]])
    assert "https://x/art.jpg" in page and "author.jpg" not in page
    assert 'twitter:card" content="summary_large_image' in page


def test_overdue_alert():
    posts = {POST["slug"]: POST}
    assert social.alerts(posts, {}, at(2, day=30)) == []
    assert "waited" in social.alerts(posts, {}, at(9, day=31))[0]


FEED = """<?xml version="1.0"?><rss version="2.0"><channel><item><title><![CDATA[כותרת]]></title>
<link>https://hashamran.substack.com/p/abc</link><pubDate>Thu, 29 Oct 2026 05:00:00 GMT</pubDate>
<enclosure url="https://cdn/x.jpg" length="0" type="image/jpeg"/></item></channel></rss>"""


def test_parse_feed():
    [a] = social.parse_feed(FEED)
    assert a == {"title": "כותרת", "slug": "abc", "post_date": "2026-10-29T05:00:00+00:00",
                 "canonical_url": "https://hashamran.substack.com/p/abc", "cover_image": "https://cdn/x.jpg"}
