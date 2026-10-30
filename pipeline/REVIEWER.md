# השמרן: the independent review (passes 2 and 3)

A model reviewing its own fresh translation misses most of its own errors, and ISO 17100 requires the revision to
be done by someone other than the translator. So the translator never runs passes 2 and 3 itself. It starts two
fresh sessions with the Agent tool (subagent_type "general-purpose"), each with only the files and instructions
below, and none of its own reasoning.

## A. Back-translator (blind)
Give it only the Hebrew `title_he`, `subtitle_he` and the three `quotes_he`, never the English. Prompt:

> Translate these Hebrew lines into plain English, as literally as good English allows. Do not guess at any
> original. Return JSON: {"title": "...", "subtitle": "...", "quotes": ["...", "...", "..."]}.

## B. Reviewer
Give it the paths to the English sections (`/tmp/<slug>/section-*.en.md`), the Hebrew draft
(`posts/<slug>/post.json`), A's back-translations, and the guides: `pipeline/TRANSLATION.md`,
`pipeline/azure/STYLE.md`, `pipeline/azure/TITLES.md`, `pipeline/US-POLITICS.md`, `pipeline/glossary.json`,
and the spelling list from `python3 pipeline/hebcheck.py posts/<slug>/post.json` (words Dicta's lexicon does not
know; most are foreign names). Prompt:

> You are the reviser of a Hebrew translation for השמרן. You did not translate it. Read the guides first.
> 1. Fidelity (against the English), paragraph by paragraph using the [P] numbers: anything missing, added or
>    changed in meaning; numbers, names, dates and quotations; tone and irony.
> 2. Hebrew only, as an editor of תכלת (STYLE.md): grammar (agreement, construct state, prepositions), glossary
>    and US-POLITICS.md consistency, translationese, the תכלת voice, spelling and punctuation. Go through the
>    Dicta spelling list: each word that is not a name or an accepted loanword is a spelling finding.
> 3. Title and subtitle against TITLES.md: accurate, idiomatic, the best of `title_options_he`?
> 4. Back-translation: compare A's English with the original title, subtitle and quoted sentences. Flag any shift
>    in meaning.
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
Copy the major findings and the lessons into the translation log.
