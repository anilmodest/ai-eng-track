"""The two records every week ends in, and what the gate checks about them.

    uv run python scripts/records.py --week 3          # prints the verdict; exit code 1 if not

decisions/week-N.md   your decision, written last, from your evidence file (DECISION_TEMPLATE.md)
ai-use/week-N.yml     what an assistant did for you this week, and what you checked
                      (AI_USE_TEMPLATE.yml)

The decision record passes when every section is filled, at least two options are named, a
rejected option is named, and every number under "Evidence" is the number at that key in
evidence/week-N.json. That last rule is the point: an assistant can write the paragraph, but the
paragraph can only say what the runs you chose to make say.

The AI-use log passes when it parses, gives the week's hours, and every entry says what you
checked. It does not judge how much help you had; it records it.

scripts/brief_data.py reads the same functions, so the mentor sees exactly what the gate saw.
"""

import argparse
import json
import math
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
SECTIONS = ("Decision", "Options", "Evidence", "Rejected", "Risk accepted")
_EVIDENCE_LINE = re.compile(r"^\s*[-*]\s*`?([A-Za-z0-9_.\[\]-]+)`?\s*=\s*(-?[0-9][0-9.,]*%?)")


@dataclass
class EvidenceLine:
    key: str
    claimed: float
    actual: float | None
    ok: bool


@dataclass
class DecisionCheck:
    present: bool
    problems: list[str] = field(default_factory=list)
    decision: str = ""
    options: list[str] = field(default_factory=list)
    rejected: str = ""
    risk: str = ""
    evidence_lines: list[EvidenceLine] = field(default_factory=list)

    @property
    def numbers_match(self) -> bool:
        return bool(self.evidence_lines) and all(e.ok for e in self.evidence_lines)

    @property
    def ok(self) -> bool:
        return self.present and not self.problems

    def as_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["numbers_match"] = self.numbers_match
        d["names_rejected"] = bool(self.rejected)
        d["ok"] = self.ok
        return d


@dataclass
class AiUseCheck:
    present: bool
    problems: list[str] = field(default_factory=list)
    hours: float | None = None
    entries: int = 0
    checked_entries: int = 0
    kept: dict[str, int] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.present and not self.problems

    def as_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["ok"] = self.ok
        return d


def _strip_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def _sections(text: str) -> dict[str, str]:
    """`## Heading` -> body, comments removed, for the headings this record uses."""
    found: dict[str, str] = {}
    for m in re.finditer(r"^## (.+?)\s*\n(.*?)(?=^## |\Z)", text, flags=re.S | re.M):
        found[m.group(1).strip()] = _strip_comments(m.group(2)).strip()
    return found


def _bullets(body: str) -> list[str]:
    return [
        line.lstrip("-* ").strip()
        for line in body.splitlines()
        if line.strip().startswith(("-", "*")) and line.lstrip("-* ").strip()
    ]


def _number(token: str) -> float:
    token = token.replace(",", "")
    if token.endswith("%"):
        return float(token[:-1]) / 100
    return float(token)


def lookup(metrics: Any, key: str) -> Any:
    """`tool_drill.after.correct_rate` or `configs[2].mrr` inside the evidence metrics."""
    node = metrics
    for part in re.findall(r"[^.\[\]]+|\[\d+\]", key):
        if part.startswith("["):
            idx = int(part[1:-1])
            if not isinstance(node, list) or idx >= len(node):
                return None
            node = node[idx]
        else:
            if not isinstance(node, dict) or part not in node:
                return None
            node = node[part]
    return node


def _matches(claimed: float, actual: float, token: str) -> bool:
    """Equal at the precision the fellow wrote: 0.85 matches 0.8512, 0.9 does not match 0.86."""
    if math.isclose(claimed, actual, rel_tol=1e-9, abs_tol=1e-12):
        return True
    digits = token.rstrip("%").split(".", 1)
    places = len(digits[1]) if len(digits) == 2 else 0
    if token.endswith("%"):
        return round(actual * 100, places) == round(claimed * 100, places)
    return round(actual, places) == round(claimed, places)


def evidence_metrics(week: int, root: Path = ROOT) -> dict[str, Any] | None:
    path = root / "evidence" / f"week-{week}.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    metrics = data.get("metrics") if isinstance(data, dict) else None
    return metrics if isinstance(metrics, dict) else None


