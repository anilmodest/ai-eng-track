# Week 4 — Agents, tools and real systems

Areas 6 and 7 of the track. About 9–10 hours, with no session. Branch: `week-4`.

The hours add up: 20 minutes on `CONCEPT.md` first, then 1 + 1 + 5 + 2 hours and a closing half
hour in the sections below.

## What you are building

Two things, and the second one is the point.

**One tool that reaches a real system.** `customer_version` answers a single question — which
version of the product one customer runs — by reading one field of one record, for this desk's
own account only.

```
customer_version(customer_id="C-1004")  ->  "v3"
customer_version(customer_id="C-2001")  ->  "refused: C-2001 belongs to another account"
```

**One task set answered three ways**, then compared with numbers: plain code (`app/agents/plain.py`),
a fixed workflow (`app/agents/workflow.py`), and an agent loop (`app/agents/agent.py`, which is
the one you write).

Why the support desk cares: the manual exists in more than one version, so the system has to look
up which version a customer runs before it can answer from the right manual. That is the whole
reason the tool exists. Without the lookup the system is guessing, and a wrong guess comes back
confident and out of the wrong version.

The three implementations are not three features. They are an experiment, and it ends in a
recommendation. **The recommended outcome of this week is that no agent goes into the finished
system.** Plain code and the workflow answer these questions for less money with more
predictability, and the agent exists so that you can say so with evidence instead of taste. You
are not being marked on shipping an agent. You are being marked on the decision.

## Agency is a cost

An **agent loop** is four lines of behaviour: the model picks a tool, you run it, you show it the
result, it picks again. A **tool schema** is the JSON description of one tool — its name,
description and argument types. It is what the model sees, and what you validate its call against
before any function runs.

What makes this hard is that you have handed the deciding away. Cost, latency and the path taken
all vary per run, so three guards go in before the loop is safe to own.

| Guard | What it is | Without it |
| --- | --- | --- |
| **Step wall** | a hard maximum number of steps, `AGENT_MAX_STEPS` | a confused loop runs until your budget is gone |
| **Money checkpoint** | a tool marked `costs_money=True` does not run until the caller has approved that spend | the model decides what you pay for |
| **Recovery** | a bad tool name or bad arguments come back as error text the model reads | one malformed call is a 500 in your service |

The second half of the week is the other half of the same idea. A **scope** is a limit enforced in
code, not requested in a prompt: a prompt is a request, a scope is a boundary. **Least agency**
means a caller gets the smallest set of tools its job needs — a reader cannot spend money.
**MCP**, the Model Context Protocol, is how an outside client (an IDE, a desktop app, another
agent) discovers and calls your tools without you writing a client for each. It is a transport and
a schema convention. It is **not** a permission system.

So: a scope you can demonstrate beats a policy you can describe. `version_for('C-2001')` raising
is output requirement O10, and it is tested. A model that has been talked into asking for another
desk's customer still does not get it, because the refusal lives in the function.

Why an interviewer cares. "Would you build this as an agent?" is a real question, and the answer
that lands is two numbers, not an opinion. "We put it behind MCP" is the moment an AI feature
becomes an infrastructure risk, and the follow-up is always: who can call what, and how did you
prove it.

## Run it and watch (1 hour, change nothing)

```
uv run python explore/w4_01_watch_the_agent_think.py
uv run python explore/w4_01_watch_the_agent_think.py "How many invoices are addressed to Contoso?"
```

Watch the transcript. Did it search before it listed? Did it extract when reading would do? Did it
finish as soon as it could? Then:

```
uv run python scripts/compare_week4.py
```

When we ran this against Gemini's free tier, plain code scored 5/6 at $0, the workflow 5/6 at
about a cent, and the agent got the first two right and then hit the provider's daily quota: four
`provider_error` rows. That is not a bug in the loop; it is Week 1's lesson arriving on schedule.
Set `MODEL_FALLBACK_PROVIDER` and run again.

## Read it (1 hour, change nothing)

Read in this order. The first three questions are Q1b in `reflections/week-4.md`.

1. **`app/agents/tools.py`** — what happens when the model calls a tool that does not exist, or
   with a `k` of 50? Why is that better than raising?
2. **`app/agents/workflow.py`** — how many model calls does it make for N invoices, and which of
   them is gated by approval?
3. **`app/mcp_scopes.py`** — what does a `reader` token get by default, and what stops it spending
   money even if the model asks nicely?
4. **`app/agents/customers.py`** — the whole scope, in thirty lines, with no function in it that
   writes. Run both of these and note which one raises:

```
uv run python -c "from app.agents.customers import version_for; print(version_for('C-1001'))"
uv run python -c "from app.agents.customers import version_for; print(version_for('C-2001'))"
```

Then open `tests/weeks/test_week4.py`. **It is the specification.** Every test name is one
behaviour, and the table below is the order to make them pass.

## Build it (5 hours)

`app/agents/agent.py` is yours. The tools, plain code, the workflow, the MCP server and the scopes
are given. Run `make next` any time to see where you are.

`run_agent(ctx, question) -> AgentResult` ends in exactly one of four states, and never in an
exception:

| `status` | Reached when |
| --- | --- |
| `done` | the model called `finish` |
| `needs_approval` | a tool raised `NeedsApproval` |
| `max_steps` | the loop used `AGENT_MAX_STEPS` steps without finishing |
| `provider_error` | `ModelError`, `ModelTimeout` or `SchemaError` from the provider |

