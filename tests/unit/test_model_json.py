"""model.json names the model you build on; the hidden evaluation's model tier runs on it."""

import json
from pathlib import Path

from app.llm.registry import CONFIGURED_PROVIDERS, FAKE_PROVIDERS, PROVIDERS

ROOT = Path(__file__).resolve().parents[2]


def test_model_json_names_a_real_provider_and_a_model() -> None:
    data = json.loads((ROOT / "model.json").read_text(encoding="utf-8"))
    assert isinstance(data, dict), "model.json is one JSON object"
    provider, model = data.get("provider"), data.get("model")
    real = set(PROVIDERS) | (CONFIGURED_PROVIDERS - {"programme"})
    assert provider in real, f"model.json: provider {provider!r} is not one of {sorted(real)}" + (
        " (a fake provider is for CI, not for building on)" if provider in FAKE_PROVIDERS else ""
    )
    assert isinstance(model, str) and model.strip(), "model.json: give the model's name"
