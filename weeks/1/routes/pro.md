# Week 1 on the pro route

**No helpers, one real constraint.** `retry.py`, `structured.py` and `cost.py` are signatures
only; you write them. The constraint: **a second provider must take over automatically when the
first is exhausted** (`MODEL_FALLBACK_PROVIDER`), proven by a live-check where the primary key is
deliberately wrong, **and** the p95 latency of `make live-check` across three runs must stay
under 3 seconds with retries on. Put both numbers in the reflection.
