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
| last hurrah | שירת הברבור | McCarthy, 2026-10-27 | used once |
| cohabitation (president vs government of rival camps) | ״קוהביטציה״, glossed once as הדו־קיום הכפוי | Parish, 2026-10-25 | used once |
| confessional state | המדינה בעלת הדת הממוסדת (confessional state) | Hankins, 2026-10-20 | used once; first try ״מדינה דתית־ממוסדת״ was awkward in the plural |
| grooming gangs (UK) | כנופיות ה״גרומינג״ | Hankins, 2026-10-20 | used once; ״טיפוח״ is a calque (cultivation, beauty care) |
| statute / statutory law | חיקוק / המשפט החקוק | Johnson, 2022-04-21 | used once; ״חוק חקוק״ is a pleonasm; avoid the biblical ״חוקים״ when the contrast is with Torah |
| stated (law) vs unstated | מפורש / לא נאמר במפורש | Johnson, 2022-04-21 | used once; ״כתוב״ echoes תורה שבכתב |
| deny / block citizenship vs revoke | למנוע / לחסום אזרחות vs לשלול אזרחות | Roberts, 2026-11-01 | used once; ״לשלול״ means taking away citizenship already held |

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

## 2026-10-30 · In-depth writing guide (STYLE.md rewritten)
Hadar asked for an in-depth style guide covering every aspect of writing, drawn from the 224 תכלת pairs and from
what translation guides for AI should contain. STYLE.md is now a 20-section guide measured on the 224 Hebrew
essays (54,070 sentences). New findings that correct the old guide:
- תכלת's sentences average 22 words (median 19), not 16, and vary widely: about 11% are 8 words or fewer and 7.5%
  are 40 or more. Hebrew sentences are a quarter shorter than the English ones of the same essays (21 against 28).
- Our eight retranslations drift from תכלת in six measurable ways: ״ואולם״ five times too often and no ״אבל״;
  ״כי״ almost never; present-tense ״אינו/אין״ too rare; ״ביותר״ and ״עצמו״ twice as often; sentences too even.
  qc now warns on each.
- תכלת writes ״ספרו״, never ״הספר שלו״; ״בידי״ for a person agent more than ״על ידי״; ״אף ש״ over ״למרות ש״;
  ״כדי ל״ over ״על מנת ל״; ״אמריקני״ (1,431) over ״אמריקאי״ (5) → glossary; ״תכנית״ and ״מרס״.
- Calques that qc now fails: בסופו של יום, לשחק תפקיד, לעשות שכל / עושה שכל, לעשות הבדל, על בסיס יומי.
  Jargon loanwords that it warns on: נרטיב, אג׳נדה, קונספט, דיסקורס, פרובלמטי, פרקטי.

### 2026-10-31 · 2026-10-27-mccarthy-brazil-and-venezuela-face-a-tough-road-back-to-sanity
- Term: lawfare → ״לוחמה משפטית״ (in quotation marks on first use). Why: the established Hebrew press form. → glossary
- Term: legitimate opposition → ״אופוזיציה לגיטימית״; the essay's argument turns on it, kept the same throughout. → glossary
- Term: leftist (noun) → ״איש השמאל״ / ״אנשי השמאל״, and "leftist incumbent" → ״הנשיא המכהן מן השמאל״. Why:
  ״שמאלן״ is slangy and pejorative in Hebrew, which the author's neutral usage is not. → glossary (avoid ״שמאלן״)
