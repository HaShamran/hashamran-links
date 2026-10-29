# השמרן: translation guide

The daily run follows this guide for every essay. Translator = Claude, inside the scheduled run.

## Register: תכלת (Azure)
Write the way the Hebrew edition of תכלת (Shalem Center, 1996–2012) read: serious, literate Israeli Hebrew for an educated general reader.
- Elevated but clear. Rich vocabulary and well-built sentences, never archaic, never bureaucratic, never slangy.
- Natural Hebrew syntax. Rebuild long English sentences into Hebrew ones rather than mirroring English word order. Prefer verbs over strings of nominal constructions (avoid "ביצוע של הבדיקה של").
- Full spelling (כתיב מלא) per the Academy's rules. Minimal niqqud, only to prevent a misreading.
- Hebrew punctuation: Hebrew quotation marks ״ ״ for quotes, a hyphen-less prefix before numbers and Latin script (ב־1983 with maqaf, or ב-1983).
- Biblical, Talmudic and classical Jewish sources: quote the original Hebrew text, not a back-translation.
- Well-known works and people: use the established Hebrew title or spelling (e.g. ״הרפובליקה״ לאפלטון, ג׳ון לוק, אדמונד ברק). Lesser-known English titles: translate, then give the original in parentheses the first time.
- Titles and subtitles: translate idiomatically, with a headline's punch. Do not translate word for word.
- Keep the author's argument, tone and irony intact. Do not soften, sharpen, summarise or add commentary.
- American-specific terms that an Israeli reader would not know: one short explanatory phrase in the text the first time, never a translator's essay.

## Glossary (extend as needed, keep consistent)
| English | Hebrew |
|---|---|
| nationalism / national conservatism | לאומיות / שמרנות לאומית |
| conservative, conservatism | שמרן, שמרנות |
| liberalism, liberal (classical) | ליברליזם, ליברלי |
| progressive, progressivism | פרוגרסיבי, פרוגרסיביזם |
| the West, Western civilization | המערב, הציוויליזציה המערבית |
| nation-state | מדינת לאום |
| sovereignty | ריבונות |
| the Founders | האבות המייסדים |
| the Constitution (US) | החוקה האמריקנית |
| Congress, Senate, House | הקונגרס, הסנאט, בית הנבחרים |
| Secretary of State | מזכיר המדינה |
| woke | ווֹק (first time: ״ווֹק״, התודעה הפרוגרסיבית החדשה) |
| elites | האליטות |
| net zero | אפס פליטות נטו |
| identity politics | פוליטיקת זהויות |
| the Right, the Left | הימין, השמאל |
| GOP, Republicans, Democrats | המפלגה הרפובליקנית, הרפובליקנים, הדמוקרטים |

## Procedure (two passes)
1. **Clean the source.** From the extracted JSON, keep only the essay itself: title, subtitle, body, and images that belong to the essay with their captions. Drop site navigation, teasers for other articles, "related" images, newsletter and subscription prompts, reprint notices,  and PDF page headers and footers. If the essay is behind a paywall or cut short, stop and mark it `paywalled`.
2. **Pass 1: translate** the cleaned essay completely, paragraph for paragraph, following this guide.
2b. **Author bio and photo.** If the original ends with an author bio and/or photo (extract.py returns `author_bio` and `author_photo`, and check the page itself if those look wrong), reproduce them: translate the bio into Hebrew (`author_bio_he`) and keep the photo URL (`author_photo`). The publisher adds them as a "על המחבר" section after the essay, before the credit line. Skip anything that is a newsletter or subscription prompt rather than a bio.
3. **Pass 2: review** against the English, paragraph by paragraph: nothing missing or added, numbers, names, dates and quotations exact, register consistent, glossary followed, Hebrew reads as written in Hebrew. Fix in place.
4. **Write the post file** (`posts/<slug>/post.json`, see below) with 3 tweet quotes, and run `python3 pipeline/finalize.py posts/<slug>/post.json`. If it fails, fix and rerun once; if it still fails, the post is held (never published) and the run raises an alert.

## Post file
Write `posts/<slug>/post.json` (slug = `YYYY-MM-DD-<author surname>-<title words>`, lowercase ASCII, date = the essay's date):
```json
{
  "slug": "2026-10-20-murray-france-stares-down-the-abyss-of-history",
  "source_url": "...", "queue_url": "<the url exactly as in state/queue.json>",
  "source_title": "...", "author": "...", "author_he": "...", "publication": "...", "date": "October 20, 2026",
  "title_he": "...", "subtitle_he": "...",
  "byline_he": "מאת ... | פורסם לראשונה ב־<publication> ב־<date in Hebrew>",
  "body_he": "Markdown body in Hebrew. The article's own images as ![כיתוב בעברית](url), in place. Embeds on their own line as the bare URL. Never the author photo.",
  "author_bio_he": "Hebrew translation of the author bio, if the original has one", "author_photo": "URL or empty",
  "quotes_he": ["tweet 1", "tweet 2", "tweet 3"],
  "source_paragraphs": 0, "he_paragraphs": 0
}
```
Then run `python3 pipeline/finalize.py posts/<slug>/post.json`: it runs the quality check, picks the cover (the article's first image, or a brand-kit cover when there is none), and marks the post `ready` for the publisher on dud.

## Tweet quotes (`quotes_he`)
Exactly 3, each a complete tweet without the link (the link is added automatically on its own line, and X shows the post's thumbnail):
- Lead with the single most striking, quotable sentence of the essay, verbatim from your Hebrew translation, in ״ ״. Shorten with [...] if needed, never change the meaning.
- Prefer sharp claims, memorable lines and surprising facts that make an Israeli reader want to click. No hashtags, no emoji, no clickbait wording that the essay doesn't support.
- After the quote, a short attribution or hook: who said it and what the essay is about (e.g. ״...״ דאגלס מארי על צרפת הבוערת.). If the quote is someone the author quotes, say who.
- Three different quotes from different parts of the essay. Each must fit in a tweet with the link (finalize.py checks; about 250 characters).
