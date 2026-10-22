# Week 1 on the pro route

**No helpers, one real constraint.** `retry.py`, `structured.py` and `cost.py` are signatures
only; you write them. The constraint: **a second provider must take over automatically when the
first is exhausted** (`MODEL_FALLBACK_PROVIDER`), proven by the failure drill's fallback probe, which
spends the primary's quota (every call answers 429, however often it is retried) and needs the
second provider to answer, **and** the p95 latency in your failure drill must stay under 3 seconds
with retries on. Both numbers are in `evidence/week-1.json`; quote them in your decision record.

Then make the primary key deliberately wrong and run `make live-check`, which goes through the
service's own client: the provider line shows both names. `FallbackClient` hands a 401,
402 or 403 to the second provider, because a key that does not work will not start working on a
retry; it does not hand over a 400, because the same bad request would fail there too. Some
providers answer a wrong key with 400. Find out what yours does, and say in the decision record
whether your fallback covers it.

Recommended: make your second provider a local model (Ollama), and say in the decision record
what it cost you in latency and what it saved in money.
