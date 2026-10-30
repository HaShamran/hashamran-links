# השמרן: the תכלת writing guide (from 224 Azure / תכלת parallel essays)

Our model is תכלת (Shalem Press, 1996–2012). Azure, its English sister journal, published many of the same
essays, so we have 224 essays in both languages (`index.csv`: about 1.4 million English and 1.1 million Hebrew
words, 54,070 Hebrew sentences). This guide is what those pairs teach, measured and checked against what
professional translation style guides cover (sources at the end). It is written for the translator, which is
Claude. Read all of it before every translation, together with `pipeline/TRANSLATION.md`; the reviewer reads it too.

**How the rules were made.** Every number here was counted in the 224 Hebrew essays (p5 / median / p95 means
the 5th percentile, median and 95th percentile of the essays). "Our drift" marks a place where our own eight
retranslations of 2026-10-30, the best we have done, still differ from תכלת. Short phrases in ״ ״ are quoted from
תכלת unless marked *(illustration)*. Several of the essays were written in Hebrew first and translated into
English, so a pair shows how the two languages correspond, not always which way the translator went. The Hebrew
side is always the model.

**Order of authority.** Meaning first, then the argument, then the voice. Where this guide conflicts with the
author's meaning, the meaning wins. Where it conflicts with `TRANSLATION.md` on process, `TRANSLATION.md` wins.
American terms are settled in `pipeline/US-POLITICS.md`, house terms in `pipeline/glossary.json`, titles in
`TITLES.md`. Hadar's decisions in `TRANSLATION.md` (Hebrew Wikipedia spells names; no bio in the source means no
bio) override everything here.

## 0. Using the corpus during a run
```
python3 pipeline/azure_corpus.py fetch                   # checks the stored copy; downloads only if missing
python3 pipeline/azure_corpus.py search "civil society"  # how תכלת rendered it, in context
python3 pipeline/azure_corpus.py search "אפוא" --he      # how a Hebrew word is used
python3 pipeline/azure_corpus.py show 42                 # a whole pair
```
Search whenever a term, idiom or construction is not settled in `pipeline/glossary.json`. If תכלת used it
consistently, follow it and add it to the glossary. The texts are Shalem Press's copyright: the permanent copy is the
private project folder `/mnt/project-files/hashamran/translation-guide/pairs/`, and they are never committed to
this public repo. Quote at most a phrase or two of them in the log.

For words תכלת never needed (it closed in 2012), the secondary guide is 100 recent השילוח essays
(`pipeline/hashiloach_corpus.py`), and American terms are in `pipeline/US-POLITICS.md`. They settle vocabulary
only. For voice and style, this guide wins.

## 1. The task: a Hebrew essay, not a translated one
Write the essay as תכלת's editors would have printed it had the author written in Hebrew. The reader is an
educated Israeli who reads essays, knows the Bible and Israeli politics, and knows America from the news.
- **Same content, new sentences.** Every claim, example, qualification, number and joke of the author stays;
  the English sentence structure does not have to. The Hebrew runs about 24% shorter than the English (words
  ratio p5 0.69 / median 0.76 / p95 0.89). Shorter comes from Hebrew's compactness, never from cuts. A ratio
  under 0.65 usually means something was dropped.
- **Keep the author's paragraphs.** תכלת kept the paragraphing almost exactly (paragraph ratio 0.81 / 0.98 /
  1.15). Reorder sentences inside a paragraph if Hebrew needs it; do not move material between paragraphs.
- **Rebuild the opening sentence for a Hebrew reader.** Azure's "Of the countries hardest hit by the current
  outbreak of anti-Semitism in Europe, France poses a particular dilemma" became ״גל האנטישמיות שפקד לאחרונה את
  אירופה לא פסח, כידוע, גם על צרפת. ואולם...״. The meaning stays and the sentence is new.
- **Identify foreign figures in a short apposition the first time**: ״העיר פעם העיתונאי והסטיריקן האמריקני ה״ל
  מנקן״, ״הוגה הדעות היווני אפלטון״, ״הביולוג הבריטי ריצ׳רד דוקינס, רציונליסט חסר פשרות״. One phrase, never a
  footnote, and only facts the essay itself supports or that are beyond dispute.
- **Use the canonical Hebrew for classic texts**: Plato's ship of state is quoted from the standard Hebrew
  translation (״כן תאר לך אניות רבות או אנייה אחת...״), not translated from the English quotation. Bible,
  Mishnah and Talmud are quoted in the original (Sefaria lookup, `pipeline/lookup.py`).
- **Use the Hebrew names of Jewish figures**: Herzl is ״בנימין זאב הרצל״ where the English has "Theodor Herzl".
- **Do not explain what the Israeli reader knows** (the Knesset, the Mishnah, the Six-Day War) and do explain
  what he does not (a state attorney general, a fraternity, a Senate hold). `US-POLITICS.md` gives the standard
  phrase.

## 2. Before writing: read for the argument
LLM translation goes wrong most often by translating sentence by sentence without the whole in view. Before
the first draft, write into `memory.md`:
1. The thesis in one Hebrew sentence, and the steps of the argument (the brief has them).
2. The argument-critical terms: the five to ten words the case rests on (treaty, nation, liberal, elite...).
   Choose each Hebrew term once, from the glossary or the corpus, and use it every time. Never vary a term for
   elegance; Hebrew readers take a new word for a new thing.
3. The author's temperature: dry, polemical, ironic, elegiac, personal. The Hebrew keeps it (section 11).
4. Every proper name, title and quotation, with its settled Hebrew form (section 13).

