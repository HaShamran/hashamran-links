"""HaShamran publisher: runs on dud every 30 minutes (Windows Task Scheduler) and publishes the next
translated post to hashamran.substack.com, web only, no email. Plain Python, no Claude, no prompts.

Usage (run.cmd and login.cmd call these):
    publisher.py run        # scheduled: publish what is due, if anything
    publisher.py login      # opens the automation Chrome window so Hadar can sign in to Substack once
    publisher.py check      # says whether the automation profile is signed in

Why dud: Substack refuses publish calls from cloud servers (403, Oct 2026). From dud's home connection,
with the cookies of a Chrome profile Hadar signed into, the same call is an ordinary signed-in publish.
If Substack still refuses the API call, the script presses Publish in that Chrome profile itself.

Pace (Hadar): 1 post a day, 2 when more than 5 are waiting; the second not before 12:00 Israel time.
Hours: 06:00 to 22:00 Israel time. Every file it writes lives in %LOCALAPPDATA%\\HaShamran.
"""
import base64
import datetime as dt
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
from zoneinfo import ZoneInfo

import requests

APP = pathlib.Path(__file__).resolve().parent
DATA = pathlib.Path(os.environ.get("LOCALAPPDATA", str(pathlib.Path.home()))) / "HaShamran"
PROFILE = DATA / "chrome-profile"
LOGS = DATA / "logs"
STATE_FILE = DATA / "published.json"
STATUS_FILE = pathlib.Path(os.environ.get("HASHAMRAN_STATUS_DIR", str(DATA))) / "publisher-status.txt"
LOCK = DATA / "publisher.lock"

PUB = "https://hashamran.substack.com"
RAW = "https://raw.githubusercontent.com/HaShamran/hashamran-links/main"
ISRAEL = ZoneInfo("Asia/Jerusalem")
HOURS = (6, 22)
SECOND_POST_HOUR = 12
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
SELF_FILES = ("dud/publisher.py", "pipeline/substack_doc.py")
EXCLUDED_DRAFTS = {221560286}  # Hadar's old RTL test draft: never publish


class LoginNeeded(RuntimeError):
    pass


