# Week 5 — What the gate checks

`make check WEEK=5` runs lint, format and strict types, the week 0 to 5 tests under both fake
providers, the evaluation gate, the attack gate (`scripts/attack.py`: no attack may succeed with the
guard on), and the records gate. The fake model obeys an instruction inside unfenced text, which
makes "did the defence work" a deterministic question.

**Tracing**

| Test | What must hold |
| --- | --- |
| `every_request_has_a_trace_with_cost_on_the_step_that_spent_it` | A request tree, cost on the model call, rolled up to the root |
| `a_cached_request_costs_nothing_in_its_trace` | No model call, no cost |
| `failures_land_in_an_error_taxonomy` | Every failure on a kind |
| `tool_calls_are_spans_under_the_request` | An agent run shows its tool calls |
| `recent_traces_are_listed_newest_first` | The listing |
| `model_and_tool_spans_carry_opentelemetry_attributes` | `gen_ai.*` names on model and tool spans |
| `an_action_that_needs_approval_leaves_an_approval_span` | The stop is in the trace |
| `a_trace_exports_in_otlp_shape` | `GET /traces/{id}/otel` |

**The guard**

| Test | What must hold |
| --- | --- |
| `wrap_untrusted_cannot_be_closed_from_inside` | Data cannot close its own fence |
| `detect_injection_strips_the_line_and_reports_it` / `..._leaves_clean_text_alone` | Known patterns stripped and reported; ordinary text untouched |
| `scan_output_flags_figures_the_source_never_stated` | A figure not in the source is flagged |
| `injected_document_is_extracted_as_data_not_instructions` / `without_the_guard_...` | The defence, and the attack without it |
| `poisoned_passage_is_flagged_on_ask` | Retrieved text is checked too |
| `kill_switch_stops_every_model_call` / `daily_budget_caps_the_blast_radius` | The limits |
| `with_the_guard_on_ticket_text_reaches_the_model_fenced` | A ticket reaches the model as data |
| `attack_script_holds_with_the_guard_on` | No attack in the set succeeds |

**Least agency**

| Test | What must hold |
| --- | --- |
| `routing_never_offers_an_action_the_request_did_not_ask_for` | Lookups, analysis and "handle this ticket" are offered no action that writes or spends |
| `routing_offers_exactly_the_action_the_request_asks_for` | An escalation request gets escalate, a credit request gets issue_credit, not both |
| `a_tool_not_offered_is_refused_whatever_the_model_asks` | The offer is enforced at the door |
| `ticket_content_cannot_make_the_agent_reach_for_an_action` | With the guard off, least agency alone stops T-2099 |

**Personal data**

| Test | What must hold |
| --- | --- |
| `mask_replaces_emails_phones_and_the_names_it_is_given` | Replaced, and unmask restores the text |
| `mask_finds_people_inside_a_json_tool_result` | Escaped newlines and escaped accents do not hide anyone |
| `mask_keeps_what_the_model_needs` | Ids, amounts, dates, codes and settings untouched |
| `the_same_person_gets_the_same_placeholder_in_one_run` | Consistent placeholders; existing ones left alone |
| `no_personal_data_reaches_the_model` | Nothing personal in any recorded model input |
| `a_draft_a_person_reads_gets_the_real_values_back` | The one approved output is restored |
| `the_blast_radius_of_each_action_tool_is_written_down` | A statement per action tool |
