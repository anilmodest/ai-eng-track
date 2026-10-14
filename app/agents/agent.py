"""Week 4: the agent. The model decides which tool to call next, reads the result, decides again.

Flexible: it can handle requests nobody wrote code for. Unpredictable: its cost, latency and path
vary per run, so the loop needs walls. The exercise is in weeks/4/README.md; what must hold:

    a step wall        at most settings.agent_max_steps model turns, then status "max_steps"
    a cost ceiling     stop with status "over_budget" once the run's model cost passes
                       settings.agent_cost_ceiling_usd
    recovery           an unknown tool or invalid arguments come back from app.tools.call as an
                       error the model reads; the loop goes on (it costs a step)
    approval           app.tools.call raises NeedsApproval for an action no person approved: stop
                       with status "needs_approval" and the pending action in `pending`
    the numbers        a "finish" whose answer states a number no tool returned is sent back with
                       app.agents.checks.why(...), not accepted (it costs a step)
    the record         every step, tokens, cost and latency, whatever the ending

The prompt is app/llm/prompts/agent_v1.md; the tools the model is shown are the ones in
app.tools.tool_schemas(), plus "finish", which is not a tool: it ends the run.
"""

import json
import time
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from app.tools import ToolContext, tool_schemas

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
    # TODO Week 4 (weeks/4/README.md): the loop, with every wall in the docstring above.
    #   transcript = [system_prompt(tools), "Request: <question>"]
    #   each turn: complete_structured(ctx.client, transcript, ToolCall, ...) -> {tool, args}
    #   finish -> check the numbers against the results so far, then done
    #   anything else -> app.tools.call(ctx, tool, args); NeedsApproval -> stop
    #   append the call and "Result of <tool>: ..." to the transcript, and go round
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
