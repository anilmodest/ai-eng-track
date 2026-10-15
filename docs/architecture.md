# How the pieces fit (programme team only)

Never shipped to a fellow. The contracts between this source repository, the route templates, a
fellow's repository and the private programme repository (`ai-eng-programme`), as built.

Fellow repositories are **public, in the fellow's own account**. Everything here is built on
`github.com/anilmodest` first and moves to the platform's organisation later
([`docs/templates.md`](templates.md), and `ai-eng-programme/docs/porting.md`). No owner name is
written into code: `PROGRAMME_OWNER`, `TEMPLATE_PREFIX` and the like are configuration, and every
repository is identified by its numeric GitHub id, which survives a transfer.

## Repositories

| Repository | Visibility | Who edits | Holds |
| --- | --- | --- | --- |
| `ai-eng-track` (this one) | public | the programme team | all the fellow material, all three routes, the template generator |
| `ai-eng-track-start`, `-core`, `-pro` | public, template repositories | CI only (`publish-templates.yml`) | one route each, nothing of the others |
| a fellow's repository | public, in their account | the fellow | their work, records, evidence and hub |
| `ai-eng-programme` | private | the programme team | the mentor kit, the runner and hidden items, variants, the registry, the mentor hub (and an App service for later) |

## A fellow's journey, as the machinery sees it

1. **Discovery** (`ai-eng-programme/kit/discovery`): the route is recommended by the mentor and
   confirmed by the lead (`programme route recommend`, `programme route confirm`, which prints the
   route's template link).
2. **Repository**: the fellow clicks *Use this template* on `<owner>/ai-eng-track-<route>`. The
   template carries `.route` and `.template.json` (route, source commit, and `week_files`: per
   week, the files that differ by route).
3. **Connect repo**: the fellow sends the repository's address and the lead records it
   (`programme connect`): the public API gives the repository id and the template it came from,
   which must be the route's. The lead sends "Your product" as a zip (the fellow's variant:
   `corpus/generated/`, `support/`, `.variant`), which the fellow merges on `week-0`. Nothing is
   installed on the fellow's repository and the programme never writes to it.
4. **Every pull request**: `check.yml` runs the gate on the fake model; the hub page rebuilds.
5. **Every merge of `week-N` to main** marks the week done. The programme's `hidden-eval.yml`
   (daily, or "Run workflow") finds merge commits with no result, collects the brief data on each
   (the week's gate, then the programme's own copy of `scripts/brief_data.py`, in a container
   with no secrets), and evaluates it: builds the fellow's image, runs it on an internal network
   whose only exit is the model proxy, sends the hidden items, keeps the result privately. The
   mentor hub builds a one-page brief from the two.
6. **Route change at session 2**: one set of files replacing the `week_files` of the weeks still
   ahead with the new route's template's versions (a pull request the service opens, once there
   is an App).

## What the fellow's service must offer the runner

| Week | Endpoint | Shape |
| --- | --- | --- |
| 2+ | `GET /search?q&k&version&mode` | hits with `filename`, `version`, `text`, `score` (a cosine) |
| 3+ | `POST /ask {question, version}` | `abstained`, `answer`, `citations[].filename`, `cost_usd` |
| 4+ | `POST /tasks/run {question, mode: "agent", approve: [tool]}` | `status` (`done`, `needs_approval`, ...), `answer`, `steps[].tool`, `pending.tool`, `calls` (the tools that ran), `cost_usd` |

The runner reaches a model only through its proxy: `MODEL_PROVIDER=openai_compat`,
`MODEL_BASE_URL`, `MODEL_API_KEY` (a run token), `MODEL_NAME` (the reference model),
`EMBED_PROVIDER=hash`. The week 4 frontier run uses `MODEL_PROVIDER=programme` with the fellow's
capped `PROGRAMME_MODEL_TOKEN`.

## The fellow's records

| File | Written by | Checked by |
| --- | --- | --- |
| `evidence/week-N.json` | `make evidence WEEK=N` (real model only) | the commit, provider and model are in it |
| `decisions/week-N.md` | the fellow, from `DECISION_TEMPLATE.md` | `scripts/records.py`: every section, a rejected option, every number equal to the evidence |
| `ai-use/week-N.yml` | the fellow, from `AI_USE_TEMPLATE.yml` | hours given, every entry says what was checked |
| `reports/brief.json` | `scripts/brief_data.py`, in CI | uploaded as `brief-data` for the mentor hub |

## The tool door (`app/tools/base.py`)

Every tool call, from the agent, the workflow or the MCP server, goes through `run_tool`, in this
order: the tool exists; it was offered to this run (week 5, `app/agents/routing.py`); its
arguments validate; if it writes or spends, a person approved it for this run; it runs, in a span
with OpenTelemetry attributes; if it returns text someone outside the desk wrote, and the context
asks for it, the text is fenced as data (week 5, `app/guard.py`). Agent and workflow runs go
through `MaskingClient` (`app/llm/masking.py`), which masks personal data when
`MASK_PERSONAL_DATA` is on and records what every model call was shown.
