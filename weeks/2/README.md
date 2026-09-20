# Week 2 — Context engineering and retrieval

Areas 3 and 4 of the track. About 9–10 hours. Branch: `week-2`.

**Goal:** your service can index the corpus, search it, and you can say which chunking strategy
is right for it **with a number**. You have seen, and paid for, the attention budget.

Read `CONCEPT.md` first. Then:

## Elaboration 1 — see it (1 hour, change nothing)

```
uv run python explore/w2_01_chunk_and_look.py
uv run python explore/w2_02_lost_in_the_middle.py --trials 3 --filler 40
uv run python explore/w2_02_lost_in_the_middle.py --trials 3 --filler 5
```

The first cuts one contract four ways. Find the table row cut in half, and the clause number
separated from its clause. The second buries one fact in 40 paragraphs of noise and asks for it,
then does the same with 5. Strong models often find the fact at every position at this size; the
cost column moves anyway. On `core` and `pro`, try `--filler 200` and watch both.

## Elaboration 2 — read it (1 hour, change nothing)

Read, in this order, and answer the three questions in `reflections/week-2.md`, Q1b:

1. `app/retrieval/chunkers.py` — which strategy would cut the invoice table? Why does
   `by_sentence` split "3. Fees." from its clause?
2. `app/retrieval/embed.py` — what does the `hash` embedder know about meaning? Why does the
   repo have it at all?
3. `app/retrieval/store.py` — search is a numpy scan. At what corpus size would you replace it,
   and with what property must the replacement keep the `search()` interface?

Then read `tests/weeks/test_week2.py`: the contract for this week.

## Exercise — build and measure (4–5 hours)

Two files are yours this week. The rest is given.

1. **`app/retrieval/metrics.py`** — implement `precision_at_k`, `recall_at_k`, `reciprocal_rank`
   and `evaluate`. The docstrings say what each means; the tests say what they return.
2. **`app/retrieval/chunkers.py::by_heading`** — one chunk per markdown section, heading kept
   with its body; sections over `max_chars` fall back to paragraphs that each still carry the
   heading. A document with no headings behaves like `by_paragraph`.

Then measure:

```
uv run python scripts/retrieval_eval.py                 # EMBED_PROVIDER=hash: the mechanics
EMBED_PROVIDER=fastembed uv run python scripts/retrieval_eval.py   # real embeddings (130 MB, once)
```

Read the two tables side by side. Pick a strategy. Set `CHUNK_STRATEGY` in `.env`. Put both tables
and one sentence of reasoning in `reflections/week-2.md`.

What your route adds:

| Route | Exercise |
| --- | --- |
| `start` | the two files above, and the measurement |
| `core` | plus hybrid search: combine lexical and semantic scores (reciprocal rank fusion is enough) and show the metric that improved |
| `pro` | plus a reranker over the top 20 (a cross-encoder via fastembed, or the model itself as judge) and a written cost/latency trade-off |

Run the gate as often as you like: `make check WEEK=2`.

## Submit (30 minutes)

- `reflections/week-2.md`: Q1, Q1b, Q2, Q3, the two eval tables, the strategy you chose and why.
- PR `week-2 → main`. CI green. Link to your mentor 24 hours before the session.

## The session (35 minutes)

You demo: index, search, and the eval table. Your mentor asks for the number that chose your
strategy, then runs a few questions the eval set does not contain. Then Week 3's sentence:
*a system that always answers is worse than one that sometimes declines.*

Pass line: CI green, a strategy chosen with a number, and you can explain a precision/recall
trade-off you saw in your own table.
