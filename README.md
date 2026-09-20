# ai-eng-track

One small service that grows, week by week, into an AI product you can defend in an interview.
Six weeks, eleven areas, one repo: yours.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/anilmodest/ai-eng-track?quickstart=1)

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

Copy `.env.example` to `.env` (Codespaces did this). The default provider is **Gemini** on Google
AI Studio's free tier: one free key, no card, from <https://aistudio.google.com/apikey>. Put it in
`.env` as `MODEL_API_KEY`, or better, as the Codespaces secret `GEMINI_API_KEY` so it survives
rebuilds and is never committed. To use another provider, change two lines:

```
MODEL_PROVIDER=groq
MODEL_API_KEY=...        # or set GROQ_API_KEY as a Codespaces secret
```

Known providers are listed in `app/llm/registry.py`. If one runs out of quota, switch. Nothing in
the code changes. That is the point of Week 1.

## How a week works

Concept (1 h) → Elaboration (2 h) → Exercise (3–5 h) → Defence (10 min with your mentor).

- Work on a branch named `week-N`. Open a PR to `main`. CI runs `make check WEEK=N`.
- Fill `reflections/week-N.md` (copy `REFLECTION_TEMPLATE.md` there) before you send the PR link.
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

## Your progress page

Every merge to `main` rebuilds a page at `https://<your-user>.github.io/ai-eng-track` from what is in
the repo: each week's gate, your own words from `reflections/`, your PRs and how many mentor comments
they got. Nothing on it is typed in by hand. Your mentor opens it before every session.

One-time switch, 10 seconds: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
Until you do, the workflow builds the page but cannot publish it, and says so.

## Deploy (optional, 10 minutes, do it in Week 0 if you can)

Your mentor can then call your service at any time, not only while your Codespace is running.

1. Create a free account at <https://huggingface.co>, then a new **Space**: Docker SDK, blank
   template, CPU basic (free). Note its name, e.g. `yourname/ai-eng-track`.
2. In the Space's **Settings → Variables and secrets**, add `MODEL_PROVIDER=gemini` and your
   `GEMINI_API_KEY` (or whichever provider you use).
3. In this GitHub repo: **Settings → Secrets and variables → Actions**. Add a secret `HF_TOKEN`
   (from <https://huggingface.co/settings/tokens>, write access) and a variable `HF_SPACE` with the
   Space name. Optionally a variable `LIVE_URL` with the Space's URL so it shows on your page.
4. Merge anything to `main`. The `deploy` workflow pushes the service to the Space; it is live a
   few minutes later at `https://yourname-ai-eng-track.hf.space/docs`.

Free Spaces sleep after inactivity and wake on the first request. That is fine.

## Keeping it free

Your Codespace runs on 2 cores. GitHub Free gives 120 core-hours a month, so about 60 hours here.
Set **Settings → Codespaces → Default idle timeout** to 15 minutes and stop the Codespace when you
finish for the day. Stuck? Ask your mentor.
