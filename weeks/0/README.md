# Week 0 — Foundations gate

Area 1 of the track is not taught here. It is checked. This week you show that the ground the
next six weeks stand on is solid, and your mentor uses what they see to place you on a route.

**There is no model anywhere in the service yet.** That is deliberate.

## What the service does today

| Endpoint | Purpose |
| --- | --- |
| `POST /documents` | Upload a `.pdf`, `.csv`, `.md` or `.txt`; it is parsed to text and stored in SQLite |
| `GET /documents/{id}` | The text and metadata back |
| `GET /documents` | List |
| `POST /jobs/reindex` | Start a slow batch job on a queue and return at once |
| `GET /jobs/{id}` | Its status |
| `GET /health` | Liveness |

One upload, drawn. Trace it in the code, then trace it aloud.

```mermaid
flowchart LR
  C["Client<br/>POST /documents"] --> R["FastAPI router<br/>app/api/documents.py"]
  R --> P["parse()<br/>app/ingest/parsers.py"]
  P --> D[("SQLite<br/>document row")]
  R -. POST /jobs/reindex .-> Q{"queue<br/>REDIS_URL set?"}
  Q -- no --> M["InMemoryQueue<br/>thread in the API process"]
  Q -- yes --> X["RedisQueue<br/>arq worker"]
  M & X --> J["reindex_all()<br/>app/jobs/tasks.py"]
  J --> D
```


## Do this (about 2 hours)

1. `make check WEEK=0` — read the output. Everything should be green.
2. `make run` — open the forwarded port, go to `/docs`, upload `samples/invoice.md`, read it back.
3. Start a reindex job, then immediately call `/health`. Notice the API did not wait.
4. Read, in this order, and be ready to explain each one in two sentences:
   - `app/main.py` → `app/api/documents.py` → `app/ingest/parsers.py` → `app/db/session.py`
   - `app/jobs/queue.py` — why are there two queues, and which one is running right now?
5. Build the production image and run it:
   ```
   docker build -t ai-eng-track .
   docker run -p 7860:7860 ai-eng-track
   ```
   Then `curl localhost:7860/health`.
6. Fill `reflections/week-0.md` (copy `REFLECTION_TEMPLATE.md` there), Q1 only: trace one upload request from
   the HTTP call to the row in SQLite, in your own words, under 150 words.

## Session 1: Discovery (45 minutes, this week)

Your mentor runs an observed task: trace one request aloud, unaided, in under three minutes;
answer one or two of the questions above; and a short fixed exercise that is the starting measure.
No pass or fail. A route is assigned, and the finished piece you will defend in Week 6 is agreed.

Then: `make route ROUTE=<what your mentor said>` once, and open `weeks/1/CONCEPT.md`.

## Optional: self-test

`QUIZ.md` in this folder has a few questions on this week's concept, each with an explanation. On the hub page they are interactive and scored, but the score lives only in your browser: it never reaches the repo, your mentor or your route. Use it to find what to re-read.
