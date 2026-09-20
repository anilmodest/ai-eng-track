"""The weekly gate: `make check WEEK=N`.

Runs lint, types, and the tests for every week up to N, once per fake provider so a provider
switch is proven rather than claimed. Writes reports/week-N.json. Exit code is the verdict.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FAKE_PROVIDERS = ["fake_a", "fake_b"]


def run(label: str, cmd: list[str], env: dict[str, str] | None = None) -> bool:
    print(f"\n=== {label}: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=ROOT, env={**os.environ, **(env or {})})
    ok = result.returncode == 0
    print(f"=== {label}: {'PASS' if ok else 'FAIL'}")
    return ok


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--week", type=int, default=0)
    parser.add_argument("--skip-static", action="store_true", help="tests only")
    args = parser.parse_args()

    route_file = ROOT / ".route"
    route = route_file.read_text().strip() if route_file.exists() else "start"
    tiers = {"start": [], "core": ["core"], "pro": ["core", "pro"]}[route]
    deselect = [m for m in ("core", "pro") if m not in tiers]
    marker_expr = " and ".join(f"not {m}" for m in deselect)

    results: dict[str, bool] = {}
    if not args.skip_static:
        results["ruff"] = run("ruff", ["uv", "run", "ruff", "check", "."])
        results["format"] = run("format", ["uv", "run", "ruff", "format", "--check", "."])
        results["mypy"] = run("mypy", ["uv", "run", "mypy"])

    week_files = [str(ROOT / "tests" / "unit")]
    for w in range(args.week + 1):
        f = ROOT / "tests" / "weeks" / f"test_week{w}.py"
        if f.exists():
            week_files.append(str(f))

    providers = FAKE_PROVIDERS if args.week >= 1 else FAKE_PROVIDERS[:1]
    for provider in providers:
        cmd = ["uv", "run", "pytest", "-q", *week_files]
        if marker_expr:
            cmd += ["-m", marker_expr]
        results[f"tests[{provider}]"] = run(
            f"tests with MODEL_PROVIDER={provider}",
            cmd,
            env={
                "MODEL_PROVIDER": provider,
                "EMBED_PROVIDER": "hash",
                "CHECK_WEEK": str(args.week),
                "CHECK_ROUTE": route,
            },
        )

    # Week 3+: the evaluation gate is part of the check, against the CI thresholds.
    if args.week >= 3 and (ROOT / "scripts" / "eval.py").exists():
        results["eval-gate"] = run(
            "evaluation gate (fake model, hash embedder, CI thresholds)",
            [
                "uv",
                "run",
                "python",
                "scripts/eval.py",
                "--thresholds",
                "eval/thresholds-ci.json",
                "--db",
                "data/eval-check.db",
            ],
            env={
                "MODEL_PROVIDER": "fake_a",
                "EMBED_PROVIDER": "hash",
                "CHUNK_STRATEGY": "paragraph",
            },
        )

    # Week 5+: no attack in eval/attacks.jsonl may succeed against the guarded service.
    if args.week >= 5 and (ROOT / "scripts" / "attack.py").exists():
        results["attack-gate"] = run(
            "attack gate (fake model, guard on)",
            ["uv", "run", "python", "scripts/attack.py", "--db", "data/attack-check.db"],
            env={
                "MODEL_PROVIDER": "fake_a",
                "EMBED_PROVIDER": "hash",
                "CHUNK_STRATEGY": "paragraph",
            },
        )

    report_path = ROOT / "reports" / f"week-{args.week}.json"
    report = json.loads(report_path.read_text()) if report_path.exists() else {}
    report["gates"] = results
    report["ok"] = all(results.values())
    report_path.parent.mkdir(exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2))

    print(f"\n=== Summary (route: {route}, week: {args.week})")
    for k, v in results.items():
        print(f"  {'PASS' if v else 'FAIL'}  {k}")
    print(f"  report: {report_path.relative_to(ROOT)}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
