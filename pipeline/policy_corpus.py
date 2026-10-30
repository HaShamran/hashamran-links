"""Fourth reference, for legal, policy and security terms only: Israeli think tanks that publish in both English
and Hebrew, side by side. One tool for all of them (pipeline/kohelet_corpus.py is the Kohelet-only form).

Banks (index files in this folder; private texts under /mnt/project-files/hashamran/translation-guide/<bank>/pairs):
- kohelet  Kohelet Policy Forum: Israeli law, the courts, international law, economy, education
- misgav   Misgav Institute for National Security and Zionist Strategy: Iran, Hezbollah, Gaza, US-Israel relations
- jiss     Jerusalem Institute for Strategy and Security: strategy, security, the region
- inss     Institute for National Security Studies: security research (added when its index exists)

Every pair was checked before it was added (see each bank's README in the project folder). Many were written in
Hebrew first, so read a pair as "this Hebrew term goes with this English one", not as a model translation. None of
them sets voice or style: תכלת (pipeline/azure/) stays primary.

Usage (as pipeline/mida_corpus.py, plus --bank):
    python3 pipeline/policy_corpus.py search "deterrence"                 # all banks
    python3 pipeline/policy_corpus.py --bank misgav search --he "הרתעה"
    python3 pipeline/policy_corpus.py count "מערכה בין המלחמות" "campaign between wars"
    python3 pipeline/policy_corpus.py --bank jiss show 12
"""
import os
import pathlib
import sys

import mida_corpus

HERE = pathlib.Path(__file__).parent
STORE = pathlib.Path(os.environ.get("POLICY_STORE", "/mnt/project-files/hashamran/translation-guide"))
BANKS = ("kohelet", "misgav", "jiss", "inss")


def use(bank):
    mida_corpus.INDEX = HERE / bank / "index.csv"
    mida_corpus.STORE = STORE / bank / "pairs"
    return mida_corpus.INDEX.exists()


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    banks = BANKS
    if argv[:1] == ["--bank"]:
        banks, argv = (argv[1],), argv[2:]
    for bank in banks:
        if use(bank):
            if len(banks) > 1:
                print(f"=== {bank}")
            mida_corpus.main(argv)
    return 0


if __name__ == "__main__":
    sys.exit(main())