## 3. Sentences
**Length.** תכלת's sentences are shorter than Azure's: 21.3 words on average against 28.5 in the English of the
same essays. Across the corpus the average sentence is 17 / 22 / 26 words (median sentence 19). Hebrew
packs more into each word, so an English sentence of 30 words usually becomes a Hebrew one of 22, or two of 11
to 15. The number of sentences stays close to the English (ratio 0.86 / 1.04 / 1.27).

**Variety matters as much as the average.** In a typical essay about 11% of the sentences have eight words or
fewer and about 7.5% have forty or more (standard deviation of sentence length 9 / 12 / 17 words). A short
sentence lands a point: ״כך צריך להיות.״ (for "This is as it should be."), ״וזוהי רק ההתחלה.״. A long one carries a
list or a chain of reasons, held together by semicolons. *Our drift:* our sentences are too even (deviation 8.7,
only 3% long). Do not chop every long English sentence into two medium ones; let some run, and let some stop short.

**How to split a long English sentence**, in order of preference:
1. Two sentences, the second opening with a connective: "the implication being that without such a plan,
   force would have to be used" → ״...משמעות הדברים הייתה כי ללא תכנית כזאת, תיאלץ ישראל להפעיל כוח.״
2. A semicolon between two full clauses that answer each other (4.1 per 1,000 words, against 2.7 in the
   English): ״במקום ליצור הזדמנויות חדשות לתעסוקה... היא מצמצמת אותן; במקום לשפר את מצבם העגום של דלי
   האמצעים, היא מנציחה אותו.״
3. A spaced dash around an inserted phrase (section 15).
4. A colon before the explanation or the list: ״ולא בכדי: ככלות הכל, מקום עבודה קבוע מספק פרנסה...״.

**Word order.** Hebrew prose puts the verb early and the new information at the end.
- *Verb before subject* in narrative, and after an opening adverbial or object: ״נבחר ז׳אן זיגלר בידי מועצת...״,
  ״בתוך עשור התהפכו היוצרות״, ״בשווייץ העניקה לו התאחדות העיתונות הזרה את פרס...״, ״לא הייתה זו התפתחות בלתי
  צפויה״, ״היה זה ניצחון נוסף...״. Use it where the sentence opens with time, place or a link to the previous
  sentence; a sentence about who did what can keep subject–verb order.
- *Topic first*: start with what the reader already knows and end with what is new, even if the English does the
  reverse. "Our social and cultural discourse ... is defined by a vocabulary and a worldview that can only be
  described as apocalyptic" → ״אוצר מילים והשקפת עולם בעלי צביון אפוקליפטי מובהק מגדירים כיום את השיח החברתי
  והתרבותי בכל נושא״.
- *An inserted phrase can sit mid-sentence* where English fronts it: "It must be stressed that Denmark's labor
  market is one of the most organized in the world" → ״שוק העבודה של דנמרק, חשוב להדגיש, הוא אחד המאורגנים
  בעולם.״

**English frames that Hebrew drops.**
| English | תכלת | not |
|---|---|---|
| It is clear that X | ״ברי ש...״, ״ברור ש...״, ״מובן ש...״ | ״זה ברור ש...״ |
| Of course, X | ״מובן ש...״, ״כמובן״ inside the sentence | ״כמובן,״ opening every point |
| There is no escaping the fact that | ״אין מנוס מן המסקנה ש...״, or state the fact | ״אין בריחה מהעובדה ש...״ |
| despite the fact that | ״אף ש...״ | ״למרות העובדה ש...״ |
| There is a special way of... | ״יש דרך מיוחדת...״ (יש works, keep it short) | ״ישנה דרך...״ |
| One would have to be X to dislike Y | ״רק אדם נרגן וחסר הומור יפסול את...״ | ״אדם יצטרך להיות...״ |
| what is needed is | ״יש צורך ב...״, ״נחוץ...״ | ״מה שנדרש הוא...״ |
| the fact that | drop it, or ״העובדה ש...״ once, where it is the subject | ״העובדה ש...״ in every clause |
| X, he writes, ... | often dropped when the attribution is clear | ״הוא כותב״ after every sentence |

**Questions.** Keep the author's rhetorical questions; Hebrew uses them a little more than English (1.2 per
1,000 words against 1.0). ״מדוע״ and ״כיצד״ are the essay's words (331, 401), ״איך״ the spoken one (112). ״האם״
opens a yes/no question (442); ״הלא״ / ״הלוא״ asks for agreement.

## 4. Verbs
- **Prefer a verb to a noun.** English stacks nominalizations ("the implementation of the decision led to");
  Hebrew prefers the verb (״משיושמה ההחלטה...״ *(illustration)*). Avoid ״לבצע״ or ״לעשות שימוש ב״ plus a
  noun where a verb exists: ״להשתמש״, not ״לעשות שימוש״; ״לבדוק״, not ״לבצע בדיקה״.
- **Tense.** An author's claims in a book or article are in the present: ״מאוטנר טוען״, ״קרמר מגולל כתב אישום״.
  Events are in the past. The English present perfect is usually the Hebrew past (״הפכה לרבת השפעה״). The
  English future in a forecast stays future. Do not shift into the historical present for narrative unless the
  author does.
- **Conditionals.** Real: ״אם...״ (2,828). Counterfactual: ״אילו״ / ״לו״ with the past (״אילו נשאלו...״), and the
  negative ״אלמלא״ / ״לולא״ (53). "would have had to" is ״היה נאלץ״, "should have" ״היה עליו״. ״גם אם״ (283) for
  "even if".
