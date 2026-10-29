# השמרן (HaShamran) automation

Hebrew translations of essays recommended by National Conservatism, published at
[hashamran.substack.com](https://hashamran.substack.com) and shared on X as [@HaShamran1948](https://x.com/HaShamran1948).
This repo is also the GitHub Pages site for the relay links (`hashamran.github.io/hashamran-links/<slug>.html`).

| Runner | When (Israel) | Does | Code |
| --- | --- | --- | --- |
| Claude cloud scheduled task | daily 05:30 | detect (Firecrawl), extract, translate, choose tweet quotes, mark ready | `RUNBOOK.md`, `pipeline/` |
| Python on dud (Task Scheduler) | every 30 min, 06–22 | publish due posts to Substack, web only, 1–2 a day | `dud/publisher.py` |
| GitHub Actions | every 15 min | relay pages, tweets via Buffer at ~11/16/21, alerts as issues | `.github/workflows/social.yml`, `pipeline/social.py` |

Claude never clicks Publish or Post: public steps are plain scripts and official APIs.

State: `state/seen.json` (every essay ever listed), `state/queue.json` (to translate), `posts/<slug>/post.json`
(translated), `posts/index.json` (what dud reads), `state/live.json` (live on Substack), `state/tweets.json` (sent).

Setup on dud: copy `dud/` and `pipeline/substack_doc.py` into a folder, double-click `setup.cmd`, sign in to
Substack in the Chrome window it opens. Status: `publisher-status.txt` in that folder. When it says
ACTION NEEDED, double-click `login.cmd`.

Secrets: `BUFFER_API_KEY` as a GitHub Actions secret. Nothing secret lives in this public repo.

Tests: `python -m pytest tests`
