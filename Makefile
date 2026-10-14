# Fellow-facing commands. Every week's README refers to these and nothing else.
WEEK ?= 0
ROUTE ?=
# uv may live in ~/.local/bin (pip --user) before the shell's PATH knows it; find it anyway.
UV ?= $(shell command -v uv 2>/dev/null || (test -x $(HOME)/.local/bin/uv && echo $(HOME)/.local/bin/uv) || echo uv)

.PHONY: setup next check evidence test lint types run worker live-check fmt hub

setup:            ## Install everything (Codespaces runs this for you)
	$(UV) sync

next:             ## What to do now: the week, the files to edit, the first thing not working
	$(UV) run python scripts/next_step.py

check:            ## Run this week's gate: lint + types + tests, writes reports/week-$(WEEK).json
	$(UV) run python scripts/check.py --week $(WEEK)

ONLY ?=
evidence:         ## This week's measurements on a REAL model -> evidence/week-$(WEEK).json (ONLY=name for one)
	$(UV) run python scripts/evidence.py --week $(WEEK) $(if $(ONLY),--only $(ONLY),)

test:
	$(UV) run pytest -q

lint:
	$(UV) run ruff check .
	$(UV) run ruff format --check .

types:
	$(UV) run mypy

fmt:
	$(UV) run ruff format .
	$(UV) run ruff check --fix .

run:              ## Start the API on :8000
	$(UV) run uvicorn app.main:app --reload --port 8000

worker:           ## Start the Redis job worker (needs REDIS_URL)
	$(UV) run arq app.jobs.worker.WorkerSettings

live-check:       ## Hit the real provider from .env with the sample documents
	$(UV) run python scripts/live_check.py

hub:              ## Your hub page from this checkout, now: http://localhost:8001 (Codespaces opens it)
	$(UV) run python scripts/hub_data.py
	for w in $$(ls weeks); do $(UV) run python scripts/check.py --week $$w --skip-static >/dev/null 2>&1 || true; done
	$(UV) run python scripts/build_pages.py
	$(UV) run python -m http.server 8001 --directory site

# source-only:begin
# Programme team only; never in a fellow's repository.
templates:        ## Build the three route templates into build/templates/start|core|pro
	$(UV) run python scripts/templates.py build --all --out build/templates
# source-only:end
