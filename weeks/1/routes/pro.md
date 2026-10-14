# Week 1 on the pro route

**No helpers, one real constraint.** `retry.py`, `structured.py` and `cost.py` are signatures
only; you write them. The constraint: **a second provider must take over automatically when the
first is exhausted** (`MODEL_FALLBACK_PROVIDER`), proven by a failure drill where the primary key is
deliberately wrong, **and** the p95 latency in your failure drill must stay under 3 seconds with
retries on. Both numbers are in `evidence/week-1.json`; quote them in your decision record.

Recommended: make your second provider a local model (Ollama), and say in the decision record
what it cost you in latency and what it saved in money.
