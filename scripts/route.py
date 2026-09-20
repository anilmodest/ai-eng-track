"""`make route ROUTE=start|core|pro`: set your difficulty once, after placement.

The exercises are the same on every route. What changes is how much is given to you:
  start  everything in app/llm is given; you build the endpoint, schema and idempotency
  core   retry and structured-output handling are removed; you write them
  pro    as core, plus the cost table; you also add routing, fallback and streaming
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REMOVE: dict[str, list[str]] = {
    "start": [],
    "core": ["app/llm/retry.py", "app/llm/structured.py"],
    "pro": ["app/llm/retry.py", "app/llm/structured.py", "app/llm/cost.py"],
}

STUB = '''"""Removed for your route. Rebuild it: the tests in tests/weeks/ say what it must do."""

raise NotImplementedError("{name}: build me (see weeks/1/README.md)")
'''


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[1] not in REMOVE:
        print("usage: make route ROUTE=start|core|pro")
        return 2
    route = argv[1]
    for rel in REMOVE[route]:
        path = ROOT / rel
        if path.exists() and "Removed for your route" not in path.read_text():
            path.write_text(STUB.format(name=rel))
            print(f"stubbed {rel}")
    (ROOT / ".route").write_text(route + "\n")
    print(f"route set to {route} (.route). Tier tests for this route now run in `make check`.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
