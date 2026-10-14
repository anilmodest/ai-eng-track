# Week 1 — What the gate checks

`make check WEEK=1` runs, in order, with no API key and no network:

| Gate | Passes when |
| --- | --- |
| Lint, format, types | `ruff check`, `ruff format --check` and strict `mypy` are clean |
| Tests, provider A | Every week 0 and week 1 test passes with `MODEL_PROVIDER=fake_a` |
| Tests, provider B | The same tests pass, unchanged, with `MODEL_PROVIDER=fake_b` |
| Records | `decisions/week-1.md` is complete, names a rejected option, and every number in it is in `evidence/week-1.json`; `ai-use/week-1.yml` gives the hours and says what you checked |

The week 1 tests (`tests/weeks/test_week1.py`) check behaviour that must hold, one sentence each.

**The extract endpoint**

| Test | What must hold |
| --- | --- |
| `extract_returns_schema_valid_json` | A good answer comes back as a valid `DocumentExtract`, not cached |
| `malformed_output_is_repaired_once` | Output that is not JSON gets exactly one repair attempt |
| `invalid_twice_is_a_typed_error_not_a_500` | Still invalid after the repair: a typed 502, never a 500 |
| `429_is_retried_then_succeeds` | Rate limits are retried until one succeeds |
| `400_is_not_retried` | A bad request is never retried |
| `hang_hits_the_timeout` | A provider that never answers becomes a 504 |
| `same_document_is_never_paid_for_twice` | The second identical request makes no provider call |
| `cost_and_latency_are_recorded` | Tokens, latency, cost and model are recorded |
| `input_is_capped_to_the_context_budget` | No more than `MAX_INPUT_CHARS` of the document is sent |

**The two tools**

| Test | What must hold |
| --- | --- |
| `tool_descriptions_tell_a_model_when_to_call_them_and_what_comes_back` | Each tool and its one argument are described in full sentences; nothing says TODO |
| `get_customer_gives_version_account_and_plan_and_nothing_personal` | Version, account and plan come back; seats and contact details do not |
| `get_customer_refuses_another_desks_customer_in_words_a_model_can_read` | Another desk's customer, or an unknown one, is `refused: ...`, revealing nothing |
| `malformed_arguments_never_reach_the_tool` | Malformed ids, missing or extra arguments, and wrong types fail validation, and the tool never runs |
| `get_ticket_gives_what_an_agent_needs_for_this_desks_tickets_only` | A desk ticket's status, priority, category, version and subject come back; another desk's ticket is refused |

**The measurements**

| Test | What must hold |
| --- | --- |
| `tool_drill_runs_and_your_descriptions_beat_the_first_draft` | The drill runs, and on the fake model (which chooses by the words in descriptions and argument patterns) yours beat the first draft |
| `schema_and_failure_drills_run_and_report` | Both drills run end to end and write their reports |

Your real-model numbers are not in the gate: they are in `evidence/week-1.json`, from
`make evidence WEEK=1`, and your decision record has to match them.
