# Week 2 — Context engineering and retrieval

Areas 3 and 4 of the track. About 9–10 hours. No session this week. Branch: `week-2`.

## What you are building

Search over the corpus that can be restricted to **one version of the manual**, plus the number
that says which way of cutting documents is right for this corpus.

```
POST /index?strategy=heading
  -> { "strategy": "heading", "embedder": "hash", "chunks": 28 }

GET  /search?q=where+is+the+connection+timeout+set&k=1&strategy=heading
  -> [ { "filename": "manual-v2-connection-timeout.md", "version": "v2", "ordinal": 0,
         "text": "## Connection timeout ...", "score": 0.64 } ]

GET  /search?q=where+is+the+connection+timeout+set&k=1&strategy=heading&version=v3
  -> [ { "filename": "manual-v3-connection-timeout.md", "version": "v3", ... } ]
```

Look at the first search. The question is about where the setting lives now, and the top hit is
the **version 2** page: the two pages are worded almost identically, and it scores 0.64. The
second search is the same question with the version the customer runs, and making that one return
nothing from version 2 is this week's exercise.

Why the support desk cares: the manual exists twice over, versions 2 and 3 worded almost
identically. A version 2 page returned for a version 3 question reads perfectly and is wrong, and
a wrong-version answer is worse than no answer.

Two words used throughout. **Chunking** is cutting a document into retrievable pieces.
**Embedding** is turning a piece of text into a vector of numbers, so that "nearest vector" can
stand in for "closest in meaning".

## The constraint everything is built under

**A question asked about version 3 may never be answered out of a version 2 page.** That is
output requirement O1, and no amount of model quality fixes it. The two pages are near-identical
strings, so similarity cannot tell them apart. Only a filter on metadata can.

What makes it hard is *where* the filter runs. It has to run **before** ranking. Filter afterwards
and the version 2 chunks take the top k slots, you drop them, and you hand back fewer hits than
you were asked for. Losing recall quietly is still losing.

Behind that sits the week's sentence: **the context window is an attention budget, not a storage
limit.** Everything you put in the window competes for attention with everything else, so past a
point more context buys more noise, more latency and more money for the same answer.

Both are interview answers. "How do you know your retrieval works?" wants a metric from your own
table. "How do you keep the wrong document out?" wants a filter that runs in the index.

## Run it and watch (1 hour, change nothing)

```
uv run python explore/w2_01_chunk_and_look.py
uv run python explore/w2_02_lost_in_the_middle.py --trials 3 --filler 40
uv run python explore/w2_02_lost_in_the_middle.py --trials 3 --filler 5
```

The first cuts one contract four ways. Find the table row cut in half, and the clause number
separated from its clause.

The second buries one fact in 40 paragraphs of noise and asks for it, then does the same with 5.
Strong models often find the fact at every position at this size; the cost column moves anyway.
On `core` and `pro`, try `--filler 200` and watch both.

Then see the two problems this week exists to solve:

```
uv run python scripts/baseline.py            # does the model already know these answers?
uv run python scripts/version_check.py       # what similarity alone returns
```

The first proves retrieval has work to do. The manual describes an invented product, so a model
answering from training is a signal that something is wrong with your corpus, not a convenience.
The second asks five version 3 questions with no filter and shows you how often the **version 2**
page wins — it is worded almost identically, and it scores higher.

Both need a provider key: see the main `README.md`, *Model access*. Default is Gemini's free tier.

## Read it (1.5 hours, change nothing)

Read `CONCEPT.md` in this folder first, about 20 minutes. Copy `REFLECTION_TEMPLATE.md` to
`reflections/week-2.md` and write the week's sentence in your own words in Q1, before you touch
code.

Then read these in this order, and answer the three questions in `reflections/week-2.md`, Q1b:

1. **`app/retrieval/chunkers.py`** — which strategy would cut the invoice table? Why does
   `by_sentence` split "3. Fees." from its clause?
2. **`app/retrieval/embed.py`** — what does the `hash` embedder know about meaning? Why does the
   repo have it at all?
3. **`app/retrieval/store.py` and `app/retrieval/vector_store.py`** — three stores behind one
   interface. Which one are you running? What does `VECTOR_STORE=sqlite_vec` buy over `numpy`,
   and what does the partition key change about *where* the version filter happens?

Then open `tests/weeks/test_week2.py`. **It is the specification.** Every test name is one
behaviour, and the table below is the order to make them pass.

## Build it (4–5 hours)

Four pieces are yours this week. The rest is given. Run `make next` any time to see where you are.

The four numbers step 1 produces, since nothing later means anything without them:

| Metric | What it means |
| --- | --- |
| precision@k | of the first k hits, the fraction that were relevant |
| recall@k | of everything relevant in the corpus, the fraction the first k hits found |
| MRR | mean reciprocal rank: 1 divided by the rank of the first relevant hit, averaged over queries |
| hit rate | the fraction of queries with at least one relevant hit in the top k |

Build in this order. Each step is done when the tests named beside it go green.

