"""Does the written material still describe the code? For whoever maintains the track.

Not part of a fellow's gate, deliberately. The pro route asks a fellow to add tests of their own,
and a check that failed because they did would punish the thing it is meant to encourage.

It exists because this drifted twice in one afternoon: growing the golden set from 42 rows to 100
left three documents stating 42, and adding the version filter and the scoped tool left nine
tests undocumented. Both were invisible until someone read the files side by side.

    uv run python scripts/audit_docs.py
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def tests_in(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return set(re.findall(r"(?:async )?def (test_\w+)", path.read_text(encoding="utf-8")))


def main() -> int:
    problems: list[str] = []

    # 1. every test a week runs should be named in that week's CHECKS.md
    for week_dir in sorted(ROOT.glob("weeks/*/")):
        n = week_dir.name
        if not n.isdigit():
            continue
        checks = week_dir / "CHECKS.md"
        if not checks.exists():
            continue
        text = checks.read_text(encoding="utf-8")
        missing = sorted(
            t.removeprefix("test_")
            for t in tests_in(ROOT / "tests" / "weeks" / f"test_week{n}.py")
            if t.removeprefix("test_") not in text
        )
        for name in missing:
            problems.append(f"weeks/{n}/CHECKS.md does not mention {name}")

    # 2. a README may not promise a test that does not exist
    for week_dir in sorted(ROOT.glob("weeks/*/")):
        n = week_dir.name
        if not n.isdigit():
            continue
        readme = week_dir / "README.md"
        if not readme.exists():
            continue
        real = {
            t.removeprefix("test_") for t in tests_in(ROOT / "tests" / "weeks" / f"test_week{n}.py")
        }
        cited = set(re.findall(r"`([a-z][a-z0-9_]{12,})`", readme.read_text(encoding="utf-8")))
        looks_like_a_test = {c for c in cited if c.count("_") >= 2}
        for name in sorted(looks_like_a_test - real):
            # only complain about names that resemble the week's own test vocabulary
            if any(word in name for word in ("_is_", "_are_", "_the_", "_that_", "_a_")):
                problems.append(f"weeks/{n}/README.md cites `{name}`, which is not a test")

    # 3. counts stated in prose should match the files they describe
    golden = ROOT / "eval" / "golden.jsonl"
    if golden.exists():
        rows = len([ln for ln in golden.read_text(encoding="utf-8").splitlines() if ln.strip()])
        for doc in sorted(ROOT.glob("weeks/*/*.md")) + sorted(ROOT.glob("docs/*.md")):
            text = doc.read_text(encoding="utf-8")
            for claim in re.findall(r"ships (\d+)", text):
                if int(claim) != rows:
                    problems.append(
                        f"{doc.relative_to(ROOT)} says the golden set ships "
                        f"{claim}; it holds {rows}"
                    )

    # 4. every eval row must point at a document that exists
    for name in ("golden.jsonl", "retrieval-queries.jsonl", "starter-questions.jsonl"):
        path = ROOT / "eval" / name
        if not path.exists():
            continue
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            row = json.loads(line)
            doc = row.get("doc")
            if doc and not (ROOT / "corpus" / doc).exists():
                problems.append(f"eval/{name}:{i} points at corpus/{doc}, which does not exist")

    if problems:
        print(f"{len(problems)} thing(s) the writing and the code disagree about:\n")
        for p in problems:
            print(f"  {p}")
        return 1
    print("The written material matches the code.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
