# השמרן: the independent review (passes 2 and 3)

A model reviewing its own fresh translation misses most of its own errors, and ISO 17100 requires the revision to
be done by someone other than the translator. So the translator never runs passes 2 and 3 itself. It starts two
fresh sessions with the Agent tool (subagent_type "general-purpose"), each with only the files and instructions
below, and none of its own reasoning.

## A. Back-translator (blind)
Give it only the Hebrew `title_he`, `subtitle_he` and the three `quotes_he`, never the English. Prompt:

> Translate these Hebrew lines into plain English, as literally as good English allows. Do not guess at any
> original. Return JSON: {"title": "...", "subtitle": "...", "quotes": ["...", "...", "..."]}.

Keep the exact Hebrew you gave it as `back_translation.source` ({"title", "subtitle", "quotes"}). If the title,
subtitle or any quote changes afterwards (for example while applying the review), run A again on the new lines:
`qc.py` fails a post whose `back_translation.source` differs from its current title, subtitle and quotes.

## B. Reviewer
Give it the paths to the English sections (`/tmp/<slug>/section-*.en.md`), the Hebrew draft
(`posts/<slug>/post.json`), A's back-translations, and the guides: `pipeline/TRANSLATION.md`,
`pipeline/azure/STYLE.md`, `pipeline/azure/TITLES.md`, `pipeline/US-POLITICS.md`, `pipeline/glossary.json`,
and the spelling list from `python3 pipeline/hebcheck.py posts/<slug>/post.json` (words Dicta's lexicon does not
know; most are foreign names), and, when it ran, the grammar list from `python3 pipeline/grammar.py
posts/<slug>/post.json` (agreement clashes found by Dicta's parser; an empty list or a warning means it was skipped,
and the review is the same without it). Prompt:

> You are the reviser of a Hebrew translation for השמרן. You did not translate it. Read the guides first.
> 1. Fidelity (against the English), paragraph by paragraph using the [P] numbers: anything missing, added or
>    changed in meaning; numbers, names, dates and quotations; tone and irony.
> 2. Hebrew only, as an editor of תכלת (STYLE.md): grammar (agreement, construct state, prepositions), glossary
>    and US-POLITICS.md consistency, translationese, the תכלת voice, spelling and punctuation. Go through the
>    Dicta spelling list: each word that is not a name or an accepted loanword is a spelling finding.
> 3. Title and subtitle against TITLES.md: accurate, idiomatic, the best of `title_options_he`?
> 4. Back-translation: compare A's English with the original title, subtitle and quoted sentences. Flag any shift
>    in meaning.
> 5. Argument-critical terms: list the 3-6 terms the essay's argument turns on (e.g. treaty vs agreement) and
>    check each is rendered the same way throughout and in a way the argument still works.
> Severity: **major** is any change of meaning in a claim, the title, the subtitle, a tweet quote or the closing
> line; a wrong attribution (a paraphrase in quotation marks, the wrong speaker); an allegation stated as fact; a
> mistranslated argument-critical term; a foreign institution given an Israeli civic name (יום הזיכרון for
> 11 November). Everything else is minor.
> Do not rewrite the translation. Return JSON:
> {"findings": [{"where": "P12" or "title" or "quote 2", "category": "accuracy|omission|grammar|terminology|style|title|back-translation",
>   "severity": "major|minor", "problem": "...", "suggestion": "..."}],
>  "back_translation_ok": true or false, "best_title": "..."}

## Applying the review
The translator fixes every major finding and every minor one it agrees with, then writes into `post.json`:
```json
"review": {"independent": true, "findings": 7, "major": 2, "fixed": 7, "not_fixed": [{"finding": "...", "why": "..."}]},
"back_translation": {"title": "...", "subtitle": "...", "quotes": ["...", "...", "..."], "meaning_kept": true}
```
`meaning_kept` is true only after every back-translation finding is fixed. `qc.py` holds a post without these.

**Check the fixes.** Fixes make new errors (in the 2026-10-30 retranslations one fix dropped a word of meaning,
another stretched a title to 10 words). After applying the review, give a third fresh session (subagent_type
"general-purpose") only the list of changed lines as {"where", "english", "before", "after"} and ask: "For each
change, does the new Hebrew say what the English says, and is it at least as good Hebrew as before? Return JSON
[{"where", "ok": true|false, "problem"}]." Fix any "ok": false, then rerun the back-translator if the title,
subtitle or quotes changed.
Copy the major findings and the lessons into the translation log.
