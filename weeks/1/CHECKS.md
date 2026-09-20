# Week 1 — What the gate checks

`make check WEEK=1` runs, in order, with no API key and no network:

| Gate | Command | Passes when |
| --- | --- | --- |
| Lint | `ruff check .` | No lint errors |
| Format | `ruff format --check .` | Code is formatted |
| Types | `mypy` (strict) | No type errors |
| Tests, provider A | `pytest` with `MODEL_PROVIDER=fake_a` | All Week 0 and Week 1 tests pass |
| Tests, provider B | the same with `MODEL_PROVIDER=fake_b` | The same tests pass unchanged |

The Week 1 tests (`tests/weeks/test_week1.py`), each one a sentence from `CONCEPT.md`:

| Test | Fake script | Expects |
| --- | --- | --- |
| `extract_returns_schema_valid_json` | `ok` | 200, valid `DocumentExtract`, `cached: false` |
| `malformed_output_is_repaired_once` | `malformed, ok` | 200 after exactly 2 calls |
| `invalid_twice_is_a_typed_error_not_a_500` | `invalid, malformed` | 502 `schema_error`, 2 calls |
| `429_is_retried_then_succeeds` | `429, 429, ok` | 200 after exactly 3 calls |
| `400_is_not_retried` | `400, ok` | 502 `provider_error`, 1 call |
| `hang_hits_the_timeout` | `hang` | 504 `provider_timeout` |
| `same_document_is_never_paid_for_twice` | `ok` | second call `cached: true`, 1 provider call total |
| `cost_and_latency_are_recorded` | `ok` | tokens > 0, cost > 0, model recorded |
| `input_is_capped_to_the_context_budget` | `ok` | user message respects `MAX_INPUT_CHARS` |

Output: `reports/week-1.json` with every test's outcome and each gate's verdict. The progress
page and your mentor read this file; you do not edit it.

`make live-check` is **not** part of the gate. It needs a real key and real network, and it is for
you and your mentor to look at, not for CI to grade.
