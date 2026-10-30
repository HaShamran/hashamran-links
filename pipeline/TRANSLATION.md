# השמרן: translation guide

The daily run follows this guide for every essay. Translator = Claude, inside the scheduled run.

## Register: תכלת (Azure)
Write the way the Hebrew edition of תכלת (Shalem Center, 1996–2012) read: serious, literate Israeli Hebrew for an educated general reader.
**`pipeline/azure/STYLE.md` is the detailed model**, drawn from 100 essays published in both Azure and תכלת: syntax,
connectives, idiom, typography and a term bank. `pipeline/azure_corpus.py` searches those pairs to show how תכלת
rendered a word or phrase.
**Secondary guide, for terms תכלת never needed** (woke, populism, DEI, the deep state): 100 recent essays from
השילוח, searched with `pipeline/hashiloach_corpus.py`. Where the two differ on voice or style, תכלת wins.
- Elevated but clear. Rich vocabulary and well-built sentences, never archaic, never bureaucratic, never slangy.
- Natural Hebrew syntax. Rebuild long English sentences into Hebrew ones rather than mirroring English word order. Prefer verbs over strings of nominal constructions (avoid "ביצוע של הבדיקה של").
- Full spelling (כתיב מלא) per the Academy's rules. Minimal niqqud, only to prevent a misreading.
- Hebrew punctuation: Hebrew quotation marks ״ ״ for quotes, a hyphen-less prefix before numbers and Latin script (ב־1983 with maqaf, or ב-1983).
- Biblical, Talmudic and classical Jewish sources: quote the original Hebrew text, not a back-translation. Get it with `python3 pipeline/lookup.py source "Deuteronomy 17:13"` (Sefaria); give the reference in Hebrew form if the author gives one.
- Well-known works and people: check `python3 pipeline/lookup.py name "John Locke" "Democracy in America"` (Hebrew Wikipedia) and use the established Hebrew title or spelling (e.g. ״הרפובליקה״ לאפלטון, ג׳ון לוק, אדמונד ברק). Lesser-known English titles: translate, then give the original in parentheses the first time.
- Titles and subtitles: translate idiomatically, with a headline's punch. Do not translate word for word.
- Keep the author's argument, tone and irony intact. Do not soften, sharpen, summarise or add commentary.
- American-specific terms: use the Hebrew form and the standard first-use explanation in `pipeline/US-POLITICS.md`, so the same term is explained the same way in every post. One short phrase in the text, the first time only, never a translator's essay.

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

## Procedure
The translator translates. A separate reviewer revises (ISO 17100: revision by someone other than the
translator; a model checking its own fresh work misses most of its errors). Everything is automatic.

0. **Read** `pipeline/azure/STYLE.md`, `pipeline/US-POLITICS.md`, `pipeline/glossary.json` and
   `pipeline/TRANSLATION-LOG.md`, and run `python3 pipeline/azure_corpus.py fetch && python3 pipeline/hashiloach_corpus.py fetch`.
1. **Clean the source.** From the extracted JSON, keep only the essay itself: title, subtitle, body, and images that belong to the essay with their captions. Drop site navigation, teasers for other articles, "related" images, newsletter and subscription prompts, reprint notices,  and PDF page headers and footers (edit the `markdown` field of `/tmp/<slug>.src.json` in place). If the essay is behind a paywall or cut short, stop and mark it `paywalled`.
2. **Prepare and brief.** `python3 pipeline/prepare.py /tmp/<slug>.src.json /tmp/<slug>/` splits the essay into
   numbered paragraphs ([P1], [P2]...) and sections of about 1,400 words, and starts `brief.md` and `memory.md`.
   Before translating a word, fill in the brief: the author's tone, what an Israeli reader will not know, the
   American allusions to localize and how, the hard terms, and the names with their Hebrew spelling
   (`lookup.py name`). It goes into `post.json` as `brief` (an object with those five keys).
3. **Pass 1: translate section by section.** For each section, read `memory.md` first, translate the section
   completely, paragraph for paragraph, following this guide, then add to `memory.md` every name and term
   settled in it. A name or term in memory is never rendered differently later. For any term or idiom the
   glossary and US-POLITICS.md do not settle, run `python3 pipeline/azure_corpus.py search "<english>"` and follow
   תכלת where it is consistent; for a term newer than 2012, check `python3 pipeline/hashiloach_corpus.py count
   <Hebrew candidates>` and use השילוח's form.