- **Modality.** Obligation: ״יש ל...״ (833), ״עלינו״, ״ראוי ל...״ (234), ״מן הראוי״, ״חייב״; ״צריך״ (220) in a
  plainer voice. Possibility: ״אפשר״ (1,101) over ״ניתן״ (545), and ״אי־אפשר״ with a maqaf (156). ״עשוי״ (173) is
  likely-and-good, ״עלול״ (138) likely-and-bad; never swap them.
- **Passive.** English passives (6 per 1,000 words) mostly become active Hebrew. When the agent is named, name
  him as the subject, or use ״בידי״ for a person (1,120) and ״על ידי״ for an action or institution (676):
  ״נבחר... בידי מועצת האו״ם״. When the agent is unknown or irrelevant, Hebrew has good passive and impersonal
  forms (״נמצא כי״, ״נהוג לומר״, ״מקובל לחשוב״). An English passive with an implied agent can take the agent
  from context: "force would have to be used" → ״תיאלץ ישראל להפעיל כוח״.
- **Verbs of saying.** Match the strength of the English: says ״אומר״, writes ״כותב״ (482), argues / claims
  ״טוען״ (206), notes ״מציין״ (154), explains ״מסביר״ (136), states / holds ״קובע״ (133), adds ״מוסיף״ (63),
  remarks ״מעיר״, admits ״מודה״, insists ״מתעקש״. "claims" in a sceptical sentence is ״טוען״ with the doubt kept
  (״לטענתו״), never upgraded to ״מוכיח״ or downgraded to ״אומר״.
- **Reflexive** without את: ״מצא עצמו״, ״להעמיד עצמה לבחינה״. *Our drift:* we use ״עצמו״ almost twice as often as
  תכלת (3.3 against 1.9 per 1,000). English "himself" for emphasis is often dropped, or ״הוא עצמו״ once.
- **Binyan and preposition go together.** Check each verb's government: ״תלוי ב״, ״השפיע על״, ״הכיר ב״ (recognized
  a state), ״הכיר את״ (knew a person), ״נמנע מ״, ״התמודד עם״, ״דן ב״, ״עסק ב״, ״זכה ל / ב״. English prepositions
  are the commonest source of error here.

## 5. Nouns and noun phrases
- **Construct state (סמיכות) and ״של״.** ״של״ appears 21 / 32 / 42 times per 1,000 words; above 42 reads as
  translated (qc fails above 4.2 per 100). Use a construct where the two nouns form a familiar unit (״שוק העבודה״,
  ״מועצת האו״ם לזכויות האדם״) and ״של״ where the owner is long, foreign, a name in Latin letters, or stressed.
- **Possessive suffixes for people.** תכלת writes ״ספרו״ (221) and practically never ״הספר שלו״ (1); likewise
  ״דבריו״, ״לדבריו״ (107), ״לדעתו״, ״בעיניו״ (104), ״עמדתו״ (95), ״מחשבתו״. ״שלו״ (891 times) is for emphasis
  (״תפקידנו שלנו״), after a construct chain, and for loanwords that do not take a suffix well (״הקריירה שלו״).
- **The article in a construct** goes on the last noun only: ״בית הספר״, ״בתי המשפט״, never ״הבית ספר״. An
  adjective after a construct agrees with the noun it describes and takes the article if that noun is definite:
  ״מועצת הביטחון החדשה״ (the council is new) vs ״מועצת הביטחון של המדינה החדשה״ *(illustration)*. Rephrase when
  it is ambiguous.
- **Chains.** Two links are normal, three is the limit (״מערכת ההגנה על זכויות האדם״). Break a longer chain with
  ״של״, a relative clause or a verb.
- **Agreement.** Adjectives and verbs agree with the noun in gender and number. States and countries are
  feminine singular, including ״ארצות הברית״ (feminine singular 179 times, plural 38): ״ארצות הברית הודיעה״.
  Companies and organizations follow their Hebrew head noun (״החברה הודיעה״, ״הארגון הודיע״); a name in Latin
  letters takes the gender of the noun it implies.
- **Numbers and nouns agree too:** ״שלושה ימים״, ״שלוש שנים״, ״שני ספרים״, ״שתי מפלגות״ (section 14).
- **Abstract nouns.** Use the established Hebrew abstract (״חירות״, ״ריבונות״, ״לאומיות״); do not coin ״־יות״ forms
  from English (״אקטיביות״ for "activism" is wrong: ״אקטיביזם״, ״פעלתנות״).
- **Generic nouns.** Hebrew uses the masculine for a mixed or generic group (״האזרח״, ״הקורא״) and the plural to
  avoid "he or she". Keep the author's choice when the gender is the point.

## 6. Pronouns and reference
- **Drop redundant possessives**: English writes "his own country", "their own children"; Hebrew writes ״ארצו״,
  ״ילדיהם״.
- **Demonstratives** follow the noun (״המאמר הזה״, ״רפורמות אלו״, ״הוויכוח ההוא״). ״הללו״ (744) is the essay's
  anaphor for "these" (״כדי שהללו יקדישו...״).
- **Not ״זה״ as a dummy subject**: "This is important because" → ״הדבר חשוב משום ש...״, ״חשיבות הדבר ב...״, not
  ״זה חשוב כי...״. ״זהו״ / ״זוהי״ (258, 232) open a summing-up sentence: ״זוהי אפוא...״.
- **First person.** English essays say "I" and "we" far more than Hebrew ones (I: 1.0 against 0.36 per 1,000;
  we: 1.8 against 0.44). Keep the author's ״אני״ where the essay is personal (memoir, a reply to a critic, a
  confession) and where the author takes a stand (״אני מבקש להפנות את תשומת הלב...״). "I think" / "I believe"
  before a claim is often dropped or becomes ״נדמה לי״, ״לדעתי״. The inclusive "we" of an argument (we Americans,
  we moderns) is ״אנו״ (809, over ״אנחנו״ 319), or an impersonal sentence. For an American author writing about
  America, "we" stays ״אנו״, so the Israeli reader knows who is speaking.

