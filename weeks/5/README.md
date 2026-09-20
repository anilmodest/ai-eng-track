# Week 5 — Observability, cost and guardrails

Areas 9 and 10 of the track. About 10 hours. Branch: `week-5`.

**Goal:** every request leaves a trace with cost attributed per step; failures have kinds; and
after being attacked with documents that carry instructions, your service holds.

Read `CONCEPT.md` first. Then:

## Elaboration 1 — see it (1 hour)

Tracing is already wired. Make some requests and read the traces:

```
make run                                     # then, in another terminal:
curl -s -F "file=@samples/invoice.md" localhost:8000/documents
curl -s -X POST localhost:8000/documents/1/extract -D - | grep -i x-request-id
curl -s localhost:8000/traces/<that id> | python -m json.tool
uv run python scripts/trace_report.py        # the dashboard, from data/app.db
```

Then get attacked. **This template ships with the guard as a pass-through**: the service works,
and it is wide open. Run:

```
uv run python scripts/attack.py
```

With the fake model, two of four attacks succeed. With a real model, run it and see; then read
`eval/attacks.jsonl` to see how ordinary the documents look.

## Elaboration 2 — read it (1 hour)

Read, in this order, and answer in `reflections/week-5.md`, Q1b:

1. `app/trace.py` — where is cost attributed, and why does the root span carry a roll-up rather
   than the sum being computed at read time?
2. `app/api/extract.py` — the guard is called in three places. Name them and say what each
   protects against. Which one is *not* about injection at all?
3. `eval/attacks.jsonl` — for each attack, which of the four defences should stop it? Is there one
   that pattern-matching would never catch?

Then read `tests/weeks/test_week5.py`.

## Exercise — get attacked, then build the guard (5 hours)

`app/guard.py` is yours. Every function exists with the right signature and does nothing:

| Function | Build |
| --- | --- |
| `preamble()` | return `GUARD_PREAMBLE` (the model must be told that fenced text is data) |
| `wrap_untrusted(text, label)` | fence the text in `<label>` tags so it cannot close its own fence |
| `detect_injection(text)` | strip lines matching known instruction patterns; report what was found |
| `scan_output(facts, source)` | flag any figure in the model's key facts that the source never states |
| `check_limits(settings, session)` | raise `Blocked("kill_switch", ...)` or `Blocked("budget_exceeded", ...)` |

Then:

```
uv run python scripts/attack.py               # must say 0 of 4 attacks succeeded
make check WEEK=5                             # runs it as a gate
```

Then the part that matters: **attack a peer**. Take one document from `corpus/`, plant an
instruction in it that would change the extraction or the answer, and send it to another fellow
(their forwarded port or live URL). Record what happened in your reflection. When one lands on
you, add it to `eval/attacks.jsonl` and make it hold. The set grows every cohort.

What your route adds:

| Route | Exercise |
| --- | --- |
| `start` | the above |
| `core` | plus one attack that `detect_injection` cannot catch (another language, an encoding, a paraphrase), a test that proves it, and the defence that does catch it |
| `pro` | plus per-token budgets in the MCP server, and a `scripts/trace_report.py` extension that shows cost per *user*, not just per request |

## Submit (30 minutes)

- `reflections/week-5.md`: Q1, Q1b, Q2, Q3, one trace explained step by step, the attack log
  (what you sent, what came back, what you changed).
- PR `week-5 → main`. CI green, including the attack gate.

## The session (35 minutes)

You demo: a trace, the dashboard, and `scripts/attack.py` holding. Your mentor plants an
instruction in a document you have not seen and sends it to your service. Then Week 6's sentence:
*interviewers ask what it did for the business, not what it scored.*

Pass line: CI green including the attack gate, one attack that got through explained, and you can
read a cost off a trace without looking at the code.
