# Week 0 — Practice quiz

Practice, untimed and repeatable. Your score stays in this browser on your hub page and never
reaches the repository or your mentor. Use it to find what to re-read; the explanations are the
point, not the score. Your mentor also assigns a short weekly check on BridgePath: different
questions, some of them timed, taken once, and your mentor sees that score.

## Q1. A version 3 customer asks how to configure the connection timeout. Why does a system that retrieves by similarity alone answer wrongly, and confidently?
- [ ] The version 3 page is missing from the corpus, so the model fills the gap from its training — both pages are in `corpus/`, and the brief asks you to read them side by side
- [ ] The question is ambiguous, so the model refuses to answer — the failure is a fluent wrong answer, not a refusal
- [x] The version 2 page shares almost all its wording, so that is the one retrieved
> Why: the two pages are nearly identical in wording and different in substance. Similarity cannot tell them apart; only the customer's version can, which is why O1 is about filtering by version, not about better matching.

## Q2. The brief says this system is an agent rather than a pipeline. What is the first reason it gives?
- [x] It cannot know which documentation page is right until it has called the tool that says which version this customer runs
- [ ] It uses a model to write the answer, and anything that calls a model in a loop counts as an agent by definition — a fixed pipeline can call a model too; that is not the difference
- [ ] Several cooperating models are needed to split the work between retrieval, answering and actions — multi-agent systems are listed as deliberately not required
> Why: what to do next depends on a fact the system has to fetch first. Even so, `REQUIREMENTS.md` says where agency goes is a decision: in week 4 you compare plain code, a fixed workflow and an agent, task type by task type.

## Q3. `scripts/baseline.py` asks the test questions with no documents attached. What result does the brief require before any retrieval is built?
- [ ] A high score, which shows the model is strong enough to build on — then retrieval would be doing no work, and every measurement after it would mean nothing
- [ ] Any score at all, since the baseline only times the calls — it scores answers, not latency
- [x] A low one: the corpus must fail a no-retrieval baseline
> Why: the product in `corpus/` is invented, every setting name and default included, so a model cannot answer from its training. A failed baseline is the proof that retrieval has a job to do.

## Q4. `POST /jobs/reindex` returns 202 within a few milliseconds while the job takes seconds. Why?
- [ ] FastAPI runs every handler on a thread pool, so no handler can ever block the server — this handler is async; it is the queue that keeps the work off the request
- [ ] SQLite commits are asynchronous, so the write finishes later — the Job row is committed before the response goes back
- [x] The handler only creates a Job row and enqueues the work; the job runs elsewhere
> Why: the API's job is to accept and acknowledge; the queue's job is to do the slow thing. `GET /jobs/{id}` then reports `queued`, `running` or `done`. That separation is what "the API stays responsive" means.

## Q5. `REDIS_URL` is empty. Which queue runs?
- [ ] `RedisQueue`, pointed at a default Redis address on localhost — the API picks the in-memory queue when the setting is empty
- [x] `InMemoryQueue`, a thread inside the API process
- [ ] None; jobs are refused until Redis is configured — the empty value is the normal development setting
> Why: `get_queue()` reads the setting once and picks the implementation. Same interface, different backing, and nothing above it knows. Week 1 does the same with the model provider.

## Q6. A fellow uploads `report.docx` to `POST /documents`. What comes back?
- [x] 415 with `{"error": "unsupported_type", ...}`
- [ ] 500, because `pypdf` fails on it — the parser picks by file suffix and never hands a `.docx` to `pypdf`
- [ ] 201 with empty text — the service refuses the file rather than storing nothing
- [ ] 400 with the stack trace in the detail — failures leave with a stable code and a short detail, never a trace
> Why: a typed error with a stable code is the contract for every failure in this service. A 500 tells the caller nothing; a 415 with a code tells them exactly what to fix.

## Q7. Day one: no model key is set yet, and you call `POST /documents/{id}/extract`. What comes back?
- [ ] 500 with a stack trace from the provider SDK — the missing key is caught before any call leaves the service
- [ ] 401 from the provider, passed through — no request reaches the provider without a key
- [x] 503 `model_not_configured`, with the fix in the detail
> Why: a dependency that is not ready is a typed error with the fix in it. `GET /health` says the same thing ahead of time: `model_ready` is false and `model_hint` names the missing key.

## Q8. According to `RULES.md`, what is the one thing that fails the programme outright?
- [ ] A red gate on a week's pull request — a red gate is the week's work, not a failure
- [ ] A wrong answer at a session, even one defended honestly — the rules name that as something that does not fail you
- [ ] Using an AI assistant to write code — you are expected to use one, and to log it
- [x] Submitting help you did not disclose
> Why: use an assistant, log it in `ai-use/week-N.yml`, and be able to explain every line. A green gate on work that is not yours teaches you nothing and tells an employer something untrue.