## 7. Negation
- **Present-tense negation is ״אין״ / ״אינו״**: 5.9 per 1,000 words, almost as common as ״לא״ (6.9).
  ״אינו אלא״ for "is nothing but", ״אין הוא...״ for emphasis, ״איננו״ / ״אינני״ (414). ״לא״ is for past, future,
  imperative and before adjectives and adverbs (״לא מבוטל״, ״לא בכדי״). *Our drift:* 3.4 per 1,000, too low; a
  sentence like ״המדינה לא מסוגלת״ should be ״המדינה אינה מסוגלת״.
- Emphasis: ״כלל״ (״אין הדבר נכון כלל״), ״כלל וכלל לא״, ״לא זו בלבד ש... אלא ש...״.
- "not only X but also Y" → ״לא רק... אלא גם״, the formal ״לא זו בלבד ש...״. "not X but Y" → ״לא... אלא...״
  (״אלא״ is the commonest connective in the corpus, 1,666 times).
- Litotes is part of the register: ״לא בכדי״, ״לא מעט״, ״במידה בלתי מבוטלת״, ״אין זה מפתיע אפוא ש...״. Use it where
  the English is understated, not to soften a flat statement.

## 8. Linking clauses: connectives, subordinators, relatives
The connectives carry the argument. qc requires at least 5 per 1,000 words and at least `min(8, words / 200)`
different ones, measured over the list in `qc.CONNECTIVES`.

**Approximate counts in the 1.1 million Hebrew words, by function** (choose by the logic, never to raise a count):
- *Contrast*: אלא 1,666 · אבל 1,580 · אך 1,095 · אולם 568 · ואולם 328 · ברם 194 · עם זאת 146 · ואילו 313 ·
  בעוד 278 · לעומת זאת 226 · מנגד 37 · מחד גיסא / מאידך גיסא ~42 each · דא עקא 19.
- *Concession*: אף ש... 634 · למרות ש... 130 · אף על פי ש... 46 · הגם ש... 42 · אם כי 92 · אמנם... אך.
- *Cause*: בשל 787 · משום ש... 518 · מפני ש... 342 · שכן 245 · מאחר ש... 217 · עקב 186 · כיוון ש... 183 · בגלל
  146 · שהרי 119.
- *Consequence*: אפוא 436 · לכן 175 · על כן 168 · לפיכך 128 · ממילא 45 · מכאן ש... 21.
- *Addition and escalation*: יתר על כן 234 · נוסף על 84 · זאת ועוד 62 · כמו כן 37 · יתרה מזו 23 · ״בנוסף״ alone at
  the head of a sentence is rare (28): prefer ״נוסף על כך״ or ״יתר על כן״.
- *Restatement and example*: למשל 919 · דוגמת 240 · כלומר 215 · כגון 206 · במילים אחרות 139 · דהיינו 68.
- *Confirmation and summary*: אכן 598 · ואמנם 351 · ואכן 150 · בסופו של דבר 342 · כאמור 59 · מכל מקום.
- *Purpose*: כדי ל... 1,634 over ״על מנת ל...״ 85 and ״במטרה ל...״ 51.
- *Time*: כאשר 920 and כש... 1,559 · לאחר ש... 382 over ״אחרי ש...״ 87 · לפני ש... 173 · בטרם 56 · עד ש... 352 · כל
  עוד 105.

**How they map.**
- Sentence-initial "But" / "Yet" / "However" → ״ואולם״, ״אולם״, ״אבל״, ״אך״, ״ברם״, ״עם זאת״; "Indeed" →
  ״ואמנם״, ״ואכן״, ״שהרי״; "Thus" / "therefore" mid-argument → ״אפוא״ after the verb (״זוהי אפוא...״, ״אין זה מפתיע
  אפוא ש...״); "After all" → ״ככלות הכל״, ״הרי״; "Of course" → ״מובן ש...״.
- *Our drift:* we open with ״ואולם״ five times as often as תכלת (2.0 against 0.37 per 1,000) and never write
  ״אבל״ (תכלת: 1.0). ״ואולם״ is one choice among six; ״אבל״ is fine in an essay, especially in a plain or personal
  voice.
- Hebrew can add a joint the English leaves implicit (״שהרי״, ״אלא ש...״), but only where the English logic has
  it. Never turn a juxtaposition into a causal claim the author did not make.

**״ש״, ״כי״ and ״אשר״.**
- "that" after a verb of saying or thinking is ״ש...״ or ״כי״ about equally often in תכלת (״טען כי״ 32 / ״טען ש״
  39; ״נראה כי״ 57 / ״נראה ש״ 105). *Our drift:* we almost never use ״כי״ (0.85 per 1,000 against 3.8). Use ״כי״
  especially where ״ש״ would stack (״אמר שהמדינה שהקימה...״ → ״אמר כי המדינה שהקימה...״).
- ״כי״ as "because" is fine in a plain voice, but in argument prefer ״שכן״, ״משום ש״, ״מפני ש״.
- The relative ״אשר״ is rare (0.8 per 1,000; many essays never use it). Use it to avoid a second ״ש״ in a row,
  after a long subject, or in a solemn passage, never as the default.
- A participle often replaces the relative clause altogether: ״המועצה, שנוסדה זה לא מכבר״ / ״העיתון לה טאן הרואה
  אור בז׳נבה״.

