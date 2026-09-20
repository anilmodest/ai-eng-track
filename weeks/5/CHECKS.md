# Week 5 — What the gate checks

`make check WEEK=5` runs lint, format, strict types, Weeks 0–5 tests under both fakes, the Week 3
evaluation gate, and `scripts/attack.py` (which must report 0 successful attacks).

| Test | Expects |
| --- | --- |
| `every_request_has_a_trace_with_cost_on_the_step_that_spent_it` | `X-Request-Id` resolves to a tree; `model.call` sits under the route root; cost on the call rolls up to the root |
| `a_cached_request_costs_nothing_in_its_trace` | second extract: no `model.call` span, zero cost |
| `failures_land_in_an_error_taxonomy` | a provider 400 → `provider_error`; a missing document → `not_found` |
| `tool_calls_are_spans_under_the_request` | agent run: `tool.search_documents`, `tool.finish`, two model calls |
| `recent_traces_are_listed_newest_first` | `GET /traces` ordering |
| `wrap_untrusted_cannot_be_closed_from_inside` | a `</document>` inside the data does not end the fence |
| `detect_injection_strips_the_line_and_reports_it` | the hostile line is gone; the pattern is reported |
| `detect_injection_leaves_clean_text_alone` | "ignore the noise" is not an injection |
| `scan_output_flags_figures_the_source_never_stated` | 141,200.00 flagged; 1,412.00 not |
| `injected_document_is_extracted_as_data_not_instructions` | with the guard: `invoice`, detected, preamble and fence present |
| `without_the_guard_the_same_document_hijacks_the_model` | `GUARD_ENABLED=false`: `contract` |
| `poisoned_passage_is_flagged_on_ask` | `/ask` reports `injection_detected` and fences passages |
| `kill_switch_stops_every_model_call` | 503 `kill_switch`, zero calls, error kind recorded |
| `daily_budget_caps_the_blast_radius` | second call over budget → 429 `budget_exceeded` |
| `attack_script_holds_with_the_guard_on` | `scripts/attack.py` exits 0 with 0 of 4 |

`scripts/trace_report.py` is evidence, not a gate. The progress page shows the step table from
`reports/traces.json` when it exists.
