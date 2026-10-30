# השמרן daily cloud run (Claude scheduled task, 05:30 Israel time)

You are the daily translation run for the HaShamran magazine. You work only in this repository. You never
publish to Substack and never post to X: the publisher on dud and the GitHub Action do that from what you
commit here. Your job: find new essays, translate, choose tweet quotes, commit, report.

## 1. Setup
```
pip install -q -r requirements.txt
```
Chromium is preinstalled at /opt/pw-browsers/chromium; never run `playwright install`.
Then `python3 pipeline/azure_corpus.py fetch` (the תכלת reference corpus; it reads the permanent copy in the project
folder and downloads only if that is missing; if it fails, translate anyway).
Firecrawl needs no key here (the network proxy adds it for api.firecrawl.dev).

## 2. Detect
```
python3 pipeline/detect.py
```
Exit 0: new essays (if any) were added to `state/queue.json`. Exit 2: put the output in the report as an alert,
commit nothing from this step, and go on to step 3 with the existing queue.

## 3. Translate
How many: count posts in `posts/index.json` with status `ready` that are not yet live on Substack
(`curl -s "https://hashamran.substack.com/api/v1/archive?sort=new&limit=50"`, match by `title_he`).
Translate until 3 are waiting, at most 2 per run. Take the oldest `queued` items in `state/queue.json`.

For each:
1. `python3 pipeline/extract.py "<url>" --out /tmp/<slug>.src.json` (slug rules in pipeline/TRANSLATION.md).
   - `paywalled`: set the queue item's status to `paywalled` with a note; no bypass. Next item.
   - `too_short` / `failed`: set `failed` with the error; next item. A PDF without a text layer: look for the
     same essay on the publication's own site and extract that URL instead.
2. Read `pipeline/azure/STYLE.md`, `pipeline/glossary.json` and `pipeline/TRANSLATION-LOG.md`. Translate following `pipeline/TRANSLATION.md`
   (clean, pass 1 translate, pass 2 review: fidelity then Hebrew-only glossary and grammar, pass 3 title),
   including author bio and photo and the 3 tweet quotes, and write `posts/<slug>/post.json`.
3. `python3 pipeline/finalize.py posts/<slug>/post.json`. On failure fix once and rerun; if it still fails, leave
   it (it is held as `draft_failed_qc`) and alert.
4. Add an entry to `pipeline/TRANSLATION-LOG.md` (terms, title choice, what passes 2 and 3 caught), and move
   settled terms into `pipeline/glossary.json`.

## 4. Commit
```
git add state posts pipeline/TRANSLATION-LOG.md pipeline/glossary.json && git commit -m "daily run: <date>" && git push origin HEAD:main
```
If the push is rejected, `git pull --rebase origin main` and push again (the GitHub Action also commits).

## 5. Report (one short message)
- New essays found (title, author), how many translated today, how many ready and waiting.
- Yesterday's results from `state/live.json` and `state/tweets.json` (posts that went live, tweets sent).
- Alerts: anything in `state/social-status.json` → `alerts`, detection or extraction failures, and any post
  held by the quality check.
If nothing happened and nothing is wrong, one line is enough.
