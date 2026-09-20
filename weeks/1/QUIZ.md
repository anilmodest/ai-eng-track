# Week 1 — Quiz

Optional, repeatable, and yours: the score is kept in your own browser on the hub page and
never reaches the repo, the mentor or the route. Use it to find out what you have not understood
yet; then go and read that part again. The explanations are the point, not the score.

## Q1. The provider returns HTTP 400. What does a correct client do?
- [ ] Retry with exponential backoff — a 400 will fail the same way every time
- [x] Fail at once with a typed error and no retry
- [ ] Switch to the fallback provider — the fallback would receive the same bad request
> Why: 400 means *we* sent something wrong. Retrying costs money and hides our bug; a 429 or 5xx is the provider's problem and may clear on the next attempt. `ModelError.retryable` is the one thing the retry helper branches on.

## Q2. `MODEL_TIMEOUT_S=20`, `MODEL_RETRY_ATTEMPTS=3`, base delay 0.5 s. Worst case, how long can one extract request take?
- [ ] 20 s — that is one attempt
- [x] About 61 s: 3 × 20 s plus 0.5 s and 1 s of backoff
- [ ] 60 s exactly — the backoff waits are added on top
> Why: each attempt has its own timeout, and the waits sit between them. Too long for an interactive call; fine for a queued batch. Which of your endpoints should be async is a Week 0 answer.

## Q3. Same document, same model, same prompt version, second call. What must happen?
- [x] The stored `extractions` row is returned with `cached: true` and no provider call is made
- [ ] A fresh call, because the model is non-deterministic and the answer might improve — paying twice for the same work is the thing idempotency exists to prevent
- [ ] A fresh call only if the first one was more than a day ago — nothing in the key is time-based
> Why: the idempotency key is `(document_id, provider, model, prompt_version)`. Change any of them and it is a different question; keep them all the same and it is the same answer, paid for once.

## Q4. You edit `extract_v1.md` to improve the prompt but leave `PROMPT_VERSION` as it is. What goes wrong?
- [ ] Nothing; the prompt file is read on every call — it is, but the cache key does not know it changed
- [x] Every previously extracted document keeps returning the old answer from the cache
- [ ] The tests fail — they do not; they never compare prompt text
> Why: the prompt is part of the idempotency key only through its version string. A prompt change without a version bump is a silent cache poisoning of your own making.

## Q5. The model returns text that is not JSON. What does `complete_structured` do?
- [ ] Raises immediately — one repair attempt comes first
- [x] Makes one more call with the validation error attached, then raises `SchemaError` if that also fails
- [ ] Retries up to three times, like a 429 — a malformed answer is not a transient failure
> Why: one repair is cheap and often works; three would be paying for stubbornness. Two failures with the error attached means a human should look. And the repair call's tokens are still billed and recorded.

## Q6. Which line in `extract.py` would be wrong on the "swappable" requirement?
- [ ] `client = get_model_client()` — that is the provider-agnostic entry point
- [x] `if client.name == "gemini": ...` — the endpoint must never branch on the provider
- [ ] `estimate_cost_usd(model_used, tokens_in, tokens_out)` — cost lookup by model name is data, not a branch
> Why: the gate runs your tests under `fake_a` and `fake_b`; a provider-specific branch is exactly what that catches. The provider is configuration. Nothing above `registry.py` may know its name.

## Q7. GitHub Models was retired while this template was being built. What changed in the repo? (stretch: core/pro)
- [x] One entry in `registry.py` and two lines in `.env.example`; no service code
- [ ] `extract.py` and every caller of the model — that is what would have changed had the model name lived in the service
- [ ] The tests — they run against the fake providers and never knew
> Why: this happened. The concept page tells the story. A provider retirement that costs two config lines is the payoff of keeping the model behind one interface.
