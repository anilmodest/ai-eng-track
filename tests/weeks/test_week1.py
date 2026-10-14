"""Week 1 gate: the model is treated as an unreliable, expensive, non-deterministic dependency.

Every test here runs against the scripted fake provider. No key, no network, no cost.
Run the whole file with MODEL_PROVIDER=fake_a and again with MODEL_PROVIDER=fake_b:
the check script does exactly that, which is how "swappable by config" is proven.
"""

import json
import os
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from httpx import AsyncClient
from sqlmodel import Session, select

from app.db.session import get_engine
from app.llm.providers.fake import FakeClient
from app.settings import get_settings
from app.support import Ticket, desk_account, desk_tickets
from app.tools import TOOLS, ToolContext, call
from app.tools.base import schema
from tests.conftest import upload

ROOT = Path(__file__).resolve().parent.parent.parent

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


# ---- The agent's first two tools: app/tools/desk.py ------------------------------------------
# These check what must hold, not how you build it. The descriptions, constraints, returned
# fields and refusal wording are yours.


@pytest.fixture
def tool_ctx(env: None) -> Iterator[ToolContext]:
    with Session(get_engine()) as session:
        yield ToolContext(session=session, settings=get_settings())


ARG = {"get_customer": "customer_id", "get_ticket": "ticket_id"}


def test_tool_descriptions_tell_a_model_when_to_call_them_and_what_comes_back() -> None:
    for name, arg in ARG.items():
        s = schema(TOOLS[name])
        assert "TODO" not in s["description"], name
        assert len(s["description"].split()) >= 12, f"{name}: say when to call it, what it returns"
        props = s["parameters"]["properties"]
        assert list(props) == [arg], f"{name} takes exactly one argument, {arg}"
        assert len(str(props[arg].get("description", "")).split()) >= 4, f"describe {arg}"
        assert s["parameters"].get("required") == [arg]


async def test_get_customer_gives_version_account_and_plan_and_nothing_personal(
    tool_ctx: ToolContext,
) -> None:
    out = await call(tool_ctx, "get_customer", {"customer_id": "C-1001"})
    data = json.loads(out)
    assert data["version"] == "v3"
    assert data["plan"] == "enterprise"
    assert data["account"] == desk_account()
    assert "240" not in out and "@" not in out, "seats and contact details stay in the desk"


async def test_get_customer_refuses_another_desks_customer_in_words_a_model_can_read(
    tool_ctx: ToolContext,
) -> None:
    for customer_id in ("C-2001", "C-9999"):
        out = await call(tool_ctx, "get_customer", {"customer_id": customer_id})
        assert out.startswith("refused:"), out
        assert "Litware" not in out and "version" not in out.split(":", 1)[1].lower()


async def test_malformed_arguments_never_reach_the_tool(tool_ctx: ToolContext) -> None:
    bad: list[tuple[str, object]] = [
        ("get_customer", {"customer_id": "1001"}),
        ("get_customer", {"customer_id": ""}),
        ("get_customer", {"customer_id": "C-1001; DROP TABLE customer"}),
        ("get_customer", {}),
        ("get_customer", {"customer_id": 1001}),
        ("get_ticket", {"ticket_id": "2010"}),
        ("get_ticket", {"ticket_id": "T-"}),
        ("get_ticket", {"ticket": "T-2010"}),
        ("get_ticket", "T-2010"),
    ]
    for name, args in bad:
        out = await call(tool_ctx, name, args)
        assert out.startswith("error:"), (name, args, out)
    assert tool_ctx.calls == [], "a call that fails validation must not run the tool"


async def test_get_ticket_gives_what_an_agent_needs_for_this_desks_tickets_only(
    tool_ctx: ToolContext,
) -> None:
    desk = desk_tickets(tool_ctx.session)
    mine = desk[0]
    data = json.loads(await call(tool_ctx, "get_ticket", {"ticket_id": mine.ticket_id}))
    assert data["ticket_id"] == mine.ticket_id
    for key in ("status", "priority", "category", "product_version", "subject", "customer_id"):
        assert data[key] == getattr(mine, key), key
    ids = {t.ticket_id for t in desk}
    other_desk = next(t for t in tool_ctx.session.exec(select(Ticket)) if t.ticket_id not in ids)
    for ticket_id in (other_desk.ticket_id, "T-9999"):
        out = await call(tool_ctx, "get_ticket", {"ticket_id": ticket_id})
        assert out.startswith("refused:"), out


def _run(script: str, *args: str) -> dict[str, Any]:
    """Run a measurement script on the fake provider; return the report it wrote."""
    env = {**os.environ, "MODEL_PROVIDER": os.environ.get("MODEL_PROVIDER") or "fake_a"}
    env.update(MODEL_FALLBACK_PROVIDER="fake_b", MODEL_RETRY_BASE_DELAY_S="0.001")
    r = subprocess.run(
        [sys.executable, f"scripts/{script}.py", *args],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    report: dict[str, Any] = json.loads((ROOT / "reports" / f"{script}.json").read_text())
    return report


def test_tool_drill_runs_and_your_descriptions_beat_the_first_draft() -> None:
    """On the fake model, which picks tools by the words in their descriptions. Your real-model
    numbers go in the evidence file; this only proves your descriptions carry the meaning."""
    report = _run("tool_drill")
    assert report["before"]["n"] == report["after"]["n"] == 20
    assert report["after"]["correct_rate"] > report["before"]["correct_rate"]


def test_schema_and_failure_drills_run_and_report() -> None:
    schema_report = _run("schema_drill")
    assert schema_report["plain"]["n"] == schema_report["enforced"]["n"] > 0
    failure = _run("failure_drill", "--calls", "3")
    assert set(failure["providers"]) == {os.environ.get("MODEL_PROVIDER") or "fake_a", "fake_b"}
    # The fake answers instantly, so the 1 ms timeout probe means something only on a real model.
    assert {"timeout", "bad_request"} <= set(failure["probes"])
