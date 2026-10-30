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
- Hard call, same essay: "pour encourager les autres" can take a Hebrew echo, ״כדי שאחרים יראו וייראו״, the
  everyday idiom that echoes ״וכל העם ישמעו ויראו״ (Deut. 17:13, checked with lookup.py source), instead of
  staying in French.

### 2026-10-30 · new tools
- `pipeline/azure/TITLES.md`: seven title moves from the 100 תכלת pairs, for pass 3.
- `pipeline/lookup.py name`: Hebrew Wikipedia spellings (ג׳ון לוק, כתבי הפדרליסט, הריטג׳ פאונדיישן). A "-" means no
  Hebrew article: transliterate, give the English in parentheses the first time, and log it.
- `pipeline/lookup.py source`: original Hebrew of a verse or passage from Sefaria, without cantillation or niqqud.

### 2026-10-30 · השילוח and American politics
- Hadar: השילוח is a secondary guide only, mainly for political terms that did not exist in תכלת's day. תכלת stays
  primary for voice. Classic-quotations bank not wanted (we rarely quote classics).
- Added 100 השילוח essays (2017–2026, 34 on the US; private project folder) and `pipeline/hashiloach_corpus.py`.
- Added `pipeline/US-POLITICS.md`: ~80 American institutions, offices, procedures and slang, each with one Hebrew
  form and one standard first-use explanation. 14 of them → glossary.
- Settled from השילוח: פוליטיקת הזהויות (14 uses, over פוליטיקת זהויות 2); ״דיפ סטייט״ glossed as מדינת צללים /
  המדינה העמוקה; הפנטגון over Wikipedia's מחומש (press usage wins).
- Open question: pro-life → ״תנועת החיים (פרו־לייף)״ proposed; Hadar may prefer another form.

### 2026-10-30 · process from research (ISO 17100, LLM-translation studies)
- New steps: translation brief; section-by-section pass 1 with a names-and-terms memory (`prepare.py`);
  independent reviewer and blind back-translator as fresh subagents (`REVIEWER.md`); fidelity check of
  paragraphs and numbers against the English in `qc.py` (`fidelity_waivers` for numbers rendered as words).
- Why: self-review misses most of a model's own errors; whole-document translation silently skips sentences;
  error scoring catches accuracy better than style, so the תכלת style measures stay.

### 2026-10-30 · audit: the new workflow run on the 7 published posts
Mohler, Rubio, Roberts, Galston, Pinkoski, Renn, Darwall, checked against today's extraction of the English by
qc.py and by fresh reviewer and back-translator subagents (REVIEWER.md). 11 major and 84 minor findings.
- Style: all 7 fail the תכלת connectives check (2.6 to 3.5 per 1,000 words, or one connective used throughout);
  Pinkoski and Renn also have too much ״של״.
- Fidelity: nothing was dropped and every number was kept. Two posts have the wrong meaning in places:
  - Pinkoski P23, ״העולם חב לאמריקה את תביעתה להגמוניה״ for "America owes the world her assertion of global
    hegemony" (reversed).
  - Rubio, the paragraph ״כבר יש סימנים לכך.״ has no source; and the byline puts the speech on the Pnyx (גבעת
    הפניקס), which the source does not say.
- Word errors caught: ״הצטדקות בשם היטלר״ for apologism (→ סנגוריה), ״אוהדתו״ for sympathy (→ אהדתו),
  ״התבצרות לאומית״ for national self-assertion (→ תביעת העוצמה הלאומית), ״הליברל לדוגמה״ for token liberal
  (→ הליברל התורן), ״אלגיה להילבילי״ for Hillbilly Elegy. → glossary [Corrected 2026-10-30: ״אמריקה השנייה״ is only the Hebrew Wikipedia article title; no Hebrew edition was found, so the literal title with the English in parentheses stands.]
- Byline: ״מאת ר׳ אלברט מוהלר״ made a Baptist leader a rabbi. Rule: never write an English initial R. as ר׳; drop
  the initial or spell it out.
- Names: several spellings differed from Hebrew Wikipedia (קת׳י הוקול, אית׳קה, קאי פאי for Chi Phi,
  למברט וילסון, אריק פוגלין). Rule: every name goes through `lookup.py name`.
- Title: ״אמריקה ואפס הפליטות: כמעט״ failed the blind back-translation ("almost" read as falling short, not
  as a narrow escape). Better: ״אפס פליטות נטו: אמריקה ניצלה בעור שיניה״.
- Allusion lost: Pinkoski's "the greatest story ever told" is a film title about Jesus, not a phrase; say so or
  echo it.
- Source cleaning: today's extraction of WORLD and UnHerd pages included hundreds of reader comments, and the WSJ
  PDF included reprint boilerplate. `prepare.essay()` now cuts the page at the end of the essay.

### 2026-10-30 · השילוח pairs and the Dicta grammar layer
- The terminology bank gained 5 English–Hebrew pairs from השילוח: Levin "Taking the Long Way" and Scruton "The
  Good of Government" (First Things, 2014), "Transgender Conformity" (First Things, 2016), Continetti "The Trump
  Revolution" (Free Beacon, 2016), Haivry and Hazony "What Is Conservatism?" (American Affairs, 2017). About 20
  more השילוח translations exist, but their Mosaic and Commentary originals are behind paywalls, so they were left out.
