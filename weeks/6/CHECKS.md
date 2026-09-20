# Week 6 — What the gate checks

`make check WEEK=6` runs everything: lint, format, strict types, Weeks 0–6 tests under both
fakes, the evaluation gate and the attack gate.

| Test | Expects |
| --- | --- |
| `health_says_what_is_running` | version, commit, prompt versions, provider, guard state |
| `health_reflects_the_build_the_deploy_wrote` | `GIT_SHA` and `APP_VERSION` from the environment win |
| `smoke_test_passes_against_the_service` | `scripts/smoke.py` exits 0 in-process |
| `smoke_test_fails_on_the_wrong_commit` | `--expect-sha deadbeef` exits 1 |
| `smoke_test_treats_the_kill_switch_as_intended` | a 503 `kill_switch` on extract is a pass, with no model call |
| `deploy_workflow_supports_rollback_by_ref` | `workflow_dispatch` with a `ref`, build info stamped, smoke test at the end |
| `smoke_script_is_runnable_standalone` | `--help` works |

The deploy, the break, the rollback and the write-up are not gates. They are the week, and they
are what the final session is about.
