# Week 6 — Practice quiz

Practice, untimed and repeatable. Your score stays in this browser on your hub page and never
reaches the repository or your mentor. Use it to find what to re-read; the explanations are the
point, not the score. Your mentor also assigns a short weekly check on BridgePath: different
questions, some of them timed, taken once, and your mentor sees that score.

## Q1. Someone runs your published image on their own machine. How do they find out which build it is, without a shell inside the container?
- [ ] The last green CI run on `main` — a green run says a commit passed, not that this image is that commit
- [ ] The newest tag listed under the repository's packages in the container registry — the newest tag published is not necessarily the one this machine pulled
- [ ] The `APP_VERSION` line in the repository's `.env.example` — that file is an example for local runs; it says nothing about a built image
- [x] `GET /health`: version, commit, build time, prompt versions and provider
> Why: the release workflow stamps the commit into `app/build_info.py` before it builds, so the running service can say what it is. A rollback shows up as a change in `git_sha`.

## Q2. You roll back with Actions, *release*, *Run workflow*, `ref: v1.0.0`. What does that run do?
- [ ] Reverts `main` to the tag and pushes it — `main` does not move; only what is published does
- [ ] Restarts the containers that are already running — a restart runs the same image again
- [x] Builds the tag's code with its commit stamped in, smoke-tests it with `--expect-sha`, then publishes it under that commit and tag
- [ ] Re-points the `latest` tag at the old image without building anything — a manual run with a ref never moves `latest`
> Why: a rollback deploys an earlier known-good build; it does not undo history. The fix comes forward as a new tag, `v1.0.1`.

## Q3. In the break-it-on-purpose step, the release workflow fails before it publishes. What does that tell you?
- [x] The exercise worked: the smoke test stopped a break before it became a tag
- [ ] The workflow is misconfigured, and the publish step should be allowed to run anyway — a smoke test that can be skipped gates nothing
- [ ] The registry rejected the image, so the package needs to be made public first — the publish step never ran; the smoke test stopped it
> Why: the smoke test runs against the built candidate image before anything is pushed. A broken build never becomes something a stranger can pull.

## Q4. During the smoke test, the version 3 question on `/ask` gets a 503 `kill_switch`. Pass or fail?
- [x] Pass, and the line says the refusal is intended
- [ ] Fail, because the check did not get a cited answer — it was refused, which is different from broken
- [ ] Pass, without printing anything about it — the operator must see that the switch is on
> Why: a smoke test that fails on intended refusals gets ignored within a week. The intended case is explicit and green, and a wrong answer still fails.

## Q5. Which sentence belongs at the top of the business write-up?
- [ ] "Faithfulness 0.91, and a decline rate of 0.95 on the unanswerable questions, ours and the hidden set's" — those are the evidence behind the sentence, not the sentence
- [ ] "A LangGraph agent with seven tools, served over MCP, with hybrid search" — a description of the system, not of what it did
- [x] "62% of tickets resolved without a person, at $0.004 a ticket, and no action nobody approved"
- [ ] "The agent is accurate, safe and cheap" — adjectives where numbers will do; an interviewer will ask "how much?"
> Why: the brief names the business metric: tickets resolved without a person, at a cost per ticket, with no action nobody approved. Fill it with your own numbers, from your evidence and `reports/`.

## Q6. What goes into the five-minute recorded demo?
- [ ] A walk through the code, file by file, so the reviewer sees how it is built — a hiring manager asks what it did, not how it is laid out
- [x] The problem, one real ticket handled, a decline, the approval stop, and what it did for the business
- [ ] The full evaluation running live, so the scores are seen to be real — that takes longer than five minutes and shows numbers, not the system
> Why: the demo is for a hiring manager. It shows the system working, the two moments it holds back (declining and stopping for approval), and the business sentence with its numbers.

## Q7. In the assisted part of the defence, you make an unseen change with your own assistant. What is your mentor watching for?
- [x] How you steer it: how you split the task, the context you give, what you check before trusting a line, and when you stop asking
- [ ] How quickly the assistant produces code — speed without checking is the failure this round exists to catch
- [ ] Whether you can finish without the assistant at all — that is the tools-closed part, earlier in the hour
> Why: the same rubric as your recorded rehearsal. The tools-closed part tests what you know; the assisted part tests what you accept, and what you catch.

## Q8. On the pro route, the rollback must be zero-downtime. How do you prove no run failed while traffic moved? (stretch: core/pro)
- [ ] Watch `/health` until it shows the new commit — it shows the switch happened, not that nothing failed during it
- [x] Run the old and new images side by side on two ports and smoke-test every 30 seconds while traffic moves
- [ ] Count the error kinds in the trace report the next day — a failed request during a switch may never reach the new service's traces
> Why: a claim of zero downtime is a measurement taken during the switch. The pro route also writes an incident report for the break as if it had reached users.
