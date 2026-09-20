#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
[ -f .env ] || cp .env.example .env
uv sync
mkdir -p data reports
uv run python scripts/check.py --week 0 || true
echo
echo "Ready. Open weeks/0/README.md and run: make run"
