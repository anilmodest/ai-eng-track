# Week 6 — Shipping and proving it

Area 11 of the track. About 8 hours including the session. Branch: `week-6`.

## What you are building

Three things, and only one of them is code:

1. **A published build someone else can run.** A tagged image in this repository's container
   registry, pullable with no account, that passes the smoke test on a machine that never built it.
2. **A rollback you performed.** Break the service on purpose, watch the release fail, deploy an
   earlier tag, and prove with the smoke test that it took. Write down how many minutes it took.
3. **One page on what it did for the business.** `reflections/writeup.md`, every number traced to
   a file in `reports/`.

```
docker run -p 7860:7860 ghcr.io/<you>/ai-eng-track:v1.0.0
uv run python scripts/smoke.py http://127.0.0.1:7860 --expect-sha <the short sha>
  -> smoke test passed
```

Why the support desk cares: for five weeks the service has only ever run on your machine. A desk
cannot be helped by something only its author can start, and nobody signs off on a feature whose
value is reported as a score.

## The constraint everything is built under

**A demo nobody else can run is not shipped.** That is the whole week. The published image is the
deliverable, and the smoke test — the four cheapest checks that prove the thing is up, is the
version you meant, answers, and declines — is how you know a stranger will get the same result
you did.

Two hard parts. The first is that this system is not deterministic: the same commit with a
different model is a different system, so the version has to include the prompt and the provider,
and `/health` has to say all three. The second is that a rollback you have only read about is not
a rollback. You do it once here, calmly, so that the one at three in the morning is the second
time.

This is also the week's interview answer, and it is the question the interview actually asks:
*what did the last AI feature you shipped do for the business?* A score is not an answer to that.
A rollback you have performed beats one you can describe, and a number with a source behind it
beats an adjective.

## Run it and watch (1 hour, change nothing)

```
make run                                       # then, in another terminal:
uv run python scripts/smoke.py http://127.0.0.1:8000
curl -s http://127.0.0.1:8000/health | python -m json.tool
```

Read what `/health` says. Every field is something a person on call would need: which build,
which prompts, which provider, whether the guard is on and whether the kill switch is pulled.

Then watch the smoke test print one line per check and stop at the first failure. Run it again
with `--expect-sha deadbeef` and watch it refuse: that is the check that catches a deploy which
quietly did nothing.

Both need a provider key: see the main `README.md`, *Model access*. Default is Gemini's free tier.

## Read it (30 minutes, change nothing)

Start with `CONCEPT.md` if you have not: 15 minutes of this half-hour, and Q1 is its sentence in
your own words. Then read in this order, and answer the three questions in
`reflections/week-6.md`, Q1b:

1. **`app/build_info.py` and the `/health` route** — the file says which commit this build is.
   Who writes it, and why does the environment win over the file's contents?
2. **`scripts/smoke.py`** — four checks, in order, stopping at the first failure. Which one is the
   cheapest possible proof that abstention is still on? And why is a `501 not_implemented` a pass?
3. **`.github/workflows/deploy.yml`** (the **release** workflow) — find where the commit is
   stamped into `app/build_info.py`, where the candidate image is smoke-tested, and why that
   happens *before* the publish step rather than after.

Then open `tests/weeks/test_week6.py`. **It is the specification** for the parts of this week that
are code. The release, the break, the rollback and the write-up are not gated by tests — they are
the week, and they are what the Defence is about (`CHECKS.md`).

Six terms worth being precise about, because the rest of the week uses them as if they were
obvious:

- **Registry** — where built images live so other people can pull them. Here it is
  `ghcr.io/<you>/ai-eng-track`, this repository's own registry. A package published by Actions
  from a public repository is public: no account, no login, nothing to configure.
- **Image tag** — a name for one build in that registry, like `:v1.0.0` or `:latest`. The
  workflow pushes the short commit sha and the version, so a tag always has a commit behind it.
- **Build stamping** — the release workflow writes the version and commit into
  `app/build_info.py` *before* building, so the running service cannot disagree with the tag it
  was published under.
- **Smoke test** — not the evaluation. Four cheap checks, under a minute, run after every deploy
  and after every rollback, that prove the service is up, is the build you meant, answers, and
  declines.
- **Rollback by ref** — redeploying an earlier tag or commit by hand: Actions, the release
  workflow, *Run workflow*, `ref: v1.0.0`. The image it publishes carries that commit's
  `build_info.py`, so `/health` tells you the rollback took.
- **Fix forward** — the opposite move: leave the rollback in place, revert the break properly on a
  branch, and ship a new version. Rolling back buys time; fixing forward is what ends the incident.

## Do it (5 hours)

The release workflow needs nothing set up: it builds the image, smoke-tests it, and publishes it
to `ghcr.io/<you>/ai-eng-track`. Hugging Face Spaces used to be the target here and is not any
more — as of September 2026 Docker Spaces need a paid subscription — so the registry is the
deliverable. A clickable URL via Render is optional (main `README.md`, *A clickable URL*).

The order is not a preference: you cannot demonstrate a rollback until there is something to roll
back to, so the tag comes first and the break comes second.

