# Week 6 — What the gate checks

`make check WEEK=6` runs everything: lint, format, strict types, weeks 0 to 6 tests under both
fakes, the evaluation gate, the attack gate and the records gate.

| Test | Expects |
| --- | --- |
| `health_says_what_is_running` | version, commit, prompt versions, provider, guard state |
| `health_reflects_the_build_the_deploy_wrote` | `GIT_SHA` and `APP_VERSION` from the environment win |
| `smoke_test_passes_against_the_service` | `scripts/smoke.py` exits 0 in-process |
| `smoke_test_fails_on_the_wrong_commit` | `--expect-sha deadbeef` exits 1 |
| `smoke_test_treats_the_kill_switch_as_intended` | a 503 `kill_switch` on ask is a pass, with no model call |
| `smoke_test_fails_when_everything_declines` | `RELEVANCE_THRESHOLD=1.5` passes the unit tests; the smoke test's `/ask` check exits 1 |
| `release_workflow_supports_rollback_by_ref` | `workflow_dispatch` with a `ref`, the commit stamped into `build_info.py`, and the smoke test gating the publish |
| `smoke_script_is_runnable_standalone` | `--help` works |
| `smoke_test_skips_exercises_that_are_not_built_yet` | a typed 501 counts as skipped, so a week 1 fellow can still release |
| `a_wrong_answer_still_fails_even_when_other_weeks_are_unbuilt` | skipping the unbuilt is not the same as passing the wrong |
| `live_traffic_can_be_sampled_and_scored` | `scripts/sample_live.py` reads the last requests and scores them |
| `the_tradeoff_table_compiles_every_decision_record` | A row for each of weeks 1 to 5 at least, each with a decision, a rejected option, and numbers that match its evidence |
| `the_ai_assisted_rehearsal_is_written_up` | `decisions/week-6-rehearsal.md`: the request, what the assistant did, what you checked, the rubric, the recording |
| `the_business_write_up_is_numbers_not_adjectives` | `reflections/writeup.md`: a page, a measurement table with numbers, links |
| `a_stranger_can_run_it_from_the_instructions_alone` | The clean-clone workflow follows the README's steps |

The release, the break, the rollback and the demo are not gates. They are the week, and they
are what the Defence is about. The release workflow smoke-tests the candidate image before
publishing, so a broken build never becomes a tag someone can pull.