| # | Build | Done when these pass |
| --- | --- | --- |
| 1 | `app/retrieval/metrics.py`: `precision_at_k`, `recall_at_k`, `reciprocal_rank` and `evaluate`. Precision divides by `k`, not by how many hits came back. `evaluate` averages per query, so a query with two relevant hits counts once towards hit rate | `precision_recall_mrr_on_a_toy_example`, `evaluate_averages_per_query`, `precision_uses_k_not_the_number_of_hits` |
| 2 | `app/retrieval/chunkers.py::by_heading`: one chunk per markdown section, heading kept with its body. A section over `max_chars` falls back to paragraphs that each still carry the heading. A document with no headings behaves like `by_paragraph` | `heading_chunker_keeps_heading_with_its_body` |
| 3 | `app/retrieval/context.py::select_and_compress`: a relevance floor relative to the best score, a shared-term check against the question, sentence-level trimming inside a kept passage, and a character budget it never exceeds | `select_and_compress_keeps_the_passage_that_answers`, `select_and_compress_drops_unrelated_passages`, `select_and_compress_trims_inside_a_passage`, `select_and_compress_respects_the_budget` |
| 4 | `app/retrieval/versions.py::applicable_versions`: the version filter, and output requirement O1. One function, called by every store before ranking. Two things are easy to get wrong, and both are in the docstring: what `None` means, and what happens to the pages that carry no version at all | `a_version_3_question_returns_no_version_2_material`, `the_filter_runs_before_ranking_not_after`, `pages_with_no_version_are_returned_for_every_version` |

That order is not a preference. You cannot measure a chunking strategy before the metrics that
score it exist, and step 4's tests search with `strategy=heading`, so step 2 has to be right first.

Ten more tests are green on the given code, and your four pieces must keep them that way:
`fixed_cuts_sentences_in_half`, `sentence_chunker_never_cuts_mid_sentence`,
`paragraph_chunker_keeps_a_table_row_whole`, `unknown_strategy_is_refused`,
`the_version_is_read_from_the_filename`, `similarity_alone_returns_the_wrong_version`,
`index_then_search_finds_the_right_document`, `reindex_replaces_rather_than_duplicates`,
`search_respects_k_and_strategy` and `unknown_strategy_on_index_is_400`. On the `core` route they
are not a free pass: the faults are planted in code you were given, so a red one there is the
finding.

Before step 3, see the damage it repairs:

```
uv run python scripts/degrade_repair.py
```

It answers the 30 queries three ways: the top 3 chunks (works), *every* chunk stuffed into the
context (degraded: watch the tokens, and with a real model the answers), and the top 10 passed
through your `select_and_compress`, which as shipped returns everything. Run it again after step
3. The repaired row should hold nearly all of the stuffed row's hits at a fraction of its tokens.

After step 4, run `scripts/version_check.py` again. The filtered column should be clean.

`make check WEEK=2` as often as you like. Red is the week's work, not a problem.

### If you get stuck

- **Rate-limited mid-exercise?** The free tiers are small. Put a second provider's key in `.env`
  and change `MODEL_PROVIDER`. Only `baseline.py` and `degrade_repair.py` need a real model; the
  gate runs on a fake provider with `EMBED_PROVIDER=hash`, so it never costs you a request.
- **A test is failing and the message is not obvious?** Open the test. It is short, and it says
  exactly what it expected.
- **On `start`?** `routes/worked_example.py` implements a sibling metric (mean average precision)
  and a sibling chunker (`by_lines`) in full. Run it, then read it beside your stub rather than
  instead of it. Copy the shape, not the code.
- **Stuck for more than an hour?** That is what the unblock call is for. Use it.

Your route changes what this week gives you: read `routes/start.md`, `routes/core.md` or
`routes/pro.md` in this folder. The hub shows which one is yours.

## Measure it and choose (2 hours)

With the gate green:

```
uv run python scripts/retrieval_eval.py                 # EMBED_PROVIDER=hash: the mechanics
EMBED_PROVIDER=fastembed uv run python scripts/retrieval_eval.py   # real embeddings (130 MB, once)
```

Read the two tables side by side. Pick a strategy. Set `CHUNK_STRATEGY` in `.env`. Put both tables
and one sentence of reasoning in `reflections/week-2.md`.

### Where the vectors live

The service runs on **sqlite-vec** by default: the index is a virtual table inside the same SQLite
file, and the version is its *partition key* — the field the index is physically split by — so a
version 3 search does not scan version 2 vectors at all. Two other stores sit behind the same
interface. Run the same evaluation against each and put the numbers in your reflection:

```
VECTOR_STORE=numpy      uv run python scripts/retrieval_eval.py   # a cosine scan, no index
VECTOR_STORE=sqlite_vec uv run python scripts/retrieval_eval.py   # the default
uv sync --extra qdrant
VECTOR_STORE=qdrant     uv run python scripts/retrieval_eval.py   # a real vector database, local
```

At this corpus size the quality numbers should come out near identical, because all three do
exact nearest-neighbour search over the same vectors. That is the expected result, and knowing
the size at which the store starts to matter is the useful half of the answer.

`docs/vector-stores.md` compares these and the hosted ones — Pinecone, Weaviate, pgvector — on
the three things that decide the choice: where it runs, whether it can filter on metadata, and
what it costs. Read it before the session; "why this one?" is an interview question, and the
answer is a number plus a constraint, not a preference.

## Submit (30 minutes)

- `reflections/week-2.md`: Q1 (the concept in your words), Q1b (the three reading questions),
  Q2 (what surprised you), Q3 (what you would change), Q4 (what you contributed and how you
  checked it), Q5 (help you used), the two eval tables, and the strategy you chose and why.
- Open a pull request `week-2 → main`. CI runs the gate. Fix anything red.

## Self-directed week

No session this week. Your gate, the held-out questions your mentor left with you in session 2,
the self-test and the hub page are your feedback. Open the PR when the gate is green; it is
reviewed at session 3. An unblock call is available if you are stuck after a real attempt.

**Pass line,** checked at session 3: CI green, a strategy chosen with a number from your own
table, and one precision/recall movement explained from that table.

## Optional: self-test

`QUIZ.md` in this folder, with an explanation for every answer. On the hub page it is interactive.
The score stays in your browser: it never reaches the repository, your mentor or your route. Use
it to find what to re-read, not to measure yourself.
