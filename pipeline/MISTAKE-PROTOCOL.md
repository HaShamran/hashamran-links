# השמרן: what to do every time a translation mistake is found

Hadar's standing rule (14 Nov 2026): every mistake, whether Hadar, a reviewer or a check finds it, goes through all
of these steps, in this order, before the work is called done. Run it in the same session that found the mistake.

1. **Fix the instance.** Correct `posts/<slug>/post.json`. If the post is already live, add each correction to
   `state/live-fixes.json` (`{"id", "slug", "find", "replace"}`, a unique id, `find` copied exactly from the post):
   dud's publisher applies it within 30 minutes and presses Update without email. Check the live page afterwards.
2. **Sweep everything we have.** Write the mistake as a Hebrew regex (and, where it has one, the English that
   triggers it) and run
   `python3 pipeline/mistake_sweep.py --he '<regex>' [--en '<English regex>'] [--qc <check>]`.
   It counts the pattern in all our posts and in the Hebrew of every reference bank (תכלת, השילוח, Mida, Kohelet,
   Misgav, JISS, INSS, Israel Hayom). Read the hits by eye: a regex over-counts.
3. **Answer three questions, with numbers.**
   - How many more times did we make it? (posts, hits, per 10,000 words)
   - Do the professional translations make it too, and how often? (per 10,000 words; תכלת first)
   - How do the archive translators render the same English so the mistake does not happen? Quote 3-5 real
     examples from the banks.
4. **Fix every other instance.** Queued posts in the repo; live posts through `state/live-fixes.json`.
5. **Make it impossible to repeat.** A mechanical pattern becomes a check in `pipeline/qc.py` (a problem when it
   is always wrong in house style, a warning when context decides) with a test in `tests/`. A judgment call
   becomes a line in the reviewer prompt in `pipeline/REVIEWER.md` and in `pipeline/azure/STYLE.md`.
6. **Note it for next time.** Add an entry to `pipeline/TRANSLATION-LOG.md` headed `Mistake:` with the answers
   from step 3 and the rule, and settled terms to `pipeline/glossary.json`. Add a line to `dev_log` in the project
   folder (dev-log rule).
7. **Tell Hadar** in one short message: the count, what the archive does, what was fixed, what now prevents it.
