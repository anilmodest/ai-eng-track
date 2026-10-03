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

ROUTE="$(cat .route 2>/dev/null || echo start)"
echo
echo "Ready. You are on the ${ROUTE} route."
case "$ROUTE" in
  start) echo "  Every helper is given, and each week's routes/worked_example.py solves a smaller one." ;;
  core)  echo "  Faults are planted in the exercise files, and you instrument the tracer yourself." ;;
  pro)   echo "  The helpers are signatures only, and each week's routes/pro.md adds one constraint." ;;
esac
echo "  Your mentor assigned it. Read weeks/N/routes/${ROUTE}.md each week."
echo
echo "Read weeks/0/BRIEF.md -- it is the client's brief, and the reason for everything after."
echo "Then, any time you are unsure what to do:  make next"
echo "(if this container was created before the uv fix, run: Codespaces: Full Rebuild Container)"
