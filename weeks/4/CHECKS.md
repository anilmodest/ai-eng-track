# Week 4 — What the gate checks

`make check WEEK=4` runs lint, format, strict types, Weeks 0–4 tests under both fakes with the
hash embedder, and the Week 3 evaluation gate.

| Test | Expects |
| --- | --- |
| `tool_schemas_are_json_schema_the_model_can_read` | five tools; `k` bounded at 10; money-costing tools marked |
| `tool_arguments_are_validated` | empty query and `k=50` are rejected before any tool runs |
| `plain_code_answers_its_questions_exactly_and_free` | 9,157.00 GBP, zero cost, zero calls |
| `plain_code_admits_what_it_cannot_do` | `status: unsupported` on a question it has no rule for |
| `workflow_stops_at_the_money_checkpoint` | `needs_approval`, no extraction, **zero** model calls |
| `workflow_runs_end_to_end_when_approved` | three extractions (one per invoice) then one answer call |
| `agent_calls_a_tool_then_finishes` | steps `search_documents`, `finish`; tokens and cost recorded |
| `agent_recovers_from_a_bad_tool_call` | unknown tool and invalid args come back as readable errors |
| `agent_hits_the_step_wall` | `AGENT_MAX_STEPS=1` ends with `max_steps` after one step |
| `scopes_are_least_agency` | reader denied `extract_document`; unknown token denied |
| `rate_limiter_is_a_sliding_window` | 3 per 10 s; a fourth is refused; the window slides; tokens are independent |
| `mcp_server_denies_out_of_scope_calls` | in-process MCP: tools listed, search allowed, extract denied with the reason |

`scripts/compare_week4.py` is evidence for the session, not a gate: its numbers depend on the
provider and on your agent.
