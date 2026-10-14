# Week 4 on the pro route

**No helpers, two real constraints.** You write the MCP server from its signatures. And:

1. **The LangGraph rebuild is core for you** (`app/agents/langgraph_agent.py`,
   `uv sync --extra langgraph`): the same walls and the same `AgentResult`, passing the same
   tests, then compared with your loop on code size, cost, speed and how hard each is to debug.
   Your decision record says which you would ship.
2. **A plan step**: before the loop, one call that writes the plan; measure it on the trajectory
   tasks with two or more tools, against the loop without it, and keep it only if it pays.
