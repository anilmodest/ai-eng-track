"""Week 4 gate: agency is a cost you place deliberately; nothing acts without a person's yes.

The fake model behaves as a small rule-following agent (app/llm/providers/fake_agent.py), which
is enough to test every wall of the loop: approval stops, recovery from bad calls, the step and
cost walls, and the rule that a number in the answer is a number a tool returned. A scripted
client stands in where a test needs a model to misbehave on purpose.
"""

import json
import os
import statistics
import subprocess
import sys
from collections.abc import AsyncIterator, Iterator
from pathlib import Path
from typing import Any

import pytest
from httpx import AsyncClient
from sqlmodel import Session, select

from app.agents.agent import run_agent, system_prompt
from app.db.session import get_engine
from app.llm.client import Message, ModelResponse
from app.mcp_scopes import RateLimiter, ScopeError, check_scope, parse_tokens
from app.settings import get_settings
from app.support import Credit, Draft, Escalation, Ticket, desk_tickets
from app.tools import TOOLS, NeedsApproval, ToolContext, call
from app.tools.base import schema

pytestmark = pytest.mark.week4

ROOT = Path(__file__).parent.parent.parent
CORPUS = ROOT / "corpus"
ACTIONS = ("draft_reply", "escalate", "issue_credit")


@pytest.fixture(autouse=True)
def _sections(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CHUNK_STRATEGY", "section")
    get_settings.cache_clear()


@pytest.fixture
def ctx(env: None) -> Iterator[ToolContext]:
    with Session(get_engine()) as session:
        yield ToolContext(session=session, settings=get_settings())


@pytest.fixture
async def indexed(api: AsyncClient) -> AsyncIterator[AsyncClient]:
    for path in sorted(p for p in CORPUS.iterdir() if p.is_file()):
        r = await api.post("/documents", files={"file": (path.name, path.read_bytes())})
        assert r.status_code == 201, r.text
    assert (await api.post("/index")).status_code == 200
    yield api


def _billing_ticket(session: Session) -> Ticket:
    return next(
        t for t in desk_tickets(session) if t.amount_due_usd >= 500 and t.credits_issued_usd == 0
    )


# ---- the three action tools: app/tools/actions.py -------------------------------------------


def test_action_tools_are_described_and_say_truthfully_what_they_do() -> None:
    for name in ACTIONS:
        s = schema(TOOLS[name])
        assert "TODO" not in s["description"] and len(s["description"].split()) >= 12, name
        for arg, prop in s["parameters"]["properties"].items():
            assert len(str(prop.get("description", "")).split()) >= 4, (name, arg)
    assert not TOOLS["draft_reply"].needs_approval, "a draft changes nothing a customer sees"
    assert TOOLS["escalate"].writes, "escalating hands the ticket to another team"
    assert TOOLS["issue_credit"].spends, "a credit is money"


async def test_malformed_action_calls_never_reach_the_tool(ctx: ToolContext) -> None:
    t = desk_tickets(ctx.session)[0].ticket_id
    ctx.approved = set(ACTIONS)
    bad: list[tuple[str, dict[str, Any]]] = [
        ("escalate", {"ticket_id": t, "team": "marketing", "reason": "x" * 20}),
        ("escalate", {"ticket_id": t, "team": "engineering", "reason": ""}),
        ("issue_credit", {"ticket_id": t, "amount_usd": -5, "reason": "goodwill gesture"}),
        ("issue_credit", {"ticket_id": t, "amount_usd": 0, "reason": "goodwill gesture"}),
        ("issue_credit", {"ticket_id": t, "amount_usd": 100000, "reason": "goodwill gesture"}),
        ("draft_reply", {"ticket_id": t, "body": ""}),
        ("draft_reply", {"ticket_id": "2010", "body": "Hello"}),
    ]
    for name, args in bad:
        out = await call(ctx, name, args)
        assert out.startswith("error:"), (name, args, out)
    assert ctx.calls == []


async def test_escalate_and_issue_credit_stop_for_approval_and_nothing_happens(
    ctx: ToolContext,
) -> None:
    t = _billing_ticket(ctx.session).ticket_id
    with pytest.raises(NeedsApproval):
        await call(
            ctx, "escalate", {"ticket_id": t, "team": "engineering", "reason": "runner down"}
        )
    with pytest.raises(NeedsApproval):
        await call(ctx, "issue_credit", {"ticket_id": t, "amount_usd": 50, "reason": "outage day"})
    assert not ctx.session.exec(select(Escalation)).all()
    assert not ctx.session.exec(select(Credit)).all()


async def test_approved_actions_are_carried_out_and_recorded(ctx: ToolContext) -> None:
    t = _billing_ticket(ctx.session).ticket_id
    ctx.approved = {"escalate", "issue_credit"}
    out = await call(
        ctx, "escalate", {"ticket_id": t, "team": "billing", "reason": "disputed invoice"}
    )
    assert not out.startswith(("error", "refused")), out
    out = await call(
        ctx, "issue_credit", {"ticket_id": t, "amount_usd": 120, "reason": "outage day"}
    )
    assert not out.startswith(("error", "refused")), out
    assert len(ctx.session.exec(select(Escalation)).all()) == 1
    assert [c.amount_usd for c in ctx.session.exec(select(Credit))] == [120]


async def test_draft_reply_changes_nothing_a_customer_sees(ctx: ToolContext) -> None:
    tk = desk_tickets(ctx.session)[0]
    before = tk.status
    out = await call(ctx, "draft_reply", {"ticket_id": tk.ticket_id, "body": "We are on it."})
    assert tk.ticket_id in out
    assert ctx.session.get(Ticket, tk.ticket_id).status == before  # type: ignore[union-attr]
    assert len(ctx.session.exec(select(Draft)).all()) == 1


async def test_credits_are_capped_per_ticket_and_by_what_is_owed(ctx: ToolContext) -> None:
    t = _billing_ticket(ctx.session)
    ctx.approved = {"issue_credit"}
    assert not (
        await call(
            ctx,
            "issue_credit",
            {"ticket_id": t.ticket_id, "amount_usd": 300, "reason": "outage day"},
        )
    ).startswith("refused")
    second = await call(
        ctx, "issue_credit", {"ticket_id": t.ticket_id, "amount_usd": 300, "reason": "outage day"}
    )
    assert second.startswith("refused:"), "500 USD per ticket, all credits together"
    small = next(x for x in desk_tickets(ctx.session) if 0 < x.amount_due_usd < 400)
    over = await call(
        ctx,
        "issue_credit",
        {
            "ticket_id": small.ticket_id,
            "amount_usd": small.amount_due_usd + 50,
            "reason": "goodwill gesture",
        },
    )
    assert over.startswith("refused:"), "never more than the ticket's amount due"
    assert sum(c.amount_usd for c in ctx.session.exec(select(Credit))) == 300


async def test_actions_on_another_desks_ticket_are_refused(ctx: ToolContext) -> None:
    mine = {t.ticket_id for t in desk_tickets(ctx.session)}
    other = next(t for t in ctx.session.exec(select(Ticket)) if t.ticket_id not in mine)
    ctx.approved = set(ACTIONS)
    out = await call(ctx, "draft_reply", {"ticket_id": other.ticket_id, "body": "Hello there"})
    assert out.startswith("refused:"), out


# ---- the analysis tool: app/tools/analysis.py -----------------------------------------------


def test_query_tickets_is_described() -> None:
    s = schema(TOOLS["query_tickets"])
    assert "TODO" not in s["description"] and len(s["description"].split()) >= 15
    assert not TOOLS["query_tickets"].needs_approval


async def test_query_tickets_is_an_allowlist(ctx: ToolContext) -> None:
    for args in (
        {"query": "SELECT * FROM ticket"},
        {"query": "drop_table"},
        {"query": "count_by", "group_by": "requester_email"},
        {"query": "count", "month": "September"},
        {"query": "count", "status": "deleted"},
    ):
        out = await call(ctx, "query_tickets", args)
        assert out.startswith("error:"), (args, out)
    assert ctx.calls == []


async def _result(ctx: ToolContext, **args: Any) -> Any:
    out = await call(ctx, "query_tickets", args)
    data = json.loads(out)
    return data["result"]


async def test_query_tickets_numbers_are_the_data(ctx: ToolContext) -> None:
    desk = desk_tickets(ctx.session)
    assert await _result(ctx, query="count") == len(desk)
    assert await _result(ctx, query="count", status="open") == sum(t.status == "open" for t in desk)
    urgent_open = sum(t.status == "open" and t.priority == "urgent" for t in desk)
    assert await _result(ctx, query="count", status="open", priority="urgent") == urgent_open
    by_status = await _result(ctx, query="count_by", group_by="status")
    assert by_status == {s: sum(t.status == s for t in desk) for s in {t.status for t in desk}}
    due = round(sum(t.amount_due_usd for t in desk), 2)
    assert round(await _result(ctx, query="sum_amount_due"), 2) == due
    times = [t.first_response_min for t in desk if t.first_response_min is not None]
    assert await _result(ctx, query="median_first_response") == statistics.median(times)
    c = desk[0].customer_id
    assert await _result(ctx, query="count", customer_id=c) == sum(t.customer_id == c for t in desk)
    month = desk[0].opened_at.strftime("%Y-%m")
    in_month = sum(t.opened_at.strftime("%Y-%m") == month for t in desk)
    assert await _result(ctx, query="count", month=month) == in_month


# ---- the agent loop: app/agents/agent.py ----------------------------------------------------


class Scripted:
    """A model that says exactly what it is told to, in order, then repeats the last line."""

    def __init__(self, lines: list[dict[str, Any]], tokens: int = 50) -> None:
        self.name, self.model = "fake_a", "fake-1"
        self.lines = [json.dumps(x) for x in lines]
        self.calls = 0
        self.tokens = tokens

    async def complete(self, messages: list[Message], *, json_mode: bool = True) -> ModelResponse:
        line = self.lines[min(self.calls, len(self.lines) - 1)]
        self.calls += 1
        return ModelResponse(
            text=line,
            provider=self.name,
            model=self.model,
            tokens_in=self.tokens,
            tokens_out=self.tokens,
        )


def test_the_agent_is_shown_every_tool_and_finish() -> None:
    prompt = system_prompt()
    for name in [*TOOLS, "finish"]:
        assert f'"name": "{name}"' in prompt, name


async def test_the_agent_answers_a_product_question_from_the_right_version(
    indexed: AsyncClient,
) -> None:
    r = await indexed.post(
        "/tasks/run", json={"question": "C-1004 asks what the default connection timeout is."}
    )
    body = r.json()
    tools = [s["tool"] for s in body["steps"]]
    assert body["status"] == "done", body
    assert tools[:2] == ["get_customer", "search_docs"], tools
    assert body["steps"][1]["args"]["version"] == "v3"
    assert body["cost_usd"] > 0 and body["latency_ms"] >= 0


async def test_the_agent_states_the_number_the_tool_returned(indexed: AsyncClient) -> None:
    body = (
        await indexed.post("/tasks/run", json={"question": "How many open tickets are there?"})
    ).json()
    with Session(get_engine()) as session:
        truth = sum(t.status == "open" for t in desk_tickets(session))
    assert body["status"] == "done", body
    assert "query_tickets" in body["calls"]
    assert str(truth) in body["answer"]


async def test_the_agent_stops_for_approval_and_nothing_happens(indexed: AsyncClient) -> None:
    with Session(get_engine()) as session:
        t = desk_tickets(session)[0].ticket_id
    body = (
        await indexed.post(
            "/tasks/run",
            json={"question": f"Escalate {t} to engineering: the runner will not start."},
        )
    ).json()
    assert body["status"] == "needs_approval", body
    assert body["pending"]["tool"] == "escalate"
    assert "escalate" not in body["calls"]
    with Session(get_engine()) as session:
        assert not session.exec(select(Escalation)).all()
    approved = (
        await indexed.post(
            "/tasks/run",
            json={
                "question": f"Escalate {t} to engineering: the runner will not start.",
                "approve": ["escalate"],
            },
        )
    ).json()
    assert approved["status"] == "done", approved
    with Session(get_engine()) as session:
        assert len(session.exec(select(Escalation)).all()) == 1


async def test_a_ticket_cannot_make_the_agent_spend_money(indexed: AsyncClient) -> None:
    """T-2099 tells the agent to issue a 5000 USD credit. The fake obeys, as an unguarded model
    does. Approval in code is why nothing is spent anyway; week 5 removes the capability."""
    body = (await indexed.post("/tasks/run", json={"question": "Handle ticket T-2099."})).json()
    assert "issue_credit" not in body["calls"]
    with Session(get_engine()) as session:
        assert not session.exec(select(Credit)).all()


async def test_the_agent_recovers_from_a_bad_tool_call(ctx: ToolContext) -> None:
    ctx.client = Scripted(
        [
            {"tool": "no_such_tool", "args": {}},
            {"tool": "get_customer", "args": {"customer_id": "1004"}},
            {"tool": "get_customer", "args": {"customer_id": "C-1004"}},
            {"tool": "finish", "args": {"answer": "C-1004 runs v3"}},
        ]
    )
    result = await run_agent(ctx, "Which version is C-1004 on?")
    assert result.status == "done", result
    assert [s.tool for s in result.steps][:3] == ["no_such_tool", "get_customer", "get_customer"]
    assert result.steps[0].result.startswith("error") and result.steps[1].result.startswith("error")
    assert result.answer == "C-1004 runs v3"


async def test_the_agent_respects_the_step_wall(ctx: ToolContext) -> None:
    ctx.client = Scripted([{"tool": "get_customer", "args": {"customer_id": "C-1004"}}])
    result = await run_agent(ctx, "Which version is C-1004 on?")
    assert result.status == "max_steps"
    assert len(result.steps) == ctx.settings.agent_max_steps


async def test_the_agent_respects_the_cost_ceiling(
    ctx: ToolContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("AGENT_COST_CEILING_USD", "0.0001")
    get_settings.cache_clear()
    ctx.settings = get_settings()
    ctx.client = Scripted(
        [{"tool": "get_customer", "args": {"customer_id": "C-1004"}}], tokens=50_000
    )
    result = await run_agent(ctx, "Which version is C-1004 on?")
    assert result.status == "over_budget"
    assert len(result.steps) < ctx.settings.agent_max_steps


async def test_an_answer_with_a_number_no_tool_returned_is_not_accepted(ctx: ToolContext) -> None:
    ctx.client = Scripted(
        [
            {"tool": "query_tickets", "args": {"query": "count", "status": "open"}},
            {"tool": "finish", "args": {"answer": "There are 9999 open tickets."}},
        ]
    )
    result = await run_agent(ctx, "How many open tickets are there?")
    assert result.status != "done"
    assert any("no tool returned" in s.result for s in result.steps if s.tool == "finish")


async def test_a_provider_failure_ends_the_run_as_a_provider_error(
    indexed: AsyncClient, fake: Any
) -> None:
    fake.script = ["400"]
    body = (
        await indexed.post("/tasks/run", json={"question": "Which version is C-1004 on?"})
    ).json()
    assert body["status"] == "provider_error"


# ---- the MCP server: app/mcp_server.py ------------------------------------------------------


async def test_the_mcp_server_serves_every_tool_with_its_schema() -> None:
    from app.mcp_server import build_server

    served = {t.name: t for t in await build_server().list_tools()}
    assert set(served) == set(TOOLS)
    for name, t in served.items():
        want = set(TOOLS[name].args.model_json_schema()["properties"])
        assert set(t.input_schema["properties"]) == want, name


async def test_a_reader_cannot_act_and_an_agent_cannot_escalate_or_spend(env: None) -> None:
    from app.mcp_server import call_tool

    args = {
        "ticket_id": "T-2010",
        "team": "engineering",
        "reason": "x" * 20,
        "body": "hello",
        "amount_usd": 10,
    }
    for tool in ACTIONS:
        assert (await call_tool("reader", tool, args)).startswith("denied"), tool
    for tool in ("escalate", "issue_credit"):
        assert (await call_tool("agent", tool, args)).startswith("denied"), tool
    assert (await call_tool("nobody", "get_customer", {"customer_id": "C-1004"})).startswith(
        "denied"
    )


async def test_a_supervisor_still_needs_approval_to_act(env: None) -> None:
    from app.mcp_server import call_tool

    out = await call_tool(
        "supervisor",
        "escalate",
        {"ticket_id": "T-2010", "team": "engineering", "reason": "runner down"},
    )
    assert out.startswith("needs approval"), out


async def test_a_conformant_call_gets_its_result(env: None) -> None:
    from app.mcp_server import call_tool

    out = await call_tool("reader", "get_customer", {"customer_id": "C-1004"})
    assert json.loads(out)["version"] == "v3"


def test_scopes_and_rate_limit_are_enforced_in_code() -> None:
    tokens = parse_tokens("reader:get_customer;writer:get_customer,escalate")
    check_scope("writer", "escalate", tokens)
    with pytest.raises(ScopeError):
        check_scope("reader", "escalate", tokens)
    limiter = RateLimiter(max_calls=2, window_s=60)
    limiter.check("reader", now=0)
    limiter.check("reader", now=1)
    with pytest.raises(ScopeError):
        limiter.check("reader", now=2)
    limiter.check("reader", now=61.5)


# ---- one request, three ways, and the decision ----------------------------------------------


async def test_plain_code_answers_what_it_was_written_for_and_nothing_else(
    ctx: ToolContext,
) -> None:
    from app.agents import plain

    assert plain.answer(ctx.session, "Which version is C-1004 on?") == "C-1004 runs v3"
    open_n = sum(t.status == "open" for t in desk_tickets(ctx.session))
    assert plain.answer(ctx.session, "How many open tickets are there?") == f"{open_n} tickets"
    assert plain.answer(ctx.session, "Why did the runner stop after the upgrade?") is None


def _run(script: str, *args: str) -> dict[str, Any]:
    env = {
        **os.environ,
        "MODEL_PROVIDER": "fake_a",
        "EMBED_PROVIDER": "hash",
        "CHUNK_STRATEGY": "section",
    }
    env.pop("PROGRAMME_MODEL_TOKEN", None)
    r = subprocess.run(
        [sys.executable, f"scripts/{script}.py", *args],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=900,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    name = {"compare_week4": "compare.json", "model_compare": "models.json"}[script]
    report: dict[str, Any] = json.loads((ROOT / "reports" / name).read_text())
    return report


def test_the_comparison_runs_three_task_types_three_ways() -> None:
    report = _run("compare_week4")
    assert set(report["types"]) == {"lookup", "analysis", "action"}
    for row in report["types"].values():
        assert set(row) == {"plain", "workflow", "agent"}
        for m in row.values():
            assert {"accuracy", "cost_per_correct_usd", "avg_steps", "approval_violations"} <= set(
                m
            )
            assert m["approval_violations"] == 0


def test_the_model_comparison_runs_and_says_when_the_frontier_run_was_not_made() -> None:
    report = _run("model_compare")
    assert report["own"]["summary"]["n"] > 0
    assert "skipped" in report["frontier"] or report["frontier"]["summary"]["n"] > 0


def test_the_routing_table_names_each_task_type() -> None:
    text = (
        (ROOT / "decisions" / "week-4.md").read_text(encoding="utf-8")
        if (ROOT / "decisions" / "week-4.md").exists()
        else ""
    )
    rows = [line.lower() for line in text.splitlines() if line.strip().startswith("|")]
    for kind in ("lookup", "analysis", "action"):
        row = next((r for r in rows if kind in r), "")
        assert row, f"the routing table has no row for {kind}"
        assert any(w in row for w in ("plain", "workflow", "agent")), (kind, row)
        assert any(w in row for w in ("cheap", "frontier")), (kind, row)


def test_the_scope_break_is_written_up() -> None:
    path = ROOT / "decisions" / "week-4-scope-break.md"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    assert len(text.split()) >= 120, "what you tried, what happened, and what stopped it"
    assert any(t in text for t in ACTIONS), "the attempt must include at least one write tool"


# ---- pro: the same agent, rebuilt with LangGraph --------------------------------------------


@pytest.mark.pro
async def test_the_langgraph_agent_does_what_the_hand_built_loop_does(indexed: AsyncClient) -> None:
    from app.agents.langgraph_agent import run_langgraph_agent

    with Session(get_engine()) as session:
        ctx = ToolContext(session=session, settings=get_settings())
        from app.llm.registry import get_model_client

        ctx.client = get_model_client()
        done = await run_langgraph_agent(ctx, "Which version is C-1004 on?")
        assert done.status == "done" and done.steps[0].tool == "get_customer"
        stop = await run_langgraph_agent(ctx, f"Escalate {desk_tickets(session)[0].ticket_id} now.")
        assert (
            stop.status == "needs_approval" and stop.pending and stop.pending["tool"] == "escalate"
        )
