# ai-eng-track

One small service that grows, week by week, into an AI product you can defend in an interview.
Six weeks, eleven areas, one repo: yours.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/OWNER/REPO?quickstart=1)

## Start here (three clicks, nothing to install)

1. You made this repo from the template. Good.
2. Click the badge above (or **Code → Create codespace on main**). Wait about 90 seconds.
3. `weeks/0/README.md` opens by itself. Follow it.

Everything is installed for you. The first check already ran. If you see `Ready.` in the
terminal, you are ready.

## The only commands you need

| Command | What it does |
| --- | --- |
| `make run` | Start the API on port 8000 (docs at `/docs`) |
| `make check WEEK=1` | This week's gate: lint, types, tests, once per fake provider. Writes `reports/week-1.json` |
| `make live-check` | Call the real provider from `.env` with the sample documents |
| `make route ROUTE=core` | Set your route once, after your mentor places you (`start`, `core`, `pro`) |
| `make fmt` | Format and auto-fix lint |

## Model access

Copy `.env.example` to `.env` (Codespaces did this). By default it uses **GitHub Models** through
the token Codespaces already has: zero signup. To use another provider, change two lines:

```
MODEL_PROVIDER=gemini
MODEL_API_KEY=...        # or set GEMINI_API_KEY as a Codespaces secret
```

Known providers are listed in `app/llm/registry.py`. If one runs out of quota, switch. Nothing in
the code changes. That is the point of Week 1.

## How a week works

Concept (1 h) → Elaboration (2 h) → Exercise (3–5 h) → Defence (10 min with your mentor).

- Work on a branch named `week-N`. Open a PR to `main`. CI runs `make check WEEK=N`.
- Fill `REFLECTION.md` (copy from `REFLECTION_TEMPLATE.md`) before you send the PR link.
- Send the link 24 hours before your session. Merge after it.

## Layout

```
app/        the service (FastAPI, SQLite, a job queue, and the model layer in app/llm)
weeks/N/    CONCEPT.md, README.md (the exercise), CHECKS.md (what the gate verifies)
explore/    small scripts you run and read, one or two per week; you never edit them
tests/      the gate; tests/weeks/test_weekN.py is the contract for week N
samples/    three documents used by tests and live-check
scripts/    check.py, live_check.py, route.py
```

## Keeping it free

Your Codespace runs on 2 cores. GitHub Free gives 120 core-hours a month, so about 60 hours here.
Set **Settings → Codespaces → Default idle timeout** to 15 minutes and stop the Codespace when you
finish for the day. Stuck? Ask your mentor.