Each step is done when the tests named beside it go green.

| # | Build | Done when these pass |
| --- | --- | --- |
| 1 | Nothing. Run `make check WEEK=4` and confirm the given tool layer is green: six schemas, `k` bounded at 10, money-costing tools marked, empty or oversized arguments rejected before any tool runs | `tool_schemas_are_json_schema_the_model_can_read`, `tool_arguments_are_validated` |
| 2 | Nothing, again. Confirm the scope (O10): the version reads, another desk's customer is refused, no writing or listing function exists, and the tool hands the model a refusal it can read rather than an exception | `the_version_lookup_reads_one_field_of_one_record`, `a_customer_on_another_desk_is_refused`, `the_registry_offers_no_way_to_write_or_to_list`, `the_tool_returns_a_refusal_the_model_can_read` |
| 3 | Run plain code and note both halves of its bargain: exact and free on the questions it was written for, honest about the ones it was not | `plain_code_answers_its_questions_exactly_and_free`, `plain_code_admits_what_it_cannot_do` |
| 4 | Run the workflow unapproved, then approved. Count the calls both times. Unapproved must spend nothing at all | `workflow_stops_at_the_money_checkpoint`, `workflow_runs_end_to_end_when_approved` |
| 5 | The loop. A system prompt from `app/llm/prompts/agent_v1.md` plus `tool_schemas()`; ask for a `ToolCall` (`tool`, `args`) through `complete_structured`; run it with `run_tool`; append `Result of <tool>: ...` to the transcript. `finish` ends it with `done`. Record every step (tool, args, result, tokens) and the total cost, including money the tools spent | `agent_calls_a_tool_then_finishes` |
| 6 | The wall. At most `AGENT_MAX_STEPS` iterations; running out ends the loop with `max_steps` | `agent_hits_the_step_wall` |
| 7 | Recovery and the checkpoint. A bad call returns readable text, so the loop carries on; `NeedsApproval` ends it with `needs_approval`; a provider failure with `provider_error`. Never an exception out of the loop | `agent_recovers_from_a_bad_tool_call` |
| 8 | Nothing to write here either. Drive the given MCP server as the `reader` token and see what guards each call: scope checked and rate limited before anything is touched, a denial that says why, a tool failing mid-call that does not take the server down | `scopes_are_least_agency`, `rate_limiter_is_a_sliding_window`, `mcp_server_denies_out_of_scope_calls` |

The order is not a preference. Steps 1 to 4 are given code, so getting them green first means any
red after that is yours. Step 5 before 6 and 7, because there is no wall to hit and nothing to
recover until the loop runs once. Step 8 is independent of the loop, so it goes last and cannot
block the comparison.

`make check WEEK=4` as often as you like. Red is the week's work, not a problem.

### If you get stuck

- **Rate-limited mid-exercise?** The free tiers are small, and the agent is the hungriest thing
  you have built. Put a second provider's key in `.env` and set `MODEL_FALLBACK_PROVIDER`. That is
  Week 1's lesson, so doing it under duress is on-topic rather than a detour.
- **A test is failing and the message is not obvious?** Open the test. It is short, and it says
  exactly what it expected.
- **On `start`?** `routes/worked_example.py` runs *one* tool call and finishes: the loop's body
  without the loop. Read it beside your stub rather than instead of it.
- **Stuck for more than an hour?** An unblock call is available after a real attempt. Use it.

Your route changes what this week gives you: read `routes/start.md`, `routes/core.md` or
`routes/pro.md` in this folder (the hub shows yours).

## Measure it and decide (2 hours)

With the gate green, produce the evidence. First the comparison:

```
uv run python scripts/compare_week4.py
```

Paste the table into `reflections/week-4.md` with one paragraph: which way you would ship for
these questions, and **what two numbers decided it**. Cost per correct answer is the number to
think about. If the paragraph recommends the agent, the two numbers have to carry it.

Then the security half. Start the server as the least-privileged token:

```
MCP_TOKEN=reader uv run python -m app.mcp_server
```

Connect any MCP client (Claude Desktop, an IDE, or `mcp dev`) and call `extract_document` as the
reader. It must be denied. Then find a way round your own scopes: a second token in `MCP_TOKENS`,
a tool that calls another tool, an argument the schema does not bound. Write down what you found,
whether or not you fixed it. One weakness found in your own permission boundary is the deliverable;
a clean sheet means you did not try hard enough.

## Submit (30 minutes)

- `reflections/week-4.md`: Q1 (the concept in your words), Q1b (the three reading questions),
  Q2 (what surprised you), Q3 (what you would change), Q4 (what you contributed and how you
  checked it),
  Q5 (help you used), the comparison table and paragraph, and the MCP finding.
- Open a pull request `week-4 → main`. CI runs the gate. Fix anything red.

## Self-directed week

No session this week. Your mentor's review of this PR lands at the Defence. Use the comparison
table and the MCP finding in your reflection to make the decisions defensible on your own.

**Pass line, checked at the Defence:** CI green, a shipping decision with two numbers behind it,
and one weakness found in your own permission boundary.

## Optional: self-test

`QUIZ.md` in this folder, with an explanation for every answer. On the hub page it is interactive.
The score stays in your browser: it never reaches the repository, your mentor or your route. Use
it to find what to re-read, not to measure yourself.
