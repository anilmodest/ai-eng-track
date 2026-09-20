# Week 3 — Grounding and evaluation

Areas 5 and 8 of the track. About 10 hours. Branch: `week-3`. The two areas the source document
says decide most hiring outcomes are Retrieval (last week) and Evaluation (this week).

**Goal:** `POST /ask` answers only from retrieved passages, cites them, declines when it should,
and a versioned evaluation with four task-specific metrics blocks a bad merge in CI.

Read `CONCEPT.md` first. Then:

## Elaboration 1 — see it (1 hour, change nothing)

```
uv run python explore/w3_01_ask_without_a_net.py
```

One unanswerable question, one real passage, three rounds. Watch the model invent a penalty
clause in round A, hedge in round B, and decline in a testable way in round C.

Then run the evaluation on the given service with the fake model and the lexical embedder:

```
MODEL_PROVIDER=fake_a EMBED_PROVIDER=hash uv run python scripts/eval.py --thresholds eval/thresholds-ci.json
```

Read the table and the "worth a look" list. Every line there is a question you can go and ask.

## Elaboration 2 — read it (1 hour, change nothing)

Read, in this order, and answer the three questions in `reflections/week-3.md`, Q1b:

1. `app/api/ask.py` — there are two abstention gates. Which one costs money, and why is the
   order they run in not negotiable?
2. `scripts/eval.py` — why are there four metrics rather than one "accuracy"? Which one would
   drop first if the chunker regressed? Which if the prompt did?
3. `eval/thresholds.json` versus `eval/thresholds-ci.json` — why two? What does CI prove, and
   what does it not?

Then read `tests/weeks/test_week3.py`.

## Exercise — build and measure (5 hours)

`app/api/ask.py` is yours. The prompt, the schemas, retrieval and the eval script are given.

1. **Gate 1:** if the top retrieval score is below `RELEVANCE_THRESHOLD`, return
   `abstained: true` with a reason, and make **no** model call.
2. **Ask:** number the passages `[1]..[k]`, call the model for an `AskAnswer`
   (`answer`, `citations`, `grounded`) through `complete_structured`.
3. **Gate 2:** if the model says `grounded: false`, or the answer is empty, or no citation
   number is valid, return `abstained: true` with the reason `the passages do not contain the
   answer`.
4. **Citations:** map each valid `[n]` to the real chunk (id, document, filename, score, text).
5. **Failures:** a provider error is a `502 provider_error`, never an abstention.

Then the measurement, which is the point of the week:

```
uv run python scripts/eval.py                          # real model, real bar (thresholds.json)
EMBED_PROVIDER=fastembed uv run python scripts/eval.py # real embeddings too
```

Paste both tables into your reflection. If `answer_rate_answerable` is low while `hit_rate`
is high, you have seen the Week 2 lesson from the other side: fix retrieval, not the prompt.

Then grow the golden set: add at least 20 questions you would actually ask of these documents,
with expected facts, and at least 5 more that cannot be answered. Run again.

Finally, wire the gate: `make check WEEK=3` already runs `scripts/eval.py` against the CI
thresholds. Open a PR that deliberately breaks citations (return `[]`) and watch CI go red.
Revert it. That red run is evidence; link it in your reflection.

What your route adds:

| Route | Exercise |
| --- | --- |
| `start` | the above |
| `core` | plus judge calibration: score 15 answers yourself 1–5, run `scripts/eval.py --judge`, and report where the judge disagreed with you and why |
| `pro` | plus a `RELEVANCE_THRESHOLD` sweep (0.2 to 0.6) with the abstention/answer trade-off plotted in your reflection, and a written argument for the value you chose |

## Submit (30 minutes)

- `reflections/week-3.md`: Q1, Q1b, Q2, Q3, the eval tables, the red CI run, the golden set
  additions.
- PR `week-3 → main`. CI green.

## The session (35 minutes)

You demo: an answered question with citations, a declined one, and the eval table. Your mentor
asks five questions of their own and watches which gate fires. Then Week 4's sentence:
*prefer the simplest thing that works; multi-agent is a last resort.*

Pass line: CI green including the eval gate, abstention shown live, and you can explain from your
own numbers where a wrong answer would have come from.