- Term: token protest → ״מחאה סמלית״, not ״מחאה לשם מחאה״ (which adds a sneer that isn't there).
- Title: chose ״ברזיל וונצואלה: מבחן האופוזיציה הלגיטימית״ over ״...הדרך הקשה חזרה לשפיות״ (a literal calque of the
  English headline), ״שירת הברבור של לולה״, ״השמאל הלטיני ויריביו״. Why: it names the essay's actual test. The reviewer agreed.
- Caught in pass 2 (major): P15 "Charging Machado would be a convenient way" was rendered as a past fact (״הייתה״),
  which states an allegation as having happened → conditional ״אם תואשם... תהיה זו״. Watch the tense of English
  "would" in hypotheticals.
- Caught in pass 2 (major): "go down in history" became ״להיזכר בהיסטוריה״ (= to recall history) → ״להיכנס לדברי הימים״.
- Caught in the fix check: ״אילו״ with future-tense verbs is ungrammatical (אילו takes past: אילו הואשמה... הייתה); a
  reviewer-suggested gloss (״העומדת בראש התביעה שלה״) added words not in the English, so it was dropped.
- Hard call: "last hurrah" → ״שירת הברבור״ (Hebrew has no exact equivalent; the swan song keeps the sense of a final act).

### 2026-11-01 · 2026-10-25-parish-poland-divided-how-politics-became-a-struggle-between-two-nations
- Term: polarisation → ״קיטוב״; affective → ״רגשי״. opponent vs enemy → ״יריב״ / ״אויב״, and "distinction" → ״ההבחנה״
  every time (the closing argument turns on it; pass 1 mixed ״ההבדל״ and ״ההבחנה״).
- Term: capture (institutions) → ״להשתלט על״ on both sides of the mirror claim; pass 1 split it into ״להשתלט״ / ״נשבו״,
  which broke the symmetry the argument rests on.
- Names (Hebrew Wikipedia): המצע האזרחי (Civic Platform, masculine: ״המצע... נעשה״), רפאל צ׳אסקובסקי, טבח קאטין, בית המשפט
  החוקתי (Constitutional Tribunal), שיחות ״השולחן העגול״.
- Title: chose ״פולין מול פולין: הפוליטיקה כמאבק בין שתי אומות״ over the literal ״פולין המפולגת...״, ״בין יריב לאויב: הפילוג
  הפולני״, ״שתי היסטוריות של פולין״. Why: the antithesis is the essay's thesis in two words.
- Caught in pass 2 (major): "This suggests that" → ״מכאן ש״ made a hedged inference a firm conclusion (→ ״הדבר מרמז ש״);
  "hardened into" → ״התקשו״ reads as "had difficulty" (→ ״התקבעו״). Pass 1 also dropped "appeared to", "helps explain",
  "precisely", "comfortably": hedges and intensifiers keep being lost.
- Hard call: "constitutional DEFCON 1" → ״כוננות חוקתית עליונה״.
- Style: ״אפוא״ ran 9 times in 2,800 words; varied with לפיכך / על כן / מכאן ש. Sentence spread warning left (measured voice).

### 2026-11-01 · 2026-10-20-hankins-a-muslim-answer-to-muslim-immigration
- Term: free exercise / public exercise (of religion) → ״חופש קיום הדת״ (in running text) and ׳קיום חופשי׳ / ׳קיום פומבי׳ (the paired distinction). Pass 1 used
  ״חופש הפולחן״ for the First Amendment right, so the essay's final distinction lost its anchor (major). Keep
  ״חופש הפולחן״ only for "freedom of worship". → glossary
- Term: confessional state → ״המדינה בעלת הדת הממוסדת (confessional state)״; establishment (of religion) → ״כינון דת״.
- Term: "at the state level" (US) → ״ברמת מדינות הברית״; ״ברמת המדינה״ reads as nationwide and blurs state vs federal (major).
- Caught in pass 2 (major): "the British Commonwealth" as a source for the Founders is Cromwell's republic → ״חבר העמים של
  אנגליה״, not ״הקהילייה הבריטית״ (an anachronism). Check "Commonwealth" by period every time.
- Caught in pass 2 (major): in a hard-hitting essay pass 1 sharpened claims: "intimidation" → ״הטלת אימה״ (→ ״הפחדת״),
  "disruptive" → ״הרסני״ (→ ״מטלטל״), "construe as" → ״כאילו״ (implies pretense; → ״כך ש״). Keep the author's exact strength.
- Title: chose ״הלקח המלזי: תשובה מוסלמית להגירה מוסלמית״ (topic: angle, keeping the original's parallel) over the bare
  literal title, ״מה שכשר לאסלאם״ (opaque alone) and a 10-word option.
- Hard call: "sauce for the Islamic goose ... Christian gander" → ״מה שכשר לאסלאם יוכשר, בהתאמות, גם לנצרות״; Arnold's
  "ignorant armies clash by night" woven in without quotation marks (unattributed in the English too).
- QC fail, fixed once: 4.0 argument connectives per 1,000 (min 5). Pass 1 rendered "nevertheless", "yet", "but here as
  elsewhere" as ״בכל זאת״ / ״ואף על פי כן״ / ״אבל״, which do not count and are flatter than תכלת's ״עם זאת״, ״אולם״, ״אך״.
  Reach for the listed connectives where the English has the joint.

## 2026-11-01 · Israel Hayom bank (fourth guide)
19 Israel Hayom columns written in Hebrew, each with the paper's own English translation (Eyal Zisser 15, Dror
Eydar 3, Amnon Lord 1; Aug–Oct 2026), added as `policy_corpus.py --bank israelhayom`. They show how current
Israeli political and security Hebrew is rendered in English (Iran, Hezbollah, the Gulf, the elections). 10
candidates were left out: Amit Segal's English columns are condensed rewrites, not translations, and three long
Eydar essays were restructured in English. Newspaper Hebrew: vocabulary only, never register.

### 2026-11-02 · 2026-10-20-paul-lgbtq-is-far-from-dead
- Term: LGB vs LGBTQ → ״הומואים, לסביות או ביסקסואלים״ / ״הזהות ההומוסקסואלית והביסקסואלית״ for LGB survey figures;
  ״להט״ב״ only where the English has LGBTQ. Pass 1 used ״להט״ב״ for both, which put trans and queer people into data
  that measures only sexual orientation.
- Term: non-heterosexual(ity) → ״לא־הטרוסקסואלי״ / ״אי־הטרוסקסואליות״; social contagion → ״הדבקה חברתית״; plateau →
  ״התייצבות״; genderfluid → ״זרימה מגדרית״ (ג׳נדר־פלואיד; ״גמישות מגדרית״ is gender nonconformity); prep school → ״פנימייה פרטית המכינה לקולג׳״.
- Title: chose ״מוקדם להספיד את הזהות הלהט״בית״ over the calque ״הלהט״ב רחוק ממוות״, ״נולדו כך? הזהות המינית כגל חברתי״,
  ״הגל הלהט״בי עוד לא נסוג״. Why: a Hebrew idiom that says what "far from dead" says.
- Caught in pass 2 (major): "political as well as social" → ״פוליטיות לא פחות משהן חברתיות״ ranked the two and sharpened
  the claim (→ ״חברתיות וגם פוליטיות״); it was also tweet quote 1.
- Caught in pass 2 (major): the subtitle stated the decline as a fact for all young Americans; the essay limits it to high
  schoolers and young men and says young women are at a record. A Hebrew subtitle needs the same fidelity check as the body.
- Style: age ranges and statistics in digits (בני 18–24), not words; ״לשיא של כל הזמנים״ and ״עושה קאמבק״ are calques/slang.
- Skipped this run: Catholic Herald (Vance on immigration), registration wall after three paragraphs → paywalled.

### 2026-11-03 · 2026-09-01-mccarthy-iceland-puts-the-freeze-on-brussels-ever-closer-union
- Term: ever closer union → ״איחוד הדוק מתמיד״; single market → ״השוק האחיד״; EEA → ״האזור הכלכלי האירופי״ (Hebrew
  Wikipedia); accession / enlargement → ״הצטרפות״ / ״התרחבות״; absorption → ״היבלעות״; accountable → ״נותן דין וחשבון״
  (kept the same in P7, P19, P21); Project Fear → ״פרויקט הפחד״, glossed once ״המוכר מימי הברקזיט״.
- Title: chose ״איסלנד מקפיאה את ״האיחוד ההדוק מתמיד״ של בריסל״ (keeps the freeze pun) over ״הכתף הקרה של איסלנד״,
  ״איסלנד אומרת לא לבריסל״, ״אירופה של אומות: הלקח מרייקיאוויק״.
- Caught in pass 2 (major): "the sovereignty and regulatory costs" → ״מחירי הריבונות״ reads as the cost of having
  sovereignty, the opposite of the point (the cost to sovereignty) → ״המחיר בריבונות ובנטל הרגולטורי״. It was also a
  tweet quote; the blind back-translation exposed it. Watch noun + ״מחיר״ constructions.
- Hard call: Washington Times print had a sidebar table spliced into P8; rebuilt the sentence from the two halves.
- Skipped this run: Mohler, "Islam vs. America" (Daily Wire via NatCon PDF): the PDF is a browser print whose sticky
  header hides one line on page 4, so a sentence is lost; the Daily Wire page is behind a login. Marked failed.
- Resolved 6 Nov (Hadar): Heritage Foundation = ״קרן הריטג׳״, as in US-POLITICS.md, not Wikipedia's ״הריטג׳ פאונדיישן״.
  The Wikipedia-spelling rule is for people's names, not established Hebrew names of institutions. Iceland bio fixed.

### 2026-11-07 · 2026-04-25-wegmann-why-tucker-carlson-is-turning-on-donald-trump
- Source: a WSJ news feature that NatCon hosts as a PDF of a web capture; comments, newsletter box and "Further Reading" dropped. A news
  report, so the register is plainer than an essay; the connectives came from the English joints (אמנם... אך, כלומר, אלא).
- Term: neoconservatives → ״הניאו־שמרנים״; regime change → ״החלפת משטרים״; anti-interventionism → ״התנגדות להתערבות צבאית בחו״ל״;
  "no new wars" → ״לא עוד מלחמות חדשות״; America First → ״אמריקה תחילה״, feminine throughout (״פירושה״, ״לדחות אותה״).
- Term: Resolute Desk → ״שולחן הרזולוט, שולחן העבודה של הנשיא״ (Wikipedia name means nothing alone); WASP explained by the text's own
  next sentence (״לבן, אנגלו־סקסי ופרוטסטנטי״).
- Title: chose ״מדוע טאקר קרלסון יצא נגד טראמפ״ (close) over ״טאקר קרלסון: ״אני מרגיש נבגד״״ (nested quote marks in a title),
  ״מאיש סוד לגולה״, ״קרלסון נגד טראמפ: הקרע על איראן״. The subtitle carries ״אני מרגיש נבגד״.
- Caught in pass 2 (major): tweet quote 1 put the reporter's paraphrase ("If America First is the gut instinct... Carlson said") inside
  Carlson's quotation marks, joined by [...]. Rule: a tweet quote may only join words inside the same speaker's quotation; the frame goes
  in the hook. The fix-check then caught that ״לדחות אותה״ had no referent inside the quote → ״לדחות את [׳אמריקה תחילה׳]״.
- Caught in pass 2 (minor, recurring kind): ״השיב לשיחות״ for "fielding calls" (received, not returned); ״מעצמות זרות״ for "foreign powers"
  in a vague smear (→ ״גורמים זרים״); ״עצוב ומשלים״ needs ״עם המצב״; ״הנחתי שהוא כן״ reads as "yes" (→ ״מתכוון לדבריו״).
- Pass 1 error caught by me before review: ״האיש שעזר לו להפוך לנשיא״ reversed who helped whom. Check the subject of every ״ש־״ clause
  after a name.

### 2026-11-07 · 2022-04-21-johnson-will-we-ever-actually-bother-with-biblical-law
- A Christian scholar writing to Christians (a Theopolis "conversation" reply). Kept his ״אנו״ as Christians; Bible references in
  Hebrew-Bible numbering (English Exod 22:1–3 = שמות כא, לז – כב, ב) with fidelity waivers; Lev 19:17 quoted from the original.
- Term: "keep the torah like you keep a garden or keep sheep" works natively in Hebrew (שמר); "break" a law → ״לשבור״, in quotation
  marks, so the garden/sheep joke survives ("Can you break a garden?"). teachings of Jesus → ״משנתו של ישו״, so it does not clash with ״תורה״.
- Title: chose ״שומרים תורה כמו ששומרים גן״ (the essay's central image) over the close ״האם נטרח אי־פעם לעסוק באמת במשפט המקראי?״,
  ״התורה אינה ספר חוקים״, ״הנוצרים והתורה: החזון שהוחמץ״.
- Caught in pass 2 (major): tweet 2 called Henri Frankfort ״ההיסטוריון״; he was an archaeologist and Assyriologist, and the source cites
  "Frankfort et al." Rule: a tweet hook describes a person only as the essay or an undisputed fact does.
- Caught in pass 2 (minor): the subtitle said "his fellow believers" where the essay says "many (possibly most?)"; ״הוערכו... על פי חוק״
  read as statute, the category the essay rejects (→ ״הועמדו חיי אדם, מבחינה משפטית, מעל הרכוש״); concessive "We may all roll our
  eyes, but" rendered as a hedge ״אולי״ (→ ״אמנם... אבל״); "let us be real" is "realistic", not ״כנים״.
- QC: English bibliographic notes fail the untranslated-paragraph check. Render notes in Hebrew form (author, translated title in italics,
  English short title, place and publisher in Hebrew, ״עמ׳״).

### 2026-11-07 · 2026-11-01-roberts-giorgia-meloni-threatens-to-remove-right-to-citizenship-from-rioting-teens
- A news report with critical framing (hard-right, post-fascist roots); kept exactly: ״הימין הקשה״ for hard-right, ״הימין הקיצוני״ for
  far-right, never merged.
- Caught in pass 2 (major): title ״לשלול אזרחות״ reads as revoking citizenship already held; the teens are not citizens yet and the bill
  blocks their path, while revocation is a separate measure in the same bill → ״למנוע אזרחות״.
- Caught in pass 2 (major): closing line "security had always been a priority" → ״בראש סדר העדיפויות״ sharpened it (→ ״בין העדיפויות״).
- Hard call: the source says the 17 October riots were "earlier this month" in a piece dated 1 November; wrote ״באוקטובר״.
- Names: Beccaria → ״בקאריה״ (Hebrew Wikipedia, Cesare Beccaria); the League → ״מפלגת הליגה״; ANSA, ASGI, YouTrend/AGI in Latin.

### 2026-11-08 · 2026-11-01-keeperman-midterms-zombie-gop-tucker-problem
- Source: a long X article (Jonathan Keeperman, two days before the 3 Nov 2026 midterms), listed on the NatCon essays page; it extracted
  cleanly, with one lead image. The X profile line (publisher and podcast links) is not an essay bio, so no bio.
- Term: Zombie GOP → ״המפלגה הרפובליקנית הזומבית״ throughout (״הרפובליקניות הזומבית״ for "Zombie Republicanism"); Vanceguard →
  ״הוואנסגארד״ glossed once as Vance + ״אוונגרד״, and "vanguard movements" later → ״תנועות ׳אוונגרד׳״ to keep the echo (not ״תנועות חלוץ״,
  which evokes Zionist youth movements); Tech Right → ״ימין הטק״; degrowth → ״הנסיגה מן הצמיחה״ (degrowth), not ״צמיחה שלילית״ (recession);
  NGO complex → ״תעשיית הארגונים הלא־ממשלתיים״, not ״ארגוני החברה האזרחית״ (positive in Israel); Never Trumpers → ״מתנגדי טראמפ המושבעים״.
- Term: nationalism/nationalist → לאומיות/לאומי, never לאומן (chauvinist). → glossary
- Caught in pass 2 (major): ״לאומנים / לאומן / מרד לאומני״ for the same camp the author calls לאומי elsewhere; ״מדוע מחק טראמפ את הפרויקט
  שלו״ read as Trump's own project (it was the old guard's; the first fix ״שלו עצמו״ made it worse, the fix-check caught it → ״שלהם״);
  "institutional reckoning" → ״חשבון הנפש״ (introspection) instead of ״התחשבנות עם המוסדות״.
- Caught in pass 2 (minor, recurring kinds): ״התגיירו ללאומיות״ (conversion to Judaism only) → ״חזרו בתשובה אל הלאומיות״; ״בידי היהודים״
  generalised "by Jews" → ״בידי יהודים״; ״מאבק בעלייה״ calque; ״הספסל שלה אינו עמוק״ sports calque → ״אין לה עתודה של ממש״; dropped
  hedges ("some of", "might portend", "really"); ואולם 11 times → varied with אבל, אך, ברם, עם זאת, אלא ש.
- Hard call: "retarded" in the closing polemic → ״מטומטמים״ (keeps the insult, without a slur about disability).
- Title: chose ״אחרי טראמפ: הזומבים, טאקר והמאבק על הירושה״ (topic: angle) over ״בחירות האמצע, המפלגה הזומבית ובעיית טאקר״ (close, dated
  by the election) and ״הטראמפיזם גווע, הזומבים מתעוררים״; the subtitle decodes ״הזומבים״.
- Correction (Hadar, 2026-11-08): "״המחנה הלאומי״: best" (asked for alternatives to ״אנשי הלאומיות״). Rule: the nationalists as a camp or people
  = ״המחנה הלאומי״; the adjective stays לאומי; never לאומן. Applied to this post. → glossary
- Correction (Hadar, 2026-11-08): "second best: הימין הלאומי". Rule: ״הימין הלאומי״ is the alternative to ״המחנה הלאומי״.
- Correction (Hadar, 2026-11-08): "third best: ״השמרנים הלאומיים״". Rule: third choice, fits where NatCon people are meant.
