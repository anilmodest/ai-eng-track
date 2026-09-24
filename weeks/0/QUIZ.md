# Week 0 — Quiz

Optional, repeatable, and yours: the score is kept in your own browser on the hub page and
never reaches the repo, the mentor or the route. Use it to find out what you have not understood
yet; then go and read that part again. The explanations are the point, not the score.

## Q1. `POST /jobs/reindex` returns 202 within a few milliseconds while the job takes seconds. Why?
- [ ] FastAPI runs every handler on a thread pool, so the job cannot block — the handler itself is async; it is the queue that keeps the work off the request
- [x] The handler only creates a Job row and enqueues the work; the job runs elsewhere (a thread or an arq worker)
- [ ] SQLite commits are asynchronous — they are not; the row is written before the response
> Why: the API's job is to accept and acknowledge; the queue's job is to do the slow thing. That separation is what "the API stays responsive" means, and it is the same shape a model call sits behind later.

## Q2. `REDIS_URL` is empty. Which queue runs?
- [x] `InMemoryQueue`, a thread inside the API process
- [ ] `RedisQueue`, with a default localhost address — only the worker falls back to localhost; the API picks the in-memory queue
- [ ] None; jobs are refused until Redis is configured
> Why: `get_queue()` reads the setting once and picks the implementation. Same interface, different backing; nothing above it knows. Week 1 does the same trick with the model provider.

## Q3. A fellow uploads `report.docx`. What comes back?
- [ ] 500, because `pypdf` cannot read it — the parser is never reached
- [x] 415 with `{"error": "unsupported_type", ...}`
- [ ] 201 with empty text — the service refuses rather than storing nothing
> Why: a typed error with a stable code is the contract for every failure in this service. A 500 tells the caller nothing; a 415 with a code tells them exactly what to fix.

## Q4. Where does `DATABASE_URL` come from, in order of precedence?
- [x] The environment, then `.env`, then the default in `Settings`
- [ ] `.env`, then the environment — the process environment always wins over the file
- [ ] `Settings` only; `.env` is documentation
> Why: pydantic-settings reads real environment variables first, so CI and the tests can override the file without editing it. That is why the tests can point every run at a fresh SQLite file.

## Q5. Why does the Week 0 Docker image run as user 1000?
- [ ] Python refuses to run as root in a container — it does not
- [x] Many container hosts refuse to run as root, and the release pipeline runs the image the same way everywhere; matching uid 1000 locally means the same behaviour in both places
- [ ] It is required for SQLite — SQLite does not care
> Why: the reason is in the Dockerfile comment. Differences between where you run it and where it runs are the source of deploy-day surprises; removing one on day zero is cheap. Week 6 publishes this image to a registry, and whoever pulls it runs it as that user.
