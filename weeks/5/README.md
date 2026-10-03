# Week 5 — Observability, cost and guardrails

Areas 9 and 10 of the track. About 10 hours. Branch: `week-5`.

## What you are building

Three things on top of the service you already have.

**1. Cost and time attributed per step.** Every request leaves a **trace**: a tree of **spans**,
one per step, each with a duration, tokens, a cost and, when it failed, a kind. **Cost
attribution** means the cost sits on the span that spent it and rolls up to the root. The request
id goes back to the caller, so a complaint can be looked up.

**2. Failures sorted by kind.** An **error taxonomy** is one bucket per cause —
`provider_timeout`, `schema_error`, `not_found` — rather than a single "12 failures" count.
Different buckets need different fixes.

**3. A defence against a document that carries instructions.** **Prompt injection** is an
instruction hidden in data the model reads. Your guard **fences** that data (wraps it in labelled
tags and tells the model that text inside the tags is never an instruction), strips the patterns
it recognises, checks the output against the source, and can be stopped dead by a **kill switch**
(one setting that blocks every model call) or a **daily budget** (a cap on model spend per day).

```
POST /documents/42/extract   ->  X-Request-Id: 7f3a19c20b84
GET  /traces/7f3a19c20b84
  -> POST /documents/{id}/extract    412 ms   $0.00094   error_kind: none
       model.call                    380 ms   $0.00094   706 in / 115 out
```

Why the support desk cares: the manual is the attack surface. Reading documents is the whole job,
so every document is untrusted input, and an instruction planted in one is the way in.

## The two sentences everything here is built under

**You cannot defend a number you cannot attribute.** "This request cost 0.4 cents" is a fact you
can report. "The repair call cost 0.3 of it" is a fact you can act on. Without spans you have the
first and not the second, so you cannot say what to change. Cost per query is a standard interview
question, and the person asking it will not read your code.

**A defence you have not attacked is a hope.** This is what makes the week hard. An injection does
not look like a bug during normal testing: the document is ordinary and the response is plausible.
The model cannot reliably tell your instruction from one in the data. Pattern filters catch the
phrasings they know about and nothing else.

So the week's interview answer is not a list of defences. It is four defences, the one attack that
still got through, and what you rely on for the case your filter cannot see.

Read `CONCEPT.md` first, then write that sentence in your own words in `reflections/week-5.md`, Q1.

## Run it and watch (1 hour, change nothing)

Make some requests and read the traces:

```
make run                                     # then, in another terminal:
curl -s -F "file=@samples/invoice.md" localhost:8000/documents
curl -s -X POST localhost:8000/documents/1/extract -D - | grep -i x-request-id
curl -s localhost:8000/traces/<that id> | python -m json.tool
uv run python scripts/trace_report.py        # the dashboard, from data/app.db
uv run python explore/w5_01_read_a_trace.py  # three requests, span trees, then the dashboard
```

The explore script asks you three questions and expects you to answer them from the traces alone,
without opening the code: which step cost the most, which request was slowest and why, which
failed and with what kind.

**Tracing is given and working on the start route only.** On core and pro, `app/trace.py` is
signatures only, so these commands show you nothing until you have instrumented the service
yourself. Read this section now, run the commands against the start route's tracer if you want to
see the target, and come back to them after step 3 of the build.

Then get attacked. **This template ships with the guard as a pass-through**: the service works,
and it is wide open. Run:

```
uv run python scripts/attack.py
```

With the fake model, two of four attacks succeed. With a real model, run it and see; then read
`eval/attacks.jsonl` to see how ordinary the documents look.

## Read it (1 hour, change nothing)

Read, in this order, and answer in `reflections/week-5.md`, Q1b:

1. **`app/trace.py`** — where is cost attributed, and why does the root span carry a roll-up
   rather than the sum being computed at read time?
2. **`app/api/ask.py`** — the guard is called in three places in this endpoint's TODO. Name
   them, and say what each one defends against. Note that `extract.py` never touches the guard
   at all, which is worth a sentence of its own.
3. **`eval/attacks.jsonl`** — for each attack, which of the four defences should stop it? Is there
   one that pattern-matching would never catch?

Then open `tests/weeks/test_week5.py`. **It is the specification.** Every test name is one
behaviour, and the table below is the order to make them pass.

## Build it (6 hours)

Two files are yours: `app/trace.py` and `app/guard.py`. `app/guard.py` has every function already,
with the right signature, doing nothing. Run `make next` any time to see where you are.

Tracing comes first, and that is not a preference. You cannot see what the guard is doing — which
step blocked, what it cost, which kind of failure it produced — until the spans exist.

