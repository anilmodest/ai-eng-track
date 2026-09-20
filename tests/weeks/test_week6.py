"""Week 6 gate: a deployed, non-deterministic system must say what it is, and be checkable after
every deploy and every rollback, by a script, in under a minute."""

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
