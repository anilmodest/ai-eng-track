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
`.github/workflows/deploy.yml`: find where the commit is stamped into `app/build_info.py`, and
where the smoke test runs.

## Exercise — ship, break, roll back, write (5 hours)

If you did not set up the Hugging Face Space in Week 0, do it now (README, "Deploy"). Set the
repository variable `LIVE_URL` so the deploy workflow runs the smoke test for you.

1. **Tag and deploy.** `git tag v1.0.0 && git push --tags`, merge to `main`, watch the deploy
   workflow. Then, from your machine:
   `uv run python scripts/smoke.py $LIVE_URL --expect-sha <the short sha of main>`.
   Paste the output into `reflections/week-6.md`.
2. **Break it on purpose.** On a branch `week-6`, change one thing that a smoke test should catch
   but unit tests would not: set `RELEVANCE_THRESHOLD=1.5` in the Space's variables, or change
   the `ask_v1.md` prompt to always answer. Merge. Run the smoke test. It must fail, and say why.
3. **Roll back.** Actions → *deploy to hugging face space* → *Run workflow* → `ref: v1.0.0`.
   Run the smoke test again with `--expect-sha` of the tag. Paste both outputs. Note the minutes.
4. **Fix forward.** Revert the break properly, tag `v1.0.1`, deploy, smoke test.
5. **Write it up.** Copy `weeks/6/WRITEUP_TEMPLATE.md` to `reflections/writeup.md` and fill it.
   Every number in it comes from `reports/`: `eval.json`, `traces.json`, `attacks.json`,
   `compare.json`. No adjectives where a number will do.

What your route adds:

| Route | Exercise |
| --- | --- |
| `start` | the above |
| `core` | plus a `scripts/sample_live.py` that pulls the last 20 `/ask` traces and scores them with the judge: continuous evaluation, once |
| `pro` | plus a written incident report for the break in step 2 as if it had reached users: timeline, blast radius from the trace report, what would have caught it earlier |

`make check WEEK=6` runs everything from all six weeks.

## Submit (30 minutes)

- `reflections/week-6.md`: Q1, the four smoke test outputs, the rollback timing.
- `reflections/writeup.md`: the one page.
- PR `week-6 → main`. CI green. Public repo, live URL in the README, progress page all green.

## The final session (60 minutes with your mentor)

The interview shape from the source document: a software round with retrieval, agent and
evaluation design layered on. Your mentor will:

- ask you to trace one `/ask` request end to end, aloud, from the HTTP call to the cited chunk;
- pick two decisions from your write-up and ask for the number behind each;
- change one thing in your `.env` live and ask what will break, before it does;
- ask what the feature did for the business, and stop you if you answer with a score.

Pass line: every week's gate green on `main`, a live URL that passes the smoke test, a rollback
you performed and can describe, and a write-up whose numbers you can defend.

"Cannot defend at the final session": you complete the track. The gap is recorded honestly and
stated plainly. That is the framework's rule, and it is the right one.

## Optional: self-test

`QUIZ.md` in this folder has a few questions on this week's concept, each with an explanation. On the hub page they are interactive and scored, but the score lives only in your browser: it never reaches the repo, your mentor or your route. Use it to find what to re-read.
