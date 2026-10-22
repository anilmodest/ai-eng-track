# Week 1 — Practice quiz

Practice, untimed and repeatable. Your score stays in this browser on your hub page and never
reaches the repository or your mentor. Use it to find what to re-read; the explanations are the
point, not the score. Your mentor also assigns a short weekly check on BridgePath: different
questions, some of them timed, taken once, and your mentor sees that score.

## Q1. The provider returns HTTP 400. What does a correct client do?
- [ ] Retry with exponential backoff until `MODEL_RETRY_ATTEMPTS` runs out — a 400 will fail the same way every time, and each attempt is billed
- [x] Fail at once with a typed error and no retry
- [ ] Hand the same request to the fallback provider — the fallback would receive the same bad request
> Why: 400 means we sent something wrong. Retrying costs money and hides our bug; a 429 or 5xx is the provider's problem and may clear on the next attempt. `ModelError.retryable` is the one thing the retry helper branches on.

## Q2. `MODEL_TIMEOUT_S=20`, `MODEL_RETRY_ATTEMPTS=3`, `MODEL_RETRY_BASE_DELAY_S=0.5`, and the provider never answers. Roughly how long until the caller gets its 504?
- [ ] 20 s, because a timeout is not retried — a timeout is retryable; a slow call may be fast next time
- [ ] About 63.5 s: three attempts plus waits of 0.5, 1 and 2 s — there is no wait after the last attempt
- [x] About 61.5 s: three attempts of 20 s, with waits of 0.5 s and 1 s between them
> Why: each attempt has its own timeout, and the waits double between attempts. Too long for an interactive call, acceptable for a queued batch: which of your endpoints should be queued is a week 0 answer.

## Q3. Same document, same provider, same model, same prompt version, second call. What must happen?
- [x] The stored `extractions` row comes back with `cached: true` and no provider call is made
- [ ] A fresh call, since the model is non-deterministic and the answer might improve — paying twice for the same work is what idempotency exists to prevent
- [ ] A fresh call if the first one is more than a day old — nothing in the key is time-based
> Why: the key is document, provider, model and prompt version. Change any of them and it is a different question; keep them all and it is the same answer, paid for once. That is requirement O7.

## Q4. The model returns text that is not JSON. What does `complete_structured` do?
- [ ] Raises `SchemaError` straight away — one repair attempt comes first
- [ ] Retries up to `MODEL_RETRY_ATTEMPTS` times with backoff, exactly as it would after a 429 — a malformed answer is not a transient failure
- [x] One more call with the validation error attached; if that fails too, `SchemaError`
> Why: one repair is cheap and often works; more would be paying for stubbornness. Still bad after the repair, the endpoint returns `502 schema_error`, never a 500, and the repair call's tokens are counted in the cost.

## Q5. Which line in `app/api/extract.py` breaks the "swappable provider" requirement?
- [ ] `client = get_model_client()` — that is the provider-agnostic entry point
- [x] `if client.name == "gemini": ...`
- [ ] `estimate_cost_usd(model_used, tokens_in, tokens_out)` — a price lookup by model name is data, not a branch
- [ ] `except ModelTimeout as e: return _error(504, ...)` — a typed failure every provider can raise
> Why: nothing in `app/api/` or `app/tools/` may name a provider, a model or an SDK. The gate runs your tests under `fake_a` and `fake_b`; code that only works against one of them named one somewhere.

## Q6. Which description of `get_customer` will a model use most reliably?
- [ ] "Gets customer data." — it says neither when to call the tool nor what comes back, so the model guesses between tools
- [x] "Look up one of this desk's customers by id and get back which product version and plan they are on."
- [ ] "Customer lookup tool. Calls `app.support.customer` and returns a JSON object built from the database row." — it describes the code, not the request; a model matches on the words a request uses
> Why: the description is the only thing the model knows about the tool. It has to say when to call it and what comes back, in the words a request will use. `scripts/tool_drill.py` measures exactly this: the same model, first-draft descriptions against yours.

## Q7. A model calls `get_customer` with `{"customer_id": "C-1001; DROP TABLE customer"}`. What should happen?
- [ ] The tool runs, and the database driver escapes the string so nothing harmful happens — a malformed id should never reach the tool, whatever the database would do with it
- [ ] The tool raises, and the agent's loop catches the exception — the model gets nothing it can act on
- [x] It fails validation, the tool never runs, and the model gets back an `error:` it can correct
> Why: constraints on the argument model reject anything that is not an id before the tool runs. `run_tool` turns the validation error into a sentence the model can read and correct. The gate checks that no malformed call reaches the tool.

## Q8. `get_customer` is asked for a customer who belongs to another desk. What should it return?
- [ ] That customer's version and plan, without the name — another desk's record is outside the scope, whatever fields are left out
- [x] Text starting `refused:` that says why and reveals nothing about the customer
- [ ] An `OutOfScope` exception, raised so the caller can tell a boundary from an outage — a model can recover from a sentence; it cannot recover from a stack trace
> Why: a refusal is a boundary doing its job, not an error. `OutOfScope` stays inside `app/support.py`; the tool turns it into words. And for the desk's own customers it returns version, account and plan, never seats or contact details.
