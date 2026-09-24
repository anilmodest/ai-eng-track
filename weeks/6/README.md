# Week 6 — Shipping and proving it

Area 11 of the track. About 8 hours. Branch: `week-6`.

**Goal:** a tagged deployment with a smoke test, one deliberate break and a proven rollback, a
one-page business write-up, and the final defence.

Read `CONCEPT.md` first. Then:

## Elaboration — see it (1 hour)

```
make run                                       # then, in another terminal:
uv run python scripts/smoke.py http://127.0.0.1:8000
curl -s http://127.0.0.1:8000/health | python -m json.tool
```

Read what `/health` says. Every field is something a person on call would need. Then read
`.github/workflows/deploy.yml`: find where the commit is stamped into `app/build_info.py`, where
the candidate image is smoke-tested, and why that happens *before* the publish step rather than
after.

## Exercise — ship, break, roll back, write (5 hours)

The release workflow needs nothing set up: it builds the image, smoke-tests it, and publishes it
to `ghcr.io/<you>/ai-eng-track`. A clickable URL is optional (README, "A clickable URL").

1. **Tag and release.** `git tag v1.0.0 && git push --tags`, then watch the **release** workflow.
   Read its summary: it prints the exact `docker run` line for what it published. Then make the
   package public (once), pull it, and prove it is the build you meant:

   ```
   docker run -d --rm -p 7860:7860 ghcr.io/<you>/ai-eng-track:v1.0.0
   uv run python scripts/smoke.py http://127.0.0.1:7860 --expect-sha <the short sha>
   ```

   Paste the output into `reflections/week-6.md`.
2. **Break it on purpose.** On a branch `week-6`, change one thing a smoke test catches and unit
   tests do not: set `RELEVANCE_THRESHOLD=1.5` in the image's environment, or change `ask_v1.md`
   so it always answers. Merge. Watch the release workflow **fail before it publishes** — that is
   the point of smoke-testing the candidate image rather than the deployment.
3. **Roll back.** Actions → *release* → *Run workflow* → `ref: v1.0.0`. Run the smoke test against
   the rolled-back image with `--expect-sha` of that tag. Paste both outputs. Note the minutes.
4. **Fix forward.** Revert the break properly, tag `v1.0.1`, release, smoke test.
5. **Score what people actually ask.** After a day of real use (yours, a peer's, your mentor's),
   run `uv run python scripts/sample_live.py --judge`. It reads the last twenty `/ask` requests,
   re-runs retrieval and scores each answer with the judge. Put the lowest five in your reflection
   with one line each on why. This is the last bullet of Area 8: sampling live traffic after
   release.
6. **Write it up.** Copy `weeks/6/WRITEUP_TEMPLATE.md` to `reflections/writeup.md` and fill it.
   Every number in it comes from `reports/`: `eval.json`, `traces.json`, `attacks.json`,
   `compare.json`. No adjectives where a number will do.

Your route changes what this week gives you: read `routes/start.md`, `routes/core.md` or
`routes/pro.md` in this folder (the hub shows yours).

`make check WEEK=6` runs everything from all six weeks.

## Submit (30 minutes)

- `reflections/week-6.md`: Q1, the smoke test outputs (release, break, rollback, fix forward),
  the rollback timing, and the `docker run` line for your published image.
- `reflections/writeup.md`: the one page.
- PR `week-6 → main`. CI green. Public repo, live URL in the README, progress page all green.

## Session 4: Defence (60 minutes, end of this week)

The interview shape from the source document: a software round with retrieval, agent and
evaluation design layered on. The starting measure from session 1 is taken again, with different
items. Your mentor will:

- ask you to trace one `/ask` request end to end, aloud, from the HTTP call to the cited chunk;
- pick two decisions from your write-up and ask for the number behind each;
- change one thing in your `.env` live and ask what will break, before it does;
- ask what the feature did for the business, and stop you if you answer with a score.

Pass line: every week's gate green on `main`, a published image that passes the smoke test
(and a live URL if you set one up), a rollback you performed and can describe, and a write-up
whose numbers you can defend.

"Cannot defend at the final session": you complete the track. The gap is recorded honestly and
stated plainly. That is the framework's rule, and it is the right one.

## Optional: self-test

`QUIZ.md` in this folder has a few questions on this week's concept, each with an explanation. On the hub page they are interactive and scored, but the score lives only in your browser: it never reaches the repo, your mentor or your route. Use it to find what to re-read.
