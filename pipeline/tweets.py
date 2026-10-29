"""Tweet text and the Buffer client that sends it to @HaShamran1948.

X's official API costs $0.20 for every post with a link (2026), so tweets go through Buffer's free plan,
which posts through X's API on our behalf. Auth: env var BUFFER_API_KEY (a GitHub Actions secret).
"""
import os

import requests
from twitter_text import parse_tweet

from common import X_HANDLE

BUFFER_API = "https://api.buffer.com"
URL_PLACEHOLDER = "https://hashamran.github.io/hashamran-links/0000-00-00-placeholder-slug-for-length.html"


def compose(quote, url):
    """The tweet: the quote as Claude wrote it (citation marks and attribution included), then the relay
    link on its own line, which X shows as a large card."""
    return f"{quote.strip()}\n\n{url}"


def weighted_length(quote):
    return parse_tweet(compose(quote, URL_PLACEHOLDER)).weightedLength


def fits(quote):
    return parse_tweet(compose(quote, URL_PLACEHOLDER)).valid


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
        found = []
        for org in orgs:
            chans = self._q("query($o: OrganizationId!) { channels(input: {organizationId: $o}) { id name service } }",
                            {"o": org["id"]})["channels"]
            found += [c for c in chans if c["service"] == "twitter"]
        mine = [c for c in found if c["name"].lstrip("@").lower() == X_HANDLE.lower()]
        if not mine:
            raise BufferError(f"No X channel @{X_HANDLE} in Buffer (found: {[c['name'] for c in found]})")
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