## 9. Word choice
**Register.** The voice is educated literary-journalistic Hebrew: richer than a newspaper, never rabbinic,
never bureaucratic, never slang. An English essay's plain words are rendered by Hebrew's standard words for
the same thing, with an occasional precise idiom (section 10).

**Loanwords.** תכלת uses established international words freely (ליברלי 639, פוליטיקה 91, אידיאולוגיה 58,
לגיטימי 38, רדיקלי 38, אתוס 29, פרוגרסיבי) and avoids jargon loanwords that have a good Hebrew word:
| Avoid | תכלת | count |
|---|---|---|
| נרטיב | סיפור, תפיסה, גרסה | 0 / 201 |
| אג׳נדה | סדר יום, מטרות | 1 / 26 |
| קונספט | מושג, רעיון | 0 / 129 |
| דיסקורס | שיח | 0 / 54 |
| פרובלמטי | בעייתי | 0 / 16 |
| פרקטי | מעשי | 2 / 86 |
| אמריקאי | אמריקני | 5 / 1,431 |
When the author uses "narrative" as a term of art (a "national narrative"), ״נרטיב״ may stand, in quotation marks
the first time. Keep the English word where the author is discussing the word itself.

**Calques: English idioms translated word for word.** These read as translation. qc fails the first five; the rest are almost absent from תכלת, so prefer the right-hand column.
| English | not | write |
|---|---|---|
| at the end of the day | בסופו של יום (1 in the corpus) | בסופו של דבר (342) |
| play a role | לשחק תפקיד (0) | למלא תפקיד (30), ״להיות גורם ב״ |
| make sense | לעשות שכל, עושה שכל | הגיוני, מתקבל על הדעת |
| make a difference | לעשות הבדל | לשנות, להשפיע |
| on a daily basis | על בסיס יומי | מדי יום |
| make use of | לעשות שימוש ב (8 essays) | להשתמש ב |
| in light of the fact that | לאור העובדה ש (8 essays) | משום ש, מאחר ש |
| in terms of | במונחים של (18, technical only) | מבחינת, מבחינה... |
| meaningful (= important) | בעל משמעות, משמעותי for everything | חשוב, של ממש, ניכר |
| address an issue | ״לתת מענה ל״ for every "address" | לדון ב, לטפל ב, להתמודד עם |

**Prepositional phrases.** ״לגבי״ (322), ״בעניין״ (328), ״בנוגע ל״ (212), ״ביחס ל״ (200), ״בכל הנוגע ל״ and ״באשר
ל״ (113 each), ״על אודות״ (76). All are correct; vary them, and use plain ״על״ (״כתב על״, ״דן ב״) where it works.

**Intensifiers and hedges keep their strength.**
- "very" ״מאוד״ (655) is used, not for every adjective; often the stronger Hebrew adjective does the work
  (״גבוה להחריד״ for "frighteningly high"). ״למדי״ / ״למדיי״ for "rather", ״די״ for "fairly".
- Superlatives: ״ביותר״ appears 1.3 per 1,000 words. *Our drift:* 2.7. "One of the most X" is ״מן ה... ביותר״ or
  ״אחד ה...״ (״אחד המאורגנים בעולם״), and not every "most" is a superlative ("most Americans" is ״רוב האמריקנים״).
- English "-ly" adverbs (17 per 1,000 English words) mostly disappear into the verb or adjective (״אישי מאוד״ for
  "deeply personal", ״היה עדיין גבוה להחריד״). ״באופן״ + adjective is used (0.7 per 1,000) but never as the
  automatic rendering; ״בצורה״ + adjective is rarer still.
- Hedges: ״ככל הנראה״, ״כנראה״, ״ייתכן״, ״אולי״ (1.1 per 1,000) match the English may / might / perhaps / probably
  one for one. Never drop a hedge, never add one, never turn "perhaps most of all" into "most of all" (״ואולי
  יותר מכל״).

**Precision over elegance.** Do not replace a word with a synonym to avoid repetition when the author repeats it
on purpose, or when it is an argument-critical term. LLMs vary words for style; תכלת repeats a key term.

## 10. Idiom and the Jewish register
From the sample pairs, the kind of phrase תכלת reaches for where the English is plain:
- "to cheers and acclaim" → ״לקול תשואות מקיר אל קיר״
- "a perfect storm of adoration and acclaim" → ״הילולת הערצה וחנופה״
- "has nothing to do with" → ״אין לה ולא כלום עם״
- "there is no end to the charges" → ״תקצר היריעה מלפרט את כל ההאשמות״
- "repays in kind" → ״משיב להם באותו מטבע״
- "frequently denounced" → ״ספגה קיתונות של ביקורת״
- "show utter disregard for" → ״רמסו ברגל גסה את״
- "all this had been turned on its head" → ״התהפכו היוצרות״
- "most of the public" → ״חלק הארי של הציבור״
- "deliberately or not" → ״מדעת או שלא מדעת״
- "committed to the principle of" → ״חרת על דגלו את עקרון...״
- "at least in principle" → ״להלכה לפחות״
- "the crisis they faced" → ״המשבר שהתרגש ובא עליהם״
- "newly formed" → ״שנוסדה זה לא מכבר״
- "invaluable" → ״שערכה לא יסולא בפז״; "and with good reason" → ״ולא בכדי״; "in short" → ״בקצרה״
Use one where it fits the author's tone, at most one or two a paragraph. Never stack them, never put idiom where
the author is dry, and never use an idiom whose literal image clashes with the context. A biblical or rabbinic
echo is welcome where the English already alludes to the same source or where Hebrew has a standard phrase for
the idea; it is never added to make a secular author sound religious.

