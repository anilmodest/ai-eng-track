"""Week 4 worked example (start route): the loop's body, without the loop.

    uv run python weeks/4/routes/worked_example.py

One turn of the agent, written out in full: ask the model for one tool call, run it through the
door every tool goes through, and handle each way it can end. Your run_agent repeats this inside
the walls (steps, cost), and adds "finish" with the numbers check.

    the model answers with a call   -> app.tools.call runs it -> the result goes back as text
    the call is malformed           -> the result is an error the model can read; go round again
    the call needs approval         -> NeedsApproval: stop, and say what is pending
    the model fails                 -> ModelError, SchemaError: stop as a provider error
"""

import asyncio
import os

from sqlmodel import Session

from app.agents.agent import system_prompt
from app.db.session import get_engine
from app.llm.client import Message, ModelError
from app.llm.registry import get_model_client
from app.llm.structured import SchemaError, complete_structured
from app.settings import get_settings
from app.tools import NeedsApproval, ToolContext, call
from app.tools.base import ToolCall


async def one_turn(ctx: ToolContext, transcript: list[Message]) -> str:
    """Returns how the turn ended: the tool's result, or why it stopped."""
    assert ctx.client is not None
    s = ctx.settings
    try:
        step, _ = await complete_structured(
            ctx.client,
            transcript,
            ToolCall,
            attempts=s.model_retry_attempts,
            base_delay_s=s.model_retry_base_delay_s,
            timeout_s=s.model_timeout_s,
        )
    except (ModelError, SchemaError) as e:
        return f"stopped, provider error: {e}"
    print(f"  the model asks for {step.tool}({step.args})")
    if step.tool == "finish":
        return f"finished: {step.args.get('answer')}"
    try:
        result = await call(ctx, step.tool, step.args)
    except NeedsApproval as e:
        return f"stopped for approval: {e.tool}({e.arguments})"
    transcript.append(Message(role="assistant", content=step.model_dump_json()))
    transcript.append(Message(role="user", content=f"Result of {step.tool}: {result}"))
    return f"result: {result[:200]}"


async def main() -> None:
    with Session(get_engine()) as session:
        ctx = ToolContext(session=session, settings=get_settings(), client=get_model_client())
        for request in ("Which version is C-1004 on?", "Escalate T-2020 to engineering now."):
            transcript = [
                Message(role="system", content=system_prompt()),
                Message(role="user", content=f"Request: {request}"),
            ]
            print(f"Request: {request}")
            for _ in range(3):
                ending = await one_turn(ctx, transcript)
                print(f"  {ending}")
                if not ending.startswith("result"):
                    break
            print()


if __name__ == "__main__":
    os.environ.setdefault("DATABASE_URL", "sqlite:///./data/worked-example-4.db")
    os.environ.setdefault("MODEL_PROVIDER", "fake_a")
    asyncio.run(main())