1. **Confirm the service says what it is.** `/health` must report version, commit, prompt
   versions, provider, guard state and kill switch, and the environment the deploy writes must
   win over the file.
   *Done when* `health_says_what_is_running` and `health_reflects_the_build_the_deploy_wrote`
   pass.
2. **Decide whether you trust the smoke test.** On the core and pro routes it is not simply
   given: run it against a healthy service and a broken one before you rely on it
   (`routes/core.md`). It must pass when the service is fine, fail on the wrong commit, treat a
   `kill_switch` refusal as intended with no model call, skip exercises that answer 501, still
   fail on a genuinely wrong answer, and run on its own from the command line.
   *Done when* `smoke_test_passes_against_the_service`, `smoke_test_fails_on_the_wrong_commit`,
   `smoke_test_treats_the_kill_switch_as_intended`,
   `smoke_test_skips_exercises_that_are_not_built_yet`,
   `a_wrong_answer_still_fails_even_when_other_weeks_are_unbuilt` and
   `smoke_script_is_runnable_standalone` pass.
3. **Tag and release.** `git tag v1.0.0 && git push --tags`, then watch the **release** workflow.
   Read its summary: it prints the exact `docker run` line for what it published. Then pull it on
   a machine that never built it, and prove it is the build you meant:

   ```
   docker run -d --rm -p 7860:7860 ghcr.io/<you>/ai-eng-track:v1.0.0
   uv run python scripts/smoke.py http://127.0.0.1:7860 --expect-sha <the short sha>
   ```

   *Done when* the smoke test exits 0 against the pulled image with `--expect-sha` of that tag,
   and `deploy_workflow_supports_rollback_by_ref` passes. Paste the output into
   `reflections/week-6.md`.
4. **Break it on purpose.** On a branch `week-6`, change one thing a smoke test catches and unit
   tests do not: set `RELEVANCE_THRESHOLD=1.5` in the image's environment, or change `ask_v1.md`
   so it always answers. Merge.
   *Done when* the release workflow **fails before it publishes** — that is the point of
   smoke-testing the candidate image rather than the deployment, and it means no broken build
   ever became a tag someone could pull.
5. **Roll back.** Actions → *release* → *Run workflow* → `ref: v1.0.0`. Run the smoke test against
   the rolled-back image with `--expect-sha` of that tag.
   *Done when* `/health` reports the earlier commit and the smoke test exits 0. Paste both
   outputs — the failing one and this one — and note the minutes it took.
6. **Fix forward.** Revert the break properly, tag `v1.0.1`, release, smoke test.
   *Done when* the release workflow publishes `v1.0.1` and the smoke test passes against it with
   `--expect-sha` of that commit.
7. **Score what people actually ask.** After a day of real use (yours, a peer's, your mentor's),
   run `uv run python scripts/sample_live.py --judge`. It reads the last twenty `/ask` requests,
   re-runs retrieval and scores each answer with the judge. Put the lowest five in your reflection
   with one line each on why. This is the last bullet of Area 8: sampling live traffic after
   release.
   *Done when* `reports/live-sample.json` exists with a judge mean printed above it, and
   `live_traffic_can_be_sampled_and_scored` passes.
8. **Write it up.** Copy `weeks/6/WRITEUP_TEMPLATE.md` to `reflections/writeup.md` and fill it.
   Every number in it comes from `reports/`: `eval.json`, `traces.json`, `attacks.json`,
   `compare.json`. No adjectives where a number will do.
   *Done when* every row of the measurement table has a number and a source, and the "what went
   wrong on the way" section is filled in — it is the section your mentor will trust most.

Your route changes what this week gives you: read `routes/start.md`, `routes/core.md` or
`routes/pro.md` in this folder (the hub shows yours).

`make check WEEK=6` runs everything from all six weeks.

### If you get stuck

- **Rate-limited mid-exercise?** The free tiers are small, and step 7 runs the judge over twenty
  requests. Put a second provider's key in `.env` and change `MODEL_PROVIDER`, or run
  `sample_live.py` without `--judge` first: the listing alone finds most drift.
- **A test is failing and the message is not obvious?** Open the test. It is short, and it says
  exactly what it expected.
- **The release workflow failed before publishing?** In step 4 that is the exercise succeeding,
  not a problem: the smoke test caught a break the unit tests did not, which is the whole reason
  it runs against the candidate image. Read which check said FAIL, and say so in your reflection.
  Outside step 4, treat that same line as the finding and fix the service, not the workflow.
- **Stuck for more than an hour?** An unblock call is available after a real attempt. Use it.

## Submit (30 minutes)

- `reflections/week-6.md`: Q1 (the concept in your words), Q1b (the three reading questions),
  Q2 (what surprised you), Q3 (what you would change), Q4 (what you contributed and how you
  checked it), Q5 (help you used), the smoke test outputs (release, break, rollback, fix
  forward), the rollback timing, and the `docker run` line for your published image.
- `reflections/writeup.md`: the one page.
- PR `week-6 → main`. CI green. Public repo, live URL in the README, progress page all green.
- Send the link to your mentor **24 hours** before the session, not at the start of it.

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
