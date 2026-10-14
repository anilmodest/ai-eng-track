"""Week 4: the same agent, rebuilt with LangGraph. Core on the pro route; stretch on start and core.

    uv sync --extra langgraph

Build the agent you wrote in app/agents/agent.py again as a LangGraph graph: a node that asks the
model for the next call, a node that runs it through app.tools.call, the same walls (steps,
cost, approval, the numbers check), and the same AgentResult, so every test and every
measurement runs on both. Then compare them on code size, cost, speed and how hard each is to
debug when it goes wrong, and say in your decision record which you would ship and why.

On start and core the comparison is supplied instead (docs/langgraph-comparison.md): read it and
state in your decision record which you would ship and why.
"""

from app.agents.agent import AgentResult
from app.tools import ToolContext


async def run_langgraph_agent(ctx: ToolContext, question: str) -> AgentResult:
    # TODO Week 4, pro: import langgraph here, not at the top, so the service runs without it.
    raise NotImplementedError("run_langgraph_agent: build me (weeks/4/routes/pro.md)")
