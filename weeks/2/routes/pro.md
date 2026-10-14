# Week 2 on the pro route

**No helpers, one real constraint.** Hybrid search is core for everyone now; your constraint is
the budget around it. **The configuration you ship must keep search p95 under 150 ms on the full
corpus** (`p95_ms` in `scripts/retrieval_eval.py`, with `EMBED_PROVIDER=fastembed`) **and must not
lose more than 0.02 of hit rate against the best of the six.** If none of the six meets both, say
which you would trade and why, with the numbers. Quote both in your decision record.