- From the השילוח translator's notes: Burke's "little platoons" is ״המחלקות הקטנות״ (gloss it on first use);
  "government" in general is ממשל or ממשלה, and "administration" is one president's ממשל. → glossary
- `grammar.py` (DictaBERT) now lists agreement clashes for the reviewer, as an optional extra layer. It found the
  planted errors ״הממשלה החליטו״ and ״שלוש ספרים״ and none in the Murray post. It does not yet catch every
  adjective error (״החלטה חשוב״ was missed), so the reviewer's own grammar read stays.

### 2026-10-30 · Kohelet bank (fourth guide, legal and policy terms)
- 72 English–Hebrew pairs from the Kohelet Policy Forum, verified before adding: 71 linked as translations by the
  site itself, 1 matched by author and numbers; 32 more candidates were rejected (summaries, abridged versions,
  mismatched lengths or numbers). Most were written in Hebrew first, so they settle term pairs, not style.
- Misgav (210 pairs) and JISS (509 pairs) added to the fourth guide, searched with `policy_corpus.py`. JISS pairs
  are linked as translations by the site; Misgav pairs were matched by date, author and numbers, and their
  openings read side by side (37 of 247 rejected). Example of what it settles: "campaign between the wars" =
  המערכה בין המלחמות (מב״ם).

### 2026-10-30 · תכלת bank grown from 100 to 224 pairs
- Crawled every article page on both sites (467 Azure, 514 תכלת with text) and matched them by issue, length,
  shared numbers, shared names and known author pairs. The matcher found all 100 existing pairs with no
  conflicts; 124 new pairs were kept after reading both openings side by side (wrong matches and letters
  printed under one heading in one magazine only were dropped). About 200 more תכלת essays exist only as PDFs.
- The new pairs include many shorter pieces (reviews, columns, 1,000–3,000 words). With them, the rule "at least
  one different connective per 150 words, up to 10" failed real תכלת prose 17% of the time. It is now one per
  200 words, up to 8 (the 5th percentile of the 224); 200 of 224 תכלת essays pass the whole style check.

### 2026-10-30 · INSS added to the fourth guide (1,201 pairs)
- INSS has no public API for publications, but its English and Hebrew sitemaps share 1,474 slugs. Both versions
  of each were downloaded and checked (length, paragraph structure, shared numbers and their order); 1,201 kept.
  Mostly security research, written in Hebrew first. Example: "Campaign between Wars" = המערכה בין המלחמות (מב״ם),
  the same as Misgav and JISS.

### 2026-10-30 · retranslation of the 8 earlier posts, and what it taught
The 8 posts translated 5–21 Oct (Mohler, Rubio, Roberts, Galston, Pinkoski, Renn, Darwall, Smith) were retranslated
from scratch with the current workflow and compared blind (the judging editor did not know which was which).
The new version won all 8 (4 by a large margin, 4 clearly), and 186 of 227 paragraph-level differences favoured
it. All 8 new versions pass qc; all 8 old ones fail it. Argument connectives went from 2.6–6.6 to 6.2–14.5 per
1,000 words. About a dozen wins came from answers already in this log; without them the new version still wins
every essay, and Smith (never audited) improved as much as any.
- Where the old version was still better: construct forms and Hebrew words over ״של״ and loanwords
  (״קמפוסי העילית״, ״אסון״), the maqaf in compound names. → TRANSLATION.md
- Still going wrong in new drafts: הסכם for treaty where the argument turns on it (Darwall); אולי for "might well"
  and for a concessive "may"; an added אפוא or ואמנם; יום הזיכרון for 11 November (both old and new first drafts);
  ״בשלום״ for "win the peace"; a rape allegation stated as fact in a tweet hook; paraphrase in quotation marks.
  → TRANSLATION.md rules, glossary
- Process gaps: the reviewer graded everything minor (0 majors in 92 findings) because "major" was undefined; 5
  of 8 back-translations were stale after the titles and quotes changed; two fixes introduced new errors.
  → REVIEWER.md (severity, argument-critical terms, fix check, rerun), qc.py (stale back-translation fails,
  titles over 8 words warn)
- Correction: ״אמריקה השנייה״ is not a Hebrew edition of Hillbilly Elegy (only the Wikipedia article title). The
  glossary entry was removed; glossary entries now record their evidence.
- Open question for Hadar: when Hebrew Wikipedia and common press usage differ on a name (למברט/למבר, הנערים/הבנים
  הגאים, ארון/אהרון), which wins? US-POLITICS.md already says the press form wins for American terms.
Full report: reports/retranslation-evaluation-2026-10-30.md in the project folder.
- Hadar settled both open questions (2026-10-30): when Hebrew Wikipedia and the press spell a name differently,
  Hebrew Wikipedia wins; when the essay's page has no author bio, the post has none, and no one goes looking for
  one elsewhere. → TRANSLATION.md