def log(msg):
    LOGS.mkdir(parents=True, exist_ok=True)
    line = f"{dt.datetime.now(ISRAEL):%Y-%m-%d %H:%M:%S} {msg}"
    with open(LOGS / f"publisher-{dt.date.today():%Y-%m}.log", "a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line)


def status(msg):
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATUS_FILE.write_text(f"{dt.datetime.now(ISRAEL):%Y-%m-%d %H:%M} {msg}\n", encoding="utf-8")


def load(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        return default


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def norm(title):
    return re.sub(r"\s+", " ", title or "").strip()


def update_self():
    """Fetch the newest publisher code from the repo, so fixes reach dud without anyone touching it."""
    changed = False
    for rel in SELF_FILES:
        try:
            r = requests.get(f"{RAW}/{rel}", params={"t": int(time.time())}, timeout=30)
            if not r.ok or len(r.content) < 500:
                continue
            target = APP / pathlib.Path(rel).name
            if not target.exists() or target.read_bytes() != r.content:
                target.write_bytes(r.content)
                changed = True
        except requests.RequestException:
            pass
    return changed


# ---------- Chrome automation profile ----------

def _context(pw, headless=True):
    PROFILE.mkdir(parents=True, exist_ok=True)
    return pw.chromium.launch_persistent_context(str(PROFILE), channel="chrome", headless=headless,
                                                 args=["--disable-blink-features=AutomationControlled"],
                                                 viewport={"width": 1280, "height": 900})


def substack_cookies():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        ctx = _context(pw)
        cookies = ctx.cookies(["https://substack.com", PUB])
        ctx.close()
    jar = {c["name"]: c["value"] for c in cookies if c["domain"].endswith("substack.com")}
    if "substack.sid" not in jar:
        raise LoginNeeded("the automation Chrome profile is not signed in to Substack")
    return "; ".join(f"{k}={v}" for k, v in jar.items())


def login():
    from playwright.sync_api import sync_playwright
    print("A Chrome window will open. Sign in to Substack there, then close the window.")
    with sync_playwright() as pw:
        ctx = _context(pw, headless=False)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(f"https://substack.com/sign-in?redirect=%2Fpublish&for_pub=hashamran")
        try:
            while ctx.pages:
                time.sleep(1)
        except Exception:
            pass
        try:
            ctx.close()
        except Exception:
            pass
    return check()


def github_ok():
    try:
        return subprocess.run([gh(), "auth", "status"], capture_output=True, text=True).returncode == 0
    except Exception:
        return False


def check():
    try:
        api = connect()
        print(f"Signed in to Substack (user {api.get_user_id()}).")
    except LoginNeeded as e:
        print(f"Not signed in: {e}. Run login.cmd.")
        status("ACTION NEEDED: double-click login.cmd and sign in to Substack")
        return 3
    if not github_ok():
        print("GitHub CLI is not signed in. Run setup.cmd again.")
        status("ACTION NEEDED: GitHub sign-in missing; run the installer line again")
        return 3
    status("OK, signed in to Substack and GitHub")
    return 0


def connect():
    from substack import Api
    try:
        api = Api(cookies_string=substack_cookies(), publication_url=PUB)
        api.get_user_id()
    except LoginNeeded:
        raise
    except Exception as e:
        raise LoginNeeded(f"Substack rejected the saved sign-in ({type(e).__name__})") from None
    return api


# ---------- what is due ----------

def archive():
    r = requests.get(f"{PUB}/api/v1/archive", params={"sort": "new", "limit": 50}, timeout=60)
    r.raise_for_status()
    return r.json()


def due_post(now, arch, index, state):
    """The next post to publish now, or (None, reason)."""
    local = now.astimezone(ISRAEL)
    if not HOURS[0] <= local.hour < HOURS[1]:
        return None, "outside publishing hours"
    live_titles = {norm(a["title"]) for a in arch}
    live_slugs = {a["slug"] for a in arch}
    waiting = [p for p in index if p.get("status") == "ready"
               and norm(p["title_he"]) not in live_titles
               and p.get("substack_slug") not in live_slugs
               and not state.get(p["slug"], {}).get("published")]
    if not waiting:
        return None, "nothing waiting"
    waiting.sort(key=lambda p: p.get("ready_at", ""))
    today = sum(1 for a in arch
                if dt.datetime.fromisoformat(a["post_date"].replace("Z", "+00:00")).astimezone(ISRAEL).date() == local.date())
    allowance = 2 if len(waiting) > 5 else 1
    if today >= allowance:
        return None, f"daily cap reached ({today} today, {len(waiting)} waiting)"
    if today >= 1 and local.hour < SECOND_POST_HOUR:
        return None, "second post waits until 12:00"
    return waiting[0], f"{len(waiting)} waiting, {today} published today"


# ---------- telling the repo what is live ----------
# Substack refuses its archive and feed to GitHub Actions, so dud (which can read them) writes one small file
# per live post, state/live/<slug>.json, through the GitHub CLI that setup signed in. The Action reads those.

REPO = "HaShamran/hashamran-links"


def gh():
    exe = shutil.which("gh") or r"C:\Program Files\GitHub CLI\gh.exe"
    if not pathlib.Path(exe).exists() and not shutil.which("gh"):
        raise RuntimeError("GitHub CLI (gh) is not installed; run setup.cmd again")
    return exe


def report_live(index, arch, state):
    """Write state/live/<slug>.json for every ready post that is live on Substack and not yet reported."""
    by_title = {norm(a["title"]): a for a in arch}
    by_slug = {a["slug"]: a for a in arch}
    for p in index:
        a = by_slug.get(p.get("substack_slug")) or by_title.get(norm(p["title_he"]))
        entry = state.setdefault(p["slug"], {}) if a else None
        if not a or entry.get("reported"):
            continue
        record = {"url": a.get("canonical_url") or f"{PUB}/p/{a['slug']}",
                  "live_at": dt.datetime.fromisoformat(a["post_date"].replace("Z", "+00:00")).isoformat(timespec="seconds"),
                  "cover": a.get("cover_image") or ""}
        content = base64.b64encode((json.dumps(record, ensure_ascii=False, indent=2) + "\n").encode()).decode()
        path = f"repos/{REPO}/contents/state/live/{p['slug']}.json"
        exists = subprocess.run([gh(), "api", path, "--jq", ".sha"], capture_output=True, text=True)
        args = [gh(), "api", "-X", "PUT", path, "-f", f"message=live: {p['slug']}", "-f", f"content={content}"]
        if exists.returncode == 0 and exists.stdout.strip():
            args += ["-f", f"sha={exists.stdout.strip()}"]
        res = subprocess.run(args, capture_output=True, text=True)
        if res.returncode != 0:
            log(f"could not report {p['slug']} as live: {res.stderr.strip()[:200]}")
            continue
        entry.update(reported=True, published=True, url=record["url"])
        save(STATE_FILE, state)
        log(f"reported live: {p['slug']} -> {record['url']}")


# ---------- building and publishing ----------

def _downloader(tmpdir):
    def fetch(url):
        if not url.startswith("http"):
            return url
        r = requests.get(url, headers={"User-Agent": UA}, timeout=60)
        if r.status_code in (403, 429):
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=60)
        r.raise_for_status()
        ext = {"image/png": ".png", "image/gif": ".gif", "image/webp": ".webp"}.get(
            r.headers.get("content-type", "").split(";")[0], ".jpg")
        path = pathlib.Path(tmpdir) / f"img{len(list(pathlib.Path(tmpdir).iterdir()))}{ext}"
        path.write_bytes(r.content)
        return str(path)
    return fetch


def build_draft(api, post):
    import substack_doc
    with tempfile.TemporaryDirectory() as tmp:
        md = substack_doc.substack_markdown(post, _downloader(tmp))
        res = api.create_draft_from_markdown(title=post["title_he"], subtitle=post.get("subtitle_he", ""),
                                             markdown=md, slug=post.get("substack_slug"))
    draft = res["draft"]
    body, cover = substack_doc.fix_images(draft.get("draft_body") or "{}", bool(post.get("author_photo")))
    body, _ = substack_doc.embed_videos(body)
    update = {"draft_body": json.dumps(body, ensure_ascii=False)}
    if cover:
        update["cover_image"] = cover
    api.put_draft(draft["id"], **update)
    return draft["id"]


def publish_api(api, draft_id):
    api.prepublish_draft(draft_id)
    api.publish_draft(draft_id, send=False, share_automatically=False)


def publish_ui(draft_id):
    """Fallback: press Publish in the signed-in Chrome profile. Web only: if the only button would email
    subscribers, stop and leave a screenshot instead."""
    from playwright.sync_api import sync_playwright
    shot = LOGS / f"publish-ui-{draft_id}-{int(time.time())}.png"
    with sync_playwright() as pw:
        ctx = _context(pw)
        page = ctx.new_page()
        try:
            page.goto(f"{PUB}/publish/post/{draft_id}", wait_until="domcontentloaded", timeout=90000)
            if "sign-in" in page.url:
                raise LoginNeeded("Substack asked for sign-in in the editor")
            page.get_by_role("button", name=re.compile(r"^\s*Continue", re.I)).first.click(timeout=30000)
            page.wait_for_timeout(3000)
            for box in page.get_by_role("checkbox", name=re.compile(r"email|send", re.I)).all():
                if box.is_checked():
                    box.uncheck()
            buttons = page.get_by_role("button", name=re.compile(r"publish", re.I))
            names = [b.inner_text().strip() for b in buttons.all()]
            safe = [i for i, n in enumerate(names) if re.search(r"publish", n, re.I) and not re.search(r"send|email", n, re.I)]
            if not safe:
                raise RuntimeError(f"no web-only publish button (saw {names})")
            buttons.nth(safe[-1]).click()
            page.wait_for_timeout(3000)
            confirm = page.get_by_role("button", name=re.compile(r"publish (now|without)", re.I))
            if confirm.count():
                confirm.first.click()
                page.wait_for_timeout(5000)
        except Exception:
            page.screenshot(path=str(shot), full_page=True)
            raise
        finally:
            ctx.close()


def wait_live(post, tries=12):
    for _ in range(tries):
        for a in archive():
            if norm(a["title"]) == norm(post["title_he"]) or a["slug"] == post.get("substack_slug"):
                return a.get("canonical_url") or f"{PUB}/p/{a['slug']}"
        time.sleep(10)
    return None


def run():
    if LOCK.exists() and time.time() - LOCK.stat().st_mtime < 25 * 60:
        log("another run is still going; skipping")
        return 0
    DATA.mkdir(parents=True, exist_ok=True)
    LOCK.write_text(str(os.getpid()))
    try:
        return _run()
    finally:
        LOCK.unlink(missing_ok=True)


def _run():
    now = dt.datetime.now(dt.timezone.utc)
    state = load(STATE_FILE, {})
    index = requests.get(f"{RAW}/posts/index.json", params={"t": int(time.time())}, timeout=60).json()
    arch = archive()
    api = connect()  # every run proves the Substack sign-in still works, so the status file is a real health check
    gh_ok = github_ok()
    if gh_ok:
        report_live(index, arch, state)
    post_meta, reason = due_post(now, arch, index, state)
    if not post_meta:
        log(f"nothing to publish: {reason}")
        if gh_ok:
            status(f"OK, signed in; nothing to publish ({reason})")
        else:
            status("ACTION NEEDED: GitHub sign-in missing; run the installer line again")
        return 0
    slug = post_meta["slug"]
    log(f"due: {slug} ({reason})")
    post = requests.get(f"{RAW}/posts/{slug}/post.json", params={"t": int(time.time())}, timeout=60).json()
    entry = state.setdefault(slug, {})
    draft_id = entry.get("draft_id") or post.get("substack_draft_id")
    if draft_id and int(draft_id) in EXCLUDED_DRAFTS:
        raise RuntimeError(f"{slug} points at the excluded test draft")
    if draft_id:
        try:
            d = api.get_draft(draft_id)
            if d.get("is_published"):
                entry.update(published=True, url=d.get("canonical_url"))
                save(STATE_FILE, state)
                log(f"{slug} was already published")
                return 0
        except Exception:
            log(f"draft {draft_id} for {slug} is gone; building a new one")
            draft_id = None
    if not draft_id:
        draft_id = build_draft(api, post)
        entry["draft_id"] = draft_id
        save(STATE_FILE, state)  # remember it at once, so a failure never makes a second copy
        log(f"draft {draft_id} built for {slug}")
    try:
        publish_api(api, draft_id)
        how = "api"
    except Exception as e:
        log(f"API publish refused ({str(e)[:200]}); pressing Publish in Chrome instead")
        publish_ui(draft_id)
        how = "browser"
    url = wait_live(post)
    if not url:
        raise RuntimeError(f"published {slug} via {how} but it is not in the archive yet")
    entry.update(published=True, url=url, published_at=now.isoformat(timespec="seconds"), how=how)
    save(STATE_FILE, state)
    log(f"PUBLISHED {slug} -> {url} (via {how})")
    report_live(index, archive(), state)
    status(f"OK, published {url}")
    return 0


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    cmd = argv[0] if argv else "run"
    if cmd == "run" and "--no-update" not in argv and update_self():
        os.execv(sys.executable, [sys.executable, str(APP / "publisher.py"), "run", "--no-update"])
    sys.path.insert(0, str(APP))
    try:
        if cmd == "login":
            return login()
        if cmd == "check":
            return check()
        return run()
    except LoginNeeded as e:
        log(f"SIGN-IN NEEDED: {e}")
        status("ACTION NEEDED: double-click login.cmd and sign in to Substack")
        return 3
    except Exception as e:
        log("ERROR " + "".join(traceback.format_exception_only(type(e), e)).strip())
        log(traceback.format_exc())
        status(f"ERROR: {str(e)[:300]}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
