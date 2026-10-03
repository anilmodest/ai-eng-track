"""Is a model key configured, and if not, exactly what to do about it.

Week 0 needs no key, so a fellow can finish it, feel set up, and only discover on the first
morning of week 1 that nothing involving a model works. The repository knows this the whole
time. It should say so before it becomes a traceback.

One place, used by three: `make next`, the Codespace's first run, and the explore scripts.
"""

from app.llm.registry import ProviderConfigError, get_model_client

HOW = """No model key is set, and everything from week 1 onward needs one.

  1. Get one free, no card:  https://aistudio.google.com/apikey
  2. In this workspace:      echo 'MODEL_API_KEY=your-key' >> .env

  Better, because a container rebuild wipes .env: add it as a Codespaces secret named
  GEMINI_API_KEY (github.com/settings/codespaces) and restart the Codespace.

  Already have a key for another provider? Set MODEL_PROVIDER=groq or openrouter and its key.
  Switching provider without touching code is week 1's whole point, so this is on-topic."""


def key_ready() -> tuple[bool, str]:
    """(is a provider usable, the reason it is not). Never raises."""
    try:
        get_model_client()
    except ProviderConfigError as exc:
        return (False, str(exc))
    except Exception as exc:  # a broken provider name, a bad URL: still worth saying plainly
        return (False, f"{type(exc).__name__}: {exc}")
    return (True, "")


def require_key() -> None:
    """For a script that cannot do anything useful without one. Exits cleanly, not with a stack.

    A traceback says "this is broken". A missing key is not broken, it is unfinished setup, and
    the difference matters on the morning a fellow meets it.
    """
    ok, why = key_ready()
    if ok:
        return
    raise SystemExit(f"\n{why}\n\n{HOW}\n")
