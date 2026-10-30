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
