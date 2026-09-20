"""List prices in USD per 1M tokens. Free tiers bill nothing; the design constraint is still real.

Unknown model -> 0.0 with a warning flag, never a crash. Re-verify before each cohort.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Price:
    input_per_m: float
    output_per_m: float


PRICES: dict[str, Price] = {
    "openai/gpt-4o-mini": Price(0.15, 0.60),
    "gpt-4o-mini": Price(0.15, 0.60),
    "openai/gpt-4o": Price(2.50, 10.00),
    "gpt-4o": Price(2.50, 10.00),
    "gemini-3.5-flash-lite": Price(0.30, 2.50),
    "gemini-3.1-flash-lite": Price(0.25, 1.50),
    "gemini-3.5-flash": Price(1.50, 9.00),
    "gemini-3.8-flash": Price(0.75, 3.75),
    "gemini-2.5-flash": Price(0.30, 2.50),
    "llama-3.3-70b-versatile": Price(0.59, 0.79),
    "llama-3.3-70b": Price(0.85, 1.20),
    "meta-llama/llama-3.3-70b-instruct:free": Price(0.0, 0.0),
    "mistral-small-latest": Price(0.10, 0.30),
    "fake-1": Price(1.00, 2.00),  # a made-up price so tests can see cost being recorded
}


def price_known(model: str) -> bool:
    return model in PRICES


def estimate_cost_usd(model: str, tokens_in: int, tokens_out: int) -> float:
    p = PRICES.get(model)
    if p is None:
        return 0.0
    return round((tokens_in * p.input_per_m + tokens_out * p.output_per_m) / 1_000_000, 6)
