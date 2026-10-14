"""Weeks 3 and 4: run the agent on the trajectory set and score the path it took.

    uv run python scripts/trajectories.py                     # eval/trajectories.jsonl, your model
    uv run python scripts/trajectories.py --set other.jsonl --out reports/x.json

Each task goes to POST /tasks/run in agent mode, with no approvals given. The score is the path:
the right first tool, the expected tools in order, the expected arguments, no forbidden tool, no
more steps than allowed, the expected ending (done, or stopped for approval), and nothing that
needs a person's approval run without one. app/eval/trajectory.py says exactly how.

Week 3 writes the twenty tasks and this command runs, even though the agent is not built until
week 4: until then every task scores zero, which is the honest number. Writes
reports/trajectories.json; `make evidence WEEK=3` and `WEEK=4` keep it.
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.eval.trajectory import TrajectoryTask, score, summarise  # noqa: E402

SET = ROOT / "eval" / "trajectories.jsonl"


def load(path: Path) -> list[TrajectoryTask]:
    return [
        TrajectoryTask.model_validate_json(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


async def run(tasks: list[TrajectoryTask]) -> dict[str, Any]:
    from httpx import ASGITransport, AsyncClient

    from app.ingest.corpus import corpus_paths
    from app.llm.registry import get_model_client
    from app.main import app

    client = get_model_client()
    scores = []
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://traj", timeout=300
    ) as api:
        for path in corpus_paths(generated=False):
            await api.post("/documents", files={"file": (path.name, path.read_bytes())})
        await api.post("/index")
        for task in tasks:
            r = await api.post("/tasks/run", json={"question": task.task, "mode": "agent"})
            out: dict[str, Any] = (
                r.json() if r.status_code == 200 else {"status": f"http_{r.status_code}"}
            )
            steps: list[dict[str, Any]] = out.get("steps", [])
            calls = [(s["tool"], s.get("args", {})) for s in steps if s.get("tool") != "finish"]
            pending = out.get("pending")
            asked = pending.get("tool") if isinstance(pending, dict) else None
            if asked and (not calls or calls[-1][0] != asked):
                calls.append((asked, pending.get("args", {})))  # type: ignore[union-attr]
            s = score(
                task,
                calls,
                status=str(out.get("status", "error")),
                executed=[c for c in out.get("calls", []) if c != "finish"],
                approved=set(),
                cost_usd=float(out.get("cost_usd", 0.0)),
            )
            scores.append(s)
            mark = "ok " if s.correct else "   "
            print(f"  {mark}{task.id:<5} {s.status:<15} {' > '.join(s.tools) or '-'}")
    return {
        "provider": client.name,
        "model": client.model,
        "summary": summarise(scores),
        "tasks": [s.model_dump() for s in scores],
    }


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default=str(SET))
    ap.add_argument("--out", default=str(ROOT / "reports" / "trajectories.json"))
    ap.add_argument("--db", default=str(ROOT / "data" / "trajectories.db"))
    args = ap.parse_args(argv)
    os.environ["DATABASE_URL"] = f"sqlite:///{Path(args.db).as_posix()}"
    Path(args.db).unlink(missing_ok=True)
    tasks = load(Path(args.set))
    print(f"trajectory set: {len(tasks)} tasks\n")
    report = asyncio.run(run(tasks))
    out = Path(args.out)
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    s = report["summary"]
    print(
        f"\ncorrect {s['correct_rate']:.2f}  first tool {s['right_first_tool_rate']:.2f}  "
        f"in order {s['tools_in_order_rate']:.2f}  avg steps {s['avg_steps']}  "
        f"unapproved actions {s['unapproved_actions']}  ({out.name})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
