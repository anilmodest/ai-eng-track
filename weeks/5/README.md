# Week 5 — Observability, security and privacy

Areas 9 and 10. 8 to 9 hours. No session; the borderline fellow's scheduled unblock call lands
here. Branch: `week-5`.

> **The one lesson.** Once the system can act, content it reads can attack it. Remove the
> capability first.

## The gap it closes

Two things a production system has and a portfolio project usually does not: tracing, so
behaviour can be explained afterwards rather than guessed at, and defence against instructions
hidden in the content the system reads. Since week 4 the worst case is no longer a wrong answer:
it is a ticket whose text persuades the agent to escalate, refund, or reveal another customer's
data. And a third: personal data that should never have reached a model provider.

## Read (1 hour)

`CONCEPT.md`. Then, answering in `reflections/week-5.md`, Q1b:

1. **`app/trace.py`**: where is cost attributed, and why does the root carry a roll-up?
2. **`app/tools/base.py`, `run_tool`**: what happens to a tool the run was not offered, and to
   text a customer wrote, before the model reads it?
3. **`eval/attacks.jsonl`**: for each attack, which defence should stop it? Is there one that
   pattern-matching would never catch?

## See it (1 hour, change nothing)

```
uv run python explore/w5_01_read_a_trace.py
uv run python scripts/attack.py --guard off       # the attacks, with no defence
MASK_PERSONAL_DATA=false uv run python scripts/privacy_check.py   # what reaches the model now
```

Read the attacks that succeed, and how ordinary the documents and tickets that carry them look.

<!-- route:start -->
**Tracing is given and working on your route.** Run the commands now and read what they show.
<!-- /route -->
<!-- route:core,pro -->
**On your route `app/trace.py` is signatures only**, so the trace commands show you nothing until
you have instrumented the service yourself. Come back to them after Core 1.
<!-- /route -->

## Build (5 to 6 hours)

Core items are needed for the lesson and checked by the gate; stretch items are shown to your
mentor and never block. Log your assistant use in `ai-use/week-5.yml` as you go.

### Core 1: tracing (`app/trace.py`<!-- route:start --> is given: read it<!-- /route -->)

Every request is a tree of spans: retrieval, tool calls, model calls and approvals, each with its
latency and cost, and OpenTelemetry's names on them (`gen_ai.request.model`,
`gen_ai.usage.input_tokens`, `gen_ai.tool.name`), so a trace reads the same in an employer's
tracing tool (`GET /traces/{id}/otel`). Every failure on an error kind; cost attributed to the step
that spent it and rolled up to the request.

### Core 2: least agency (`app/agents/routing.py`)

**Remove the capability first.** `tools_for(request)` decides which tools the agent is offered,
from the desk's request, never from what the agent reads. A lookup, an analysis or "handle this
ticket" is never offered `escalate` or `issue_credit`; a request that asks for one gets that one.
The door refuses a tool that was not offered, whatever the model asks for.

### Core 3: the guard, the second layer (`app/guard.py`)

`preamble`, `wrap_untrusted`, `detect_injection`, `scan_output` and `check_limits` (the kill
switch and the daily budget: `/extract`, `/ask` and `/tasks/run` refuse with a 503 or a 429
before any model call). With the guard on, a ticket's text and a page of the manual reach
the model fenced as data, known patterns stripped, through your functions. State what it cannot
catch.

### Core 4: personal data (`app/privacy.py`)

`mask` and `unmask`: names, emails and phone numbers replaced with placeholders before every model
call that can see a ticket (agent and workflow runs, through `app/llm/masking.py`), the same
person always the same placeholder in a run, and the real values back only in an output a person
approves (a draft). Turn it on with `MASK_PERSONAL_DATA=true`. Watch for text inside JSON: an
escaped newline before a name, an accent written as an escape, so Wójcik arrives as `W\u00f3jcik`.

### Core 5: blast radius (`decisions/week-5-blast-radius.md`)

For each action tool, what it could do if every defence failed at once, and what bounds it.

### Core 6: measure it (`make evidence WEEK=5`)

| Measurement | Script | What it tells you |
| --- | --- | --- |
| `attacks` | `scripts/attack.py` | Injections in documents, tickets and tool output, held or not, with the guard on (run `--guard off` too, for the before) |
| `privacy` | `scripts/privacy_check.py` | Personal values found in what the model was shown: zero is the proof |
| `traces` | `scripts/trace_report.py` | Cost and latency per step, failures by kind, cost per ticket and per day |

The programme's hidden attack set, which you never see, also runs on your pull request; its result
is on your mentor's brief.

### Stretch

- **Streaming**: the agent's answer streamed on a ticket endpoint, with time-to-first-token
  recorded on the trace. Shown on the brief if done; never blocks the gate.
- **Caching**: the cache hit rate on repeated requests, and what it does to your latency budget.

## Decide

**Which capability to remove rather than filter**, and **the latency budget** for a ticket, with
the numbers that support them (cost per ticket from the trace report; time-to-first-token if you
did the streaming stretch). Write `decisions/week-5.md`, quoting the evidence by key.

## What proves it

1. **The gate**: every request traced with cost on the step that spent it and OpenTelemetry
   attributes; the guard's units; tools that cannot be triggered by document or ticket content;
   no unmasked personal data in any recorded model input; the blast-radius statement.
2. **The hidden attack set** on your pull request, which you have never seen.
3. **The evidence file and the decision record.**

The result: two injections demonstrated working, one defence shipped, cost attributable per step,
and personal data that never leaves the service.

**Anti-goal: do not rely on filtering alone. Remove the capability first.**

### If you get stuck

<!-- route:start -->
- **On `start`?** `routes/worked_example.py` fences a passage and strips one pattern, with the
  test that proves both. Read it beside your stub.
<!-- /route -->
- **Stuck for more than an hour?** An unblock call is available after a real attempt. Use it.

Your route changes what this week gives you: the page in `routes/` in this folder says how.

## Submit

1. `make check WEEK=5` green, commit, `make evidence WEEK=5`, commit the evidence.
2. `decisions/week-5.md`, `decisions/week-5-blast-radius.md`, `ai-use/week-5.yml`,
   `reflections/week-5.md`.
3. Open a pull request `week-5 → main`.

## Quizzes: practice here, a short check on BridgePath

`QUIZ.md` in this folder is the practice quiz, with an explanation for every answer. On the hub page
it is interactive, untimed and repeatable, and the score stays in your browser: it never reaches the
repository, your mentor or your route. Use it to find what to re-read.

Your mentor also assigns this week's check on BridgePath. It has different questions, some of them
timed, and you take it once; your mentor sees that score. It asks about what you built and measured
this week, so the work is the preparation.