3b. **Author bio and photo.** If the original ends with an author bio and/or photo (extract.py returns `author_bio` and `author_photo`, and check the page itself if those look wrong), reproduce them: translate the bio into Hebrew (`author_bio_he`) and keep the photo URL (`author_photo`). The publisher adds them as a "על המחבר" section after the essay, before the credit line. Skip anything that is a newsletter or subscription prompt rather than a bio.
4. **Title, subtitle and tweet quotes (draft).** Read `pipeline/azure/TITLES.md`. Write at least 3 candidate titles
   (`title_options_he`): one close to the original and at least one using a תכלת move (a Hebrew pun in place of
   an English one, a Hebrew or Jewish echo, the real subject in place of an American allusion, antithesis,
   topic: angle). Choose the one that is accurate, idiomatic, under 80 characters and makes an Israeli reader
   want to read; no clickbait. The subtitle completes the title, never repeats it. Choose the 3 tweet quotes
   (below). Write the draft `posts/<slug>/post.json`.
5. **Independent review: passes 2 and 3, and the back-translation**, exactly as `pipeline/REVIEWER.md` says:
   a blind back-translator (Hebrew title, subtitle and quotes only), then a reviewer that checks fidelity
   against the English paragraph by paragraph, the Hebrew as a תכלת editor would read it, the title, and the
   back-translation. The reviewer's checklist:
   - **Fidelity:** nothing missing or added, numbers, names, dates and quotations exact, tone and irony kept.
   - **Glossary consistency:** every glossary and US-POLITICS.md term in its house form, every name as in memory.
   - **Grammar:** gender and number agreement (verbs, adjectives, numerals), construct state (סמיכות), the definite article in construct, prepositions governed by the verb, the ־ש/אשר clauses, tense consistency.
   - **The תכלת voice:** verb-first sentences where natural, formal negation (אינו, אין הוא), varied connectives (ואולם, ברם, אפוא, שהרי), sentences of moderate length.
   - **Translationese:** English word order, chains of nominal constructions, "עושה שימוש", "הוא זה ש", calques of English idioms, too many possessive "של".
   - **Spelling and punctuation:** full spelling (כתיב מלא), ״ ״ quotation marks (never "), maqaf before numbers and Latin script, no stray Latin words except where the guide keeps them.
   Fix the findings and record `review` and `back_translation` in `post.json`.
6. **Quality check.** `python3 pipeline/finalize.py posts/<slug>/post.json /tmp/<slug>.src.json`. Besides the
   format checks, it compares the Hebrew with the English (paragraph count; every number of two or more digits
   kept, or listed in `fidelity_waivers` as `{"number": "1960", "reason": "שנות השישים"}`), requires the brief,
   the independent review and the back-translation, and measures the תכלת voice (argument connectives, variety
   of connectives, density of ״של״, sentence length; calibrated so 92 of the 100 תכלת essays pass). If a style
   check fails, revise the prose itself as STYLE.md describes; never sprinkle connectives in to reach the
   number. If it fails, fix and rerun once; if it still fails, the post is held (never published) and the run
   raises an alert.
7. **Update the translation log**: the reviewer's major findings, the title choice, the style measures, and any
   term settled (move settled terms into the glossary).

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
  "brief": {"tone": "...", "audience_gap": "...", "allusions": "...", "hard_terms": "...", "names": "..."},
  "review": {"independent": true, "findings": 0, "major": 0, "fixed": 0, "not_fixed": []},
  "back_translation": {"title": "...", "subtitle": "...", "quotes": ["...", "...", "..."], "meaning_kept": true},
  "fidelity_waivers": [],
  "source_paragraphs": 0, "he_paragraphs": 0
}
```
Then run `python3 pipeline/finalize.py posts/<slug>/post.json /tmp/<slug>.src.json`: it runs the quality check, picks the cover (the article's first image, or a brand-kit cover when there is none), and marks the post `ready` for the publisher on dud.

## Tweet quotes (`quotes_he`)
Exactly 3, each a complete tweet without the link (the link is added automatically on its own line, and X shows the post's thumbnail):
- Lead with the single most striking, quotable sentence of the essay, verbatim from your Hebrew translation, in ״ ״. Shorten with [...] if needed, never change the meaning.
- Prefer sharp claims, memorable lines and surprising facts that make an Israeli reader want to click. No hashtags, no emoji, no clickbait wording that the essay doesn't support.
- After the quote, a short attribution or hook: who said it and what the essay is about (e.g. ״...״ דאגלס מארי על צרפת הבוערת.). If the quote is someone the author quotes, say who.
- Three different quotes from different parts of the essay. Each must fit in a tweet with the link (finalize.py checks; about 250 characters).
