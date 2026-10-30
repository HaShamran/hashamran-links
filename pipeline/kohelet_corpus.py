"""Fourth reference, for terminology only: Kohelet Policy Forum articles published in both English and Hebrew.

72 pairs (2013–2026) from kohelet.org.il: op-eds, legal memos and journal essays on Israeli law, the courts,
international law, security, the economy and education. Strong for legal, constitutional and policy terms (legal
adviser, justiciability, the Genocide Convention, the ICJ); thin on American politics. Most were written in Hebrew
and translated into English, the opposite of our direction (index.csv column original: he, en, or empty when the
page does not say), so read a pair as "this Hebrew term goes with this English one", not as a model translation.
It never sets voice or style: תכלת (pipeline/azure/) stays primary.

Each pair was checked before it was added: linked as translations by the site itself (71) or by author and numbers
(1), and kept only when the Hebrew is 0.6–1.25 times the English in words, at least a quarter of their numbers are
shared, the paragraph counts are close and the dates are within 90 days.

The texts are Kohelet's copyright: the private copy is the project folder
/mnt/project-files/hashamran/translation-guide/kohelet/pairs/<dir>/{en,he}.md, never this public repo.

Usage (as pipeline/mida_corpus.py):
    python3 pipeline/kohelet_corpus.py search "judicial review"
    python3 pipeline/kohelet_corpus.py search --he "ייעוץ משפטי"
    python3 pipeline/kohelet_corpus.py count "שפיטות" "זכות עמידה"
    python3 pipeline/kohelet_corpus.py show 12
"""
import os
import pathlib
import sys

import mida_corpus

mida_corpus.INDEX = pathlib.Path(__file__).with_name("kohelet") / "index.csv"
mida_corpus.STORE = pathlib.Path(os.environ.get("KOHELET_STORE",
                                                "/mnt/project-files/hashamran/translation-guide/kohelet/pairs"))

if __name__ == "__main__":
    sys.exit(mida_corpus.main())
