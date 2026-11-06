# השמרן daily cloud run (Claude scheduled task, 05:30 Israel time)

You are the daily translation run for the HaShamran magazine. You work only in this repository. You never
publish to Substack and never post to X: the publisher on dud and the GitHub Action do that from what you
commit here. Your job: find new essays, translate, choose tweet quotes, commit, report.

## 1. Setup
```
pip install -q -r requirements.txt
```
Chromium is preinstalled at /opt/pw-browsers/chromium; never run `playwright install`.
Then `python3 pipeline/azure_corpus.py fetch && python3 pipeline/hashiloach_corpus.py fetch` (the תכלת reference corpus; it reads the permanent copy in the project
folder and downloads only if that is missing; if it fails, translate anyway).
Firecrawl needs no key here (the network proxy adds it for api.firecrawl.dev).

## 2. Detect
```
python3 pipeline/detect.py
```
Exit 0: new essays (if any) were added to `state/queue.json`. Exit 2: put the output in the report as an alert,
commit nothing from this step, and go on to step 3 with the existing queue.

Then top up the queue: `python3 pipeline/backfill.py`. Hadar's rule (6 Nov 2026) is at least two articles live
every day, and the page adds essays more slowly than that. When fewer than 3 essays are queued, this moves the newest
older essays from the page (listed before detection began) into the queue. New essays stay ahead of them. List
any backfilled titles in the report.

## 3. Translate
How many: count posts in `posts/index.json` with status `ready` that are not yet live on Substack
(`curl -s "https://hashamran.substack.com/api/v1/archive?sort=new&limit=25"`, a `{"posts": [...]}` object; limit above 25 gets a 400; match by `title_he`).
Translate until 6 are waiting, at most 3 per run. dud publishes 2 a day whenever 2 or more are ready, and Hadar's
rule is at least 2 a day, so the buffer has to cover a day when an item fails, is paywalled, or is held.
A backfilled item that is not an essay or article (a video, podcast, or social post), or that is clearly not right for
השמרן, gets the status `skipped` with a one-line reason. Then take the next one. Take the oldest `queued` items in `state/queue.json`.

For each:
1. `python3 pipeline/extract.py "<url>" --out /tmp/<slug>.src.json` (slug rules in pipeline/TRANSLATION.md).
   - `paywalled`: set the queue item's status to `paywalled` with a note; no bypass. Next item.
   - `too_short` / `failed`: set `failed` with the error; next item. A PDF without a text layer: look for the
     same essay on the publication's own site and extract that URL instead.
2. Read `pipeline/azure/STYLE.md`, `pipeline/US-POLITICS.md`, `pipeline/glossary.json` and `pipeline/TRANSLATION-LOG.md`. Translate following `pipeline/TRANSLATION.md`
   (clean, prepare and brief, pass 1 section by section with memory, title and quotes, independent review and
   blind back-translation by fresh subagents per `pipeline/REVIEWER.md`),
   including author bio and photo and the 3 tweet quotes, and write `posts/<slug>/post.json`.
3. `python3 pipeline/finalize.py posts/<slug>/post.json /tmp/<slug>.src.json`. On failure fix once and rerun; if it still fails, leave
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
