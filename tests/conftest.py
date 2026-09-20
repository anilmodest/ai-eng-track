"""Shared fixtures: a fresh SQLite file, an in-memory queue and a scripted fake model per test."""

import json
import os
from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from app.db import session as db_session
from app.jobs import queue as job_queue
from app.jobs.queue import InMemoryQueue
from app.llm import registry
from app.llm.providers.fake import FakeClient
from app.settings import get_settings

SAMPLES = Path(__file__).parent.parent / "samples"


@pytest.fixture
def env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path.as_posix()}/test.db")
    monkeypatch.setenv("REDIS_URL", "")
    monkeypatch.setenv("MODEL_PROVIDER", os.environ.get("MODEL_PROVIDER") or "fake_a")
    monkeypatch.setenv("MODEL_API_KEY", "")
    monkeypatch.setenv("MODEL_FALLBACK_PROVIDER", "")
    monkeypatch.setenv("MODEL_TIMEOUT_S", "0.2")
    monkeypatch.setenv("MODEL_RETRY_BASE_DELAY_S", "0.001")
    get_settings.cache_clear()
    db_session.reset_engine()
    job_queue.reset_queue()
    registry.reset_model_client()
    yield
    get_settings.cache_clear()
    db_session.reset_engine()
    job_queue.reset_queue()
    registry.reset_model_client()


@pytest.fixture
def fake(env: None) -> FakeClient:
    """A scripted model. Tests call fake.script = [...] before the request they care about."""
    from app.main import app

    client = FakeClient(name=get_settings().model_provider, script="ok")
    app.dependency_overrides[registry.get_model_client] = lambda: client
    return client


@pytest.fixture
def queue(env: None) -> InMemoryQueue:
    q = job_queue.get_queue()
    assert isinstance(q, InMemoryQueue)
    return q


@pytest.fixture
async def api(env: None) -> AsyncIterator[AsyncClient]:
    from app.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


async def upload(api: AsyncClient, name: str = "invoice.md") -> int:
    r = await api.post("/documents", files={"file": (name, (SAMPLES / name).read_bytes())})
    assert r.status_code == 201, r.text
    return int(r.json()["id"])


# ---- reports/week-N.json: what the progress page and the mentor read -----------------------


_results: dict[str, str] = {}


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    if report.when == "call" or (report.when == "setup" and report.failed):
        _results[report.nodeid] = "passed" if report.passed else "failed"


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    week = os.environ.get("CHECK_WEEK")
    if week is None:
        return
    results = _results
    out = {
        "week": int(week),
        "route": os.environ.get("CHECK_ROUTE", "start"),
        "passed": sum(1 for v in results.values() if v == "passed"),
        "failed": sum(1 for v in results.values() if v == "failed"),
        "tests": [
            {"id": k.split("::")[-1], "file": k.split("::")[0], "outcome": v}
            for k, v in sorted(results.items())
        ],
    }
    Path("reports").mkdir(exist_ok=True)
    Path(f"reports/week-{week}.json").write_text(json.dumps(out, indent=2))
