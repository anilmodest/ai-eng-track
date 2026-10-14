"""Week 1: how often does the model call the right tool, with valid arguments? Before and after.

    uv run python scripts/tool_drill.py                  # your model, from .env
    MODEL_PROVIDER=fake_a uv run python scripts/tool_drill.py   # the plumbing, no key

Twenty support-desk requests (eval/tool_drill.jsonl), each needing exactly one of the two tools
you designed. Every request is run twice on the same model:

    before   the tools described the way a first draft usually is (eval/tool_drill_before.json)
    after    the tools as you described them in app/tools/desk.py

A call is correct when it names the right tool, its arguments pass YOUR validation, and they
carry the id the request was about. Writes reports/tool_drill.json; `make evidence WEEK=1` keeps
it. The difference between the two runs is caused by nothing but your descriptions.
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pydantic import ValidationError  # noqa: E402

from app.llm.client import Message, ModelError  # noqa: E402
from app.llm.cost import estimate_cost_usd, price_known  # noqa: E402
from app.llm.registry import get_model_client  # noqa: E402
from app.llm.structured import SchemaError, complete_structured  # noqa: E402
from app.settings import get_settings  # noqa: E402
from app.tools import TOOLS, tool_schemas  # noqa: E402
from app.tools.base import ToolCall  # noqa: E402

DRILL = ROOT / "eval" / "tool_drill.jsonl"
BEFORE = ROOT / "eval" / "tool_drill_before.json"
PROMPT = (ROOT / "app" / "llm" / "prompts" / "tool_call_v1.md").read_text(encoding="utf-8")
DRILL_TOOLS = ["get_customer", "get_ticket"]
OUT = ROOT / "reports" / "tool_drill.json"


def before_schemas() -> list[dict[str, Any]]:
    """The same two tools, as a first draft describes them: vague, and unconstrained."""
    drafts = json.loads(BEFORE.read_text(encoding="utf-8"))
    out = []
    for name in DRILL_TOOLS:
        d = drafts[name]
        props = {a: {"type": "string", "description": text} for a, text in d["args"].items()}
        out.append(
            {
                "name": name,
                "description": d["description"],
                "parameters": {"type": "object", "properties": props, "required": list(props)},
            }
        )
    return out


async def run(label: str, schemas: list[dict[str, Any]], items: list[dict[str, str]]) -> Any:
    s = get_settings()
    client = get_model_client()
    rows = []
    tokens_in = tokens_out = 0
    started = time.perf_counter()
    for item in items:
        messages = [
            Message(role="system", content=f"{PROMPT}\nTools:\n{json.dumps(schemas, indent=1)}"),
            Message(role="user", content=f"Request: {item['request']}"),
        ]
        row: dict[str, Any] = {"request": item["request"], "expected": item["tool"]}
        try:
            call, responses = await complete_structured(
                client,
                messages,
                ToolCall,
                attempts=s.model_retry_attempts,
                base_delay_s=s.model_retry_base_delay_s,
                timeout_s=s.model_timeout_s,
            )
        except (ModelError, SchemaError) as e:
            row.update(tool=None, error=type(e).__name__, correct=False)
            rows.append(row)
            continue
        tokens_in += sum(r.tokens_in for r in responses)
        tokens_out += sum(r.tokens_out for r in responses)
        spec = TOOLS.get(call.tool)
        try:
            valid = spec is not None and bool(spec.args.model_validate(call.args))
        except ValidationError:
            valid = False
        values = " ".join(str(v) for v in call.args.values()).upper()
        right_tool = call.tool == item["tool"]
        right_value = item["value"].upper() in values
        row.update(
            tool=call.tool,
            args=call.args,
            right_tool=right_tool,
            valid_args=valid,
            right_value=right_value,
            invented_tool=call.tool not in DRILL_TOOLS,
            correct=right_tool and valid and right_value,
        )
        rows.append(row)
    n = len(rows)

    def rate(key: str) -> float:
        return round(sum(1 for r in rows if r.get(key)) / n, 3) if n else 0.0

    model = client.model
    cost = estimate_cost_usd(model, tokens_in, tokens_out) if price_known(model) else 0.0
    summary = {
        "n": n,
        "correct_rate": rate("correct"),
        "right_tool_rate": rate("right_tool"),
        "valid_args_rate": rate("valid_args"),
        "invented_tool_rate": rate("invented_tool"),
        "errors": sum(1 for r in rows if r.get("error")),
        "cost_usd": round(cost, 6),
        "seconds": round(time.perf_counter() - started, 2),
    }
    print(
        f"{label:<7} correct {summary['correct_rate']:.2f}  right tool "
        f"{summary['right_tool_rate']:.2f}  valid args {summary['valid_args_rate']:.2f}  "
        f"invented {summary['invented_tool_rate']:.2f}  errors {summary['errors']}"
    )
    return {**summary, "calls": rows}


async def main() -> int:
    items = [json.loads(line) for line in DRILL.read_text(encoding="utf-8").splitlines() if line]
    client = get_model_client()
    print(f"tool drill: {len(items)} requests on {client.name} / {client.model}\n")
    before = await run("before", before_schemas(), items)
    after = await run("after", tool_schemas(DRILL_TOOLS), items)
    report = {
        "provider": client.name,
        "model": client.model,
        "before": before,
        "after": after,
        "delta_correct_rate": round(after["correct_rate"] - before["correct_rate"], 3),
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    delta = report["delta_correct_rate"]
    print(f"\nchange in correct calls: {delta:+.2f}   (reports/tool_drill.json)")
    print("Read the wrong calls in the report before you change a description: why that one?")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