**English idioms.** If a Hebrew idiom fits exactly, use it. If not, translate the meaning plainly. If the idiom
adds nothing, drop it. Never translate the image word for word (section 9, calques).

## 11. Tone, voice and irony
- **Keep the temperature.** A dry policy essay stays dry; a polemic keeps its edge; a personal essay keeps its
  ״אני״. Do not raise the register of a plain author with idiom, and do not flatten an author who writes
  ornately.
- **Irony and sarcasm survive.** Scare quotes stay scare quotes (״ההיסטוריה ה׳רביזיוניסטית׳ הזאת״ *(illustration;
  the corpus prints them with plain marks)*). Understatement stays understated. A joke is translated as a joke, even if the
  wording changes; if it cannot be made to work in Hebrew, keep the point and say less.
- **Do not editorialize.** No ״למרבה הצער״, ״כידוע״, ״כמובן״ that the author did not write or clearly imply. An
  allegation stays an allegation (״לטענתו״, ״לכאורה״ where the English says "allegedly").
- **Opponents are quoted fairly.** The author's opponent is translated as precisely as the author.

## 12. Quotations
- Quote marks are ״ ״; a quotation inside a quotation takes ׳ ׳. Punctuation that is not part of the quoted words
  goes outside the closing mark.
- Translate quoted English speech so it sounds spoken, in the speaker's register. If the source exists in
  Hebrew (a Hebrew book, an Israeli speaker, a Bible verse), use the Hebrew original, never a back-translation.
- Words the author inserts into a quotation go in square brackets: ״[יש לך] נטייה ותחושה... מדהימות להוקעה ולמרי״.
- Quotation marks only around words someone actually said or wrote. A paraphrase gets none.
- Attribution verbs (section 4) may move into the quotation, as תכלת does with ״לצערנו״, הודה, ״הדיבור על
  ׳רנסנס׳ מעיד...״ (the nested quote in single marks).

