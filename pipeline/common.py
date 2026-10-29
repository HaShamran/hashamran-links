"""Shared paths, JSON helpers and Israel-time helpers for the HaShamran pipeline."""
import datetime as dt
import json
import pathlib
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).resolve().parent.parent
STATE = ROOT / "state"
POSTS = ROOT / "posts"
BRAND = ROOT / "brand"

ISRAEL = ZoneInfo("Asia/Jerusalem")
PUBLICATION_URL = "https://hashamran.substack.com"
PAGES_URL = "https://hashamran.github.io/hashamran-links"
RAW_URL = "https://raw.githubusercontent.com/HaShamran/hashamran-links/main"
X_HANDLE = "HaShamran1948"
BROWSER_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")


def load_json(path, default=None):
    try:
        return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


def save_json(path, data):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def utcnow():
    return dt.datetime.now(dt.timezone.utc)


def iso(t):
    return t.astimezone(dt.timezone.utc).isoformat(timespec="seconds")


def parse_iso(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def israel_date(t):
    return t.astimezone(ISRAEL).date()
