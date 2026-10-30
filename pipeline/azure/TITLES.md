# השמרן: how תכלת titled its essays (pass 3)

The 224 parallel essays (`index.csv`) show the same essay titled twice, once by Azure in English and once by
תכלת in Hebrew. About 40 of the Hebrew titles are close to the English. The other 60 were rethought for the
Hebrew reader. These are the moves they used. In pass 3, write at least one candidate with a close title and
at least one with one of these moves, then choose.

## 1. Keep it close when the English already works in Hebrew
A plain, strong English title stays plain:
- Is There a Future for French Jewry? → ״האם יש עתיד ליהדות צרפת?״
- The Decline of Israeli Sociology → ״שקיעת הסוציולוגיה הישראלית״
- The Tower of Babel and the Birth of Nationhood → ״מגדל בבל והולדת הרעיון הלאומי״
- Judaism as a First Language → ״היהדות כשפת אם״
Questions stay questions. A close title is never word for word: ״הולדת הרעיון הלאומי״, not ״לידת הלאומיות״.

## 2. Replace an English pun with a Hebrew one, never translate the pun
- Voodoo Demographics → ״דמגוגרפיה״ (demagogy plus demography)
- Death by Taxes → ״מיסוי וטעייה״ (on ניסוי וטעייה)
- The Supreme Court In Loco Parentis → ״שופטים ללא גבולות״ (on רופאים ללא גבולות)
- Education's Forsaken Vision → ״חינוך בלי מרכאות״
- Staring Down the Barrel: Israel's Oil Problem → ״מחיר החבית: כיצד מפרקים את נשק הנפט?״
- Strikes Again → ״משק יום הדין״
If no Hebrew pun comes naturally, use another move. A forced pun is worse than none.

## 3. Reach for a Hebrew or Jewish echo the reader knows
- Act and Comprehend → ״נעשה ונשמע״ (Exodus 24:7)
- Love's Human Bondage: A Biblical Warning → ״עזה כמוות אהבה: אזהרה מקראית״ (Song of Songs 8:6)
- Jacob Birnbaum and the Struggle for Soviet Jewry → ״...והמאבק למען יהדות הדממה״
- Lawrence of Judea → ״לורנס איש ציון״
- Is This Land Still Our Land? → ״להציל את הקופסה הכחולה״ (the JNF box, an Israeli icon)
- State Your Occupation → ״בעקבות הזמן הציוני האבוד״ (Proust, as Hebrew readers know him)
Check any biblical or rabbinic wording with `python3 pipeline/lookup.py source "<ref>"`.

## 4. Replace an allusion the Israeli reader won't catch with the essay's real subject
- Nathan the Wise → ״אלתרמן כשמרן״
- Far Away, So Close → ״התיאולוגיה של הדבקות״
- Now I Am Become Life → ״אחריותו של בורא בזעיר אנפין״
- Ziegler's Follies → ״מהפכן החצר של האו״ם״
- Cruel Britannia → ״גאווה ודעה קדומה״ (swapped for a British allusion Hebrew readers do know)
- Zohan and the Quest for Jewish Utopia → ״בין שתי אוטופיות״
For our American essays this is the most common case: pop-culture and political allusions that mean nothing in
Hebrew. Name the subject, or find the Israeli equivalent.

## 5. Antithesis and parallel phrasing
- Israel's Electoral Complex → ״שיטה יחסית, כישלון מוחלט״
- The State of Freedom and the State of Emergency → ״מצב החירום ומצב החירות״ (reordered for the climax)
- Old Fears, New Threats → ״פחדים ישנים, איומים חדשים״
- The Midrash as Marriage Guide → ״גברים מבבל, נשים מארץ ישראל״
- A Chilly Welcome for Arab Democracy → ״דמוקרטיה מצרית ודמוקרטופוביה ישראלית״

## 6. One evaluative word that states the essay's verdict
- The Spectacles of Isaiah Berlin → ״המשקפיים העכורים של ישעיה ברלין״
- Tom Segev's New Mandate → ״המנדט המפוקפק של תום שגב״
- A Nation Conceived in Defeat → ״הראשית העגומה של העם היהודי״
Only when the essay's argument fully supports the verdict.

## 7. Topic, colon, angle
- Reagan Reconsidered → ״רייגן: בחינה מחודשת״
- Globalization: Just Do It → ״גלובליזציה: כתב הגנה״
- The Road to Democracy in the Arab World → ״דמוקרטיה במזרח התיכון: הוראות הפעלה״
- A Tragedy Shrouded in Silence → ״חורבן קהילות ארצות ערב: האסון שנגנז״
Short noun phrase first, the hook after the colon.

## Shape
- Most are 2 to 6 words. Use a noun phrase over a sentence. No clickbait and no exclamation marks.
- Bring it home when the essay allows: Zionism's Compatriots → ״ישראל ומדינות הלאום החדשות״.
- Record in the translation log which move won and why.
