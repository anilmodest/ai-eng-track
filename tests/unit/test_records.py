"""The weekly records: a decision whose numbers match the evidence, and an honest AI-use log."""

import json
from pathlib import Path

from scripts.records import check_ai_use, check_decision, lookup

DECISION = """# Week 1 decision

## Decision
Retry 429 and 5xx three times with a 20 second timeout; never retry a 400.

## Options
- three attempts, 20 s timeout
- five attempts, 60 s timeout

## Evidence
- failure_drill.gemini.recovered_rate = 0.95
- tool_drill.after.correct_rate = 85% (was 55%)

## Rejected
Five attempts: p95 latency rose to 41 s for no extra recoveries.

## Risk accepted
A long provider outage still fails the request; the fallback provider covers it.
"""


def _write(root: Path, decision: str = DECISION, metrics: dict[str, object] | None = None) -> None:
    (root / "decisions").mkdir()
    (root / "decisions" / "week-1.md").write_text(decision, encoding="utf-8")
    (root / "evidence").mkdir()
    metrics = metrics or {
        "failure_drill": {"gemini": {"recovered_rate": 0.951}},
        "tool_drill": {"after": {"correct_rate": 0.85}},
    }
    (root / "evidence" / "week-1.json").write_text(json.dumps({"metrics": metrics}))


def test_a_complete_record_whose_numbers_match_passes(tmp_path: Path) -> None:
    _write(tmp_path)
    check = check_decision(1, tmp_path)
    assert check.ok, check.problems
    assert check.numbers_match and len(check.evidence_lines) == 2
    assert len(check.options) == 2 and "Five attempts" in check.rejected


def test_a_number_the_evidence_does_not_say_fails(tmp_path: Path) -> None:
    _write(tmp_path, metrics={"failure_drill": {"gemini": {"recovered_rate": 0.81}}})
    check = check_decision(1, tmp_path)
    assert not check.ok and not check.numbers_match
    assert any("says 0.95" in p for p in check.problems)
    assert any("tool_drill.after.correct_rate" in p for p in check.problems)


def test_missing_sections_and_missing_evidence_are_named(tmp_path: Path) -> None:
    _write(tmp_path, decision="# x\n\n## Decision\nsomething\n\n## Options\n- one\n")
    (tmp_path / "evidence" / "week-1.json").unlink()
    problems = " | ".join(check_decision(1, tmp_path).problems)
    assert "'Rejected' is empty" in problems and "at least two options" in problems
    assert "make evidence WEEK=1" in problems
    assert not check_decision(2, tmp_path).present


def test_lookup_walks_dicts_and_lists() -> None:
    metrics = {"configs": [{"mrr": 0.4}, {"mrr": 0.7}], "a": {"b": 1}}
    assert lookup(metrics, "configs[1].mrr") == 0.7
    assert lookup(metrics, "a.b") == 1
    assert lookup(metrics, "a.c") is None and lookup(metrics, "configs[5].mrr") is None


def test_ai_use_log(tmp_path: Path) -> None:
    (tmp_path / "ai-use").mkdir()
    log = tmp_path / "ai-use" / "week-1.yml"
    log.write_text(
        "hours: 9\nentries:\n"
        "  - {when: 2026-10-20, tool: Copilot, asked: retry loop, produced: code,"
        " checked: ran the 429 drill, kept: partly}\n"
        "  - {when: 2026-10-21, tool: Claude, asked: schema, produced: a model,"
        " checked: '', kept: yes}\n",
        encoding="utf-8",
    )
    check = check_ai_use(1, tmp_path)
    assert check.hours == 9 and check.entries == 2 and check.checked_entries == 1
    assert check.kept == {"partly": 1, "yes": 1}
    assert not check.ok and "entry 2 does not say what you checked" in check.problems
    log.write_text("hours: 4\nentries: []\n", encoding="utf-8")
    assert check_ai_use(1, tmp_path).ok  # no assistant used is a valid, honest answer
    assert not check_ai_use(3, tmp_path).present


def test_an_evidence_key_with_a_plus_is_checked(tmp_path: Path) -> None:
    # Week 2's own example: retrieval.configs.section+hybrid.hit_rate
    decision = DECISION.replace(
        "- tool_drill.after.correct_rate = 85% (was 55%)",
        "- retrieval.configs.section+hybrid.hit_rate = 0.82",
    )
    metrics: dict[str, object] = {
        "failure_drill": {"gemini": {"recovered_rate": 0.951}},
        "retrieval": {"configs": {"section+hybrid": {"hit_rate": 0.82}}},
    }
    _write(tmp_path, decision=decision, metrics=metrics)
    check = check_decision(1, tmp_path)
    assert check.ok, check.problems
    assert len(check.evidence_lines) == 2
