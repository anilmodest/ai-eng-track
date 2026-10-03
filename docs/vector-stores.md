# Where the vectors live

Three stores ship behind one interface, and three more are worth knowing by name. The point of
the interface is that choosing between them becomes a measurement rather than a preference, and
"why this one?" is a question you will be asked.

Change `VECTOR_STORE` in `.env`. Nothing else in the service changes.

## The three you can run

| | How it runs | Metadata filtering | What it costs | When you would pick it |
| --- | --- | --- | --- | --- |
| **numpy** | No index at all: every chunk is read out of SQLite and compared in one pass | In Python, after the rows are loaded | Nothing | A few thousand chunks, and you want the fewest moving parts. It is also the control: if a real store is not beating this, it is not earning its place |
| **sqlite_vec** | A `vec0` virtual table in the same SQLite file. An extension, not a service | In the index. The version is a **partition key**, so the index is physically split by version | Nothing | The default here. One file to back up, no process to keep alive, and the filter happens before the search rather than after |
| **qdrant** | A real vector database. A local folder with no server, or a hosted instance, through the identical client | In the index, on arbitrary payload fields | Nothing locally; a free tier hosted | When you outgrow one file, want a filter over several fields, or want to say in an interview that you have used one |

## Three more you should be able to talk about

| | How it runs | Worth knowing |
| --- | --- | --- |
| **Pinecone** | Hosted only | The one most often named in job adverts. No local mode, so you cannot test without an account |
| **Weaviate** | Hosted or self-run | Hybrid search and a schema with real types, if you want structure as well as vectors |
| **pgvector** | An extension to PostgreSQL | If the organisation already runs Postgres, this is frequently the correct answer and the cheapest to operate. The vectors sit next to the rest of the data, so a filter is an ordinary `WHERE` |

## The thing that actually decides it here

Not speed. **Filtering.**

This service has to answer out of one version of a manual and never the other, and six of the
corpus pages exist twice, worded almost identically. A store that can only rank by similarity
forces you to over-fetch and filter afterwards, which quietly costs you recall: the wrong
version's chunks take the top slots, you drop them, and you are left with fewer results than you
asked for. Every store here filters *before* ranking, which is why
`tests/weeks/test_week2.py::test_the_filter_runs_before_ranking_not_after` exists.

FAISS is deliberately absent from the list above for the same reason. It is a fast index, not a
database: no metadata, no filtering, so expressing the version constraint means keeping a second
structure in step with it by hand.

## Measure it rather than take this on trust

```
VECTOR_STORE=numpy      uv run python scripts/retrieval_eval.py
VECTOR_STORE=sqlite_vec uv run python scripts/retrieval_eval.py
uv sync --extra qdrant
VECTOR_STORE=qdrant     uv run python scripts/retrieval_eval.py
```

At this corpus size the quality numbers should be near identical, because all three are doing
exact nearest-neighbour search over the same vectors. That is the expected result and it is worth
writing down: at ten documents the store is not your problem, and knowing the size at which it
becomes one is the useful part of the answer.

## Going hosted in week 6, if you want to

```
export VECTOR_STORE=qdrant
export QDRANT_URL=https://<your cluster>.qdrant.io
```

That is the whole change. Free tier, no card. It is optional: the published image runs on
sqlite-vec with nothing to host, which is why that is the default.
