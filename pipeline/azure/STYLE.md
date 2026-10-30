# השמרן: the תכלת voice (from 100 Azure / תכלת parallel essays)

Our model is תכלת (Shalem Press, 1996–2012). Azure, its English sister journal, published many of the same
essays, so we have 100 essays in both languages (`index.csv`, about 940,000 English and 750,000 Hebrew words).
This page is what those pairs teach. Read it before every translation, together with `pipeline/TRANSLATION.md`.

## Using the corpus during a run
```
python3 pipeline/azure_corpus.py fetch                   # checks the stored copy; downloads only if missing
python3 pipeline/azure_corpus.py search "civil society"  # how תכלת rendered it, in context
python3 pipeline/azure_corpus.py search "אפוא" --he      # how a Hebrew word is used
python3 pipeline/azure_corpus.py show 42                 # a whole pair
```
Search whenever a term, idiom or construction is not settled in `pipeline/glossary.json`. If תכלת used it
consistently, follow it and add it to the glossary. The texts are Shalem Press's copyright: the permanent copy is the
private project folder `/mnt/project-files/hashamran/translation-guide/pairs/`, and they are never committed to
this public repo. Quote at most a phrase or two
of them in the log.

## 1. A Hebrew essay, not a translated one
תכלת's editors rewrote for the Israeli reader. The Hebrew is about 20% shorter than the English (750 vs 940
thousand words). Part of that is Hebrew's compactness and part is editing: the Jenin essay, for example, drops
the English opening about Iraq.
- **Rebuild the opening sentence for a Hebrew reader.** Azure's "Of the countries hardest hit by the current
  outbreak of anti-Semitism in Europe, France poses a particular dilemma" became ״גל האנטישמיות שפקד לאחרונה את
  אירופה לא פסח, כידוע, גם על צרפת. ואולם...״. The meaning stays and the sentence is new.
- **Identify foreign figures in a short apposition the first time**: ״העיר פעם העיתונאי והסטיריקן האמריקני ה״ל
  מנקן״, ״הוגה הדעות היווני אפלטון״. One phrase, never a footnote.
- **Use the canonical Hebrew for classic texts**: Plato's ship of state is quoted from the standard Hebrew
  translation (״כן תאר לך אניות רבות או אנייה אחת...״), not translated from the English quotation.
- **Use the Hebrew names of Jewish figures**: Herzl is ״בנימין זאב הרצל״ where the English has "Theodor Herzl".
- For us (we translate other people's essays and credit them) there is one limit: rebuild sentences and reorder
  within a paragraph freely, but do not drop the author's arguments or examples.

## 2. Syntax
- **Verb before subject** in narrative and argument: ״נבחר ז׳אן זיגלר בידי מועצת...״, ״בתוך עשור התהפכו
  היוצרות״, ״לא הייתה זו התפתחות בלתי צפויה״, ״היה זה ניצחון נוסף...״.
- **Formal negation and copula**: אינו / אינה / אין הוא (״אין הוא אזרח רע הנגרר לפשע״), ״...אינה אלא תסמין של...״.
  In the corpus ״אינו/אינה״ appear about 2,000 times.
- **Reflexive without את**: ״מצא עצמו״, ״להעמיד עצמה לבחינה״.
- **Medium-length sentences** (about 16 words on average). A long English sentence becomes two Hebrew ones, or
  one joined with a semicolon. תכלת uses ; often.
- **Construct chains are short.** Use a verb or a relative clause instead of a third construct link.

## 3. Connectives and the essay's joints
These carry the argument. Corpus counts per 720,000 Hebrew words:
אלא 1,666 · אך 1,095 · אף 980 · אולם 568 / ואולם 328 · **אפוא 436** · הרי 267 / שהרי 119 · למעשה 283 · כלומר 215 ·
שכן 209 · כמובן 200 · ברם 194 · לכן 175 / על כן 168 · עם זאת 146 · יתר על כן 142 · לפיכך 128 · דהיינו 68 ·
כאמור 59 · לא זו בלבד 59 · ממילא 45 · לאמיתו של דבר 38 · זאת ועוד 34 · דא עקא 19.
- Vary them. A paragraph that opens with "But" or "Yet" usually opens with ״ואולם״ or ״ברם״, and "Indeed" with
  ״ואמנם״. "Thus" or "therefore" in the middle of an argument is usually ״אפוא״, placed after the verb (״זוהי
  אפוא...״).
- Avoid the colloquial ״בעצם״ and ״באמת״ as sentence fillers. They do appear, but rarely.

## 4. Register: idiom, used sparingly and exactly
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
Use one where it fits the author's tone. Never stack them, and never put idiom where the author is dry.

## 5. Spelling and typography
- כתיב מלא. Dates are written ״ב־26 במרס 2008״ and ״בשנת 1977״.
- Maqaf before numbers: ״ב־1983״ (555 times in the corpus) over ״ב-1983״ (324).
- Acronyms with gershayim: צה״ל, האו״ם, חז״ל, אופ״ק.
- Dash: a spaced dash between clauses (״זיגלר – פרופסור לסוציולוגיה... – במרכזה של...״).
- תכלת's web edition used plain " for quotation marks. We print the proper ״ ״, which is the same convention
  set correctly.
- Older forms that we modernize: ״ארצות־הברית״ and ״ברית־המועצות״ with a maqaf become ״ארצות הברית״ and ״ברית
  המועצות״. The corpus has both ״ציביליזציה״ and ״ציוויליזציה״. We use ״ציוויליזציה״.

## 6. Term bank (how תכלת rendered recurring terms; the settled ones are in glossary.json)
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
