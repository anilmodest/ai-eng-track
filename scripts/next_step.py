"""`make next`: the one screen that says what to do now.

A red gate tells you nine things are not built. It does not tell you which file to open, and the
week's README is a long document you have to read before you can start. That is three hops before
you type any code, on the morning you are least able to afford them.

This closes the loop: the week you are on, the files that still carry an unbuilt exercise, the
behaviours that are not working yet, and the four things to open, in order.

Nothing here is a second source of truth. The files are found by the markers the stubs already
carry, and the failures come from the last gate run, so this cannot drift from the repository.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

ROUTE_MEANS = {
    "start": "every helper is given, and routes/worked_example.py solves a smaller one in full",
    "core": "faults are planted in the exercise files; the gate catches some, review the rest",
    "pro": "the helpers are signatures only, and routes/pro.md adds one constraint",
}

GOAL = {
    0: "prove the ground the next six weeks stand on, and meet the client's brief",
    1: "a model call that survives failure, never pays twice, and records what it cost",
    2: "retrieval you can choose with a number, and an answer from the right version",
    3: "answers that cite their source, decline when they should, and a gate that "
    "stops a change making things worse",
    4: "a tool that refuses what it should, and three ways to do the same job compared",
    5: "cost and time per step, and a document that tries to take over your service",
    6: "something published that someone else can run, broken on purpose and rolled back",
}


def route() -> str:
    marker = ROOT / ".route"
    value = marker.read_text().strip() if marker.exists() else "start"
    return value if value in ROUTE_MEANS else "start"


def report(week: int) -> dict[str, Any] | None:
    path = ROOT / "reports" / f"week-{week}.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        return None


def current_week() -> int:
    """The first week that is not green. A week with no report has not been run."""
    weeks = sorted(int(p.parent.name) for p in ROOT.glob("weeks/*/README.md"))
    for n in weeks:
        rep = report(n)
        if rep is None or not rep.get("ok"):
            return n
    return weeks[-1]


def unbuilt_files(week: int) -> list[tuple[str, int, str]]:
    """Files still carrying this week's exercise marker, from the markers themselves."""
    pattern = re.compile(rf"(?:TODO Week {week}\b|Week {week}:? (?:exercise|build me))")
    found: list[tuple[str, int, str]] = []
    for path in sorted(ROOT.glob("app/**/*.py")):
        if "__pycache__" in str(path):
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for i, line in enumerate(lines, 1):
            if pattern.search(line):
                note = line.strip().lstrip("#").strip()
                note = re.sub(r'^(return |raise |")', "", note)[:70]
                found.append((str(path.relative_to(ROOT)).replace("\\", "/"), i, note))
                break
    return found


def failing(week: int) -> list[str]:
    rep = report(week)
    if not rep:
        return []
    return [
        str(t.get("id", "")).removeprefix("test_").replace("_", " ")
        for t in rep.get("tests", [])
        if t.get("outcome") != "passed" and f"test_week{week}.py" in str(t.get("file", ""))
    ]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--week", type=int, default=None)
    args = ap.parse_args()

    week = args.week if args.week is not None else current_week()
    r = route()
    rep = report(week)
    week_dir = f"weeks/{week}"

    print(f"\n  Week {week}, route {r}")
    print(f"  {ROUTE_MEANS[r]}")
    print(f"\n  Building: {GOAL.get(week, '')}")

    # Week 0 needs no key, so this is the first place a fellow can be told before they trip.
    if week >= 1:
        from app.llm.keys import HOW, key_ready

        ready, why = key_ready()
        if not ready:
            print(f"\n  BLOCKED: {why}\n")
            print("\n".join("  " + line for line in HOW.splitlines()))
            print("\n  Everything below needs that first.")

    if rep is None:
        print("\n  The gate has not run for this week yet. Start with:\n")
        print(f"      make check WEEK={week}\n")
        print("  Red is expected: each failing check is one thing you have not built.")
        return 0

    files = unbuilt_files(week)
    if files:
        print("\n  Still to build")
        for path, line, note in files:
            print(f"      {path}:{line}")
            if note:
                print(f"          {note}")

    not_working = failing(week)
    if not_working:
        print(f"\n  Not working yet ({len(not_working)}) - each one is a behaviour, in order")
        for name in not_working[:10]:
            print(f"      {name}")
        if len(not_working) > 10:
            print(f"      ... and {len(not_working) - 10} more")

    print("\n  Open, in this order")
    opens: list[tuple[str, str]] = [(f"{week_dir}/README.md", "the exercise, step by step")]
    if files:
        opens.append((files[0][0], "where the TODO is"))
    opens.append((f"tests/weeks/test_week{week}.py", "the contract: what each name means"))
    if r == "start" and (ROOT / week_dir / "routes" / "worked_example.py").exists():
        opens.append((f"{week_dir}/routes/worked_example.py", "a smaller one, solved in full"))
    else:
        opens.append((f"{week_dir}/routes/{r}.md", "what your route gives you"))
    width = max(len(path) for path, _ in opens)
    for path, why in opens:
        print(f"      {path.ljust(width)}   {why}")

    if not files and not not_working and rep.get("ok"):
        print(f"\n  Week {week} is green. Next:")
        print(f"      fill reflections/week-{week}.md   (copy REFLECTION_TEMPLATE.md)")
        print(f"      git switch -c week-{week} && git add -A && git commit -m 'week {week}'")
        print(f"      git push -u origin week-{week} && gh pr create --fill --base main")
    else:
        print(f"\n  Then: make check WEEK={week}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
