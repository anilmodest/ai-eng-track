"""Week 1 gate: the model is treated as an unreliable, expensive, non-deterministic dependency.

Every test here runs against the scripted fake provider. No key, no network, no cost.
Run the whole file with MODEL_PROVIDER=fake_a and again with MODEL_PROVIDER=fake_b:
the check script does exactly that, which is how "swappable by config" is proven.
"""

import pytest
from httpx import AsyncClient

from app.llm.providers.fake import FakeClient
from tests.conftest import upload

pytestmark = pytest.mark.week1


async def test_extract_returns_schema_valid_json(api: AsyncClient, fake: FakeClient) -> None:
    doc_id = await upload(api)
    r = await api.post(f"/documents/{doc_id}/extract")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["cached"] is False
    assert body["provider"] == fake.name
    ex = body["extract"]
    assert ex["doc_type"] == "invoice"
    assert 3 <= len(ex["key_facts"]) <= 5
    assert len(ex["summary"].split()) <= 60
    assert 0 <= ex["confidence"] <= 1


async def test_malformed_output_is_repaired_once(api: AsyncClient, fake: FakeClient) -> None:
    doc_id = await upload(api)
    fake.script = ["malformed", "ok"]
    r = await api.post(f"/documents/{doc_id}/extract")
    assert r.status_code == 200, r.text
    assert fake.calls == 2
    assert r.json()["extract"]["doc_type"] == "invoice"


async def test_invalid_twice_is_a_typed_error_not_a_500(api: AsyncClient, fake: FakeClient) -> None:
    doc_id = await upload(api)
    fake.script = ["invalid", "malformed"]
    r = await api.post(f"/documents/{doc_id}/extract")
    assert r.status_code == 502
    assert r.json()["error"] == "schema_error"
    assert fake.calls == 2


async def test_429_is_retried_then_succeeds(api: AsyncClient, fake: FakeClient) -> None:
    doc_id = await upload(api)
    fake.script = ["429", "429", "ok"]
    r = await api.post(f"/documents/{doc_id}/extract")
    assert r.status_code == 200, r.text
    assert fake.calls == 3


async def test_400_is_not_retried(api: AsyncClient, fake: FakeClient) -> None:
    doc_id = await upload(api)
    fake.script = ["400", "ok"]
    r = await api.post(f"/documents/{doc_id}/extract")
    assert r.status_code == 502
    assert r.json()["error"] == "provider_error"
    assert fake.calls == 1


async def test_hang_hits_the_timeout(api: AsyncClient, fake: FakeClient) -> None:
    doc_id = await upload(api)
    fake.script = ["hang"]
    r = await api.post(f"/documents/{doc_id}/extract")
    assert r.status_code == 504
    assert r.json()["error"] == "provider_timeout"


async def test_same_document_is_never_paid_for_twice(api: AsyncClient, fake: FakeClient) -> None:
    doc_id = await upload(api)
    first = await api.post(f"/documents/{doc_id}/extract")
    second = await api.post(f"/documents/{doc_id}/extract")
    assert first.status_code == second.status_code == 200
    assert fake.calls == 1
    assert second.json()["cached"] is True
    assert second.json()["extract"] == first.json()["extract"]


async def test_cost_and_latency_are_recorded(api: AsyncClient, fake: FakeClient) -> None:
    doc_id = await upload(api)
    body = (await api.post(f"/documents/{doc_id}/extract")).json()
    assert body["tokens_in"] > 0 and body["tokens_out"] > 0
    assert body["cost_usd"] > 0
    assert body["latency_ms"] >= 0
    assert body["model"] == "fake-1"


async def test_input_is_capped_to_the_context_budget(
    api: AsyncClient, fake: FakeClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.settings import get_settings

    monkeypatch.setenv("MAX_INPUT_CHARS", "500")
    get_settings.cache_clear()
    doc_id = await upload(api, "contract.txt")
    r = await api.post(f"/documents/{doc_id}/extract")
    assert r.status_code == 200
    user_msg = next(m for m in fake.last_messages if m.role == "user")
    assert len(user_msg.content) < 700  # 500 chars of document plus the short preamble
