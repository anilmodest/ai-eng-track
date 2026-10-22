# Week 1 — The model as a component, and its first tools

Areas 2 and 6. 8 to 10 hours. Session 2 (Direction) at the end of this week. Branch: `week-1`.

> **The one lesson.** A model is an unreliable dependency. Its output must fit a schema, and its
> tools must be described exactly, or it calls them wrongly.

## The gap it closes

Most people's first instinct is to treat a model like a function: call it, get the answer. It is
not. It is a service someone else owns, and it behaves like the least reliable dependency in your
system. Someone who has only used a chat window writes code that has no timeout, retries a
permanent error forever, has no idea what a call costs, and hands the model a vague tool
description and is surprised when it calls the tool with the wrong arguments. This week is the
difference between someone who has used a model and someone who can put one in a system.

## What you are building

Two things, on the service you already have.

**An endpoint that reads one document and returns structured facts about it**: a title, the kind
of document, a short summary, a few key facts, and how confident the model is.

```
POST /documents/42/extract
  -> { "title": "Connection timeout", "doc_type": "report", "summary": "...",
       "key_facts": ["default is 15 seconds", "..."], "confidence": 0.82 }
```

**The agent's first two tools**, which every later week builds on: `get_customer` (which version,
which account, which plan) and `get_ticket` (what a ticket says and where it stands). They read
the desk's own data, loaded in week 0 (`support/`).

## The constraint everything is built under

**Nothing in `app/api/` or `app/tools/` may name a provider, a model or an SDK.** Not `openai`,
not `gemini`, not `if provider == ...`. The gate runs every test under two different fake
providers; code that worked against only one of them named one somewhere. "How would you move off
this provider?" is a real interview question, and "edit one line of `.env`" is a real answer.

## Read (1 hour)

`CONCEPT.md` first. Then `app/llm/` in this order, and answer the three questions in
`reflections/week-1.md`, Q1b:

1. **`client.py`**: the contract. What is the one thing a caller may branch on when a call fails?
2. **`registry.py`**: where is `MODEL_PROVIDER` read, and what does `FallbackClient` do that
   `retry.py` does not?
3. **`providers/fake.py`**: why does this file exist, and what would break in CI without it?

Then `app/tools/base.py`: the one door every tool call goes through.

## See it (1 hour, change nothing)

```
uv run python explore/w1_01_same_prompt_x5.py     # the same prompt, five answers, five costs
uv run python explore/w1_02_break_it.py           # 429, 429, ok; a 400; a timeout
uv run python explore/w1_03_vague_tools.py        # two badly described tools, wrong calls
```

All three need a provider key (main `README.md`, *Model access*). Note what varies, what the
retry helper does with each failure, and which wrong tool calls a better description would have
prevented.

## Build (5 to 7 hours)

Every item is **core** (needed for the lesson, checked by the gate) or **stretch** (worth doing,
shown to your mentor, never blocking). Use any assistant you like and log it as you go in
`ai-use/week-1.yml`. `make next` tells you where you are; `make check WEEK=1` as often as you like.
Red is the week's work, not a problem.

### Core 1: the extract endpoint (`app/api/extract.py`)

What the model must return, validated by `DocumentExtract`:

| Field | Rule |
| --- | --- |
| `title` | 1–200 characters |
| `doc_type` | one of `invoice`, `contract`, `report`, `letter`, `other` |
| `summary` | at most 60 words |
| `key_facts` | 3 to 5 strings |
| `confidence` | 0.0 to 1.0 |

What must hold:

- **Output fits the schema, or fails loudly.** Invalid or malformed output gets **one** repair
  attempt with the validation error attached. Still bad: `502 schema_error`. Never a 500.
- **Only failures worth retrying are retried.** 429, 5xx and timeouts, up to
  `MODEL_RETRY_ATTEMPTS`, with growing waits. A 400 never: `502 provider_error` at once.
- **Every attempt has a timeout** (`MODEL_TIMEOUT_S`): `504 provider_timeout`.
- **The same work is never paid for twice.** The same document, provider, model and prompt version
  returns the stored result with `cached: true` and makes no provider call.
- **Every call is costed.** Tokens in and out, latency and list-price cost (`app/llm/cost.py`),
  repairs included, stored with the result.
- **At most `MAX_INPUT_CHARS` of the document is sent.**

Two words worth being precise about. **Idempotent**: calling it twice has the same effect as
calling it once; here, the same answer and no second bill. **List-price cost**: what the
provider's published rate card says the call cost, computed from tokens so the number exists.

### Core 2: two tools you design (`app/tools/desk.py`)

What is fixed: the names `get_customer` and `get_ticket`, the one argument each takes
(`customer_id`, `ticket_id`), and the data, read only through `app/support.py`.

What is yours:

- **The descriptions.** Of each tool and of its argument: when a model should call it and what it
  gets back, in the words a request uses. The description is a prompt.
- **The constraints.** A malformed id (`"1001"`, `""`, `"C-1001; DROP TABLE"`, a number) fails
  validation and never reaches the tool. The model gets back an error it can act on.
- **What each tool returns.** What the desk needs to work on the request, and nothing else: no
  seat counts, no contact details.
