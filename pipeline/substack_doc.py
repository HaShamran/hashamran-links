"""Builds the Substack draft for a post: Markdown for python-substack, then Hadar's image rules applied to
Substack's document. Used by the publisher on dud (dud/publisher.py); no network here except image fetches
the caller supplies.

Image rules (Hadar, 2026-10-23): the article's own images stay in place; the author photo is small (120px)
and only in the "על המחבר" section at the bottom; it is never the cover or share image. When the article has
no image of its own, the brand-kit cover goes first, because Substack's share card uses the first image.
"""
import json
import re

CREDIT = "המאמר תורגם לעברית בידי מערכת ״השמרן״."
AUTHOR_PHOTO_WIDTH = 120
IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)")
YOUTUBE_RE = re.compile(r"^https?://(?:www\.|m\.)?(?:youtube(?:-nocookie)?\.com/(?:watch\?v=|embed/|shorts/|live/)"
                        r"|youtu\.be/)([\w-]{11})")


def credit_md(post):
    return f"> {CREDIT} [למאמר המקורי ב־{post['publication']}]({post['source_url']})"


def bio_md(post):
    """'About the author' section, when the original essay has an author bio and/or photo."""
    if not (post.get("author_bio_he") or post.get("author_photo")):
        return ""
    parts = ["**על המחבר**"]
    if post.get("author_photo"):
        parts.append(f"![{post.get('author_he') or post['author']}]({post['author_photo']})")
    if post.get("author_bio_he"):
        parts.append(post["author_bio_he"].strip())
    return "\n\n".join(parts)


def substack_markdown(post, fetch_image=lambda url: url):
    """Byline, (brand cover,) body with every image fetched to a local file and its caption as the image
    title, author section, credit line."""
    blocks = [f"*{post['byline_he']}*"]
    body = post["body_he"].strip()
    if post.get("brand_cover") and post.get("cover_image"):
        blocks.append(f"![{post['title_he']}]({fetch_image(post['cover_image'])})")
    for block in re.split(r"\n\s*\n", body):
        b = block.strip()
        img = IMG_RE.fullmatch(b)
        if img:
            cap = img.group(1).replace('"', "״")
            blocks.append(f'![{cap}]({fetch_image(img.group(2))} "{cap}")')
        else:
            blocks.append(b)
    bio = bio_md(post)
    if bio:
        for b in bio.split("\n\n"):
            img = IMG_RE.fullmatch(b)
            blocks.append(f"![{img.group(1)}]({fetch_image(img.group(2))})" if img else b)
    blocks.append(credit_md(post))
    return "\n\n".join(blocks) + "\n"


def walk(body):
    """Every node of a Substack document, in document order."""
    stack = [body] if body else []
    while stack:
        n = stack.pop()
        if isinstance(n, dict):
            yield n
            stack.extend(reversed(n.get("content") or []))


def fix_images(body, has_author_photo):
    """Shrinks the author photo (the last image when there is one) and returns (body, cover src): the first
    image that is not the author photo."""
    if isinstance(body, str):
        body = json.loads(body)
    images = [n for n in walk(body) if n.get("type") == "image2"]
    author_img = images[-1] if has_author_photo and images else None
    if author_img:
        author_img["attrs"].update(resizeWidth=AUTHOR_PHOTO_WIDTH, imageSize="normal", fullscreen=False)
    cover = next((n["attrs"]["src"] for n in images if n is not author_img), None)
    return body, cover


def embed_videos(body):
    """Turns each paragraph that is only a YouTube link into Substack's video player."""
    if isinstance(body, str):
        body = json.loads(body)
    count = 0
    for i, node in enumerate(body.get("content") or []):
        if node.get("type") != "paragraph":
            continue
        text = "".join(c.get("text", "") for c in node.get("content") or []).strip()
        m = YOUTUBE_RE.match(text)
        if m and " " not in text:
            body["content"][i] = {"type": "youtube2", "attrs": {"videoId": m.group(1), "startTime": None, "endTime": None}}
            count += 1
    return body, count
