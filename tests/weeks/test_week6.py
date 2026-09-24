"""Week 6 gate: a deployed, non-deterministic system must say what it is, and be checkable after
every deploy and every rollback, by a script, in under a minute."""

import json
import subprocess
import sys
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from app.llm.providers.fake import FakeClient
from scripts import smoke

pytestmark = pytest.mark.week6

ROOT = Path(__file__).parent.parent.parent


async def test_health_says_what_is_running(api: AsyncClient) -> None:
    h = (await api.get("/health")).json()
    assert h["status"] == "ok"
    assert h["version"] and h["git_sha"]
    assert h["prompts"] == {"extract": "extract_v1", "ask": "ask_v1"}
    assert h["provider"] in {"fake_a", "fake_b"}
    assert h["guard_enabled"] is True and h["kill_switch"] is False


async def test_health_reflects_the_build_the_deploy_wrote(
    api: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("GIT_SHA", "abc1234")
    monkeypatch.setenv("APP_VERSION", "v1.2.0")
    h = (await api.get("/health")).json()
    assert h["git_sha"] == "abc1234" and h["version"] == "v1.2.0"


async def test_smoke_test_passes_against_the_service(fake: FakeClient) -> None:
    from app.main import app

    code = await smoke.run("http://smoke", transport=ASGITransport(app=app))
    assert code == 0


async def test_smoke_test_fails_on_the_wrong_commit(fake: FakeClient) -> None:
    from app.main import app

    code = await smoke.run("http://smoke", expect_sha="deadbeef", transport=ASGITransport(app=app))
    assert code == 1


async def test_smoke_test_treats_the_kill_switch_as_intended(
    fake: FakeClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.main import app
    from app.settings import get_settings

    monkeypatch.setenv("KILL_SWITCH", "true")
    get_settings.cache_clear()
    code = await smoke.run("http://smoke", transport=ASGITransport(app=app))
    assert code == 0
    assert fake.calls == 0


async def test_live_traffic_can_be_sampled_and_scored(
    api: AsyncClient, fake: FakeClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Two /ask requests leave notes on their root spans; the sampler finds and judges them."""
    import io
    from contextlib import redirect_stdout

    from app.settings import get_settings
    from scripts import sample_live

    monkeypatch.setenv("CHUNK_STRATEGY", "paragraph")
    get_settings.cache_clear()
    corpus = ROOT / "corpus"
    for path in sorted(corpus.iterdir()):
        await api.post("/documents", files={"file": (path.name, path.read_bytes())})
    await api.post("/index", params={"strategy": "paragraph"})
    await api.post("/ask", json={"question": "What is the personal car mileage rate?"})
    await api.post("/ask", json={"question": "zxq plimbo vortex kettle"})
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = await sample_live.run(n=10, judge=True)
    out = buf.getvalue()
    assert code == 0
    assert "recent /ask requests" in out and "judge mean" in out, out
    report = json.loads((ROOT / "reports" / "live-sample.json").read_text())
    answered = [r for r in report["rows"] if not r["declined"]]
    assert answered and answered[0]["judge_score"] == 4  # the fake judge


async def test_smoke_test_skips_exercises_that_are_not_built_yet() -> None:
    """A fellow at Week 1 must still be able to release: 501 is "not built", not "broken".

    Driven against a stand-in service that answers like the template does before Week 3.
    """
    import io
    from contextlib import redirect_stdout

    from fastapi import FastAPI
    from fastapi.responses import JSONResponse

    stub = FastAPI()
    not_built = JSONResponse(
        status_code=501, content={"error": "not_implemented", "detail": "Week 3"}
    )

    @stub.get("/health")
    def _health() -> dict[str, object]:
        return {"status": "ok", "version": "v0", "git_sha": "abc1234", "provider": "fake_a"}

    @stub.post("/documents", status_code=201)
    def _upload() -> dict[str, int]:
        return {"id": 1}

    @stub.get("/documents/{doc_id}")
    def _doc(doc_id: int) -> dict[str, str]:
        return {"text": "Northwind Traders invoice"}

    @stub.post("/documents/{doc_id}/extract")
    def _extract(doc_id: int) -> JSONResponse:
        return not_built

    @stub.post("/ask")
    def _ask() -> JSONResponse:
        return not_built

    buf = io.StringIO()
    with redirect_stdout(buf):
        code = await smoke.run("http://stub", transport=ASGITransport(app=stub))
    out = buf.getvalue()
    assert code == 0, out
    assert "extract: Week 1 not built yet" in out and "ask: Week 3 not built yet" in out


def test_a_wrong_answer_still_fails_even_when_other_weeks_are_unbuilt() -> None:
    from httpx import Response

    from scripts.smoke import _not_built

    assert _not_built(Response(501, json={"error": "not_implemented", "detail": "x"})) is True
    assert _not_built(Response(501, json={"error": "provider_error", "detail": "x"})) is False
    assert _not_built(Response(500, text="boom")) is False
    assert _not_built(Response(200, json={"ok": True})) is False


def test_deploy_workflow_supports_rollback_by_ref() -> None:
    wf = (ROOT / ".github" / "workflows" / "deploy.yml").read_text(encoding="utf-8")
    assert "workflow_dispatch" in wf and "ref:" in wf
    assert "build_info.py" in wf, "the deploy must stamp the commit into the service"
    assert "smoke.py" in wf, "every deploy ends with the smoke test"


def test_smoke_script_is_runnable_standalone() -> None:
    p = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "smoke.py"), "--help"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert p.returncode == 0 and "expect-sha" in p.stdout
