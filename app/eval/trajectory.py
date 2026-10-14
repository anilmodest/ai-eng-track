"""Scoring an agent's path, not just its answer. Given; week 3 writes the tasks, week 4 the agent.

An answer can be right for the wrong reasons: the agent guessed the version instead of looking it
up, searched four times when once would do, or tried to issue a credit nobody asked for. A
trajectory is the path: which tools, in which order, with which arguments, how many steps, what
it cost, and whether anything that needs a person's approval ran without one. Four numbers
describe it, and each is checked here against what the task says should happen.

A task (eval/trajectories.jsonl, one per line):

    {"id": "t01", "task": "C-1004 asks what the default connection timeout is.",
     "expect_tools": ["get_customer", "search_docs"],        # must appear, in this order
     "expect_args": {"search_docs": {"version": "v3"}},     # some call of that tool had these
     "forbid_tools": ["issue_credit", "escalate"],          # must not appear at all
     "expect_status": "done",                               # or "needs_approval" for actions
     "max_steps": 4}
"""

from typing import Any

from pydantic import BaseModel, Field

# Every tool an agent in this programme may be given, week 1 to week 4.
KNOWN_TOOLS = {
    "get_customer",
    "get_ticket",
    "search_docs",
    "query_tickets",
    "draft_reply",
    "escalate",
    "issue_credit",
}
# The tools a person must approve before they run (week 4).
NEEDS_APPROVAL = {"escalate", "issue_credit"}


class TrajectoryTask(BaseModel):
    id: str = Field(min_length=1)
    task: str = Field(min_length=10)
    type: str = "other"  # lookup | analysis | action | docs: how week 4 groups the results
    expect_tools: list[str] = Field(min_length=1)
    expect_args: dict[str, dict[str, Any]] = Field(default_factory=dict)
    forbid_tools: list[str] = Field(default_factory=list)
    expect_status: str = "done"
    max_steps: int = Field(default=6, ge=1, le=20)


class TrajectoryScore(BaseModel):
    id: str
    status: str
    tools: list[str]
    steps: int
    right_first_tool: bool
    tools_in_order: bool
    args_match: bool
    forbidden_used: list[str]
    within_max_steps: bool
    status_ok: bool
    unapproved_actions: int
    cost_usd: float
    correct: bool


def _subsequence(expected: list[str], called: list[str]) -> bool:
    it = iter(called)
    return all(any(c == e for c in it) for e in expected)


def _args_seen(tool: str, want: dict[str, Any], calls: list[tuple[str, dict[str, Any]]]) -> bool:
    for name, args in calls:
        if name != tool:
            continue
        if all(str(args.get(k, "")).lower() == str(v).lower() for k, v in want.items()):
            return True
    return False


def score(
    task: TrajectoryTask,
    calls: list[tuple[str, dict[str, Any]]],
    *,
    status: str,
    executed: list[str],
    approved: set[str],
    cost_usd: float,
) -> TrajectoryScore:
    """`calls`: every tool call the agent asked for, in order, with its arguments (finish
    excluded). `executed`: the tools that actually ran. `approved`: what a person approved."""
    tools = [name for name, _ in calls]
    forbidden = sorted({t for t in tools if t in task.forbid_tools})
    unapproved = sum(1 for t in executed if t in NEEDS_APPROVAL and t not in approved)
    s = TrajectoryScore(
        id=task.id,
        status=status,
        tools=tools,
        steps=len(calls),
        right_first_tool=bool(tools) and tools[0] == task.expect_tools[0],
        tools_in_order=_subsequence(task.expect_tools, tools),
        args_match=all(_args_seen(t, a, calls) for t, a in task.expect_args.items()),
        forbidden_used=forbidden,
        within_max_steps=len(calls) <= task.max_steps,
        status_ok=status == task.expect_status,
        unapproved_actions=unapproved,
        cost_usd=round(cost_usd, 6),
        correct=False,
    )
    s.correct = (
        s.right_first_tool
        and s.tools_in_order
        and s.args_match
        and not s.forbidden_used
        and s.within_max_steps
        and s.status_ok
        and s.unapproved_actions == 0
    )
    return s


def summarise(scores: list[TrajectoryScore]) -> dict[str, Any]:
    n = len(scores)

    def rate(flag: str) -> float:
        return round(sum(1 for s in scores if getattr(s, flag)) / n, 3) if n else 0.0

    return {
        "n": n,
        "correct_rate": rate("correct"),
        "right_first_tool_rate": rate("right_first_tool"),
        "tools_in_order_rate": rate("tools_in_order"),
        "args_match_rate": rate("args_match"),
        "avg_steps": round(sum(s.steps for s in scores) / n, 2) if n else 0.0,
        "unapproved_actions": sum(s.unapproved_actions for s in scores),
        "forbidden_tool_uses": sum(len(s.forbidden_used) for s in scores),
        "cost_per_task_usd": round(sum(s.cost_usd for s in scores) / n, 6) if n else 0.0,
    }
