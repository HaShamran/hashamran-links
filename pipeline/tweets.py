"""Tweet text and the Buffer client that sends it to @HaShamran1948.

X's official API costs $0.20 for every post with a link (2026), so tweets go through Buffer's free plan,
which posts through X's API on our behalf. Auth: env var BUFFER_API_KEY (a GitHub Actions secret).
"""
import os

import re
import unicodedata

import requests

from common import X_HANDLE

BUFFER_API = "https://api.buffer.com"
URL_PLACEHOLDER = "https://hashamran.github.io/hashamran-links/0000-00-00-placeholder-slug-for-length.html"


def compose(quote, url):
    """The tweet: the quote as Claude wrote it (citation marks and attribution included), then the relay
    link on its own line, which X shows as a large card."""
    return f"{quote.strip()}\n\n{url}"


# X's counting rules (twitter-text config v3): any link counts 23; Latin, Hebrew and most punctuation count 1;
# other characters (CJK, emoji) count 2; the limit is 280.
MAX_WEIGHT = 280
URL_WEIGHT = 23
LIGHT_RANGES = ((0, 4351), (8192, 8205), (8208, 8223), (8242, 8247))
URL_RE = re.compile(r"https?://\S+")


def tweet_weight(text):
    text = unicodedata.normalize("NFC", text)
    links = URL_RE.findall(text)
    rest = URL_RE.sub("", text)
    light = lambda c: any(lo <= ord(c) <= hi for lo, hi in LIGHT_RANGES)
    return URL_WEIGHT * len(links) + sum(1 if light(c) else 2 for c in rest)


def weighted_length(quote):
    return tweet_weight(compose(quote, URL_PLACEHOLDER))


def fits(quote):
    return weighted_length(quote) <= MAX_WEIGHT


class BufferError(RuntimeError):
    pass


class Buffer:
    def __init__(self, key=None):
        self.key = key or os.environ.get("BUFFER_API_KEY", "").strip()
        if not self.key:
            raise BufferError("BUFFER_API_KEY is not set")

    def _q(self, query, variables=None):
        r = requests.post(BUFFER_API, json={"query": query, "variables": variables or {}}, timeout=60,
                          headers={"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"})
        if r.status_code == 401:
            raise BufferError("Buffer rejected the API key (401)")
        try:
            data = r.json()
        except ValueError:
            raise BufferError(f"Buffer HTTP {r.status_code}: {r.text[:200]}") from None
        if data.get("errors"):
            raise BufferError("Buffer error: " + "; ".join(e.get("message", "") for e in data["errors"])[:300])
        return data["data"]

    def x_channel_id(self):
        """The id of the one X channel named @HaShamran1948; refuses anything else."""
        orgs = self._q("query { account { organizations { id } } }")["account"]["organizations"]
        everything = []
        for org in orgs:
            everything += self._q("query($o: OrganizationId!) { channels(input: {organizationId: $o}) { id name service } }",
                                  {"o": org["id"]})["channels"]
        found = [c for c in everything if str(c["service"]).lower() in ("twitter", "x")]
        mine = [c for c in found if c["name"].lstrip("@").lower() == X_HANDLE.lower()]
        if not mine:
            seen = [f"{c['service']}:{c['name']}" for c in everything]
            raise BufferError(f"No X channel @{X_HANDLE} in Buffer ({len(orgs)} organizations; channels: {seen})")
        return mine[0]["id"]

    def post_now(self, channel_id, text):
        q = """mutation($input: CreatePostInput!) { createPost(input: $input) {
                 ... on PostActionSuccess { post { id } }
                 ... on MutationError { message } } }"""
        res = self._q(q, {"input": {"channelId": channel_id, "text": text,
                                    "schedulingType": "automatic", "mode": "shareNow"}})["createPost"]
        if not res.get("post"):
            raise BufferError(f"Buffer refused the post: {res.get('message')}")
        return res["post"]["id"]
