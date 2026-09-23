#!/usr/bin/env bash
# Runs once when the Codespace is created. Everything a fellow needs, nothing they must do.
set -uo pipefail
cd "$(dirname "$0")/.."

# uv comes from the image (.devcontainer/Dockerfile). This is a belt-and-braces fallback for
# anyone opening the repo in a plain container that does not have it.
if ! command -v uv >/dev/null 2>&1; then
  echo "== uv not in the image, installing into ~/.local/bin"
  pip install --user -q uv || pip install -q uv
  export PATH="$HOME/.local/bin:$PATH"
  grep -q '.local/bin' "$HOME/.bashrc" 2>/dev/null || echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
fi
echo "== uv $(uv --version)"

echo "== installing the project"
[ -f .env ] || cp .env.example .env
uv sync
mkdir -p data reports

echo "== first check"
uv run python scripts/check.py --week 0 || echo "(check reported a failure; open weeks/0/README.md and read the output above)"

echo
echo "Ready. Open weeks/0/README.md and run: make run"
echo "(if this container was created before the uv fix, run: Codespaces: Full Rebuild Container)"
