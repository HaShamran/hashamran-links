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

## Glossary
The house glossary is `pipeline/glossary.json`: for each term, the English (`en`), our Hebrew (`he`), variants we
do not use (`avoid`) and a `note`. Follow it everywhere, keep it consistent, and extend it (see the translation
log below). `qc.py` fails a post that uses an `avoid` variant.

## Translation log
`pipeline/TRANSLATION-LOG.md` is our memory between runs. **Read it before translating** and **add to it after
each essay** (format at the top of the log). Record anything that will help the next translation:
- Terms unique to our sphere of discourse (movements, institutions, slogans, people, coined phrases) and the
  Hebrew we chose, with the reason.
- Hard calls: idioms, irony, puns, American references, titles of books and articles.
- What passes 2 and 3 caught in pass 1 (recurring errors are the most useful entries).
- Every correction from Hadar or a reader, verbatim, and what rule it implies.
When a term has been used the same way twice, or Hadar settles it, add it to `glossary.json` (with any wrong
variants under `avoid`) and mark the log entry `→ glossary`. A recurring style lesson goes into this guide.

## Procedure (three passes)
0. **Read** `pipeline/glossary.json` and `pipeline/TRANSLATION-LOG.md`.
1. **Clean the source.** From the extracted JSON, keep only the essay itself: title, subtitle, body, and images that belong to the essay with their captions. Drop site navigation, teasers for other articles, "related" images, newsletter and subscription prompts, reprint notices,  and PDF page headers and footers. If the essay is behind a paywall or cut short, stop and mark it `paywalled`.
2. **Pass 1: translate** the cleaned essay completely, paragraph for paragraph, following this guide. Note every term you had to decide on.
2b. **Author bio and photo.** If the original ends with an author bio and/or photo (extract.py returns `author_bio` and `author_photo`, and check the page itself if those look wrong), reproduce them: translate the bio into Hebrew (`author_bio_he`) and keep the photo URL (`author_photo`). The publisher adds them as a "על המחבר" section after the essay, before the credit line. Skip anything that is a newsletter or subscription prompt rather than a bio.
3. **Pass 2: review**, in two readings. Fix in place.
   - **2a. Fidelity, against the English**, paragraph by paragraph: nothing missing or added, numbers, names, dates and quotations exact, tone and irony kept.
   - **2b. Hebrew only, as an editor of תכלת would read it**, without looking at the English:
     - Glossary consistency: every glossary term in its house form, and every new term rendered the same way throughout (names, institutions, recurring phrases). Same person, same spelling.
     - Grammar: gender and number agreement (verbs, adjectives, numerals), construct state (סמיכות), the definite article in construct, prepositions governed by the verb, the ־ש/אשר clauses, tense consistency.
     - Translationese: English word order, chains of nominal constructions, "עושה שימוש", "הוא זה ש", calques of English idioms, too many possessive "של".
     - Spelling and punctuation: full spelling (כתיב מלא), ״ ״ quotation marks (never "), maqaf before numbers and Latin script, no stray Latin words except where the guide keeps them.
4. **Pass 3: the title.** A separate pass, after the body is final:
   - Write at least 3 candidate Hebrew titles (`title_options_he`): one close to the original, and others that carry its punch the way a Hebrew editor would headline it (wordplay, a Hebrew or Jewish echo only when it fits the essay, a sharp claim from the body).
   - Choose the one that is accurate to the argument, idiomatic, short (under 80 characters), and makes an Israeli reader want to read. No clickbait the essay doesn't support. Put it in `title_he` (it stays in `title_options_he`).
   - Then check the subtitle (`subtitle_he`) against the chosen title: it should complete it, not repeat it.
   - Log the candidates and why the winner won in the translation log.
5. **Write the post file** (`posts/<slug>/post.json`, see below) with 3 tweet quotes, and run `python3 pipeline/finalize.py posts/<slug>/post.json`. If it fails, fix and rerun once; if it still fails, the post is held (never published) and the run raises an alert.
6. **Update the translation log** (and the glossary, when a term is settled).

## Post file
Write `posts/<slug>/post.json` (slug = `YYYY-MM-DD-<author surname>-<title words>`, lowercase ASCII, date = the essay's date):
```json
{
  "slug": "2026-10-20-murray-france-stares-down-the-abyss-of-history",
  "source_url": "...", "queue_url": "<the url exactly as in state/queue.json>",
  "source_title": "...", "author": "...", "author_he": "...", "publication": "...", "date": "October 20, 2026",
  "title_he": "...", "title_options_he": ["<chosen title>", "...", "..."], "subtitle_he": "...",
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
