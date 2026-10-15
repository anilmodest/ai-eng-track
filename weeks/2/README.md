# Week 2 — Context and retrieval, as the agent's main tool

Areas 3 and 4. 8 to 10 hours. One of the two decisive weeks. No session. Branch: `week-2`.

> **The one lesson.** The same model gives a different answer when you give it different context.
> Choosing the context is the job.

## The gap it closes

The model has never seen your documents. There are two ways to fix that: put everything in the
question, or find the relevant pieces first and send only those. With the whole corpus, the
first is not merely unwise: on a free tier it is refused, and on a paid one it costs real money per
question. You measure that rather than being told it. A candidate who cannot explain how they
chose their retrieval approach loses the interview at that question.

## What you are building

Search over the corpus that can be restricted to **one version of the manual**, that combines
keyword and meaning search, and that the agent can call as a tool, with the version its first
tool returned.

```
GET /search?q=where+is+the+connection+timeout+set&k=1&strategy=section
  -> [ { "filename": "manual-v2-connection-timeout.md", "version": "v2", ... } ]   # the trap

GET /search?q=where+is+the+connection+timeout+set&k=1&strategy=section&version=v3&mode=hybrid
  -> [ { "filename": "manual-v3-connection-timeout.md", "version": "v3", ... } ]
```

The first search is the version trap: the version 2 page is worded almost identically, so a
version 3 question gets a version 2 answer that reads perfectly.

## The constraint everything is built under

**A question about version 3 may never be answered out of a version 2 page** (output requirement
O1). No model quality fixes it: the two pages are near-identical strings, so similarity cannot
tell them apart. Only a filter on metadata can, and it has to run **before** ranking. Filter
afterwards and the version 2 chunks take the top k slots, you drop them, and you hand back fewer
hits than were asked for. Losing recall quietly is still losing.

## Read (1 hour)

