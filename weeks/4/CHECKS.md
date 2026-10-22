# Week 4 — What the gate checks

`make check WEEK=4` runs lint, format and strict types, the week 0 to 4 tests under both fake
providers, the evaluation gate, and the records gate. The fake model acts as a small
rule-following agent; a scripted model stands in where a test needs one to misbehave.

**Tools that act, and the analysis tool**

| Test | What must hold |
| --- | --- |
| `action_tools_are_described_and_say_truthfully_what_they_do` | Described in full; `draft_reply` is not flagged (a person reads the draft before anything is sent), `escalate` writes, `issue_credit` spends |
| `malformed_action_calls_never_reach_the_tool` | A team that does not exist, an empty reason or body, a bad amount, a bad id: refused before running |
| `escalate_and_issue_credit_stop_for_approval_and_nothing_happens` | Without approval: a stop, and nothing written |
| `approved_actions_are_carried_out_and_recorded` | With approval: done, and recorded |
| `draft_reply_changes_nothing_a_customer_sees` | A draft is saved; the ticket is unchanged |
| `credits_are_capped_per_ticket_and_by_what_is_owed` | All credits on a ticket within the cap, and never more than is owed |
| `actions_on_another_desks_ticket_are_refused` | Another desk's ticket is refused |
| `query_tickets_is_described` | Described; read-only |
| `query_tickets_is_an_allowlist` | A query, a group or a filter that is not on the list never runs |
| `query_tickets_numbers_are_the_data` | Counts, groups, sums, median and filters equal the desk's data |

**The loop**

| Test | What must hold |
| --- | --- |
| `the_agent_is_shown_every_tool_and_finish` | The prompt lists every tool and `finish` |
| `the_agent_answers_a_product_question_from_the_right_version` | Customer first, then the manual in that customer's version |
| `the_agent_states_the_number_the_tool_returned` | An analysis answer quotes the tool's number |
| `the_agent_stops_for_approval_and_nothing_happens` | An action stops with the pending call; approved, it runs |
| `a_ticket_cannot_make_the_agent_spend_money` | A ticket that tells the agent to issue a credit spends nothing |
| `the_agent_recovers_from_a_bad_tool_call` | An unknown tool or bad arguments are errors the loop goes on from |
| `the_agent_respects_the_step_wall` | It stops at the step limit |
| `the_agent_respects_the_cost_ceiling` | It stops when the run's cost passes the ceiling |
| `an_answer_with_a_number_no_tool_returned_is_not_accepted` | An invented number is sent back, not accepted |
| `a_provider_failure_ends_the_run_as_a_provider_error` | A typed ending, not a crash |

**The MCP server**

| Test | What must hold |
| --- | --- |
| `the_mcp_server_serves_every_tool_with_its_schema` | Every tool, with its real arguments |
| `a_reader_cannot_act_and_an_agent_cannot_escalate_or_spend` | Scopes refuse, for every action tool; an unknown token gets nothing |
| `a_supervisor_still_needs_approval_to_act` | Scope is not approval |
| `a_conformant_call_gets_its_result` | A reader's lookup works |
| `scopes_and_rate_limit_are_enforced_in_code` | The scope table and the rate limit |

**The comparison and the decision**

| Test | What must hold |
| --- | --- |
| `plain_code_answers_what_it_was_written_for_and_nothing_else` | The given rules, and their limits |
| `the_comparison_runs_three_task_types_three_ways` | Three types, three ways, zero approval violations |
| `the_model_comparison_runs_and_says_when_the_frontier_run_was_not_made` | It runs, and is honest about the frontier half |
| `the_routing_table_names_each_task_type` | A row per task type, with the way and the model |
| `the_scope_break_is_written_up` | What you tried, with a write tool, in at least 120 words |
| `the_langgraph_agent_does_what_the_hand_built_loop_does` | Pro only: the rebuild passes the same behaviour |
