"""Week 1, elaboration 3: two tools, described badly. Watch the model call them wrongly.

    uv run python explore/w1_03_vague_tools.py

Change nothing. The model is offered two tools whose descriptions say almost nothing, and six
requests that each need one of them. Note which requests go to the wrong tool, which get an id in
the wrong argument, and which get a tool that does not exist. Then read your own descriptions in
app/tools/desk.py with the same eyes: the description is the only thing the model knows about the
tool.
"""

import asyncio
import json

from app.llm.client import Message
from app.llm.registry import get_model_client
from app.llm.structured import complete_structured
from app.settings import get_settings
from app.tools.base import ToolCall

PROMPT = open("app/llm/prompts/tool_call_v1.md", encoding="utf-8").read()

VAGUE = [
    {
        "name": "lookup",
        "description": "Looks things up.",
        "parameters": {
            "type": "object",
            "properties": {"id": {"type": "string", "description": "The id."}},
            "required": ["id"],
        },
    },
    {
        "name": "fetch",
        "description": "Fetches records.",
        "parameters": {
            "type": "object",
            "properties": {"ref": {"type": "string", "description": "A reference."}},
            "required": ["ref"],
        },
    },
]
# What each tool really does, which the model is never told: lookup = a customer, fetch = a ticket.
REQUESTS = [
    ("Which version is customer C-1004 on?", "lookup"),
    ("What is the status of ticket T-2010?", "fetch"),
    ("What plan is C-1007 on?", "lookup"),
    ("How urgent is T-2047?", "fetch"),
    ("Customer C-1003 says ticket T-2014 is urgent. Is it?", "fetch"),
    ("Escalate T-2005 to engineering.", "none: no tool can do that"),
]


async def main() -> None:
    s = get_settings()
    client = get_model_client()
    print(f"provider={client.name} model={client.model}\n")
    tools = json.dumps(VAGUE, indent=1)
    for request, meant in REQUESTS:
        messages = [
            Message(role="system", content=f"{PROMPT}\nTools:\n{tools}"),
            Message(role="user", content=f"Request: {request}"),
        ]
        call, _ = await complete_structured(
            client,
            messages,
            ToolCall,
            attempts=s.model_retry_attempts,
            base_delay_s=s.model_retry_base_delay_s,
            timeout_s=s.model_timeout_s,
        )
        verdict = "right" if call.tool == meant else f"meant {meant}"
        print(f"{request}\n    -> {call.tool}({json.dumps(call.args)})   {verdict}\n")
    print("Which mistakes would a better description have prevented? Which would a constraint?")


if __name__ == "__main__":
    from app.llm.keys import require_key

    require_key()
    asyncio.run(main())