| # | Build | Done when these pass |
| --- | --- | --- |
| 1 | `begin_request`, `span`, `add_usage`, `end_request` and the readers. A request root, a `model.call` span under it, cost on the call rolled up to the root, and `GET /traces` newest first | `every_request_has_a_trace_with_cost_on_the_step_that_spent_it`, `recent_traces_are_listed_newest_first` |
| 2 | Spans for the steps that are not model calls. A cached extract makes no `model.call` span and costs zero; an agent run shows its tool calls as spans under the request | `a_cached_request_costs_nothing_in_its_trace`, `tool_calls_are_spans_under_the_request` |
| 3 | `mark_error`: every failure lands on an `ErrorKind`, on the root. A provider 400 is `provider_error`; a missing document is `not_found` | `failures_land_in_an_error_taxonomy` |
| 4 | `preamble()` returns `GUARD_PREAMBLE`, and `wrap_untrusted(text, label)` fences the text in `<label>` tags so the data cannot close its own fence | `wrap_untrusted_cannot_be_closed_from_inside` |
| 5 | `detect_injection(text)`: strip lines matching known instruction patterns and report what was found. "Ignore the noise outside" is not an injection | `detect_injection_strips_the_line_and_reports_it`, `detect_injection_leaves_clean_text_alone` |
| 6 | `scan_output(facts, source)`: flag any figure in the model's key facts that the source never states. A figure the document does not contain did not come from the document | `scan_output_flags_figures_the_source_never_stated` |
| 7 | Wire the guard into `/extract` and `/ask`: preamble on the system prompt, every passage and document through `detect_injection` then `wrap_untrusted`. With `GUARD_ENABLED=false` the same document still hijacks the model | `injected_document_is_extracted_as_data_not_instructions`, `without_the_guard_the_same_document_hijacks_the_model`, `poisoned_passage_is_flagged_on_ask` |
| 8 | `check_limits(settings, session)`: raise `Blocked("kill_switch", ...)` → 503 with zero calls, or `Blocked("budget_exceeded", ...)` → 429 once today's spend has reached `DAILY_BUDGET_USD` | `kill_switch_stops_every_model_call`, `daily_budget_caps_the_blast_radius` |

`app.trace.spent_since()` gives the spend that the budget check reads. That is why step 1 comes
before step 8: the budget is enforced from your own trace data.

`make check WEEK=5` as often as you like. Red is the week's work, not a problem.

Your route changes what you are given: read `routes/start.md`, `routes/core.md` or `routes/pro.md`
in this folder (the hub shows yours). On start, tracing is given and the guard's docstrings name
each defence, with `routes/worked_example.py` solving a one-label, one-pattern version in full. On
core, the guard is implemented with faults planted but not located or counted. On pro, both files
are signatures only, and there is an extra constraint.

### If you get stuck

- **Rate-limited mid-exercise?** The free tiers are small. Put a second provider's key in `.env`
  and change `MODEL_PROVIDER`. Nothing this week is provider-specific, so the switch costs you
  nothing.
- **A test is failing and the message is not obvious?** Open the test. It is short, and it says
  exactly what it expected. `CHECKS.md` in this folder lists what each one wants in one line.
- **On `start`?** `routes/worked_example.py` fences a `<passage>` and strips one pattern, with the
  test that proves both. Read it beside your stub rather than instead of it.
- **Stuck for more than an hour?** An unblock call is available after a real attempt. Use it.

## Attack it and prove the defence (1 hour 30 minutes)

The attack set must fail before the defence and pass after it. You have already seen it fail, in
*Run it and watch*: two of four succeeded against the pass-through guard. Now:

```
uv run python scripts/attack.py               # must say 0 of 4 attacks succeeded
make check WEEK=5                             # runs it as a gate
```

That gate is one test: `attack_script_holds_with_the_guard_on`.

Then the part that matters: **attack a peer**. Take one document from `corpus/`, plant an
instruction in it that would change the extraction or the answer, and send it to another fellow
(their forwarded port or live URL). Record what happened in your reflection. When one lands on
you, add it to `eval/attacks.jsonl` and make it hold. The set grows every cohort.

Finally, read one cost off a trace without opening any code. `scripts/trace_report.py` is evidence
rather than a gate: run it and explain the step table to someone who does not code.

## Submit (30 minutes)

- `reflections/week-5.md`: Q1, Q1b, Q2, Q3, Q4 (what you contributed and how you checked it),
  Q5 (help you used), one trace explained step by step, and the attack log (what you sent, what
  came back, what you changed).
- PR `week-5 → main`. CI green, including the attack gate.

## Self-directed week

No session this week. The attack you plant in a peer's project and the one that lands on yours are
the feedback. Record both in the reflection; the Defence will ask about them. An unblock call is
available after a real attempt.

**Pass line, checked at the Defence:** CI green including the attack gate, one attack that got
through explained with the change it caused, and a cost read off a trace without opening code.

## Optional: self-test

`QUIZ.md` in this folder has a few questions on this week's concept, each with an explanation. On
the hub page they are interactive and scored, but the score lives only in your browser: it never
reaches the repository, your mentor or your route. Use it to find what to re-read.