`CONCEPT.md` first, then [worked example A](../../docs/worked-examples.md#example-a-retrieval-metrics-week-2)
for how to read the metrics. Then, answering the three questions in `reflections/week-2.md`, Q1b:

1. **`app/retrieval/chunkers.py`**: which strategy would cut the invoice table? What does
   `by_section` repeat, and what does that cost?
2. **`app/retrieval/embed.py`**: what does the `hash` embedder know about meaning? Why does the
   repository have it at all?
3. **`app/retrieval/store.py`**: where does the version filter run, for meaning search and for
   keyword search, and why must it be the same place for both?

## See it (1 hour, change nothing)

```
uv run python explore/w2_01_chunk_and_look.py                     # one contract, cut four ways
uv run python explore/w2_02_lost_in_the_middle.py --trials 3 --filler 40
uv run python scripts/version_check.py                            # what similarity alone returns
uv run python scripts/baseline.py                                 # does the model already know?
```

The last one matters first. The manual describes an invented product, so a model answering it
from training is a signal that something is wrong with your corpus, not a convenience. If the
baseline comes back high, report it rather than working around it.

## Build (5 to 7 hours)

Core items are needed for the lesson and checked by the gate; stretch items are shown to your
mentor and never block. Log your assistant use as you go in `ai-use/week-2.yml`.

### Core 1: measure retrieval (`app/retrieval/metrics.py`)

Precision at k, recall at k, reciprocal rank, and `evaluate`, which averages them per query.
Precision divides by k, not by how many hits came back.

### Core 2: a heading-aware chunker (`app/retrieval/chunkers.py`, `by_heading`)

One chunk per markdown section, its heading kept with its body; an oversized section falls back to
paragraphs that each still carry the heading; a document without headings behaves like
`by_paragraph`. It is measured against two given strategies, `paragraph` and `section` (which
also repeats the page title and overlaps paragraphs).

### Core 3: the version filter (`app/retrieval/versions.py`, `applicable_versions`)

One function, called by every store before ranking, and by keyword search too. Two things are easy
to get wrong, and both are in its docstring: what `None` means, and what happens to the pages that
carry no version at all.

### Core 4: hybrid search (`app/retrieval/hybrid.py`)

`bm25_scores`: one score per document; rare query terms count for more, repeats count for less
each time, and a long document does not win just by being long. `reciprocal_rank_fusion`: merge
rankings by rank, not by score. The store does the rest: `SEARCH_MODE=hybrid` (or `mode=hybrid` on
`/search`) runs both over the same version-filtered chunks and fuses them.

### Core 5: the agent's second tool (`app/tools/search.py`, `search_docs`)

You design it as you designed `get_customer`: its description, its constraints and what each
result carries back. The version is **required**: a search without one is the version trap with
extra steps. A malformed call (an empty query, version `v4`, k of 500) never reaches the search.
Each result says which file and version it came from, so the model can cite it; no results is an
answer in words.

### Core 6: measure it on a real model (`make evidence WEEK=2`)

| Measurement | Script | What it tells you |
| --- | --- | --- |
| `baseline` | `scripts/baseline.py` | The model with no retrieval at all, on the thirty starter questions |
| `retrieval` | `scripts/retrieval_eval.py` | Six configurations, `paragraph`, `heading` and `section`, each dense and hybrid: P@k, R@k, MRR, hit rate, the version trap, context tokens and search latency |
| `context` | `scripts/context_experiment.py` | The same model on twenty questions with five contexts: none, the wrong version, the right one, the right one with far too many others, and the right one buried in the middle |

The retrieval numbers mean more with real embeddings: put `EMBED_PROVIDER=fastembed` in `.env`
(130 MB downloaded once) before you run it.

### Stretch

- **The vector stores, compared.** `VECTOR_STORE=numpy`, `sqlite_vec` (the default; the version is
  its partition key) and `qdrant` (`uv sync --extra qdrant`) behind one interface; run the
  retrieval measurement on each. [`docs/vector-stores.md`](../../docs/vector-stores.md) compares
  them and the hosted ones (Pinecone, Weaviate, pgvector) on where they run, metadata filtering
  and cost.
- **k.** Run the retrieval measurement at `--k 3` and `--k 8` and see what precision and the
  context tokens do.

## Decide

**The retrieval configuration you ship, and the k you ship with**, chosen from the six measured
configurations and what a question costs; **and how much context to send**, read off the context
experiment. Set `CHUNK_STRATEGY`, `SEARCH_MODE` and `SEARCH_K` in `.env` to match, and write
`decisions/week-2.md`, quoting the evidence by key (for example
`- retrieval.configs.section+hybrid.hit_rate = 0.9`).

## What proves it

1. **The gate**: the metrics, the chunker, the version filter (a version 3 question returns zero
   version 2 chunks, before ranking), BM25 and fusion, `search_docs`, and the context experiment
   running. `CHECKS.md` lists every check.
2. **The hidden evaluation**, on what you merge: hit rate and version accuracy on questions you
   have not seen, on the programme's model. Your mentor brings you the totals, never the
   questions.
3. **The evidence file and the decision record**, which the gate checks against each other.

The result: a retrieval configuration chosen with a number rather than an opinion, and the
comparison table to show for it.

**Anti-goal: do not touch the prompt or the final answer quality.** This week is retrieval only.

### If you get stuck

- **Rate-limited?** Only the three measurements need a real model; the gate runs on a fake one
  with `EMBED_PROVIDER=hash`, so it never costs you a request.
- **A test is failing and the message is not obvious?** Open the test. It is short.
<!-- route:start -->
- **On `start`?** `routes/worked_example.py` implements a sibling metric (mean average precision)
  and a sibling chunker (`by_lines`) in full. Run it, then read it beside your stubs.
<!-- /route -->
- **Stuck for more than an hour?** That is what the unblock call is for. Use it.

Your route changes what this week gives you: the page in `routes/` in this folder says how.

## Submit

1. `make check WEEK=2` green, commit, `make evidence WEEK=2`, commit the evidence.
2. `decisions/week-2.md`, `ai-use/week-2.yml`, `reflections/week-2.md` (Q1 to Q5).
3. Open a pull request `week-2 → main`.

## A week without a session

Your mentor reads the brief built from the week you merged and gives a one-click verdict: on
track, something to probe at session 3, or an offer of an unblock call. The gate and the hub page
are your feedback this week, and your mentor passes on the hidden evaluation's totals.

## Optional: self-test

`QUIZ.md` in this folder, with an explanation for every answer. The score stays in your browser.
