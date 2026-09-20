# Week 1 — Working with a model as a component

Area 2 of the track. About 9–10 hours. Branch: `week-1`.

**Goal:** add one model-backed endpoint that returns schema-valid JSON, survives the provider
misbehaving, never pays twice for the same work, and moves to a different provider by editing
`.env` alone.

Read `CONCEPT.md` first. Then:

## Elaboration 1 — see it (1 hour, change nothing)

```
uv run python explore/w1_01_same_prompt_x5.py
uv run python explore/w1_02_break_it.py
```

The first sends one prompt five times. Note what varies: wording, facts, tokens, milliseconds.
The second breaks the dependency on purpose (429, 429, ok; then a 400; then a 50 ms timeout against
your real provider) and shows the retry helper coping. Watch the backoff delays.

Both scripts need a provider and a key: see `README.md`, Model access. The default is Gemini's
free tier. If it rate-limits you, switch to `groq` or `openrouter`; that switch is the week's lesson.

## Elaboration 2 — read it (1 hour, change nothing)

Read `app/llm/` in this order and answer the three questions in `reflections/week-1.md`, Q1b:

1. `client.py` — the contract. What is the one thing a caller may branch on when a call fails?
2. `registry.py` — where does `MODEL_PROVIDER` get read, and what does `FallbackClient` do that
   `retry.py` does not?
3. `providers/fake.py` — why does this file exist, and what would break in CI without it?

Then read `tests/weeks/test_week1.py`. It is the contract for your endpoint. Every test there is a
sentence from `CONCEPT.md` turned into code.

## Exercise — build it (4–5 hours)

Implement `POST /documents/{id}/extract` in `app/api/extract.py`. The stub is there; the route is
registered; the response models exist in `app/api/schemas.py`.

The endpoint returns an `ExtractOut` whose `extract` is a `DocumentExtract`:

| Field | Rule |
| --- | --- |
| `title` | 1–200 characters |
| `doc_type` | one of `invoice`, `contract`, `report`, `letter`, `other` |
| `summary` | at most 60 words |
| `key_facts` | 3 to 5 strings |
| `confidence` | 0.0 to 1.0 |

Requirements (each one is a test):

1. **Schema.** Validate the model's output. Malformed or invalid → one repair attempt with the
   error attached → then a `502` with `{"error": "schema_error"}`. Never a 500.
2. **Timeouts and retries.** `MODEL_TIMEOUT_S` per attempt → `504 provider_timeout`.
   Retry 429/5xx/timeout up to `MODEL_RETRY_ATTEMPTS` with exponential backoff. Never retry 400 →
   `502 provider_error` on the first failure.
3. **Idempotency.** Store the result in the `extractions` table with `document_id, provider,
   model, prompt_version, tokens_in, tokens_out, latency_ms, cost_usd`. A second call for the same
   `document_id + provider + model + prompt_version` returns the stored row with `cached: true`
   and makes **zero** provider calls.
4. **Cost and latency.** Record tokens, latency and list-price cost (`app/llm/cost.py`) for every
   call, including a repair call if there was one.
5. **Budget.** Send at most `MAX_INPUT_CHARS` of the document.
6. **Swappable.** Nothing in `app/api/extract.py` may name a provider, a model or an SDK. The
   gate runs your tests under two different fake providers to prove it.

What your route gives you:

| Route | Given | You build |
| --- | --- | --- |
| `start` | `retry.py`, `structured.py`, `cost.py` all working | the endpoint, the cache lookup, the `Extraction` row |
| `core` | `retry.py` and `structured.py` are stubs | the above, plus retry with backoff and the validate–repair loop |
| `pro` | as core, plus `cost.py` is a stub | the above, plus routing by input size, `MODEL_FALLBACK_PROVIDER`, and a streaming variant |

Run the gate as often as you like: `make check WEEK=1`.

## Switch (30 minutes)

With the gate green, run `make live-check` against your default provider. Paste the table into
`reflections/week-1.md`. Change `MODEL_PROVIDER` (and the key) in `.env`. Restart. Run it again. Paste
that table too.

Then: `git diff main -- app/` must contain no provider-specific code. If it does, that is the
finding of the week; fix it.

## Submit (30 minutes)

- `reflections/week-1.md`: Q1 (concept in your words), Q1b (three reading questions), Q2 (what
  surprised you), Q3 (what you would change), both live-check tables.
- Open a PR `week-1 → main`. CI runs the gate. Fix anything red.
- Send the PR link to your mentor 24 hours before the session.

## The session (35 minutes)

You demo: extract a document, extract it again (zero calls), switch provider live. Your mentor
probes the diff and runs three documents you have not seen. Then the Week 2 sentence.

Pass line: CI green, provider switch shown, and you can explain, unprompted, why the model is
treated as untrusted.

## Optional: self-test

`QUIZ.md` in this folder has a few questions on this week's concept, each with an explanation. On the hub page they are interactive and scored, but the score lives only in your browser: it never reaches the repo, your mentor or your route. Use it to find what to re-read.
