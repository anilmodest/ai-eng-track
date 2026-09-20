"""Week 3 gate: a system that always answers is worse than one that sometimes declines.

The fake model answers from the passage that shares most words with the question and admits
"not grounded" when little overlaps. That is enough to test every mechanism here: threshold
abstention before any call, model-declared abstention after, citations that resolve to real
chunks, and an evaluation script that blocks when its numbers are not met.
"""

import subprocess
import sys
from pathlib import Path

import pytest
from httpx import AsyncClient

from app.llm.providers.fake import FakeClient

pytestmark = pytest.mark.week3

ROOT = Path(__file__).parent.parent.parent
CORPUS = ROOT / "corpus"


async def _load_and_index(api: AsyncClient) -> None:
    for path in sorted(CORPUS.iterdir()):
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
    # k=1: the only valid citation is [1]. The fake cites its best passage, which must be [1].
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
