# Week 4 — Agents, tools and real systems

Areas 6 and 7 of the track. About 9–10 hours. Branch: `week-4`.

**Goal:** one task set solved three ways and compared with numbers; an agent loop with a wall, a
money checkpoint and error recovery; the service exposed over MCP with scopes you have tried to
break.

Read `CONCEPT.md` first. Then:

## Elaboration 1 — see it (1 hour, change nothing)

```
uv run python explore/w4_01_watch_the_agent_think.py
uv run python explore/w4_01_watch_the_agent_think.py "How many invoices are addressed to Contoso?"
```

Watch the agent's transcript. Did it search before it listed? Did it extract when reading would
do? Did it finish as soon as it could? Then:

```
uv run python scripts/compare_week4.py
```

When we ran this against Gemini's free tier, plain code scored 5/6 at $0, the workflow 5/6 at
about a cent, and the agent got the first two right and then hit the provider's daily quota:
four `provider_error` rows. That is not a bug in the loop; it is Week 1's lesson arriving on
schedule. Set `MODEL_FALLBACK_PROVIDER` and run again.

## Elaboration 2 — read it (1 hour, change nothing)

Read, in this order, and answer in `reflections/week-4.md`, Q1b:

1. `app/agents/tools.py` — what happens when the model calls a tool that does not exist, or with
   a `k` of 50? Why is that better than raising?
2. `app/agents/workflow.py` — how many model calls does it make for N invoices, and which of them
   is gated by approval?
3. `app/mcp_scopes.py` — what does a `reader` token get by default, and what stops it spending
   money even if the model asks nicely?

Then read `tests/weeks/test_week4.py`.

## Exercise — build and compare (5 hours)

`app/agents/agent.py` is yours. Tools, plain code, the workflow, the MCP server and scopes are
given.

Build `run_agent(ctx, question) -> AgentResult`:

1. A system prompt from `app/llm/prompts/agent_v1.md` plus `tool_schemas()`.
2. A loop of at most `AGENT_MAX_STEPS`: ask the model for a `ToolCall` (`tool`, `args`) through
   `complete_structured`; run it with `run_tool`; append `Result of <tool>: ...` to the transcript.
3. `finish` ends the loop with `status: done`. Running out of steps ends it with `max_steps`.
4. `NeedsApproval` from a tool ends it with `needs_approval`; a provider failure with
   `provider_error`. Never an exception out of the loop.
5. Record every step (tool, args, result, tokens) and the total cost, including money spent by tools.

Then measure: `scripts/compare_week4.py`, table into your reflection, with one paragraph: which
way would you ship for these questions, and what two numbers decided it.

Then the MCP part, which is the security half of the week:

```
MCP_TOKEN=reader uv run python -m app.mcp_server
```

Connect any MCP client (Claude Desktop, an IDE, or `mcp dev`) and call `extract_document` as the
reader. It must be denied. Then find a way round your own scopes: a second token in
`MCP_TOKENS`, a tool that calls another tool, an argument the schema does not bound. Write down
what you found, whether or not you fixed it.

Your route changes what this week gives you: read `routes/start.md`, `routes/core.md` or
`routes/pro.md` in this folder (the hub shows yours).

Run the gate as often as you like: `make check WEEK=4`.

## Submit (30 minutes)

- `reflections/week-4.md`: Q1, Q1b, Q2, Q3, the comparison table and paragraph, the MCP finding.
- PR `week-4 → main`. CI green.

## Self-directed week

No session this week. Your mentor's review of this PR lands at the Defence. Use the comparison
table and the MCP finding in your reflection to make the decisions defensible on your own. An
unblock call is available after a real attempt.

Pass line, checked at the Defence: CI green, a shipping decision with two numbers behind it, one
weakness found in your own permission boundary.

## Optional: self-test

`QUIZ.md` in this folder has a few questions on this week's concept, each with an explanation. On the hub page they are interactive and scored, but the score lives only in your browser: it never reaches the repo, your mentor or your route. Use it to find what to re-read.
