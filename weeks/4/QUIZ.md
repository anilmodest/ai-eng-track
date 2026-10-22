# Week 4 — Practice quiz

Practice, untimed and repeatable. Your score stays in this browser on your hub page and never
reaches the repository or your mentor. Use it to find what to re-read; the explanations are the
point, not the score. Your mentor also assigns a short weekly check on BridgePath: different
questions, some of them timed, taken once, and your mentor sees that score.

## Q1. `issue_credit` stops for a person's approval and `query_tickets` does not. What makes that so?
- [ ] The agent's prompt tells it to ask before crediting — a rule in a prompt is a request, and `explore/w4_02` shows a runner that trusts it paying out
- [ ] The MCP scopes, where only a supervisor may credit — a scope says who may ask; the tasks API has no token and the credit still stops
- [x] The spends flag on its spec, which `run_tool` checks in code
- [ ] The cost ceiling, which stops any run that spends money — the ceiling caps what the run's model calls cost, not money paid to a customer
> Why: approval sits on what writes or spends, and the flag on the spec is the whole of the permission. Get the flag wrong and the door opens; that is why saying truthfully which tools write and which spend is your job this week.

## Q2. A ticket owes 900 USD and already carries 400 USD of credits. A person approves `issue_credit` for 150 USD on it. What happens?
- [ ] 150 USD is credited, because a person approved that exact amount — approval lets the tool run; the cap is checked inside it
- [x] Refused in words, nothing spent: 550 USD passes the 500 cap
- [ ] 100 USD is credited and the rest refused — the person approved 150; paying a different amount is not the tool's call
- [ ] The run stops for approval again — it was approved; the refusal comes from the tool itself
> Why: the cap counts every credit on the ticket, including those already on its record, and a credit never exceeds what is owed. Approval and the cap are separate checks, and both must pass.

## Q3. The model calls `query_tickets` with `{"query": "average_resolution_time"}`. What happens?
- [x] It fails validation, the model reads the error, and no query runs
- [ ] It runs, because the tool is read-only and so cannot do harm — read-only is not enough; only the queries on the allowlist ever run
- [ ] The tool falls back to SQL the model writes — there is no SQL path, and that is the point of an allowlist
> Why: a model that can write SQL can read another desk's rows or invent a column. Five parameterised questions, over this desk's tickets only, is the whole surface; anything else is an error the model can recover from.

## Q4. `query_tickets` returned a count of 9 urgent open tickets. The agent calls `finish` with "There are 11 urgent open tickets." What happens?
- [ ] It is accepted, and the run ends with status `done` — the number check runs before any answer is accepted
- [ ] The loop corrects 11 to 9 itself and then accepts the answer — the loop never rewrites an answer; the model must state the number
- [x] It goes back to the model, naming 11; that costs a step
- [ ] The run ends with `provider_error` — nothing failed at the provider; the answer was well formed
> Why: "the number in the answer is the number the query returned" is enforced, not hoped for (`app/agents/checks.py`). The check reads numerals and skips ids, versions and dates, which is also why the prompt still asks for figures exactly as returned.

## Q5. Through MCP, a `supervisor` token calls `escalate`, and `MCP_APPROVED` is not set. What comes back?
- [ ] The escalation is recorded, since a supervisor may escalate — scope says who may ask; approval says yes
- [ ] `denied: ...` — the supervisor's scope includes escalate; denial comes from the scope check
- [ ] An exception, and the client loses the connection — the server always answers in text and stays up
- [x] `needs approval: ...`, and nothing is written
> Why: a scope and an approval are two different checks, both in code, on every call. Passing the first only gets the call as far as the second.

## Q6. Which request does an agent handle that a fixed workflow cannot?
- [ ] "Which version does C-1004 run?" — plain code answers that exactly, at no cost
- [x] One where the next step depends on what the previous tool returned
- [ ] Any request that ends in an action — the workflow also drafts, and also stops for approval
- [ ] Any request about numbers in the tickets — the workflow has one model call choose the query, and code states the number
> Why: a workflow cannot change its mind; if the first step returns something unexpected, it carries on regardless. That is what an agent buys, at a price, and the comparison says per task type whether the price is worth it.

## Q7. The cheap model gets lookups and actions right and fails the multi-step tasks; a frontier model gets everything right at thirty times the cost. What goes in your routing table's model column?
- [ ] Frontier for every row, to be safe — that pays thirty times over on tasks the cheap model already gets right
- [ ] Cheap for every row, since it is right most of the time — then the multi-step tasks stay wrong
- [x] Cheap where it is right, frontier only where it fails
> Why: model size is a cost, like agency. The routing table decides both per task type, from the numbers in your comparison and model files, and the model column must agree with them.

## Q8. You rebuild the agent in LangGraph with the same tools, walls and tests. On the trajectory set, compared with the hand-built loop, what do you expect to find? (stretch: core/pro)
- [ ] Fewer model calls, because the graph skips steps the hand-built loop takes — the model makes the same choices either way
- [x] Identical calls and cost; they differ in reading, debugging and resuming
- [ ] No need for approval in code, since the graph pauses for a person — the pause still has to be wired to the same door
> Why: the model does the same work in both, so the choice rests on what you pay to read, debug and depend on, and on what you get: a graph is easier to extend with nodes, and its checkpointer can resume a run. On pro you build it and decide; on start and core, `docs/langgraph-comparison.md` has the numbers.
