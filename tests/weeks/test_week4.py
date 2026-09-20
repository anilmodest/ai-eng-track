"""Week 4 gate: prefer the simplest thing that works; a tool call is a permission decision.

The fake model's agent behaviour is scripted (search, then finish with the first hit), which is
enough to test the loop's walls: schema validation, recovery from a bad call, the money
checkpoint, the step limit. Plain code and the workflow are tested for real answers.
"""

from pathlib import Path

import pytest
from httpx import AsyncClient

from app.agents.tools import SearchArgs, tool_schemas
from app.llm.providers.fake import FakeClient
from app.mcp_scopes import RateLimiter, ScopeError, check_scope, parse_tokens

pytestmark = pytest.mark.week4

CORPUS = Path(__file__).parent.parent.parent / "corpus"


async def _load_and_index(api: AsyncClient) -> None:
    for path in sorted(CORPUS.iterdir()):
        r = await api.post("/documents", files={"file": (path.name, path.read_bytes())})
        assert r.status_code == 201, r.text
    assert (await api.post("/index", params={"strategy": "paragraph"})).status_code == 200


@pytest.fixture(autouse=True)
def _paragraphs(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.settings import get_settings

    monkeypatch.setenv("CHUNK_STRATEGY", "paragraph")
    get_settings.cache_clear()


# ---- tools ---------------------------------------------------------------------------------


def test_tool_schemas_are_json_schema_the_model_can_read() -> None:
    schemas = {s["name"]: s for s in tool_schemas()}
    assert set(schemas) == {
        "list_documents",
        "search_documents",
        "get_document",
        "extract_document",
        "finish",
    }
    assert schemas["search_documents"]["parameters"]["properties"]["k"]["maximum"] == 10
    assert "[costs money]" in schemas["extract_document"]["description"]
    assert "[costs money]" not in schemas["search_documents"]["description"]


def test_tool_arguments_are_validated() -> None:
    with pytest.raises(ValueError):
        SearchArgs(query="", k=3)
    with pytest.raises(ValueError):
        SearchArgs(query="x", k=50)


# ---- plain code ----------------------------------------------------------------------------


async def test_plain_code_answers_its_questions_exactly_and_free(api: AsyncClient) -> None:
    await _load_and_index(api)
    r = await api.post(
        "/tasks/run",
        json={"question": "What is the total due across all invoices in GBP?", "mode": "plain"},
    )
    out = r.json()
    assert out["status"] == "done" and "9,157.00 GBP" in out["answer"]
    assert out["cost_usd"] == 0 and out["calls"] == []


async def test_plain_code_admits_what_it_cannot_do(api: AsyncClient) -> None:
    await _load_and_index(api)
    r = await api.post(
        "/tasks/run",
        json={"question": "What does the fleet report say about Leeds?", "mode": "plain"},
    )
    assert r.json()["status"] == "unsupported"


# ---- workflow ------------------------------------------------------------------------------


async def test_workflow_stops_at_the_money_checkpoint(api: AsyncClient, fake: FakeClient) -> None:
    await _load_and_index(api)
    r = await api.post(
        "/tasks/run",
        json={"question": "Which invoice has the largest total?", "mode": "workflow"},
    )
    out = r.json()
    assert out["status"] == "needs_approval"
    assert "extract_document" not in out["calls"]
    assert fake.calls == 0, "no money was spent without approval"


async def test_workflow_runs_end_to_end_when_approved(api: AsyncClient, fake: FakeClient) -> None:
    await _load_and_index(api)
    r = await api.post(
        "/tasks/run",
        json={
            "question": "Which invoice has the largest total?",
            "mode": "workflow",
            "approved": True,
        },
    )
    out = r.json()
    assert out["status"] == "done"
    assert out["calls"].count("extract_document") == 3  # three invoices in the corpus
    assert out["calls"][-1] == "answer"
    assert out["cost_usd"] > 0


# ---- agent ---------------------------------------------------------------------------------


async def test_agent_calls_a_tool_then_finishes(api: AsyncClient, fake: FakeClient) -> None:
    await _load_and_index(api)
    r = await api.post(
        "/tasks/run", json={"question": "When is the Woodgrove invoice due?", "mode": "agent"}
    )
    out = r.json()
    assert out["status"] == "done", out
    assert [s["tool"] for s in out["steps"]] == ["search_documents", "finish"]
    assert out["tokens_in"] > 0 and out["cost_usd"] > 0
    # The scripted fake finishes with the first search hit; which document that is depends on
    # the embedder (lexical, here), which is Week 2's lesson, not this test's.
    assert out["answer"].startswith("document_id=")


async def test_agent_recovers_from_a_bad_tool_call(api: AsyncClient, fake: FakeClient) -> None:
    """A wrong tool name comes back as text the model reads; the loop does not crash."""
    from app.agents.tools import ToolContext, run_tool

    await _load_and_index(api)
    ctx = ToolContext(session=None, embedder=None, settings=None, client=fake)  # type: ignore[arg-type]
    assert (await run_tool(ctx, "teleport", {})).startswith("error: unknown tool")
    assert (await run_tool(ctx, "search_documents", {"query": ""})).startswith(
        "error: invalid arguments"
    )


async def test_agent_hits_the_step_wall(
    api: AsyncClient, fake: FakeClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.settings import get_settings

    monkeypatch.setenv("AGENT_MAX_STEPS", "1")
    get_settings.cache_clear()
    await _load_and_index(api)
    r = await api.post(
        "/tasks/run", json={"question": "When is the Woodgrove invoice due?", "mode": "agent"}
    )
    out = r.json()
    assert out["status"] == "max_steps"
    assert len(out["steps"]) == 1


# ---- MCP: scopes, rate limits, and a real round trip ---------------------------------------


def test_scopes_are_least_agency() -> None:
    tokens = parse_tokens(
        "reader:search_documents,get_document;analyst:search_documents,extract_document"
    )
    check_scope("reader", "search_documents", tokens)
    with pytest.raises(ScopeError):
        check_scope("reader", "extract_document", tokens)
    with pytest.raises(ScopeError):
        check_scope("nobody", "search_documents", tokens)
    check_scope("analyst", "extract_document", tokens)


def test_rate_limiter_is_a_sliding_window() -> None:
    rl = RateLimiter(max_calls=3, window_s=10)
    for t in (0.0, 1.0, 2.0):
        rl.check("reader", now=t)
    with pytest.raises(ScopeError):
        rl.check("reader", now=3.0)
    rl.check("reader", now=11.0)  # the first call has left the window
    rl.check("analyst", now=3.0)  # a different token has its own window


async def test_mcp_server_denies_out_of_scope_calls(
    api: AsyncClient, fake: FakeClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Drive the MCP server in-process: list tools, call one allowed, one denied."""
    from app import mcp_server

    await _load_and_index(api)
    monkeypatch.setattr(mcp_server, "TOKEN", "reader")
    server = mcp_server.build_server()
    tools = {t.name for t in await server.list_tools()}
    assert {"search_documents", "get_document", "extract_document"} <= tools

    result = await server.call_tool("search_documents", {"query": "toner cartridge", "k": 2})
    text = _text(result)
    assert "woodgrove" in text.lower()

    denied = _text(await server.call_tool("extract_document", {"document_id": 1}))
    assert denied.startswith("denied:") and "may not call extract_document" in denied


def _text(result: object) -> str:
    """MCP returns a result with content blocks; flatten whatever shape the SDK gives to text."""
    if isinstance(result, tuple):
        result = result[0]
    blocks = getattr(result, "content", result)
    if isinstance(blocks, list):
        return " ".join(getattr(b, "text", str(b)) for b in blocks)
    return getattr(blocks, "text", str(blocks))
