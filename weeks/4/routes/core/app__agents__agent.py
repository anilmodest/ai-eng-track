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

from app.agents.tools import NeedsApproval, ToolContext, run_tool, tool_schemas
from app.llm.client import Message, ModelError, ModelTimeout
from app.llm.cost import estimate_cost_usd
from app.llm.structured import SchemaError, complete_structured

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
    started = time.perf_counter()
    transcript: list[Message] = [
        Message(role="system", content=_system_prompt()),
        Message(role="user", content=f"Question: {question}"),
    ]
    steps: list[AgentStep] = []
    tokens_in = tokens_out = 0
    cost = 0.0
    status = "max_steps"
    answer = ""

    for n in range(1, 10_000):
        try:
            call, responses = await complete_structured(
                ctx.client,
                transcript,
                ToolCall,
                attempts=ctx.settings.model_retry_attempts,
                base_delay_s=ctx.settings.model_retry_base_delay_s,
                timeout_s=ctx.settings.model_timeout_s,
            )
        except (ModelError, ModelTimeout, SchemaError) as e:
            status, answer = "provider_error", str(e)
            break
        t_in = sum(r.tokens_in for r in responses)
        t_out = sum(r.tokens_out for r in responses)
        tokens_in += t_in
        tokens_out += t_out
        cost += estimate_cost_usd(responses[-1].model, t_in, t_out)

        if call.tool == "finish":
            result = await run_tool(ctx, "finish", call.args)
            steps.append(
                AgentStep(
                    n=n,
                    tool="finish",
                    args=call.args,
                    result=result,
                    tokens_in=t_in,
                    tokens_out=t_out,
                )
            )
            status, answer = "done", result
            break

        try:
            result = await run_tool(ctx, call.tool, call.args)
        except NeedsApproval as e:
            transcript.append(Message(role="user", content=f"Result of {call.tool}: {e}"))
            continue
            steps.append(
                AgentStep(
                    n=n,
                    tool=call.tool,
                    args=call.args,
                    result=str(e),
                    tokens_in=t_in,
                    tokens_out=t_out,
                )
            )
            status, answer = "needs_approval", str(e)
            break
        steps.append(
            AgentStep(
                n=n,
                tool=call.tool,
                args=call.args,
                result=result[:2000],
                tokens_in=t_in,
                tokens_out=t_out,
            )
        )
        transcript.append(Message(role="assistant", content=call.model_dump_json()))
        transcript.append(Message(role="user", content=f"Result of {call.tool}: {result[:4000]}"))

    return AgentResult(
        answer=answer,
        status=status,
        steps=steps,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        cost_usd=round(cost, 6),
        latency_ms=int((time.perf_counter() - started) * 1000),
    )
