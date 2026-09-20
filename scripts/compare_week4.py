"""Week 4: one task set, three ways. Compare on correctness, cost and latency; then argue.

    uv run python scripts/compare_week4.py                # real provider from .env, approved spend
    uv run python scripts/compare_week4.py --modes plain,workflow

Runs eval/tasks.jsonl through /tasks/run in each mode and prints one row per mode: how many
tasks came out correct (expected phrase in the answer), total cost, mean latency, mean calls.
Writes reports/compare.json. The number to think about is cost per correct answer.
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
TASKS = ROOT / "eval" / "tasks.jsonl"


async def run(modes: list[str]) -> int:
    from httpx import ASGITransport, AsyncClient

    from app.main import app

    tasks = [json.loads(ln) for ln in TASKS.read_text(encoding="utf-8").splitlines() if ln.strip()]
    report: dict[str, Any] = {}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://cmp") as api:
        for path in sorted((ROOT / "corpus").iterdir()):
            r = await api.post("/documents", files={"file": (path.name, path.read_bytes())})
            assert r.status_code == 201, r.text
        assert (await api.post("/index")).status_code == 200

        header = f"{'mode':<9} {'correct':>8} {'cost $':>9} {'mean ms':>8} {'mean calls':>11}"
        print(header)
        print("-" * len(header))
        for mode in modes:
            rows = []
            for t in tasks:
                r = await api.post(
                    "/tasks/run", json={"question": t["q"], "mode": mode, "approved": True}
                )
                out = r.json()
                ok = out["status"] == "done" and t["expect"].lower() in out["answer"].lower()
                rows.append(
                    {
                        "id": t["id"],
                        "status": out["status"],
                        "correct": ok,
                        "cost_usd": out.get("cost_usd", 0.0),
                        "latency_ms": out.get("latency_ms", 0),
                        "calls": len(out.get("calls", [])),
                        "answer": out.get("answer", "")[:160],
                    }
                )
            correct = sum(1 for r in rows if r["correct"])
            cost = sum(r["cost_usd"] for r in rows)
            ms = sum(r["latency_ms"] for r in rows) / len(rows)
            calls = sum(r["calls"] for r in rows) / len(rows)
            print(f"{mode:<9} {correct:>4}/{len(rows):<3} {cost:>9.5f} {ms:>8.0f} {calls:>11.1f}")
            report[mode] = {
                "correct": correct,
                "of": len(rows),
                "cost_usd": round(cost, 6),
                "mean_latency_ms": int(ms),
                "mean_calls": round(calls, 2),
                "cost_per_correct": round(cost / correct, 6) if correct else None,
                "rows": rows,
            }
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / "compare.json").write_text(json.dumps(report, indent=2))
    print("\nwrote reports/compare.json. Which way would you ship, for these questions, and why?")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--modes", default="plain,workflow,agent")
    ap.add_argument("--db", default=str(ROOT / "data" / "compare.db"))
    args = ap.parse_args()
    os.environ["DATABASE_URL"] = f"sqlite:///{Path(args.db).as_posix()}"
    Path(args.db).unlink(missing_ok=True)
    return asyncio.run(run(args.modes.split(",")))


if __name__ == "__main__":
    sys.exit(main())
