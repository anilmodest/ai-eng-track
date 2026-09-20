# Week 6 — Quiz

Optional, repeatable, and yours: the score is kept in your own browser on the hub page and
never reaches the repo, the mentor or the route. Use it to find out what you have not understood
yet; then go and read that part again. The explanations are the point, not the score.

## Q1. Which tag is live right now, and how do you know without a shell?
- [x] `GET /health` on the live URL reports `version`, `git_sha`, `built_at`, the prompt versions and the provider
- [ ] The last green CI run on `main` — CI passing is not the same as that commit being deployed
- [ ] The Space's settings page — it shows what was pushed, not what is running
> Why: the deploy workflow stamps `app/build_info.py` so the running service can say what it is. A rollback is visible as a change in `git_sha`.

## Q2. You want to break the service on purpose for the rollback exercise. Which change would a smoke test catch but unit tests would not?
- [ ] Renaming a test function — unit tests would catch that, or not run at all
- [x] `RELEVANCE_THRESHOLD=1.5` in the Space's variables: every question now abstains, and the smoke test's "ask declines nonsense" passes while a real question would fail
- [ ] Deleting the corpus — the corpus is not deployed; it is uploaded
> Why: the smoke test checks behaviour on the deployed system with its real configuration. Unit tests check code with test configuration. The exercise is to feel that difference.

## Q3. The rollback: what exactly does "Run workflow with ref = v1.0.0" do?
- [x] Checks out that tag, stamps its commit into `build_info.py`, pushes that tree to the Space, and runs the smoke test against it
- [ ] Reverts `main` to the tag — `main` does not move; only the deployment does
- [ ] Restarts the Space — restarting runs the same broken code again
> Why: rollback means "deploy an earlier known-good build", not "undo the commit". Your `main` keeps the history; the fix comes forward as a new tag.

## Q4. The smoke test's third check gets a 503 `kill_switch`. Pass or fail?
- [x] Pass, and it says so: a typed refusal from a switch someone set on purpose is intended behaviour
- [ ] Fail; extract did not work — it was refused, which is different from broken
- [ ] Pass silently — silently is wrong; the operator must see that the switch is on
> Why: a smoke test that fails on intended refusals gets ignored within a week. Make the intended case explicit and green.

## Q5. Which sentence belongs in the business write-up?
- [ ] "Hit rate 0.94, abstention 1.00" — those are the sources, not the sentence
- [x] "Classifying an incoming document went from a person's ten minutes to two seconds and a fifth of a cent, with the passage it came from attached"
- [ ] "We used RAG with a Gemini model" — a description of the system, not of what it did
> Why: interviewers ask what it did for the business. A sentence with a unit in it (minutes, cents, per document) is the answer; a score is the evidence behind it.

## Q6. At 10,000 documents a day, what breaks first in this service?
- [ ] The model's accuracy — accuracy does not change with volume; cost and limits do
- [x] Provider rate limits and the daily budget, then the single SQLite file, then the numpy scan as the corpus grows
- [ ] GitHub Pages — the page is static; it does not serve requests
> Why: the write-up asks for this on purpose. The order of what breaks is a design answer; "add a bigger model" is not.

## Q7. "Cannot defend at the final session." What does the framework say happens? (stretch: core/pro)
- [x] The fellow completes the track; the gap is recorded honestly and stated plainly; no hard fail
- [ ] The fellow repeats Week 6 — there is no repeat; there is an honest record
- [ ] The route changes retroactively — routes are set at discovery, never after the fact
> Why: a hard fail is unenforceable in a one-to-one relationship, and pretending otherwise makes the checkpoint decorative. Honesty about the gap is the standard.
