# Week 3 — What the gate checks

`make check WEEK=3` runs lint, format, strict types, then Weeks 0–3 tests under `fake_a` and
`fake_b` with `EMBED_PROVIDER=hash`. Two of the Week 3 tests run `scripts/eval.py` itself.

| Test | Expects |
| --- | --- |
| `answers_with_citations_that_resolve` | an answerable question returns an answer, a citation naming the right file and a real chunk id, and non-zero usage |
| `abstains_below_threshold_without_calling_the_model` | nonsense scores under the threshold: abstained, reason mentions the threshold, **zero** model calls, zero cost |
| `abstains_when_the_model_says_not_grounded` | `grounded: false` from the model becomes an abstention with no answer and no citations |
| `unanswerable_question_is_declined` | a real-looking question the corpus cannot answer is declined |
| `citation_numbers_outside_the_context_are_dropped` | with `k=1` only `[1]` survives |
| `provider_failure_is_not_an_abstention` | a 400 from the provider is a `502 provider_error` |
| `eval_gate_passes_on_ci_thresholds` | `scripts/eval.py --thresholds eval/thresholds-ci.json` exits 0 |
| `eval_gate_blocks_when_a_threshold_is_not_met` | the same with `--min-hit 1.01` exits 1 and prints `GATE FAIL` |

Two threshold files, on purpose:

- `eval/thresholds-ci.json` — what CI can hold with the fake model and lexical embedder. It
  proves the pipeline and catches regressions in retrieval, grounding and citations.
- `eval/thresholds.json` — the real bar, met with a real model. You run it and paste the table.

`reports/eval.json` holds every row; the progress page shows the four metrics from your last run.
