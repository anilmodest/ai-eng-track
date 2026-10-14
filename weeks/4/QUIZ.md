# Week 4 — Quiz

Optional, repeatable, and yours: the score is kept in your own browser on the hub page and
never reaches the repo, the mentor or the route. Use it to find out what you have not understood
yet; then go and read that part again. The explanations are the point, not the score.

## Q1. Why does `issue_credit` need approval and `query_tickets` does not?
- [x] One spends money and cannot be undone; the other only reads, from an allowlist, over this desk's rows
- [ ] Credits are slower to compute — speed is not the reason; consequence is
- [ ] Because the prompt says so — a rule in a prompt is a request; the flag on the spec is the boundary
> Why: approval sits on what writes or spends. Everything else the agent may do freely, and least agency (week 5) removes even the asking where a request does not need it.

## Q2. The model calls a tool that does not exist. What does a good loop do?
- [ ] Raise an exception and end the request with a 500 — the loop must not crash on the model's mistake
- [x] Return an error message as the tool result so the model can read it and choose again
- [ ] Silently pick the closest tool name — guessing on the model's behalf is how wrong actions happen
> Why: `run_tool` turns unknown tools and invalid arguments into text. The model reads it and recovers; the service never sees an exception.

## Q3. The workflow answered every action correctly at a twentieth of the agent's cost. So you route actions to the workflow?
- [x] For that task type, if the measurement holds on the hidden set too; the routing table is per task type, from numbers
- [ ] Always use the workflow — it cannot handle a request whose steps depend on what the first tool returns
- [ ] Always use the agent — its flexibility is a cost you place deliberately, not a default
> Why: cost per correct answer, per task type, is the comparison. Predictability is a cost too.

## Q4. The agent's answer says "about a dozen open tickets" and query_tickets returned 9. What happens?
- [x] The answer is sent back with the number nothing returned named; it costs a step, and it is not accepted
- [ ] It is accepted: "about a dozen" is close enough — a support desk acts on the number
- [ ] The run fails with an error — the model gets one more chance to state the tool's number
> Why: "the number in the answer is the number the query returned" is enforced, not hoped for (app/agents/checks.py).

## Q5. Through MCP, a `supervisor` token calls `escalate` with no approval set. What comes back?
- [ ] The escalation is recorded: the supervisor's scope allows it — scope says who may ask, not yes
- [x] `needs approval: ...` and nothing is written
- [ ] `denied` — the scope allows escalate; approval is the separate check
> Why: a scope and an approval are two different checks, both in code, on every call.

## Q6. A cheap model gets the analysis tasks right and the multi-step ones wrong; the frontier model gets both right at thirty times the cost. What goes in the model column of your routing table?
- [ ] Frontier everywhere — you pay thirty times for the tasks the cheap model already gets right
- [x] Cheap for the task types it gets right, frontier only where the measurement says it fails
- [ ] Cheap everywhere — then the multi-step tasks stay wrong
> Why: model size is a cost like agency. Put each where the measurement says it pays.

## Q7. Name a way past your own scopes that the tests do not cover. (stretch)
- [x] Any concrete one: a second token in `MCP_TOKENS`, a tool whose schema is looser than its code, `MCP_APPROVED` set for a whole server's life
- [ ] There is none; the tests cover scopes and approval — they cover what they cover
- [ ] Only a network attacker could — the boundary is inside the process; the caller is already past the network
> Why: the exercise is to look. A permission boundary you have not tried to cross is a diagram, not a boundary.
