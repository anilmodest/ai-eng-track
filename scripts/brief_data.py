"""What your mentor's weekly brief is built from, collected from this repository into one file.

    uv run python scripts/brief_data.py --week 3       # writes reports/brief.json

CI runs it on every pull request and uploads the file as the artifact `brief-data`. The programme
builds your mentor's one-page brief from it, beside the hidden-evaluation result, so your mentor
reads one page instead of your pull request. Nothing in it is typed by hand and nothing in it is
hidden from you: run it yourself and read what your mentor will see.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.records import check_ai_use, check_decision  # noqa: E402

# How the files a fellow changed are grouped on the brief. First match wins.
AREAS: list[tuple[str, str]] = [
    ("app/tools/", "tools"),
    ("app/agents/", "agent"),
    ("app/retrieval/", "retrieval"),
    ("app/llm/", "model layer"),
    ("app/api/", "api"),
    ("app/eval/", "evaluation"),
    ("app/", "service"),
    ("eval/", "test sets"),
    ("tests/", "tests"),
    ("decisions/", "records"),
    ("ai-use/", "records"),
    ("evidence/", "records"),
    ("reflections/", "records"),
    ("scripts/", "scripts"),
    (".github/", "workflows"),
]


def git(*args: str) -> str:
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def read_json(rel: str) -> Any:
    path = ROOT / rel
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def area(path: str) -> str:
    return next((name for prefix, name in AREAS if path.startswith(prefix)), "other")


def changed_files(base: str) -> list[dict[str, Any]]:
    """Files changed on this branch since it left `base`, with lines added and removed."""
    merge_base = git("merge-base", base, "HEAD")
    if not merge_base:
        return []
    rows = []
    for line in git("diff", "--numstat", merge_base, "HEAD").splitlines():
        added, removed, path = line.split("\t", 2)
        rows.append(
            {
                "path": path,
                "area": area(path),
                "added": int(added) if added.isdigit() else 0,
                "removed": int(removed) if removed.isdigit() else 0,
            }
        )
    return rows


def reflection(week: int) -> dict[str, str]:
    path = ROOT / "reflections" / f"week-{week}.md"
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    out: dict[str, str] = {}
    for m in re.finditer(r"^## (Q\d+b?)\.[^\n]*\n(.*?)(?=^## |\Z)", text, flags=re.S | re.M):
        body = re.sub(r"<!--.*?-->", "", m.group(2), flags=re.S).strip()
        out[m.group(1).lower()] = body
    return out


def checks(week: int) -> dict[str, Any]:
    report = read_json(f"reports/week-{week}.json") or {}
    tests = report.get("tests", [])
    failed = [t["id"] for t in tests if t.get("outcome") != "passed"]
    return {
        "ok": bool(report.get("ok")),
        "gates": report.get("gates", {}),
        "total": len(tests),
        "passed": len(tests) - len(failed),
        "failed": failed,
    }


def own_eval(week: int) -> dict[str, Any]:
    """Headline numbers from this week's evidence; falls back to the last eval report."""
    evidence = read_json(f"evidence/week-{week}.json") or {}
    metrics = evidence.get("metrics", {}) if isinstance(evidence, dict) else {}
    source = metrics.get("eval") or read_json("reports/eval.json") or {}
    summary = source.get("summary", source) if isinstance(source, dict) else {}
    return {k: v for k, v in summary.items() if isinstance(v, int | float)}


def build(week: int, base: str) -> dict[str, Any]:
    route_file = ROOT / ".route"
    variant_file = ROOT / ".variant"
    return {
        "week": week,
        "sha": git("rev-parse", "HEAD"),
        "repo": git("config", "--get", "remote.origin.url"),
        "route": route_file.read_text().strip() if route_file.exists() else "start",
        "variant": variant_file.read_text().strip() if variant_file.exists() else "default",
        "checks": checks(week),
        "own_eval": own_eval(week),
        "previous_week_own_eval": own_eval(week - 1) if week > 1 else {},
        "evidence": read_json(f"evidence/week-{week}.json"),
        "decision": check_decision(week).as_dict(),
        "ai_use": check_ai_use(week).as_dict(),
        "reflection": reflection(week),
        "changed_files": changed_files(base),
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Collect the data the mentor brief is built from")
    parser.add_argument("--week", type=int, required=True)
    parser.add_argument("--base", default="origin/main", help="what the branch is compared with")
    parser.add_argument("--out", type=Path, default=ROOT / "reports" / "brief.json")
    args = parser.parse_args(argv)

    data = build(args.week, args.base)
    args.out.parent.mkdir(exist_ok=True)
    args.out.write_text(json.dumps(data, indent=2), encoding="utf-8")
    d, a = data["decision"], data["ai_use"]
    print(
        f"wrote {args.out.relative_to(ROOT) if args.out.is_relative_to(ROOT) else args.out}: "
        f"checks {data['checks']['passed']}/{data['checks']['total']}, "
        f"decision {'ok' if d['ok'] else 'not yet'}, AI-use log {'ok' if a['ok'] else 'not yet'}, "
        f"{len(data['changed_files'])} files changed"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