def check_decision(week: int, root: Path = ROOT) -> DecisionCheck:
    path = root / "decisions" / f"week-{week}.md"
    if not path.exists():
        return DecisionCheck(
            present=False,
            problems=[f"decisions/week-{week}.md is missing (copy DECISION_TEMPLATE.md)"],
        )
    found = _sections(path.read_text(encoding="utf-8"))
    out = DecisionCheck(present=True)
    for name in SECTIONS:
        if not found.get(name) or not re.search(r"[A-Za-z0-9]", found[name]):
            out.problems.append(f"section '{name}' is empty")
    out.decision = found.get("Decision", "")
    out.options = _bullets(found.get("Options", ""))
    out.rejected = found.get("Rejected", "")
    out.risk = found.get("Risk accepted", "")
    if len(out.options) < 2:
        out.problems.append("name at least two options you measured")

    metrics = evidence_metrics(week, root)
    if metrics is None:
        out.problems.append(f"evidence/week-{week}.json is missing: run make evidence WEEK={week}")
    for line in found.get("Evidence", "").splitlines():
        m = _EVIDENCE_LINE.match(line)
        if not m:
            continue
        key, token = m.group(1), m.group(2).rstrip(".,")
        claimed = _number(token)
        raw = lookup(metrics, key) if metrics is not None else None
        actual = float(raw) if isinstance(raw, int | float) and not isinstance(raw, bool) else None
        ok = actual is not None and _matches(claimed, actual, token)
        out.evidence_lines.append(EvidenceLine(key=key, claimed=claimed, actual=actual, ok=ok))
        if actual is None and metrics is not None:
            out.problems.append(f"evidence key '{key}' is not in evidence/week-{week}.json")
        elif not ok and actual is not None:
            out.problems.append(f"'{key}' says {token} but the evidence file says {actual:g}")
    if not out.evidence_lines:
        out.problems.append("no evidence lines: one per line as `- <key> = <number>`")
    return out


def check_ai_use(week: int, root: Path = ROOT) -> AiUseCheck:
    path = root / "ai-use" / f"week-{week}.yml"
    if not path.exists():
        return AiUseCheck(
            present=False,
            problems=[f"ai-use/week-{week}.yml is missing (copy AI_USE_TEMPLATE.yml)"],
        )
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        return AiUseCheck(present=True, problems=[f"ai-use/week-{week}.yml does not parse: {e}"])
    out = AiUseCheck(present=True)
    if not isinstance(data, dict):
        out.problems.append("the log must be a mapping with 'hours' and 'entries'")
        return out
    hours = data.get("hours")
    if isinstance(hours, int | float) and not isinstance(hours, bool) and hours > 0:
        out.hours = float(hours)
    else:
        out.problems.append("give the week's hours as a number above 0")
    entries = data.get("entries")
    if not isinstance(entries, list):
        out.problems.append("'entries' must be a list (an empty list if you used no assistant)")
        return out
    for i, entry in enumerate(entries, 1):
        if not isinstance(entry, dict):
            out.problems.append(f"entry {i} is not a mapping")
            continue
        out.entries += 1
        if str(entry.get("checked") or "").strip():
            out.checked_entries += 1
        else:
            out.problems.append(f"entry {i} does not say what you checked")
        if not str(entry.get("tool") or "").strip() or not str(entry.get("asked") or "").strip():
            out.problems.append(f"entry {i} needs the tool and what you asked")
        kept = str(entry.get("kept", "")).strip().lower()
        kept = {"true": "yes", "false": "no"}.get(kept, kept)
        if kept not in ("yes", "partly", "no"):
            out.problems.append(f"entry {i}: kept must be yes, partly or no")
        else:
            out.kept[kept] = out.kept.get(kept, 0) + 1
    return out


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Check this week's decision record and AI-use log")
    parser.add_argument("--week", type=int, required=True)
    parser.add_argument("--json", action="store_true", help="print the result as JSON")
    args = parser.parse_args(argv)

    decision = check_decision(args.week)
    ai_use = check_ai_use(args.week)
    if args.json:
        print(json.dumps({"decision": decision.as_dict(), "ai_use": ai_use.as_dict()}, indent=2))
    else:
        for label, check in (("decision record", decision), ("AI-use log", ai_use)):
            print(f"{'PASS' if check.ok else 'FAIL'}  {label}")
            for problem in check.problems:
                print(f"      - {problem}")
    return 0 if decision.ok and ai_use.ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
