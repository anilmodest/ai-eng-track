"""Week 1: your failure policy, measured on two real providers.

    uv run python scripts/failure_drill.py                       # MODEL_PROVIDER and the fallback
    uv run python scripts/failure_drill.py --providers gemini,groq

For each provider: the same structured call several times under YOUR policy (MODEL_RETRY_ATTEMPTS,
MODEL_TIMEOUT_S, MODEL_RETRY_BASE_DELAY_S), counting every attempt the retry helper makes, the
latency the caller sees (p50 and p95), what failed and how, and the cost per call. Then two
probes on the first provider: a timeout far too short to meet, and a model name that does not
exist. The first must be retried and end in a timeout; the second must not be retried at all.

Writes reports/failure_drill.json; `make evidence WEEK=1` keeps it. Your decision this week, the
failure policy, is read off these numbers.
"""

import argparse
import asyncio
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.api.schemas import DocumentExtract  # noqa: E402
from app.llm.client import Message, ModelClient, ModelError, ModelResponse  # noqa: E402
from app.llm.cost import estimate_cost_usd, price_known  # noqa: E402
from app.llm.registry import build_client  # noqa: E402
from app.llm.structured import SchemaError, complete_structured  # noqa: E402
from app.settings import Settings, get_settings  # noqa: E402

PROMPT = (ROOT / "app" / "llm" / "prompts" / "extract_v1.md").read_text(encoding="utf-8")
DOC = (ROOT / "samples" / "invoice.md").read_text(encoding="utf-8")
OUT = ROOT / "reports" / "failure_drill.json"


class Counting:
    """Wraps a client to count every attempt and how each one ended. Changes nothing else."""

    def __init__(self, inner: ModelClient) -> None:
        self.inner = inner
        self.name = inner.name
        self.model = inner.model
        self.attempts = 0
        self.statuses: list[str] = []

    async def complete(self, messages: list[Message], *, json_mode: bool = True) -> ModelResponse:
        self.attempts += 1
        try:
            r = await self.inner.complete(messages, json_mode=json_mode)
        except ModelError as e:
            self.statuses.append(str(e.status or type(e).__name__))
            raise
        self.statuses.append("ok")
        return r


def messages() -> list[Message]:
    return [
        Message(role="system", content=PROMPT),
        Message(role="user", content=f"<document>\n{DOC}\n</document>"),
    ]


async def one_call(
    client: Counting, s: Settings, *, attempts: int, timeout_s: float
) -> tuple[str, int, int, int]:
    """(outcome, ms the caller waited, tokens in, tokens out)."""
    started = time.perf_counter()
    try:
        _, responses = await complete_structured(
            client,
            messages(),
            DocumentExtract,
            attempts=attempts,
            base_delay_s=s.model_retry_base_delay_s,
            timeout_s=timeout_s,
        )
    except SchemaError:
        return "schema_error", int((time.perf_counter() - started) * 1000), 0, 0
    except ModelError as e:
        kind = "timeout" if "exceeded" in str(e) else f"provider_error_{e.status}"
        return kind, int((time.perf_counter() - started) * 1000), 0, 0
    ms = int((time.perf_counter() - started) * 1000)
    return "ok", ms, sum(r.tokens_in for r in responses), sum(r.tokens_out for r in responses)


async def drill(provider: str, s: Settings, calls: int) -> dict[str, Any]:
    key = s.model_api_key if provider == s.model_provider else s.model_fallback_api_key
    model = s.model_name if provider == s.model_provider else None
    client = Counting(build_client(provider, model=model, api_key=key, settings=s))
    outcomes, latencies, cost = [], [], 0.0
    for _ in range(calls):
        outcome, ms, t_in, t_out = await one_call(
            client, s, attempts=s.model_retry_attempts, timeout_s=s.model_timeout_s
        )
        outcomes.append(outcome)
        latencies.append(ms)
        if price_known(client.model):
            cost += estimate_cost_usd(client.model, t_in, t_out)
    ok = outcomes.count("ok")
    q = statistics.quantiles(latencies, n=20) if len(latencies) >= 2 else latencies * 19
    row = {
        "model": client.model,
        "calls": calls,
        "ok": ok,
        "ok_rate": round(ok / calls, 3),
        "attempts": client.attempts,
        "retries": client.attempts - calls,
        "outcomes": {o: outcomes.count(o) for o in sorted(set(outcomes))},
        "attempt_statuses": {st: client.statuses.count(st) for st in sorted(set(client.statuses))},
        "p50_ms": int(statistics.median(latencies)),
        "p95_ms": int(q[18]),
        "cost_usd": round(cost, 6),
        "cost_per_call_usd": round(cost / calls, 6),
    }
    print(
        f"  {provider:<12} ok {ok}/{calls}  retries {row['retries']}  p50 {row['p50_ms']} ms  "
        f"p95 {row['p95_ms']} ms  ${row['cost_per_call_usd']:.6f}/call"
    )
    return row


async def probes(provider: str, s: Settings) -> dict[str, Any]:
    key = s.model_api_key if provider == s.model_provider else s.model_fallback_api_key
    slow = Counting(build_client(provider, model=s.model_name, api_key=key, settings=s))
    outcome, ms, _, _ = await one_call(slow, s, attempts=s.model_retry_attempts, timeout_s=0.001)
    timeout = {"outcome": outcome, "attempts": slow.attempts, "ms": ms}
    wrong = Counting(build_client(provider, model="no-such-model-x", api_key=key, settings=s))
    outcome2, ms2, _, _ = await one_call(wrong, s, attempts=s.model_retry_attempts, timeout_s=10)
    bad = {"outcome": outcome2, "attempts": wrong.attempts, "ms": ms2}
    print(f"  timeout probe   {timeout['outcome']} after {timeout['attempts']} attempts")
    print(f"  bad-model probe {bad['outcome']} after {bad['attempts']} attempts (want 1)")
    return {"timeout": timeout, "bad_request": bad}


async def main(argv: list[str]) -> int:
    s = get_settings()
    ap = argparse.ArgumentParser()
    ap.add_argument("--providers", default="")
    ap.add_argument("--calls", type=int, default=8)
    args = ap.parse_args(argv)
    names = [p for p in args.providers.split(",") if p] or [
        p for p in (s.model_provider, s.model_fallback_provider) if p
    ]
    if len(names) < 2:
        print(
            "note: one provider only. Week 1 asks for two: set MODEL_FALLBACK_PROVIDER and its key"
        )
    policy = {
        "attempts": s.model_retry_attempts,
        "timeout_s": s.model_timeout_s,
        "base_delay_s": s.model_retry_base_delay_s,
    }
    print(f"failure drill, policy {policy}\n")
    providers = {name: await drill(name, s, args.calls) for name in names}
    report = {"policy": policy, "providers": providers, "probes": await probes(names[0], s)}
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("\nwrote reports/failure_drill.json")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main(sys.argv[1:])))