- **Every refusal, in words.** A customer or ticket on another desk, or one that does not exist,
  is `refused: <why>`, not an exception. A model can recover from a sentence; it cannot recover
  from a stack trace.

### Core 3: measure it on a real model (`make evidence WEEK=1`)

With the gate green, commit, then run `make evidence WEEK=1`. It runs three measurements on your
real model and writes `evidence/week-1.json`:

| Measurement | Script | What it tells you |
| --- | --- | --- |
| `schema_drill` | `scripts/schema_drill.py` | How often plain "reply in JSON" breaks the schema, against schema-enforced output with one repair. The case for Pydantic, as your number |
| `tool_drill` | `scripts/tool_drill.py` | Twenty requests, run with first-draft descriptions and with yours: right tool, valid arguments, right id. The rise is caused by nothing but your descriptions |
| `failure_drill` | `scripts/failure_drill.py` | Your failure policy on **two** providers: retries, p50 and p95 latency, cost per call, and two probes (an impossible timeout, a model that does not exist) |

Get keys from two providers and set the second as `MODEL_FALLBACK_PROVIDER`: the failure drill
needs both, and so will week 4, when the agent becomes the hungriest thing you run.

### Stretch

- **A local model as your second provider** (Ollama, `MODEL_FALLBACK_PROVIDER=ollama`). Several
  employers screen for it; a 2-CPU Codespace runs only small models, slowly. Recommended on pro.
- **A cost ceiling per call**: refuse, with a typed error, any call whose input would cost more
  than a limit you choose.

## Decide

**Your failure policy**: which errors retry, how many times, the timeout, and the most you will
pay for one call, read off the failure drill on your two providers. **And the model you build
on**, checked against the minimum standard in [`docs/models.md`](../../docs/models.md), and
written into `model.json` at the repository's root: the hidden evaluation's model tier runs on it.

Write it in `decisions/week-1.md` (from `DECISION_TEMPLATE.md`): the decision, the options you
measured, the evidence as keys into your evidence file (for example
`- failure_drill.providers.gemini.p95_ms = 2140`), the option you rejected and why, and the risk
you accepted.

## What proves it

1. **The gate** (`make check WEEK=1`, also on your pull request): the endpoint's behaviour under
   scripted failures on two fake providers, your tools' schemas, scope, validation and refusals,
   the three measurements running, and your records. `CHECKS.md` lists every check.
2. **The evidence file**, from a real model, tied to the commit.
3. **The decision record**, whose numbers the gate checks against the evidence file.

Plus one result that has to be demonstrably true: the provider swapped with zero code difference
(`git diff main -- app/` names no provider), the second identical request making zero provider
calls, and a measured rise in correct tool calls caused by your own descriptions.

**Anti-goal: do not tune the answer prompt.** This week is the plumbing and the tool contracts. A
week spent improving wording has missed the point.

### If you get stuck

- **Rate-limited mid-exercise?** Switch `MODEL_PROVIDER` to your second key. That switch is the
  week's lesson, so doing it under duress is on-topic rather than a detour.
- **A test is failing and the message is not obvious?** Open the test. It is short, and it says
  what must hold.
<!-- route:start -->
- **On `start`?** `routes/worked_example.py` solves a smaller version of the endpoint in full, and
  `routes/worked_example_tool.py` designs one smaller tool in full. Read them beside your stubs
  rather than instead of them.
<!-- /route -->
- **Stuck for more than an hour?** That is what the two unblock calls are for. Use one.

Your route changes what this week gives you: the page in `routes/` in this folder says how.

## Submit

1. `make check WEEK=1` green, then commit, then `make evidence WEEK=1`, and commit the evidence.
2. `decisions/week-1.md`, `ai-use/week-1.yml` and `reflections/week-1.md` (Q1 to Q5).
3. Open a pull request `week-1 → main` and send the link to your mentor **24 hours** before the
   session.

## Session 2: Direction (45 minutes, end of this week)

Your mentor reads a one-page brief built from your pull request beforehand (about ten minutes),
not your diff during the call.

| Min | What happens |
| --- | --- |
| 0–8 | You demo: extract a document, extract it again (zero calls), switch provider live |
| 8–25 | Tools closed. Your mentor probes your decision record and your tool schemas, typing questions on the pull request |
| 25–37 | Assisted. Unseen requests from the programme; you fix one failure with your own assistant while your mentor watches how you steer it and what you check |
| 37–42 | Route confirmed, or a correction recommended. The plan for weeks 2–6 |
| 42–45 | Week 2's sentence, said back: *the same model gives a different answer when you give it different context* |

**This is the one point where your route can change.** After it, it holds.

## Quizzes: practice here, a short check on BridgePath

`QUIZ.md` in this folder is the practice quiz, with an explanation for every answer. On the hub page
it is interactive, untimed and repeatable, and the score stays in your browser: it never reaches the
repository, your mentor or your route. Use it to find what to re-read.

Your mentor also assigns this week's check on BridgePath. It has different questions, some of them
timed, and you take it once; your mentor sees that score. It asks about what you built and measured
this week, so the work is the preparation.
