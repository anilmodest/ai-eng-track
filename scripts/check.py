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


ROUTE_MEANS = {
    "start": "every helper is given, and weeks/N/routes/worked_example.py solves a smaller one",
    "core": "faults are planted in the exercise files, and you instrument the tracer yourself",
    "pro": "the helpers are signatures only, and routes/pro.md adds one constraint",
}


def run(label: str, cmd: list[str], env: dict[str, str] | None = None) -> bool:
    print(f"\n=== {label}: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=ROOT, env={**os.environ, **(env or {})})
    ok = result.returncode == 0
    print(f"=== {label}: {'PASS' if ok else 'FAIL'}")
    return ok


def this_weeks_work(week: int) -> tuple[int, int, bool]:
    """(failed, total, all of them are in this week's own test file).

    A red gate means two completely different things and the difference matters more than the
    number. Every failure inside tests/weeks/test_week<N>.py is the exercise: it is red because
    you have not written it yet, and it is red on purpose. A failure anywhere else is a
    regression you have caused in work that used to pass, and that is the one to stop for.
    """
    report = ROOT / "reports" / f"week-{week}.json"
    if not report.exists():
        return (0, 0, False)
    try:
        tests = json.loads(report.read_text()).get("tests", [])
    except json.JSONDecodeError:
        return (0, 0, False)
    failed = [t for t in tests if t.get("outcome") != "passed"]
    mine = [t for t in failed if f"test_week{week}.py" in str(t.get("file", ""))]
    return (len(failed), len(tests), bool(failed) and len(mine) == len(failed))


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

    print(f"=== week {args.week}, route {route}")
    print(f"    {ROUTE_MEANS.get(route, '')}")
    if args.week:
        print(f"    the exercise: weeks/{args.week}/README.md")

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
    # Every gate runs the fake providers and the lexical embedder on purpose: the numbers prove
    # the pipeline holds, not that answers are good. Recorded so nothing downstream shows them
    # as a measure of quality.
    report["provider_mode"] = "fake"
    report["ok"] = all(results.values())
    report_path.parent.mkdir(exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2))

    print(f"\n=== Summary: week {args.week}, route {route}")
    for k, v in results.items():
        print(f"  {'PASS' if v else 'FAIL'}  {k}")
    print(f"  report: {report_path.relative_to(ROOT)}")

    if not report["ok"]:
        failed, total, only_this_week = this_weeks_work(args.week)
        print()
        if only_this_week:
            print(f"  {failed} of {total} checks fail, and all {failed} are in")
            print(
                f"  tests/weeks/test_week{args.week}.py. That is this week's work, not a problem:"
            )
            print("  each failing test name is one behaviour you have not built yet.")
            print("  Run  make next  for the file to open and the first one to build.")
            if route == "start":
                print(f"  On start, weeks/{args.week}/routes/worked_example.py solves a smaller")
                print("  version of the same thing in full. Read it beside the stub.")
        elif failed:
            print(f"  {failed} of {total} checks fail, and some are outside")
            print(f"  tests/weeks/test_week{args.week}.py: work that passed before does not now.")
            print("  Fix those first; a regression is worth more of your attention than a stub.")
            print("  Run  make next  to see which.")
        else:
            print("  The tests pass. Something else above does not: read the first FAIL line.")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
