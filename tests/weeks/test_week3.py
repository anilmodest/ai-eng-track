"""Week 3 gate: a system that always answers is worse than one that sometimes declines.

The fake model answers from the passage that shares most words with the question and admits
"not grounded" when little overlaps. That is enough to test every mechanism here: threshold
abstention before any call, model-declared abstention after, citations that resolve to real
chunks, and an evaluation script that blocks when its numbers are not met.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from httpx import AsyncClient

from app.llm.providers.fake import FakeClient

pytestmark = pytest.mark.week3

ROOT = Path(__file__).parent.parent.parent
CORPUS = ROOT / "corpus"


async def _load_and_index(api: AsyncClient) -> None:
    for path in sorted(p for p in CORPUS.iterdir() if p.is_file()):
        r = await api.post("/documents", files={"file": (path.name, path.read_bytes())})
        assert r.status_code == 201, r.text
    r = await api.post("/index", params={"strategy": "paragraph"})
    assert r.status_code == 200


@pytest.fixture(autouse=True)
def _paragraphs(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.settings import get_settings

    monkeypatch.setenv("CHUNK_STRATEGY", "paragraph")
    get_settings.cache_clear()


async def test_answers_with_citations_that_resolve(api: AsyncClient, fake: FakeClient) -> None:
    await _load_and_index(api)
    r = await api.post("/ask", json={"question": "What is the personal car mileage rate?"})
    assert r.status_code == 200, r.text
    out = r.json()
    assert out["abstained"] is False
    assert "45 pence" in out["answer"]
    assert out["citations"], "an answer without a citation is not grounded"
    c = out["citations"][0]
    assert c["filename"] == "policy-contoso-expenses.md"
    assert c["chunk_id"] > 0 and "45 pence" in c["text"]
    assert out["tokens_in"] > 0 and out["cost_usd"] > 0


async def test_abstains_below_threshold_without_calling_the_model(
    api: AsyncClient, fake: FakeClient
) -> None:
    await _load_and_index(api)
    r = await api.post("/ask", json={"question": "zxq plimbo vortex kettle"})
    out = r.json()
    assert out["abstained"] is True
    assert "threshold" in out["reason"]
    assert fake.calls == 0, "declining should cost nothing"
    assert out["cost_usd"] == 0


async def test_abstains_when_the_model_says_not_grounded(
    api: AsyncClient, fake: FakeClient
) -> None:
    await _load_and_index(api)
    fake.script = ["ungrounded"]
    r = await api.post("/ask", json={"question": "What is the personal car mileage rate?"})
    out = r.json()
    assert out["abstained"] is True
    assert out["reason"] == "the passages do not contain the answer"
    assert out["answer"] is None and out["citations"] == []
    assert fake.calls == 1


async def test_unanswerable_question_is_declined(api: AsyncClient, fake: FakeClient) -> None:
    await _load_and_index(api)
    r = await api.post("/ask", json={"question": "What is the capital of Australia?"})
    assert r.json()["abstained"] is True


async def test_citation_numbers_outside_the_context_are_dropped(
    api: AsyncClient, fake: FakeClient
) -> None:
    await _load_and_index(api)
    fake.script = ["badcite"]  # cites [7]; only 5 passages were sent
    r = await api.post("/ask", json={"question": "What is the personal car mileage rate?"})
    assert r.status_code == 200, "an out-of-range citation must not crash the request"
    out = r.json()
    assert out["abstained"] is True, "an answer with no valid citation is not grounded"
    assert out["citations"] == []


async def test_valid_citations_map_to_real_chunks(api: AsyncClient, fake: FakeClient) -> None:
    await _load_and_index(api)
    r = await api.post("/ask", json={"question": "What is the personal car mileage rate?", "k": 1})
    out = r.json()
    assert out["abstained"] is False
    assert [c["n"] for c in out["citations"]] == [1]


async def test_provider_failure_is_not_an_abstention(api: AsyncClient, fake: FakeClient) -> None:
    await _load_and_index(api)
    fake.script = ["400"]
    r = await api.post("/ask", json={"question": "What is the personal car mileage rate?"})
    assert r.status_code == 502
    assert r.json()["error"] == "provider_error"


def _run_eval(*extra: str) -> subprocess.CompletedProcess[str]:
    env = {
        "MODEL_PROVIDER": "fake_a",
        "EMBED_PROVIDER": "hash",
        "CHUNK_STRATEGY": "paragraph",
        "PATH": __import__("os").environ["PATH"],
        "SYSTEMROOT": __import__("os").environ.get("SYSTEMROOT", ""),
    }
    return subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "eval.py"),
            "--thresholds",
            str(ROOT / "eval" / "thresholds-ci.json"),
            "--db",
            str(ROOT / "data" / "eval-test.db"),
            "--corpus",
            "core",
            *extra,
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )


def test_eval_gate_passes_on_ci_thresholds() -> None:
    p = _run_eval()
    assert p.returncode == 0, p.stdout + p.stderr
    assert "GATE PASS" in p.stdout


def test_eval_gate_blocks_when_a_threshold_is_not_met() -> None:
    p = _run_eval("--min-hit", "1.01")
    assert p.returncode == 1
    assert "GATE FAIL" in p.stdout
    assert "hit_rate" in p.stdout and "FAIL" in p.stdout


# ---- Your own test set: eval/my-test-set.jsonl ----------------------------------------------


def _jsonl(path: Path) -> list[dict[str, Any]]:
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    return [json.loads(x) for x in lines if x.strip()]


def _ngrams(text: str, n: int = 8) -> set[tuple[str, ...]]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {tuple(words[i : i + n]) for i in range(len(words) - n + 1)}


def test_my_test_set_has_100_questions_in_the_required_composition() -> None:
    rows = _jsonl(ROOT / "eval" / "my-test-set.jsonl")
    kinds = [r.get("kind") for r in rows]
    assert len(rows) == 100, f"{len(rows)} questions; the set is exactly 100"
    assert kinds.count("straightforward") == 60, "60 straightforward"
    assert kinds.count("no_answer") == 20, "20 the documents cannot answer"
    assert kinds.count("version") == 20, "20 that depend on the version"
    assert len({r["id"] for r in rows}) == 100 and len({r["q"].lower() for r in rows}) == 100
    corpus = {p.name for p in CORPUS.rglob("*") if p.is_file()}
    for r in rows:
        if r["kind"] == "no_answer":
            assert not r.get("expect"), r["id"]
            continue
        assert r.get("expect") and r.get("doc") in corpus, r["id"]
        if r["kind"] == "version":
            assert r.get("version") in ("v2", "v3"), r["id"]


def test_my_test_set_is_written_from_what_a_user_would_ask() -> None:
    """Not from the documents, and not from the programme's set. The cheapest honest check: a
    question that repeats eight words in a row from a document was copied from it."""
    rows = _jsonl(ROOT / "eval" / "my-test-set.jsonl")
    golden = {r["q"].lower() for r in _jsonl(ROOT / "eval" / "golden.jsonl")}
    assert not [r["id"] for r in rows if r["q"].lower() in golden], "copied from golden.jsonl"
    seen: set[tuple[str, ...]] = set()
    for p in CORPUS.rglob("*"):
        if p.is_file() and p.suffix in (".md", ".txt", ".csv"):
            seen |= _ngrams(p.read_text(encoding="utf-8"))
    copied = [r["id"] for r in rows if _ngrams(r["q"]) & seen]
    assert len(copied) <= 5, f"these repeat a document word for word: {copied}"


# ---- The judge you build: app/eval/judge.py -------------------------------------------------


def test_the_judge_prompt_is_written() -> None:
    from app.eval.judge import PROMPT_PATH

    prompt = PROMPT_PATH.read_text(encoding="utf-8")
    assert prompt.startswith("TASK: judge") and "TODO" not in prompt
    for word in ("claim", "faithful", "unsupported"):
        assert word in prompt.lower(), word


async def test_the_judge_grades_faithfulness_from_the_passages(env: None) -> None:
    from app.eval.judge import judge

    passages = [
        "The timeout is the environment variable KESTREL_CONNECT_TIMEOUT, in whole seconds. "
        "The default is 15 seconds."
    ]
    good = await judge("What is the timeout?", passages, "The default timeout is 15 seconds.")
    assert good.faithful and good.claims >= 1 and good.supported == good.claims
    bad = await judge(
        "What is the timeout?",
        passages,
        "The default timeout is 15 seconds. Restart the billing service after changing it.",
    )
    assert not bad.faithful and bad.supported < bad.claims
    assert any("billing" in c for c in bad.unsupported)


def test_judge_labels_are_thirty_answers_you_labelled() -> None:
    rows = _jsonl(ROOT / "eval" / "judge-labels.jsonl")
    labelled = [r for r in rows if isinstance(r.get("label"), bool)]
    assert len(labelled) >= 30, f"{len(labelled)} labelled; scripts/judge_agreement.py --sample 30"
    for r in labelled:
        assert r.get("q") and r.get("answer") and r.get("passages"), r.get("id")
    assert 0 < sum(r["label"] for r in labelled) < len(labelled), (
        "some of each, or it tests nothing"
    )


# ---- Trajectories: eval/trajectories.jsonl and app/eval/trajectory.py -----------------------


def test_trajectory_set_has_twenty_well_formed_tasks() -> None:
    from app.eval.trajectory import KNOWN_TOOLS, TrajectoryTask

    tasks = [TrajectoryTask.model_validate(r) for r in _jsonl(ROOT / "eval" / "trajectories.jsonl")]
    assert len(tasks) >= 20, f"{len(tasks)} tasks; write at least 20"
    assert len({t.id for t in tasks}) == len(tasks)
    for t in tasks:
        used = set(t.expect_tools) | set(t.expect_args) | set(t.forbid_tools)
        assert used <= KNOWN_TOOLS, (t.id, used - KNOWN_TOOLS)
    assert sum(1 for t in tasks if "version" in t.expect_args.get("search_docs", {})) >= 3
    assert sum(1 for t in tasks if {"issue_credit", "escalate"} & set(t.forbid_tools)) >= 3


def test_trajectory_scoring_reads_the_path() -> None:
    from app.eval.trajectory import TrajectoryTask, score

    task = TrajectoryTask(
        id="x",
        task="C-1004 asks about the default connection timeout.",
        expect_tools=["get_customer", "search_docs"],
        expect_args={"search_docs": {"version": "v3"}},
        forbid_tools=["issue_credit"],
        max_steps=3,
    )
    good = [("get_customer", {"customer_id": "C-1004"}), ("search_docs", {"version": "V3"})]
    s = score(
        task,
        good,
        status="done",
        executed=["get_customer", "search_docs"],
        approved=set(),
        cost_usd=0.001,
    )
    assert s.correct
    wrong = [("search_docs", {"version": "v2"}), ("get_customer", {}), ("issue_credit", {})]
    s = score(
        task,
        wrong,
        status="done",
        executed=["search_docs", "get_customer", "issue_credit"],
        approved=set(),
        cost_usd=0.0,
    )
    assert not s.correct and not s.right_first_tool and not s.args_match
    assert s.forbidden_used == ["issue_credit"] and s.unapproved_actions == 1


def _script(name: str, *args: str) -> dict[str, Any]:
    env = {
        **os.environ,
        "MODEL_PROVIDER": "fake_a",
        "EMBED_PROVIDER": "hash",
        "CHUNK_STRATEGY": "paragraph",
        "EVAL_CORPUS": "core",
    }
    r = subprocess.run(
        [sys.executable, f"scripts/{name}.py", *args],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    out = {"trajectories": "trajectories.json", "threshold_curve": "threshold.json"}[name]
    report: dict[str, Any] = json.loads((ROOT / "reports" / out).read_text())
    return report


def test_the_trajectory_command_runs() -> None:
    report = _script("trajectories")
    assert report["summary"]["n"] >= 3


def test_the_threshold_curve_runs_and_declines_more_as_it_rises() -> None:
    curve = _script("threshold_curve")["curve"]
    assert len(curve) == 7
    declines = [p["correct_declines"] + p["wrong_declines"] for p in curve]
    assert declines == sorted(declines)