## 13. Names, titles and foreign words
- **People.** The Hebrew Wikipedia spelling wins (Hadar's rule); otherwise the established press spelling;
  otherwise transliterate by sound, with geresh for ג׳ ז׳ צ׳ and וו for w. Look names up with `pipeline/lookup.py`.
  Pointing (ניקוד) only when a foreign name would be misread, and only the first time (״רוברט מוּגַבֶּה״).
- **Forms of address.** Drop "Mr." and "Ms." (מר 36, גב׳ 4 in the whole corpus). Keep functional titles:
  ״פרופ׳״ (87), ״ד״ר״, ״הרב״ (387), ״הנשיא״, ״השופט״, ״הסנאטור״.
- **Books, films, journals.** Use the Hebrew title of a confirmed Hebrew edition; otherwise translate the title
  in italics, with the English in parentheses the first time when the reader might look for it:
  ״אימפריית החוק (*Law's Empire*)״. Newspapers by their name in Hebrew letters: ״וול סטריט ג׳ורנל״, ״לה מונד״.
- **Organizations and programs.** Hebrew name if one is established (האו״ם, האיחוד האירופי); otherwise
  transliterate and explain once (״אגודת המחקר המזרח־תיכוני (MESA)״ *(illustration)*). The names of programs,
  operations and parties take single quotes: ״׳פראנס אינטר׳״, ״פרויקט ׳תלפיות׳״, ״מפלגת ׳אל־נהדה׳ (התחייה)״.
- **Acronyms.** An established Hebrew acronym with gershayim (צה״ל, האו״ם, ארה״ב only in tables). A foreign
  acronym with no Hebrew form stays in Latin letters after the Hebrew name the first time (״החזית האלג׳יראית
  לשחרור לאומי (FLN)״), and Latin letters after that. Hebrew prefixes attach with a maqaf: ״ב־FLN״.
- **American institutions**: `US-POLITICS.md`. Never give a foreign institution an Israeli civic name
  (״היועץ המשפטי לממשלה״ is Israel's, not a state attorney general).

## 14. Numbers, dates, units
- **Years.** ״בשנת 1977״ (878) and ״ב־1977״ (327) are both standard; use the maqaf, not a hyphen (״ב-1977״ 187 is
  the older web form). Decades in words: ״בשנות השישים״ (229), ״שנות התשעים״.
- **Dates**: ״ב־26 במרס 2008״, ״בחודש יולי האחרון״. תכלת writes ״מרס״ (24) more than ״מרץ״ (15); we write ״מרס״.
- **Numbers in words** below ten and for round numbers in prose (״שלושה מכתבים״, ״כחמישים תלמידים״, ״עשרים
  ספרים״); digits for 10 and above, for statistics, money and anything exact. Numbers agree in gender with the
  noun (״שלוש שנים״, ״שלושה חודשים״, ״שתים־עשרה שנה״, ״שש־עשרה שנה״).
- **Percent** in words in prose: ״כשמונים אחוזים מן השכירים״ (אחוזים 536, % 78); % in data-heavy passages.
- **Money**: ״10 מיליון דולר״, ״2.5 מיליארד דולר״; ״כ־״ for "about" (״כחמישים״, ״כ־300 מיליון״).
- **Ranges** with an en dash and no spaces (״1948–1967״).
- **Every number of two or more digits in the English appears in the Hebrew**, or is listed in
  `fidelity_waivers` with the reason (qc checks this).

## 15. Punctuation and typography
Hebrew essays punctuate a little more densely than English ones (per 1,000 words, Hebrew against the English of
the same essays): comma 80 / 74, semicolon 4.1 / 2.7, colon 6.3 / 4.8, parentheses 4.3 / 3.3, dash 8.8 / 5.2.
- **Comma** where you would pause. No comma before ״ו״ inside a list; a comma before ״ו״ only between two full
  clauses. A comma after a fronted adverbial phrase, not after a single word (״בקצרה,״ but ״כיום יש...״).
- **Semicolon** between parallel or contrasting full clauses (section 3).
- **Colon** before an explanation, a list or a quotation, never in place of a comma.
- **Dash**: a spaced en dash ( – ) around an apposition or an aside (״זיגלר – פרופסור לסוציולוגיה... – במרכזה
  של...״) and before a sharp addition (״וחשוב לא פחות – מעניק מידה של ודאות״). Not every English em dash
  becomes a dash: a comma or parentheses are often better.
- **Parentheses** for brief explanations and original-language names. Brackets inside parentheses.
- **Maqaf** ־ (no spaces) joins a prefix to a number or Latin letters (״ב־1983״, ״ה־FLN״), forms compounds
  (״רב־תרבותיות״, ״אי־אפשר״, ״לא־יהודי״) and compound numbers
  (״שש־עשרה״). We write ״ארצות הברית״ and ״ברית המועצות״ without one.
- **Gershayim** ״ in acronyms (צה״ל), **geresh** ׳ in abbreviations and transliteration (פרופ׳, ג׳ורג׳).
  Never an English " or '. qc fails English double quotes.
- **Italics** for titles of books, films, journals and for the author's own emphasis. English italic emphasis
  on a word can also become word order (put the word last) when italics would look foreign.
- **Exclamation marks** are almost absent (0 in the median essay). Keep one only where the English has one.
- **Ellipsis** … for omitted words inside a quotation.
- **Every sentence ends with a period**, including the last one in a paragraph.
- **Bidirectional text**: a Latin word, number or URL inside a Hebrew sentence must not drag the punctuation to
  the wrong side; put a Hebrew word next to the punctuation or rephrase.

## 16. Spelling
- כתיב מלא by the Academy's rules, checked by `pipeline/hebcheck.py`: ״מאוד״, ״אמריקני״, ״ציוויליזציה״,
  ״אפריקני״, ״תכנית״ (168 against ״תוכנית״ 2), ״אי־אפשר״.
- Older forms we modernize: ״ארצות־הברית״ and ״ברית־המועצות״ with a maqaf become ״ארצות הברית״ and ״ברית
  המועצות״. The corpus has both ״ציביליזציה״ and ״ציוויליזציה״; we use ״ציוויליזציה״.
- One spelling per name in the whole post; the glossary and `lookup.py` hold the settled ones.

## 17. Titles, subtitles, tweets
`TITLES.md` covers the headline (2 to 6 words, a noun phrase or a short sentence, never a calque of an English
pun) and the subtitle. Tweets follow `TRANSLATION.md`: an allegation stays an allegation, and no quotation marks
around a paraphrase.

## 18. Where our drafts drift (measured 2026-10-30)
Our eight retranslations against the 224 תכלת essays (median essay). qc warns on the first six (at about the
5th or 95th percentile of תכלת, so 7 to 11 of the 224 essays trip each one): a warning is a prompt to reread, not
an order. Fix it in the prose where the essay allows; never add or remove words just to move a number.

| measure (per 1,000 words) | תכלת p5 / median / p95 | ours | fix |
|---|---|---|---|
| ״ואולם״ | 0 / 0.37 / 1.48 | 2.0 | vary contrast: אבל, אך, אולם, ברם, עם זאת, ואילו |
| ״אין / אינו״ forms | 2.5 / 5.9 / 11.5 | 3.4 | present-tense negation (section 7) |
| ״כי״ (all uses) | 1.4 / 3.8 / 8.5 | 0.85 | alternate with ״ש״ after verbs of saying |
| ״ביותר״ | 0 / 1.3 / 2.9 | 2.7 | fewer superlatives (section 9) |
| ״עצמו / עצמה / עצמם״ | 0.7 / 1.9 / 4.2 | 3.3 | drop emphatic "himself" |
| sentence-length deviation (words) | 8.9 / 11.9 / 17.2 | 8.7 | let some sentences run, some stop short |
| sentences of 40+ words | 2.3% / 7.5% / 16% | 2.9% | |
| ״אבל״ | 0 / 1.0 / 4.8 | 0 | ״אבל״ is allowed |
| ״למשל״ | 0 / 0.7 / 1.9 | 0 | introduce examples |
| average sentence (words) | 17 / 22 / 26 | 18 | |

## 19. Self-check before the review
The categories follow MQM, the standard error typology for translation review; `REVIEWER.md` assigns severity.
1. **Accuracy**: nothing added, nothing omitted, every number, name, date and quotation right; hedges and
   intensifiers at the English strength; allegations still allegations; irony intact.
2. **Terminology**: argument-critical terms identical throughout; glossary and `US-POLITICS.md` followed; no
   Israeli civic names for foreign institutions.
3. **Fluency (grammar)**: agreement of gender and number, numbers with nouns, the article in constructs, verb
   government (section 4), no calques (section 9).
4. **Style**: sentence length and variety, connectives varied and true to the logic, ״אין״ negation, ״של״
   density, register even, no stacked idioms, the author's temperature.
5. **Locale conventions**: names by Hebrew Wikipedia, dates and numbers (section 14), punctuation and
   typography (section 15), spelling (hebcheck).
6. **Read it aloud** in your head as a תכלת reader would. Any sentence that you would not expect to find in
   תכלת is rewritten, not polished.

## 20. Term bank (how תכלת rendered recurring terms; the settled ones are in glossary.json)
| English | תכלת | Note |
|---|---|---|
| sovereignty, sovereign | ריבונות, ריבוני/ריבונית, ריבון | |
| nation-state | מדינת הלאום | |
| nationalism | לאומיות | not לאומנות, which is pejorative (chauvinism) |
| liberalism, liberal democracy | ליברליזם, דמוקרטיה ליברלית | |
| liberty, freedom | חירות | חופש for specific freedoms: חופש הביטוי |
| the West, Western civilization | המערב, הציוויליזציה המערבית | |
| the Enlightenment | הנאורות | |
| secular | חילוני | |
| haredi, ultra-Orthodox | חרדי, חרדים | |
| Diaspora / exile | הגולה, התפוצות / הגלות | Diaspora as a place is גולה; exile as a condition is גלות |
| redemption, messianism | גאולה, משיחיות | |
| revelation, covenant | התגלות, ברית | |
| the Bible, biblical | המקרא, מקראי | תנ״ך where the context is everyday or educational |
| the Sages, rabbinic | חז״ל, חכמים; רבני | |
| halacha | ההלכה | |
| Supreme Court (Israel), judicial activism | בית המשפט העליון, אקטיביזם שיפוטי | |
| rule of law, separation of powers | שלטון החוק, הפרדת רשויות | |
| civil society, public sphere | החברה האזרחית, המרחב הציבורי | |
| self-determination, self-government | הגדרה עצמית, ממשל עצמי | |
| elite(s) | עילית, אליטה/אליטות | |
| intellectuals, intelligentsia | אינטלקטואלים, אנשי רוח; האינטליגנציה | |
| academia | האקדמיה | |
| political correctness | התקינות הפוליטית | |
| relativism, pluralism, multiculturalism | רלטיביזם (מוסרי), פלורליזם, רב־תרבותיות | |
| universalism, particularism | אוניברסליזם, פרטיקולריזם | |
| assimilation, the Emancipation | התבוללות, האמנציפציה | |
| legitimacy | לגיטימיות | |
| totalitarianism, tyranny | טוטליטריות, עריצות | |
| just war, deterrence | מלחמה צודקת, הרתעה | |
| terrorism, terrorist | טרור, מחבל / ארגון טרור | a Palestinian gunman is מחבל |
| settlers, settlements | מתנחלים, התנחלויות; ההתיישבות | |
| the territories, occupation | השטחים, הכיבוש | the author's own term, kept, with quotation marks if the author distances himself |
| statesman | מדינאי | |
| the public good | טובת הציבור | |
| virtue(s) | מידות טובות, מידה; סגולה | |
| republic, republican (political idea) | רפובליקה, רפובליקני | |
| national identity, collective identity | זהות לאומית, זהות קיבוצית | |
| heritage, canon | מורשת, קאנון | |
| Christianity, the Church, Catholic | הנצרות, הכנסייה, קתולי | |
| United Nations, EU, Muslim Brotherhood | האו״ם, האיחוד האירופי, האחים המוסלמים | |
| equality, justice, rights, duty, authority | שוויון, צדק, זכויות, חובה, סמכות | |
| the American / Americans | אמריקני / אמריקנים | never אמריקאי |
| administration (US) | ממשל (״ממשל רייגן״) | |

## Sources consulted for the structure of this guide
- Professional translation and localization style guides: what they contain (tone and formality, grammar,
  terminology, punctuation, locale formats, examples), e.g. [Lokalise](https://docs.lokalise.com/en/articles/8217808-style-guide),
  [Phrase](https://support.phrase.com/hc/en-us/articles/25124298060060), the
  [WordPress Polyglots template](https://make.wordpress.org/polyglots/handbook/for-editors/glossary-style-guide/style-guide-template/),
  and [Cochrane's guide to creating one](https://documentation.cochrane.org/spaces/TH/pages/384303158/Creating+a+style+guide).
  An [EAMT 2026 study](https://aclanthology.org/2026.eamt-2.31.pdf) found AI translation loses quality when a
  guide states only exceptions and leaves out the general grammar rules, which is why this guide spells them out.
- The [Microsoft Hebrew localization style guide](https://download.microsoft.com/download/a/2/f/a2ff07cc-afca-4db8-9ed7-fd1b706abf1c/heb-isr-StyleGuide.pdf):
  rewrite rather than translate word for word; avoid ״לעשות שימוש״, ״לבצע״ + noun; drop redundant possessives;
  ״על ידי״ before an action and ״באמצעות״ before an instrument; adjectives agree; numbers below ten in words; comma
  rules; maqaf and dashes; punctuation outside quotation marks. (It is written for software, so its informal
  register is not ours.)
- [MQM](https://www.w3.org/community/mqmcg) (Multidimensional Quality Metrics), the error typology of accuracy,
  fluency, terminology, style and locale conventions used for section 19 and `REVIEWER.md`.
- Research on translationese in LLM output: asking a model to "be natural" in general helps little, while
  revising its own draft against concrete indicators and showing it real examples helps more
  ([Slator on the study](https://tech.slator.com/?p=104183), [Luxembourg CUCO lab](https://cucolab.uni.lu/blog/conversations-5-less-translated-translations),
  [arXiv 2505.16612](https://arxiv.org/pdf/2505.16612v1)). Hence the measured drift table, the corpus search and
  the separate review passes, rather than general advice.
- The Academy of the Hebrew Language on punctuation and spelling, through `hebcheck.py`, and its
  [note on the calque "meaningful"](https://hebrew-academy.org.il/wp-content/uploads/עוד-על-בחינות-הבגרות-בהבעה-עברית.pdf).
