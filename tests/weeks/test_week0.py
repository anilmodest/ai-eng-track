"""Week 0 gate: the service works before any model is involved."""

import pytest
from httpx import AsyncClient

from app.jobs.queue import InMemoryQueue
from tests.conftest import upload

pytestmark = pytest.mark.week0


async def test_health(api: AsyncClient) -> None:
    r = await api.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


async def test_upload_then_read_back(api: AsyncClient) -> None:
    doc_id = await upload(api, "invoice.md")
    r = await api.get(f"/documents/{doc_id}")
    assert r.status_code == 200
    body = r.json()
    assert body["filename"] == "invoice.md"
    assert "Northwind" in body["text"]
    assert body["char_count"] == len(body["text"])


async def test_no_model_key_is_a_typed_error_not_a_stack_trace(
    api: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Day one, before a key is pasted: the service still answers like a service."""
    from app.llm import registry
    from app.settings import get_settings

    monkeypatch.setenv("MODEL_PROVIDER", "gemini")
    monkeypatch.setenv("MODEL_API_KEY", "")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    get_settings.cache_clear()
    registry.reset_model_client()
    doc_id = await upload(api)
    r = await api.post(f"/documents/{doc_id}/extract")
    assert r.status_code == 503, r.text
    body = r.json()
    assert body["error"] == "model_not_configured"
    assert "aistudio.google.com" in body["detail"] and ".env" in body["detail"]
    h = (await api.get("/health")).json()
    assert h["model_ready"] is False and "no key" in h["model_hint"]


async def test_health_says_the_model_is_ready_when_it_is(api: AsyncClient) -> None:
    h = (await api.get("/health")).json()
    assert h["model_ready"] is True and h["model_hint"] is None


async def test_unsupported_type_is_a_typed_error(api: AsyncClient) -> None:
    r = await api.post("/documents", files={"file": ("x.docx", b"...")})
    assert r.status_code == 415
    assert r.json()["error"] == "unsupported_type"


async def test_missing_document_is_404(api: AsyncClient) -> None:
    r = await api.get("/documents/999")
    assert r.status_code == 404 and r.json()["error"] == "not_found"


async def test_batch_job_runs_without_blocking(api: AsyncClient, queue: InMemoryQueue) -> None:
    for name in ("invoice.md", "contract.txt", "report.csv"):
        await upload(api, name)
    r = await api.post("/jobs/reindex")
    assert r.status_code == 202
    job_id = r.json()["id"]
    # The API answered before the job finished: that is the whole point of a queue.
    assert (await api.get("/health")).status_code == 200
    await queue.drain()
    r = await api.get(f"/jobs/{job_id}")
    assert r.json()["status"] == "done"
    assert r.json()["detail"] == "reindexed 3 documents"
