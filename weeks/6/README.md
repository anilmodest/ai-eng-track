# Week 6 — Shipping it, presenting it and proving it

Area 11. 8 to 9 hours. Session 4 (Defence) at the end of this week. Branch: `week-6`.

> **The one lesson.** Say what it did for the business, and defend it with or without an
> assistant.

## The gap it closes

The last one, and it is not technical. A fellow can build everything above and still fail the
interview by describing it in metrics. This week you learn to say what it did for the business,
aloud and on camera, not only on paper; to release and roll back a system whose output is not
deterministic; and to do an unseen change with your assistant while someone watches, because that
round now sits in many interviews beside the one without tools.

## What you are building

Five things, and only the first is code:

1. **A published, versioned build someone else can run**, a tag in this repository's container
   registry, and **a rollback you performed**.
2. **The trade-off table**, compiled from your six decision records (`scripts/tradeoffs.py`).
3. **One page on what it did for the business**, `reflections/writeup.md`.
4. **A five-minute recorded demo** for a hiring manager.
5. **An AI-assisted rehearsal**: an unseen change, done with your assistant, recorded, and
   reviewed by you against the rubric.

```
docker run -p 7860:7860 ghcr.io/<you>/<your-repo>:v1.0.0
uv run python scripts/smoke.py http://127.0.0.1:7860 --expect-sha <the short sha>
  -> smoke test passed
```

## The constraint everything is built under

**A demo nobody else can run is not shipped.** The published image is the deliverable, and the
smoke test (the cheapest checks that prove the thing is up, is the version you meant, answers and
declines) is how you know a stranger gets what you got. This system is not deterministic: the same
commit with a different model or prompt is a different system, so `/health` says the commit, the
prompt versions and the provider. And a rollback you have only read about is not a rollback.

## Read (30 minutes)

`CONCEPT.md`. Then `scripts/smoke.py`, `.github/workflows/release.yml` and
`.github/workflows/clean-clone.yml`, answering in `reflections/week-6.md`, Q1b: what does each
check in the smoke test catch that the unit tests cannot?

## Build (5 to 6 hours)

Core items are needed for the lesson and checked by the gate; stretch items are shown to your
mentor and never block. Log your assistant use in `ai-use/week-6.yml`.

### Core 1: release, break, roll back, fix forward

In this order, because you cannot roll back until there is something to roll back to.

1. **The service says what it is.** `/health` reports version, commit, prompt versions, provider,
   guard state and kill switch; the environment the release workflow writes wins over the file.
2. **You trust the smoke test.** Run it against a healthy service and a broken one before you rely
   on it; your page in `routes/` says how much of it your route gives you. It passes when the
   service is fine, fails on the wrong commit, treats a kill-switch refusal as intended, skips
   exercises that are not built, still fails on a wrong answer, and runs on its own.
3. **Tag and release.** `git tag v1.0.0 && git push --tags`, then watch the **release** workflow.
   Pull the image on a machine that never built it and run the smoke test with `--expect-sha`.
4. **Break it on purpose.** On `week-6`, change one thing the smoke test catches and the unit
   tests do not (`RELEVANCE_THRESHOLD=1.5` in the image's environment, say: no passage clears it,
   so the service declines everything and the smoke test's third check, the version 3 question
   on `/ask`, fails). The release workflow must **fail before it publishes**.
5. **Roll back.** Actions, *release*, *Run workflow*, `ref: v1.0.0`; smoke-test the rolled-back
   image with `--expect-sha` of that tag. Note how many minutes it took.
6. **Fix forward.** Revert the break properly, tag `v1.0.1`, release, smoke test.

A public URL is optional (main `README.md`, *A clickable URL*).

### Core 2: the trade-off table (`scripts/tradeoffs.py`)

It compiles your six decision records into one table: what you chose, the numbers, what you
rejected and the risk you accepted. A week whose numbers do not match its evidence is marked. The
table is the spine of your write-up and of the defence.

### Core 3: the write-up (`reflections/writeup.md`)

Copy `weeks/6/WRITEUP_TEMPLATE.md`. Every number comes from your evidence files and `reports/`;
no adjectives where a number will do. Link the release and the demo recording.

