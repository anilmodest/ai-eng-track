"""Week 4: your model against a frontier model, on your trajectory set. Where does size pay?

    uv run python scripts/model_compare.py

Runs scripts/trajectories.py twice: once on your own model (from .env), and once on the frontier
model through the programme's capped key, if you have it (PROGRAMME_MODEL_BASE_URL,
PROGRAMME_MODEL_TOKEN and PROGRAMME_FRONTIER_MODEL, Codespaces secrets the programme gives you).
You pay for nothing; the run is capped. Without the key, the frontier half says it was not run.

For each task type in the set: how often the path was right, the cost per correct task and the
steps, on both models. Small models usually fail first on multi-step planning and on choosing
among many tools; a frontier model can cost ten to fifty times as much per call. The answer is
usually a mix, decided task type by task type, and your routing table's model column is read off
this file. Writes reports/models.json; `make evidence WEEK=4` keeps it.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "reports" / "models.json"


def run(env: dict[str, str], out: Path) -> dict[str, Any]:
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "trajectories.py"),
            "--out",
            str(out),
            "--db",
            str(out.with_suffix(".db")),
        ],
        cwd=ROOT,
        env=env,
        check=False,
    )
    report: dict[str, Any] = json.loads(out.read_text()) if out.exists() else {}
    return report


def by_type(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    from app.eval.trajectory import TrajectoryTask

    tasks = {
        t.id: t
        for t in (
            TrajectoryTask.model_validate_json(x)
            for x in (ROOT / "eval" / "trajectories.jsonl").read_text("utf-8").splitlines()
            if x.strip()
        )
    }
    out: dict[str, dict[str, Any]] = {}
    for row in report.get("tasks", []):
        kind = tasks[row["id"]].type if row["id"] in tasks else "other"
        out.setdefault(kind, {"n": 0, "correct": 0, "cost": 0.0, "steps": 0})
        o = out[kind]
        o["n"] += 1
        o["correct"] += int(row["correct"])
        o["cost"] += row["cost_usd"]
        o["steps"] += row["steps"]
    return {
        k: {
            "n": v["n"],
            "accuracy": round(v["correct"] / v["n"], 3),
            "cost_per_correct_usd": round(v["cost"] / v["correct"], 6) if v["correct"] else None,
            "avg_steps": round(v["steps"] / v["n"], 2),
        }
        for k, v in out.items()
    }


def main() -> int:
    own = run(dict(os.environ), ROOT / "reports" / "trajectories-own.json")
    result: dict[str, Any] = {
        "own": {
            "model": own.get("model"),
            "summary": own.get("summary", {}),
            "by_type": by_type(own),
        }
    }
    needed = ("PROGRAMME_MODEL_BASE_URL", "PROGRAMME_MODEL_TOKEN", "PROGRAMME_FRONTIER_MODEL")
    missing = [k for k in needed if not os.environ.get(k)]
    if missing:
        result["frontier"] = {"skipped": f"not run: {', '.join(missing)} not set"}
    else:
        env = {
            **os.environ,
            "MODEL_PROVIDER": "programme",
            "MODEL_NAME": os.environ["PROGRAMME_FRONTIER_MODEL"],
        }
        frontier = run(env, ROOT / "reports" / "trajectories-frontier.json")
        result["frontier"] = {
            "model": frontier.get("model"),
            "summary": frontier.get("summary", {}),
            "by_type": by_type(frontier),
        }
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({k: v.get("by_type", v) for k, v in result.items()}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
