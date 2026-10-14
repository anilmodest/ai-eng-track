# The agent loop by hand, and the same agent in LangGraph

Supplied for start and core, where the rebuild is a stretch. On pro you build it yourself
(`app/agents/langgraph_agent.py`) and measure it. Either way, your week 4 decision record says
which you would ship and why.

The comparison below was made by the programme on the reference solution: the same twenty
trajectory tasks, the same tools, the same walls (steps, cost, approval, the numbers check), and
the same `AgentResult`, so every test and measurement runs on both.

| | Hand-built loop (`agent.py`) | LangGraph (`langgraph_agent.py`) |
| --- | --- | --- |
| Lines of code (loop only) | about 90 | about 110, plus the graph definition |
| Dependencies | none beyond the service | `langgraph` and what it pulls in |
| Walls (steps, cost, approval, numbers) | `break` statements in one loop | conditions on the edges out of two nodes |
| Model calls and cost on the trajectory set | identical | identical |
| Time per task | the same within noise | a few milliseconds more per step |
| Resuming after approval | start a new run with the tool approved | its checkpointer can resume the same run |
| When a tool misbehaves | the stack trace points at your loop | the stack trace is three frames deeper, inside the graph runtime |
| Reading it cold | one function, top to bottom | a state type, two nodes, two routers |

What the numbers say: on this agent, neither is cheaper or more accurate, because the model does
the same work either way. What differs is what you pay in reading, debugging and dependencies, and
what you get: a graph is easier to extend with more nodes (a planner, a reviewer, a human step
that pauses and resumes), and harder to step through when one node does something unexpected.

The question for your decision record is not which is better in general. It is which you would
ship for this agent, now, and what would change your mind.
