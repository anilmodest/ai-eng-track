"""Week 4: the agent loop, written. Read it as a reviewer before you trust it with money."""

import json
import time
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from app.agents.checks import unsupported_numbers, why
from app.llm.client import Message, ModelError, ModelTimeout
from app.llm.cost import estimate_cost_usd
from app.llm.structured import SchemaError, complete_structured
from app.tools import NeedsApproval, ToolContext, call, tool_schemas
from app.tools.base import ToolCall

PROMPT_VERSION = "agent_v1"
_PROMPT = (Path(__file__).parent.parent / "llm" / "prompts" / f"{PROMPT_VERSION}.md").read_text()
FINISH = {
    "name": "finish",
    "description": "End the run with your answer to the request.",
    "parameters": {
        "type": "object",
        "properties": {"answer": {"type": "string", "description": "The answer, with figures."}},
        "required": ["answer"],
    },
}


class AgentStep(BaseModel):
    n: int
    tool: str
    args: dict[str, Any]
    result: str
    tokens_in: int
    tokens_out: int


class AgentResult(BaseModel):
    answer: str
    status: str  # done | needs_approval | max_steps | over_budget | provider_error
    steps: list[AgentStep]
    pending: dict[str, Any] | None = None  # {"tool", "args"} when stopped for approval
    tokens_in: int
    tokens_out: int
    cost_usd: float
    latency_ms: int


def system_prompt(tools: list[str] | None = None) -> str:
    """The prompt, then every tool the model may call, as JSON. Given."""
    schemas = [*tool_schemas(tools), FINISH]
    return f"{_PROMPT}\n\nTools:\n{json.dumps(schemas, indent=1)}"


async def run_agent(
    ctx: ToolContext, question: str, *, tools: list[str] | None = None
) -> AgentResult:
    assert ctx.client is not None
    started = time.perf_counter()
    transcript = [
        Message(role="system", content=system_prompt(tools)),
        Message(role="user", content=f"Request: {question}"),
    ]
    steps: list[AgentStep] = []
    results: list[str] = []
    tokens_in = tokens_out = 0
    cost = 0.0
    status, answer = "max_steps", ""
    pending: dict[str, Any] | None = None
    ceiling = ctx.settings.agent_cost_ceiling_usd

    for n in range(1, ctx.settings.agent_max_steps + 1):
        try:
            step, responses = await complete_structured(
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

        if step.tool == "finish":
            text = str(step.args.get("answer", "")).strip()
            missing = unsupported_numbers(text, results)
            result = why(missing) if missing else (text or "error: finish needs an answer")
            steps.append(
                AgentStep(
                    n=n,
                    tool="finish",
                    args=step.args,
                    result=result,
                    tokens_in=t_in,
                    tokens_out=t_out,
                )
            )
            if text and not missing:
                status, answer = "done", text
                break
        else:
            try:
                result = await call(ctx, step.tool, step.args)
            except NeedsApproval as e:
                steps.append(
                    AgentStep(
                        n=n,
                        tool=step.tool,
                        args=step.args,
                        result=str(e),
                        tokens_in=t_in,
                        tokens_out=t_out,
                    )
                )
                status, answer = "needs_approval", str(e)
                pending = {"tool": e.tool, "args": e.arguments}
                break
            results.append(result)
            steps.append(
                AgentStep(
                    n=n,
                    tool=step.tool,
                    args=step.args,
                    result=result[:2000],
                    tokens_in=t_in,
                    tokens_out=t_out,
                )
            )

        transcript.append(Message(role="assistant", content=step.model_dump_json()))
        transcript.append(Message(role="user", content=f"Result of {step.tool}: {result[:4000]}"))
        transcript = transcript[-6:]  # keep the context small
        if ctx.spent_usd > ceiling:
            status, answer = "over_budget", f"stopped: the run's model cost passed {ceiling:g} USD"
            break

    return AgentResult(
        answer=answer,
        status=status,
        steps=steps,
        pending=pending,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        cost_usd=round(cost + ctx.spent_usd, 6),
        latency_ms=int((time.perf_counter() - started) * 1000),
    )
