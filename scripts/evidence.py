"""`make evidence WEEK=N`: run this week's measurements on a REAL model and keep the numbers.

    make evidence WEEK=2                 # every measurement for week 2
    make evidence WEEK=2 ONLY=context    # one of them again; the others are kept

Writes evidence/week-N.json:

    {"week", "commit", "dirty", "provider", "model", "at", "route", "variant",
     "metrics": {"<measurement>": {...what its script reported...}}}

Rule 2 of the programme: a number that cannot be re-run is a claim. Every number in your decision
record must be in this file, and the gate checks that it is. The file says which commit, provider
and model produced it, so a number from last week's code or a different model is visible.

It refuses to run on the fake providers. The fake model proves the plumbing holds; it says
nothing about whether answers are good, and evidence is about whether answers are good.
"""

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.llm.registry import FAKE_PROVIDERS, PROVIDERS  # noqa: E402
from app.settings import get_settings  # noqa: E402


@dataclass(frozen=True)
class Measure:
    name: str
    cmd: list[str]  # run with `uv run python`, from the repo root
    report: str  # the JSON it writes, relative to the repo root


# Each week's measurements: the command, and the JSON it writes. The scripts are the ones the week
# README names; this only runs them on the real model and keeps what they wrote.
WEEKS: dict[int, list[Measure]] = {
    1: [
        Measure("schema_drill", ["scripts/schema_drill.py"], "reports/schema_drill.json"),
        Measure("tool_drill", ["scripts/tool_drill.py"], "reports/tool_drill.json"),
        Measure("failure_drill", ["scripts/failure_drill.py"], "reports/failure_drill.json"),
    ],
    2: [
        Measure("baseline", ["scripts/baseline.py"], "reports/baseline.json"),
        Measure("retrieval", ["scripts/retrieval_eval.py"], "reports/retrieval.json"),
        Measure("context", ["scripts/context_experiment.py"], "reports/context.json"),
    ],
    3: [
        Measure(
            "eval",
            ["scripts/eval.py", "--judge", "--set", "eval/my-test-set.jsonl"],
            "reports/eval.json",
        ),
        Measure("threshold", ["scripts/threshold_curve.py"], "reports/threshold.json"),
        Measure("judge", ["scripts/judge_agreement.py"], "reports/judge.json"),
        Measure("trajectories", ["scripts/trajectories.py"], "reports/trajectories.json"),
    ],
    4: [
        Measure("compare", ["scripts/compare_week4.py"], "reports/compare.json"),
        Measure("trajectories", ["scripts/trajectories.py"], "reports/trajectories.json"),
        Measure("models", ["scripts/model_compare.py"], "reports/models.json"),
    ],
    5: [
        Measure("attacks", ["scripts/attack.py"], "reports/attacks.json"),
        Measure("privacy", ["scripts/privacy_check.py"], "reports/privacy.json"),
        Measure(
            "traces", ["scripts/trace_report.py", "--db", "data/attack.db"], "reports/traces.json"
        ),
    ],
    6: [
        Measure(
            "eval", ["scripts/eval.py", "--set", "eval/my-test-set.jsonl"], "reports/eval.json"
        ),
        Measure("tradeoffs", ["scripts/tradeoffs.py"], "reports/tradeoffs.json"),
    ],
}


def git(*args: str) -> str:
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def model_in_use() -> tuple[str, str]:
    s = get_settings()
    spec = PROVIDERS.get(s.model_provider)
    fallback = "fake-1" if s.model_provider in FAKE_PROVIDERS else ""
    model = s.model_name or (spec.default_model if spec else fallback)
    return s.model_provider, model


def read_text(path: Path, default: str) -> str:
    return path.read_text(encoding="utf-8").strip() if path.exists() else default


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Run this week's measurements on a real model")
    parser.add_argument("--week", type=int, required=True)
    parser.add_argument("--only", default="", help="re-run one measurement, keep the others")
    parser.add_argument(
        "--allow-fake", action="store_true", help="tests only: let the fake provider through"
    )
    args = parser.parse_args(argv)

    measures = WEEKS.get(args.week)
    if not measures:
        print(f"week {args.week} has no measurements to keep")
        return 0
    if args.only:
        measures = [m for m in measures if m.name == args.only]
        if not measures:
            names = ", ".join(m.name for m in WEEKS[args.week])
            print(f"no measurement called {args.only!r} in week {args.week}; there are: {names}")
            return 2

    provider, model = model_in_use()
    if provider in FAKE_PROVIDERS and not args.allow_fake:
        print(f"MODEL_PROVIDER is {provider}: evidence needs a real model.")
        print("Set MODEL_PROVIDER and a key in .env (make live-check proves it works), then rerun.")
        return 2

    out_path = ROOT / "evidence" / f"week-{args.week}.json"
    previous: dict[str, Any] = {}
    if out_path.exists() and args.only:
        previous = json.loads(out_path.read_text(encoding="utf-8")).get("metrics", {})

    metrics: dict[str, Any] = dict(previous)
    failed: list[str] = []
    for m in measures:
        script = ROOT / m.cmd[0]
        if not script.exists():
            print(f"\n=== {m.name}: {m.cmd[0]} is not in this repository yet")
            failed.append(m.name)
            continue
        print(f"\n=== {m.name}: uv run python {' '.join(m.cmd)}")
        report = ROOT / m.report
        report.unlink(missing_ok=True)
        r = subprocess.run(["uv", "run", "python", *m.cmd], cwd=ROOT, env=dict(os.environ))
        if not report.exists():
            print(f"=== {m.name}: wrote no {m.report} (exit {r.returncode})")
            failed.append(m.name)
            continue
        metrics[m.name] = json.loads(report.read_text(encoding="utf-8"))
        # A gate script exits 1 when it is under a threshold; the numbers are still evidence.
        print(
            f"=== {m.name}: kept {m.report}" + (f" (exit {r.returncode})" if r.returncode else "")
        )

    record = {
        "week": args.week,
        "commit": git("rev-parse", "HEAD"),
        "dirty": bool(git("status", "--porcelain")),
        "provider": provider,
        "model": model,
        "at": datetime.now(UTC).isoformat(timespec="seconds"),
        "route": read_text(ROOT / ".route", "start"),
        "variant": read_text(ROOT / ".variant", "default"),
        "metrics": metrics,
    }
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    sha = str(record["commit"])[:7]
    print(f"\nwrote {out_path.relative_to(ROOT)} ({provider} / {model}, commit {sha})")
    if record["dirty"]:
        print("  note: uncommitted changes; commit, then rerun, so the commit in the file is real")
    if failed:
        print(f"  not measured: {', '.join(failed)}")
        return 1
    print(f"  now write decisions/week-{args.week}.md from these numbers (DECISION_TEMPLATE.md)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
