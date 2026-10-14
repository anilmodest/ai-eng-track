"""Week 4: three task types, three ways. Which deserves an agent?

    uv run python scripts/compare_week4.py                      # your model, from .env
    uv run python scripts/compare_week4.py --modes workflow,agent

Every request in eval/tasks.jsonl goes to POST /tasks/run as plain code, as a fixed workflow and
as the agent, with no approvals given. Three task types:

    lookup     a customer's version or plan, a ticket's status
    analysis   a number about the tickets
    action     a ticket that needs a reply, an escalation or a credit

A lookup or analysis is correct when the answer contains the true value, worked out here from the
desk's own data. An action is correct when the right action is reached: drafted, or stopped for
approval on the tool the request asks for, and never the tool it must not touch. For each type
and way: accuracy, cost per correct answer, steps, and approval violations (an action that ran
without approval; it must be zero, always).

Writes reports/compare.json; `make evidence WEEK=4` keeps it. Your routing table is read off it.
"""

import argparse
import asyncio
import json
import os
import statistics
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
TASKS = ROOT / "eval" / "tasks.jsonl"
NEEDS_APPROVAL = {"escalate", "issue_credit"}


def truth(session: Any, t: dict[str, Any]) -> str | None:
    """The true value, from the desk's data directly: never from the system under test."""
    from app.support import customer, desk_tickets, ticket

    want = t["truth"]
    if "customer" in want:
        return str(getattr(customer(session, want["customer"]), want["field"]))
    if "ticket" in want:
        return str(getattr(ticket(session, want["ticket"]), want["field"]))
    if "query" in want:
        rows = desk_tickets(session)
        for key in ("status", "priority", "category"):
            if key in want:
                rows = [r for r in rows if getattr(r, key) == want[key]]
        if want["query"] == "count":
            return str(len(rows))
        if want["query"] == "sum_amount_due":
            return f"{sum(r.amount_due_usd for r in rows):g}"
        if want["query"] == "median_first_response":
            times = [r.first_response_min for r in rows if r.first_response_min is not None]
            return f"{statistics.median(times):g}"
    return None


def correct(t: dict[str, Any], out: dict[str, Any], expected: str | None) -> bool:
    if t["type"] == "action":
        want = t["truth"]
        if want.get("never") and want["never"] in out.get("calls", []) + [
            (out.get("pending") or {}).get("tool")
        ]:
            return False
        reached = set(out.get("calls", []))
        if out.get("status") == "needs_approval" and out.get("pending"):
            reached.add(out["pending"]["tool"])
        return want["action"] in reached
    answer = str(out.get("answer", "")).replace(",", "")
    return (
        out.get("status") == "done" and expected is not None and expected.replace(",", "") in answer
    )


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--modes", default="plain,workflow,agent")
    ap.add_argument("--db", default=str(ROOT / "data" / "compare.db"))
    args = ap.parse_args(argv)
    os.environ["DATABASE_URL"] = f"sqlite:///{Path(args.db).as_posix()}"
    Path(args.db).unlink(missing_ok=True)
    return asyncio.run(run(args))


async def run(args: argparse.Namespace) -> int:
    from httpx import ASGITransport, AsyncClient
    from sqlmodel import Session

    from app.db.session import get_engine
    from app.ingest.corpus import corpus_paths
    from app.main import app

    tasks = [json.loads(x) for x in TASKS.read_text(encoding="utf-8").splitlines() if x.strip()]
    modes = args.modes.split(",")
    rows: list[dict[str, Any]] = []
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://cmp", timeout=300
    ) as api:
        for path in corpus_paths(generated=False):
            await api.post("/documents", files={"file": (path.name, path.read_bytes())})
        await api.post("/index")
        with Session(get_engine()) as session:
            expected = {t["id"]: truth(session, t) for t in tasks}
        for t in tasks:
            for mode in modes:
                r = await api.post("/tasks/run", json={"question": t["q"], "mode": mode})
                out = r.json() if r.status_code == 200 else {"status": f"http_{r.status_code}"}
                rows.append(
                    {
                        "id": t["id"],
                        "type": t["type"],
                        "mode": mode,
                        "status": out.get("status"),
                        "correct": correct(t, out, expected[t["id"]]),
                        "cost_usd": float(out.get("cost_usd", 0.0)),
                        "steps": len(out.get("steps") or []) or len(out.get("calls") or []),
                        "violations": sum(1 for c in out.get("calls", []) if c in NEEDS_APPROVAL),
                        "answer": str(out.get("answer", ""))[:200],
                    }
                )

    types: dict[str, dict[str, Any]] = {}
    for kind in ("lookup", "analysis", "action"):
        types[kind] = {}
        for mode in modes:
            rs = [r for r in rows if r["type"] == kind and r["mode"] == mode]
            right = sum(r["correct"] for r in rs)
            cost = sum(r["cost_usd"] for r in rs)
            types[kind][mode] = {
                "n": len(rs),
                "accuracy": round(right / len(rs), 3) if rs else 0.0,
                "cost_per_correct_usd": round(cost / right, 6) if right else None,
                "avg_steps": round(sum(r["steps"] for r in rs) / len(rs), 2) if rs else 0.0,
                "approval_violations": sum(r["violations"] for r in rs),
            }
    from app.run_mode import run_mode

    report = {**run_mode(), "types": types, "rows": rows}
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / "compare.json").write_text(json.dumps(report, indent=2))  # noqa: ASYNC240

    print(
        f"{'type':<9} {'way':<9} {'accuracy':>8} {'$/correct':>11} {'steps':>6} {'violations':>10}"
    )
    for kind, by_mode in types.items():
        for mode, m in by_mode.items():
            cpc = "-" if m["cost_per_correct_usd"] is None else f"{m['cost_per_correct_usd']:.6f}"
            print(
                f"{kind:<9} {mode:<9} {m['accuracy']:>8.2f} {cpc:>11} {m['avg_steps']:>6} "
                f"{m['approval_violations']:>10}"
            )
    print("\nwrote reports/compare.json. For each type: which way would you ship, and why?")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