### Core 4: a stranger can run it

`.github/workflows/clean-clone.yml` runs on your `week-6` pull request: a fresh machine, the
README's steps and nothing else, then the smoke test. If it fails, the README is wrong, not the
machine.

### Core 5: the recorded demo, and the AI-assisted rehearsal

**Demo**: five minutes, recorded, for a hiring manager: the problem, the system working on one
real ticket, the decline, the approval stop, and what it did for the business. Link it in the
write-up.

**Rehearsal**: ask your mentor for an unseen change request. Set a 30-minute timer, record your
screen, and make the change with your assistant. Then copy `weeks/6/REHEARSAL_TEMPLATE.md` to
`decisions/week-6-rehearsal.md` and review yourself against the rubric, honestly, before session 4.

### Core 6: measure it (`make evidence WEEK=6`)

| Measurement | Script | What it tells you |
| --- | --- | --- |
| `eval` | `scripts/eval.py --set eval/my-test-set.jsonl` | The full evaluation on your own set, at the score you will defend |
| `tradeoffs` | `scripts/tradeoffs.py` | The table, as the gate checked it |

The hidden evaluation runs on what you merge; the full evaluation must pass on both sets.

### Stretch

- **Score live traffic.** After a day of real use, `uv run python scripts/sample_live.py --judge`
  scores the last twenty `/ask` requests with your judge. Put the lowest five in your reflection.

## Decide

Nothing new to decide this week: **say what you decided**, from the trade-off table, in the
write-up, in the demo and at the defence. `decisions/week-6.md` records the one decision of the
week: the release you will defend, by tag, and the evidence it passed.

## What proves it

1. **The gate**: the service's health, the smoke test, the rollback workflow, the trade-off table
   compiled with every week's numbers matching, the rehearsal, the write-up and the clean-clone job.
2. **The released image** returns a correct, cited answer to a supplied question.
3. **The full evaluation** passes at the recorded score, on your set and on the hidden one.
4. **The demo** is submitted.

**Anti-goal: do not add features in week 6.**

### If you get stuck

- **The release workflow failed before publishing?** In step 4 that is the exercise succeeding:
  the smoke test caught a break the unit tests did not. Anywhere else, fix the service, not the
  workflow.
<!-- route:start -->
- **On `start`?** `routes/worked_example.py` is a two-check smoke test for a smaller service.
<!-- /route -->
- **Stuck for more than an hour?** An unblock call is available after a real attempt. Use it.

Your route changes what this week gives you: the page in `routes/` in this folder says how.

## Submit

1. `make check WEEK=6` green, commit, `make evidence WEEK=6`, commit the evidence.
2. `decisions/week-6.md`, `decisions/week-6-rehearsal.md`, `reflections/writeup.md`,
   `ai-use/week-6.yml`, `reflections/week-6.md`.
3. Open a pull request `week-6 → main` and send the link **24 hours** before the session.

## Session 4: Defence (60 minutes, end of this week)

Everything that can be checked without you is checked before the call (the sign-off checklist on
your mentor's brief). The hour is yours:

| Min | What happens |
| --- | --- |
| 0–8 | Demo of the released system, as you would show a hiring manager |
| 8–28 | Tools closed. Your mentor picks three of your decision records and one file you changed: why this, what else, what would break |
| 28–43 | Assisted. An unseen change request, done live with your own assistant |
| 43–55 | The measure from session 1, with different items, timed at ten minutes |
| 55–60 | What you would do next; your mentor closes |

"Cannot defend at the final session": you complete the track. The gap is recorded honestly and
stated plainly. That is the framework's rule, and it is the right one.

## Quizzes: practice here, a short check on BridgePath

`QUIZ.md` in this folder is the practice quiz, with an explanation for every answer. On the hub page
it is interactive, untimed and repeatable, and the score stays in your browser: it never reaches the
repository, your mentor or your route. Use it to find what to re-read.

Your mentor also assigns this week's check on BridgePath. It has different questions, some of them
timed, and you take it once; your mentor sees that score. It asks about what you built and measured
this week, so the work is the preparation.
