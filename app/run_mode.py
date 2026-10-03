"""Which model and embedder produced a number, recorded beside the number itself.

A run on the fake providers and the lexical embedder proves the pipeline holds together: that
retrieval returns something, that citations line up, that a regression is caught. It says nothing
about whether answers are good. Those are different claims, and a report that does not say which
one it is making will eventually be read as the stronger one.

Every report records the mode, so nothing downstream can show a CI number as a measure of quality.
"""

from app.settings import get_settings

FAKE_PROVIDERS = frozenset({"fake_a", "fake_b"})
LEXICAL_EMBEDDERS = frozenset({"hash"})


def run_mode() -> dict[str, str]:
    """`real` only when both the model and the embedder are real. Otherwise `fake`."""
    settings = get_settings()
    real = (
        settings.model_provider not in FAKE_PROVIDERS
        and settings.embed_provider not in LEXICAL_EMBEDDERS
    )
    return {
        "provider_mode": "real" if real else "fake",
        "model_provider": settings.model_provider,
        "embed_provider": settings.embed_provider,
    }
