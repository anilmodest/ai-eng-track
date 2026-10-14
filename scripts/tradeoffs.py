"""Week 6: the trade-off table, compiled from your six decision records. Nothing typed twice.

    uv run python scripts/tradeoffs.py              # writes reports/tradeoffs.json and .md

One row per week that has a decision record: what you chose, the numbers behind it (from the
evidence file, as the gate checked them), what you rejected and the risk you accepted. This is the
table your write-up and the defence start from; an interviewer's "what did you trade off?" is
answered by reading it. A week whose numbers do not match its evidence is shown, and marked.
"""

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.records import check_decision  # noqa: E402


def first_sentence(text: str) -> str:
    text = " ".join(line.strip("|- ") for line in text.splitlines() if line.strip())
    return text.split(". ")[0].rstrip(".") + "." if text else ""


def main() -> int:
    rows: list[dict[str, Any]] = []
    for week in range(1, 7):
        d = check_decision(week)
        if not d.present:
            continue
        rows.append(
            {
                "week": week,
                "decision": first_sentence(d.decision),
                "evidence": [
                    {"key": e.key, "value": e.actual, "ok": e.ok} for e in d.evidence_lines
                ],
                "rejected": first_sentence(d.rejected),
                "risk": first_sentence(d.risk),
                "numbers_match": d.numbers_match,
            }
        )
    out = ROOT / "reports"
    out.mkdir(exist_ok=True)
    (out / "tradeoffs.json").write_text(json.dumps({"weeks": rows}, indent=2), encoding="utf-8")
    lines = [
        "| Week | We chose | Because | We rejected | Risk accepted |",
        "| --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        because = "; ".join(
            f"{e['key']} = {e['value']:g}" for e in r["evidence"] if e["value"] is not None
        )
        mark = "" if r["numbers_match"] else " (numbers do not match the evidence)"
        lines.append(
            f"| {r['week']} | {r['decision']} | {because}{mark} | {r['rejected']} | {r['risk']} |"
        )
    (out / "tradeoffs.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\n{len(rows)} decision records compiled -> reports/tradeoffs.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
