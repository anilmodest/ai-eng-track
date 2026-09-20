"""Week 5: the dashboard a non-engineer can read, from the spans table.

    uv run python scripts/trace_report.py [--db data/app.db]

Per step: how many, how slow (p50, p95), how much. Per request: the five most expensive. Per
failure: which kind, how often. Writes reports/traces.json for the progress page.
"""

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def pct(values: list[int], p: float) -> int:
    if not values:
        return 0
    s = sorted(values)
    return s[min(len(s) - 1, int(round((len(s) - 1) * p)))]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=str(ROOT / "data" / "app.db"))
    args = ap.parse_args()
    os.environ["DATABASE_URL"] = f"sqlite:///{Path(args.db).as_posix()}"

    from sqlmodel import Session, select

    from app.db.session import get_engine
    from app.trace import Span

    with Session(get_engine()) as session:
        spans = session.exec(select(Span)).all()
    if not spans:
        print("no spans yet: make some requests first")
        return 0

    by_name: dict[str, list[Span]] = defaultdict(list)
    for s in spans:
        by_name[s.name].append(s)
    roots = [s for s in spans if s.parent is None]
    errors = Counter(s.error_kind for s in roots if s.error_kind)

    print(f"{'step':<28} {'n':>5} {'p50 ms':>7} {'p95 ms':>7} {'cost $':>9} {'share':>6}")
    print("-" * 68)
    total_cost = sum(s.cost_usd for s in roots) or 1.0
    steps: dict[str, dict[str, float | int]] = {}
    for name, group in sorted(by_name.items(), key=lambda kv: -sum(s.cost_usd for s in kv[1])):
        durs = [s.duration_ms for s in group]
        cost = sum(s.cost_usd for s in group)
        is_root = group[0].parent is None
        # Roots carry the roll-up of their children, so only child steps get a share.
        share = f"{cost / total_cost:>5.0%}" if not is_root else "  root"
        print(
            f"{name:<28} {len(group):>5} {pct(durs, 0.5):>7} {pct(durs, 0.95):>7} "
            f"{cost:>9.5f} {share}"
        )
        steps[name] = {
            "count": len(group),
            "p50_ms": pct(durs, 0.5),
            "p95_ms": pct(durs, 0.95),
            "cost_usd": round(cost, 6),
        }

    print(
        f"\nrequests: {len(roots)}   total cost ${total_cost:.5f}   "
        f"mean ${total_cost / len(roots):.5f} per request"
    )
    print("\nmost expensive requests:")
    for s in sorted(roots, key=lambda s: -s.cost_usd)[:5]:
        print(
            f"  {s.request_id}  {s.name:<26} {s.duration_ms:>6} ms  ${s.cost_usd:.5f}"
            f"  {s.error_kind or ''}"
        )
    print("\nfailures by kind:")
    for kind, n in errors.most_common():
        print(f"  {kind:<20} {n}")
    if not errors:
        print("  none")

    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / "traces.json").write_text(
        json.dumps(
            {
                "requests": len(roots),
                "total_cost_usd": round(total_cost, 6),
                "steps": steps,
                "errors": dict(errors),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
