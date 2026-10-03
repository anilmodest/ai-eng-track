# Week 1 — Working with a model as a component

Area 2 of the track. About 9 hours including the session. Branch: `week-1`.

## What you are building

An endpoint that reads one uploaded document and returns **structured facts about it**: a title,
what kind of document it is, a short summary, a few key facts, and how confident the model is.

```
POST /documents/42/extract
  -> { "title": "Connection timeout", "doc_type": "report", "summary": "...",
       "key_facts": ["default is 15 seconds", "..."], "confidence": 0.82 }
```

Why the support desk cares: before anything can answer a question *from* a document, something
has to read it reliably. That is this week. Nothing you build here is clever — it is the part
that has to keep working at three in the morning when the provider is having a bad day.

## The constraint everything is built under

**Nothing in `app/api/extract.py` may name a provider, a model or an SDK.** Not `openai`, not
`gemini`, not `if provider == ...`. The model is a component you call through an interface, and
a component you can swap is the difference between a demo and a system.

The gate proves it by running your tests under two different fake providers. If your code worked
against only one of them, it named one of them somewhere.

This is also the week's interview answer. "How would you move off this provider?" is a real
question, and "edit one line of `.env`" is a real answer.

## Run it and watch (1 hour, change nothing)

```
uv run python explore/w1_01_same_prompt_x5.py
uv run python explore/w1_02_break_it.py
```

The first sends the **same prompt five times**. Note what changes between runs: wording, facts,
token counts, milliseconds. That variance is the thing you are building around.

The second breaks the provider on purpose — two 429s then success, then a 400, then a 50 ms
timeout — and shows the retry helper coping. Watch the backoff delays grow.

Both need a provider key: see the main `README.md`, *Model access*. Default is Gemini's free tier.

## Read it (1 hour, change nothing)

Read `app/llm/` in this order, and answer the three questions in `reflections/week-1.md`, Q1b:

1. **`client.py`** — the contract. What is the one thing a caller may branch on when a call fails?
2. **`registry.py`** — where does `MODEL_PROVIDER` get read, and what does `FallbackClient` do
   that `retry.py` does not?
3. **`providers/fake.py`** — why does this file exist, and what would break in CI without it?

Then open `tests/weeks/test_week1.py`. **It is the specification.** Every test name is one
behaviour, and the list below is the order to make them pass.

## Build it (5 hours)

Everything is in `app/api/extract.py`. The stub is there, the route is registered, the response
models are in `app/api/schemas.py`. Run `make next` any time to see where you are.

What the model must return:

| Field | Rule |
| --- | --- |
| `title` | 1–200 characters |
| `doc_type` | one of `invoice`, `contract`, `report`, `letter`, `other` |
| `summary` | at most 60 words |
| `key_facts` | 3 to 5 strings |
| `confidence` | 0.0 to 1.0 |

Build in this order. Each step is done when the tests named beside it go green.

| # | Build | Done when these pass |
| --- | --- | --- |
| 1 | Call the model, validate what comes back against `DocumentExtract`, return it | `extract_returns_schema_valid_json` |
| 2 | Invalid or malformed output: **one** repair attempt with the error attached. Still bad → `502 schema_error`. Never a 500 | `malformed_output_is_repaired_once`, `invalid_twice_is_a_typed_error_not_a_500` |
| 3 | Record `tokens_in`, `tokens_out`, `latency_ms` and list-price `cost_usd` (`app/llm/cost.py`) for **every** call, including a repair | `cost_and_latency_are_recorded` |
| 4 | Store the result in the `extractions` table. A second call for the same `document_id + provider + model + prompt_version` returns the stored row with `cached: true` and makes **zero** provider calls | `same_document_is_never_paid_for_twice` |
| 5 | `MODEL_TIMEOUT_S` per attempt → `504 provider_timeout`. Retry 429, 5xx and timeouts up to `MODEL_RETRY_ATTEMPTS` with exponential backoff. **Never** retry a 400 → `502 provider_error` on the first failure | `429_is_retried_then_succeeds`, `400_is_not_retried`, `hang_hits_the_timeout` |
| 6 | Send at most `MAX_INPUT_CHARS` of the document | `input_is_capped_to_the_context_budget` |

Steps 1 and 2 first is not a preference: nothing else can be tested until the endpoint returns
something.

Two words that appear above and are worth being precise about. **Idempotent** means calling it
twice has the same effect as calling it once — here, the same answer and no second bill.
**List-price cost** means what the provider's published rate card says this call cost; nobody is
reading your invoice, you are computing it from tokens so the number exists at all.

`make check WEEK=1` as often as you like. Red is the week's work, not a problem.

### If you get stuck

- **Rate-limited mid-exercise?** The free tiers are small. Put a second provider's key in `.env`
  and change `MODEL_PROVIDER`. That switch is the week's lesson, so doing it under duress is
  on-topic rather than a detour.
- **A test is failing and the message is not obvious?** Open the test. It is short, and it says
  exactly what it expected.
- **On `start`?** `routes/worked_example.py` solves a smaller version of this in full. Read it
  beside your stub rather than instead of it.
- **Stuck for more than an hour?** That is what the two unblock calls are for. Use one.

Your route changes what you are given: read `routes/start.md`, `routes/core.md` or
`routes/pro.md` in this folder. The hub shows which one is yours.

## Prove the swap (30 minutes)

With the gate green:

```
make live-check                      # your default provider
# change MODEL_PROVIDER and the key in .env, then:
make live-check                      # a different one
```

Paste both tables into `reflections/week-1.md`. Then:

```
git diff main -- app/
```

There must be no provider-specific code in it. A line like `import openai`, `if provider ==
"gemini":` or a hard-coded model name is a fail. If you find one, that is the finding of the
week — fix it and say so in your reflection.

## Submit (30 minutes)

- `reflections/week-1.md`: Q1 (the concept in your words), Q1b (the three reading questions),
  Q2 (what surprised you), Q3 (what you would change), Q4 (what you contributed and how you
  checked it), Q5 (help you used), and both live-check tables.
- Open a pull request `week-1 → main`. CI runs the gate. Fix anything red.
- Send the link to your mentor **24 hours** before the session, not at the start of it.

## Session 2: Direction (45 minutes, end of this week)

Your mentor reads the pull request and your reflection before the call, not during it.

| Min | What happens |
| --- | --- |
| 0–7 | You demo: extract a document, extract it again (zero calls), switch provider live |
| 7–20 | Your mentor probes the diff, typing questions as review comments on the pull request |
| 20–30 | Held-out documents you have not seen. Watch the behaviour, not the code |
| 30–40 | Route confirmed or corrected, in writing. The plan for weeks 2–6 set against what you did |
| 40–45 | Week 2's sentence, said back: *context is an attention budget* |

**This is the one point where your route can change.** After it, it holds.

**Pass line:** CI green under both fakes, the provider switch demonstrated, and a reason drawn
from your own work for treating the model as untrusted.

## Optional: self-test

`QUIZ.md` in this folder, with an explanation for every answer. On the hub page it is interactive.
The score stays in your browser: it never reaches the repository, your mentor or your route. Use
it to find what to re-read, not to measure yourself.
