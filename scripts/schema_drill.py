"""Week 1: is Pydantic worth it? A number, not a rule.

    uv run python scripts/schema_drill.py              # your model, from .env

The same documents, the same model, two ways of asking for the same five fields:

    plain     "reply in JSON with these keys", then json.loads and the schema, once, no repair
    enforced  the extract prompt with every rule, validated against DocumentExtract, one repair
              attempt with the error attached (your complete_structured)

For each, how many answers fit the schema, and how the others broke: not JSON at all, or JSON
that breaks a rule (a summary over 60 words, two key facts, an invented doc_type). Writes
reports/schema_drill.json; `make evidence WEEK=1` keeps it. Every later week puts tool arguments
and actions through the same models, so this is the number behind all of them.
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

from app.api.schemas import DocumentExtract  # noqa: E402
from app.llm.client import Message, ModelError  # noqa: E402
from app.llm.registry import get_model_client  # noqa: E402
from app.llm.structured import SchemaError, complete_structured  # noqa: E402
from app.settings import get_settings  # noqa: E402

PLAIN = (
    "TASK: extract\nRead the document and reply in JSON with the keys title, doc_type, summary, "
    "key_facts and confidence."
)
ENFORCED = (ROOT / "app" / "llm" / "prompts" / "extract_v1.md").read_text(encoding="utf-8")
OUT = ROOT / "reports" / "schema_drill.json"


def documents(limit: int) -> list[Path]:
    """The sample documents and the business documents of the corpus: mixed shapes on purpose."""
    found = sorted((ROOT / "samples").glob("*")) + sorted(
        p for p in (ROOT / "corpus").glob("*") if not p.name.startswith("manual-")
    )
    return [p for p in found if p.suffix in (".md", ".txt", ".csv")][:limit]


def classify(text: str) -> str:
    try:
        DocumentExtract.model_validate(json.loads(text))
        return "ok"
    except json.JSONDecodeError:
        return "not_json"
    except ValidationError:
        return "breaks_schema"


async def plain(doc: str) -> tuple[str, int]:
    s = get_settings()
    client = get_model_client()
    messages = [
        Message(role="system", content=PLAIN),
        Message(role="user", content=doc[: s.max_input_chars]),
    ]
    try:
        r = await client.complete(messages, json_mode=False)
    except ModelError:
        return "provider_error", 0
    return classify(r.text), r.tokens_in + r.tokens_out


async def enforced(doc: str) -> tuple[str, int, bool]:
    s = get_settings()
    client = get_model_client()
    messages = [
        Message(role="system", content=ENFORCED),
        Message(role="user", content=f"<document>\n{doc[: s.max_input_chars]}\n</document>"),
    ]
    try:
        _, responses = await complete_structured(
            client,
            messages,
            DocumentExtract,
            attempts=s.model_retry_attempts,
            base_delay_s=s.model_retry_base_delay_s,
            timeout_s=s.model_timeout_s,
        )
    except SchemaError:
        return "breaks_schema", 0, True
    except ModelError:
        return "provider_error", 0, False
    tokens = sum(r.tokens_in + r.tokens_out for r in responses)
    return "ok", tokens, len(responses) > 1


def summarise(outcomes: list[str], tokens: int, repaired: int = 0) -> dict[str, Any]:
    n = len(outcomes)
    counts = {k: outcomes.count(k) for k in ("ok", "not_json", "breaks_schema", "provider_error")}
    return {
        "n": n,
        **counts,
        "ok_rate": round(counts["ok"] / n, 3) if n else 0.0,
        "repaired": repaired,
        "tokens": tokens,
    }


async def main() -> int:
    client = get_model_client()
    docs = documents(limit=15)
    print(f"schema drill: {len(docs)} documents on {client.name} / {client.model}\n")
    started = time.perf_counter()
    p_out, e_out, p_tok, e_tok, repaired = [], [], 0, 0, 0
    for path in docs:
        text = path.read_text(encoding="utf-8")
        p, pt = await plain(text)
        e, et, rep = await enforced(text)
        p_out.append(p)
        e_out.append(e)
        p_tok += pt
        e_tok += et
        repaired += int(rep and e == "ok")
        print(f"  {path.name:<38} plain {p:<14} enforced {e}{' (repaired)' if rep else ''}")
    report: dict[str, Any] = {
        "provider": client.name,
        "model": client.model,
        "plain": summarise(p_out, p_tok),
        "enforced": summarise(e_out, e_tok, repaired),
        "seconds": round(time.perf_counter() - started, 1),
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(
        f"\nfits the schema: plain {report['plain']['ok_rate']:.2f}, enforced "
        f"{report['enforced']['ok_rate']:.2f} ({repaired} needed the repair)  "
        "(reports/schema_drill.json)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
