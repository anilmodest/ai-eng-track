"""Way 3: an agent. The model decides which tool to call next, reads the result, decides again.

Flexible: it can answer questions nobody wrote code for. Unpredictable: cost, latency and the
path it takes vary per run, and a loop needs a wall (max steps), a checkpoint on money, and a
way to recover from its own bad calls. Most cancelled agent projects were this, applied to a
problem a workflow would have solved.
"""

import json
import time
from pathlib import Path

from pydantic import BaseModel, Field

from app.agents.tools import ToolContext, tool_schemas

PROMPT_VERSION = "agent_v1"
_PROMPT = (Path(__file__).parent.parent / "llm" / "prompts" / f"{PROMPT_VERSION}.md").read_text()


class ToolCall(BaseModel):
    tool: str = Field(min_length=1)
    args: dict[str, object] = Field(default_factory=dict)


class AgentStep(BaseModel):
    n: int
    tool: str
    args: dict[str, object]
    result: str
    tokens_in: int
    tokens_out: int


class AgentResult(BaseModel):
    answer: str
    status: str  # done | needs_approval | max_steps | provider_error
    steps: list[AgentStep]
    tokens_in: int
    tokens_out: int
    cost_usd: float
    latency_ms: int


def _system_prompt() -> str:
    tools = json.dumps(tool_schemas(), indent=1)
    return f"{_PROMPT}\n\nTools:\n{tools}"


async def run_agent(ctx: ToolContext, question: str) -> AgentResult:
    # TODO Week 4 (weeks/4/README.md). The loop:
    #   transcript = [system prompt from _system_prompt(), user "Question: ..."]
    #   for n in 1..ctx.settings.agent_max_steps:
    #       call, responses = await complete_structured(ctx.client, transcript, ToolCall, ...)
    #           (ModelError, ModelTimeout, SchemaError) -> status "provider_error", stop
    #       add tokens and estimate_cost_usd(...) to the totals
    #       if call.tool == "finish": run_tool(...) -> status "done", answer, stop
    #       result = await run_tool(ctx, call.tool, call.args)
    #           NeedsApproval -> status "needs_approval", stop
    #       record an AgentStep; append the call and "Result of <tool>: ..." to the transcript
    #   ran out of steps -> status "max_steps"
    #   cost_usd = model cost + ctx.spent_usd (money the tools spent)
    started = time.perf_counter()
    return AgentResult(
        answer="Week 4 exercise: implement run_agent",
        status="not_implemented",
        steps=[],
        tokens_in=0,
        tokens_out=0,
        cost_usd=0.0,
        latency_ms=int((time.perf_counter() - started) * 1000),
    )
