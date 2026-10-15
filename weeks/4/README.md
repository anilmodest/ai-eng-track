# Week 4 — Agents that act, and where agency pays

Areas 6, 7 and 8. 9 to 10 hours. No session. Branch: `week-4`.

> **The one lesson.** Agency and model size are both costs. Put each where the measurement says it
> pays, and never let the model act without approval.

## The gap it closes

The difference between a workflow, where you wrote the steps and the model does one job inside
each, and an agent, where the model chooses its own steps. An agent is slower, more expensive and
less predictable, and on some tickets it is the only thing that works. A junior candidate who can
say, from something they built and measured, which tasks deserve an agent and which do not, and
how they stopped it acting without permission, is rare.

## What you are building

The support-desk agent the programme has been heading for: it looks things up, analyses the
ticket data with numbers it did not invent, and takes actions (a reply, an escalation, a credit),
the risky ones only with a person's approval.

```
POST /tasks/run {"question": "Escalate T-2020 to engineering: the runner will not start."}
  -> {"status": "needs_approval", "pending": {"tool": "escalate", "args": {...}}, "calls": ["get_ticket"]}

POST /tasks/run {"question": "...the same...", "approve": ["escalate"]}
  -> {"status": "done", "calls": ["get_ticket", "escalate"], ...}
```

## Read (1 hour)

`CONCEPT.md`. Then, answering in `reflections/week-4.md`, Q1b:

1. **`app/tools/base.py`, `run_tool`**: in which order are arguments validated and approval
   checked, and why does that order matter for a credit of 5000 USD?
2. **`app/agents/workflow.py`**: what can it not do that the agent can?
3. **`app/mcp_scopes.py`**: what is the difference between a scope and an approval?

## See it (30 minutes, change nothing)

```
uv run python explore/w4_01_watch_the_agent_think.py      # what an agent spends on a lookup
uv run python explore/w4_02_approval_in_the_prompt.py     # a credit nobody approved
```

The second needs your action tools, so run it again after Core 1. Watch a runner that trusts the
prompt pay out, and the real door refuse.

## Build (5 to 7 hours)

Core items are needed for the lesson and checked by the gate; stretch items are shown to your
mentor and never block. Log your assistant use in `ai-use/week-4.yml` as you go.

### Core 1: three tools that act (`app/tools/actions.py`)

`draft_reply` (no side effect a customer sees), `escalate` (writes) and `issue_credit` (spends,
capped per ticket). What is yours: the descriptions, the constraints (a team that does not exist,
a negative or huge amount, an empty reason), **which write and which spend** (the flag on the spec
is the whole of the permission), the cap (500 USD per ticket across all credits, never more than
is owed), and refusals in words. Approval is enforced for you in `app/tools/base.py`; your job is
to tell it the truth.

### Core 2: one analysis tool (`app/tools/analysis.py`, `query_tickets`)

Read-only, parameterised queries from an allowlist, over this desk's tickets only: `count`,
`count_by`, `sum_amount_due`, `sum_credits_issued`, `median_first_response`, with filters. A query
or a filter that is not on the list fails validation. The result must be unambiguous: which query,
which filters, and the number.

### Core 3: the agent loop (`app/agents/agent.py`, `run_agent`)

The loop, with every wall in its docstring: a step wall, a cost ceiling
(`AGENT_COST_CEILING_USD`), recovery from bad calls, the approval stop with the pending action,
and the number check on `finish` (`app/agents/checks.py`).

<!-- route:start -->
### Core 4: the MCP server is given

On start, `app/mcp_server.py` is given and working: read it, and run the MCP tests against your
tools. Then do Core 5.
<!-- /route -->
<!-- route:core,pro -->
### Core 4: the MCP server (`app/mcp_server.py`)

You write it: every tool in the registry with its real schema, the token's scope before anything
runs, a rate limit, approval through `app.tools.call`, and always an answer in text. Its
docstring says what must hold.
<!-- /route -->

### Core 5: one request, three ways, and two models (`make evidence WEEK=4`)

| Measurement | Script | What it tells you |
| --- | --- | --- |
| `compare` | `scripts/compare_week4.py` | Plain code, the workflow and your agent on three task types (lookup, analysis, action): accuracy, cost per correct answer, steps, approval violations |
| `trajectories` | `scripts/trajectories.py` | Your agent on your twenty week 3 tasks: the path, not just the answer |
| `models` | `scripts/model_compare.py` | The trajectory set on your model, and once on a frontier model through the programme's capped key |

For the frontier run, the programme gives you `PROGRAMME_MODEL_BASE_URL`, `PROGRAMME_MODEL_TOKEN`
and `PROGRAMME_FRONTIER_MODEL` as Codespaces secrets. You pay nothing; the run is capped. Without
them the frontier half says it was not run.

### Core 6: break your own scope (`decisions/week-4-scope-break.md`)

Try, deliberately, to make something act that should not: a token outside its scope, an action
without approval, a ticket that tells the agent what to do. At least one attempt must use a tool
that writes. Write up what you tried, what happened and what stopped it, whether or not it worked.

### Stretch

- **The LangGraph rebuild** of the same agent: <!-- route:pro -->core on your route
  (`app/agents/langgraph_agent.py`, `uv sync --extra langgraph`).<!-- /route -->
  <!-- route:start,core -->read the supplied comparison, [`docs/langgraph-comparison.md`](../../docs/langgraph-comparison.md),
  and say in your decision record which you would ship.<!-- /route -->
- **Plan then execute**: a planning step before the loop, measured on the multi-step tasks.

## Decide

**The routing table**: for each task type, plain code, workflow or agent, **and** which model,
cheap or frontier, and the numbers that decided it. Put it in `decisions/week-4.md` as a table:

```
| Task type | Way | Model | Why |
| --- | --- | --- | --- |
| lookup | ... | cheap | ... |
| analysis | ... | ... | ... |
| action | ... | ... | ... |
```

<!-- route:pro -->And whether to ship LangGraph or the hand-built loop.<!-- /route -->

## What proves it

1. **The gate**: the action tools (validation, approval, the cap, scope), `query_tickets`
   (allowlist, the numbers are the data), every wall of the loop, the MCP server's scopes and
   approval, the three-way comparison and the model comparison running, the routing table and the
   scope-break write-up.
2. **The hidden evaluation**, on what you merge: zero unapproved actions on the hidden set, and every number the
   analysis tool states matching the ground truth.
3. **The evidence file and the decision record**, with the routing table's model column agreeing
   with the cheap-against-frontier table.

**Anti-goal: do not build a multi-agent system.**

### If you get stuck

- **Rate-limited?** The agent is the hungriest thing you run. Your fallback provider from week 1
  is for exactly this.
<!-- route:start -->
- **On `start`?** `routes/worked_example.py` runs one turn of the loop in full: the call, the
  result, the error, the approval stop. Your loop repeats it inside the walls.
<!-- /route -->
- **Stuck for more than an hour?** An unblock call is available after a real attempt. Use it.

Your route changes what this week gives you: the page in `routes/` in this folder says how.

## Submit

1. `make check WEEK=4` green, commit, `make evidence WEEK=4`, commit the evidence.
2. `decisions/week-4.md` with the routing table, `decisions/week-4-scope-break.md`,
   `ai-use/week-4.yml`, `reflections/week-4.md`.
3. Open a pull request `week-4 → main`.

## A week without a session

Your mentor reads the brief and gives a one-click verdict. The gate and the hub page are your
feedback, and your mentor passes on the hidden evaluation's totals.

## Optional: self-test

`QUIZ.md` in this folder. The score stays in your browser.
