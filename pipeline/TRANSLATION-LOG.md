# השמרן: translation log

What we learn from each translation, so the next one is better. The daily run reads this before translating
and adds an entry after each essay (see `pipeline/TRANSLATION.md`). This repo is public: no names of private
people, no secrets.

Settled terms move to `pipeline/glossary.json`; mark the entry `→ glossary` when they do.

## How to write an entry
```
### YYYY-MM-DD · <slug>
- Term: <English> → <Hebrew>. Why: <reason>. [→ glossary]
- Title: chose ״...״ over ״...״, ״...״. Why: ...
- Caught in pass 2/3: <what pass 1 got wrong> → <fix>.
- Hard call: <idiom / reference / irony> → <how it was handled>.
- Correction (Hadar, date): "<verbatim>". Rule: <what to do from now on>.
- Open question: <anything Hadar should settle>.
```

## Terms under watch (not yet in the glossary)
| English | Hebrew used | Where | Status |
|---|---|---|---|
| MAGA | MAGA (Latin script, as in Hebrew press) | Smith, 2026-10-21 | used once |
| ICE (US immigration agency) | ICE | Smith, 2026-10-21 | used once; consider a first-use gloss: רשות ההגירה והמכס |
| American Moment (organization) | אמריקן מומנט in the subtitle, American Moment in the body | Smith, 2026-10-21 | inconsistent: settle one form (proposed: Hebrew transliteration, Latin in parentheses the first time) |
| remigration | remigration (Latin) | Murray, 2026-10-20 | used once; Hebrew form needed (proposed: ״רה־הגירה״) |
| Robert's Rules of Order | Robert's Rules of Order (Latin) | Greer, 2023-03-30 | used once; proposed: ״כללי הנוהל של רוברט״ (Robert's Rules of Order) |

## Entries

### 2026-10-30 · setup
- Log started. Process now has three passes: pass 1 translate, pass 2 review (2a fidelity against the English,
  2b Hebrew-only read for glossary consistency and grammar), pass 3 title (at least 3 candidates, choose, log).
- Glossary moved from TRANSLATION.md to `pipeline/glossary.json` with `avoid` variants that `qc.py` rejects.
- Seeded "Terms under watch" from the three posts translated so far.

### 2026-10-30 · תכלת corpus
- Hadar: no human step anywhere; the system stays fully automated.
- Added `pipeline/azure/` (style guide STYLE.md, index of 100 Azure/תכלת parallel essays) and
  `pipeline/azure_corpus.py` (fetch and search the pairs at run time). 33 corpus terms → glossary.
- Open question: תכלת's web text uses plain " quotes; we keep ״ ״ (same convention, proper glyph).

### 2026-10-30 · style measured against תכלת
- Our first translations vs תכלת, per 10,000 words: אך 1 vs 15, אולם 1 vs 8, אפוא 1 vs 6, ברם/הרי/ואמנם/על כן ~0 vs
  2–3; ״של״ 17% more. Lesson: our Hebrew leaned on ואולם alone and on ״של״. qc.py now checks this.
- Caught in murray-france: ״ואיזה אזהרות היו״ → ״ואילו אזהרות היו!״ (איזה is singular; plural takes אילו).
- Hard call, same essay: "pour encourager les autres" can take a Hebrew echo, ״כדי שאחרים יראו וייראו״ (Deut. 17:13),
  instead of staying in French.
