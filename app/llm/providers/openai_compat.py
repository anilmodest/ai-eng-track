"""One adapter for every provider that speaks the OpenAI chat-completions dialect.

GitHub Models, Gemini, Groq, OpenRouter, Cerebras, Mistral and OpenAI itself all do. The only
things that differ are base_url, the key, and the model name: all of them configuration.
"""

import openai
from openai.types.chat import ChatCompletionMessageParam

from app.llm.client import Message, ModelError, ModelResponse, ModelTimeout


class OpenAICompatClient:
    def __init__(
        self, *, name: str, base_url: str, api_key: str, model: str, timeout_s: float
    ) -> None:
        self.name = name
        self.model = model
        self._timeout_s = timeout_s
        # max_retries=0: retrying is OUR decision (app/llm/retry.py), not the SDK's.
        self._client = openai.AsyncOpenAI(
            base_url=base_url, api_key=api_key, timeout=timeout_s, max_retries=0
        )

    async def complete(self, messages: list[Message], *, json_mode: bool = True) -> ModelResponse:
        payload: list[ChatCompletionMessageParam] = [
            {"role": m.role, "content": m.content}  # type: ignore[misc]
            for m in messages
        ]
        try:
            resp = await self._client.chat.completions.create(
                model=self.model,
                messages=payload,
                temperature=0,
                response_format={"type": "json_object"} if json_mode else {"type": "text"},
            )
        except openai.APITimeoutError as e:
            raise ModelTimeout(self._timeout_s) from e
        except openai.RateLimitError as e:
            raise ModelError(str(e), status=429, retryable=True) from e
        except openai.APIStatusError as e:
            raise ModelError(str(e), status=e.status_code, retryable=e.status_code >= 500) from e
        except openai.APIConnectionError as e:
            raise ModelError(str(e), status=None, retryable=True) from e

        choice = resp.choices[0] if resp.choices else None
        text = (choice.message.content if choice and choice.message else None) or ""
        usage = resp.usage
        return ModelResponse(
            text=text,
            provider=self.name,
            model=resp.model or self.model,
            tokens_in=usage.prompt_tokens if usage else 0,
            tokens_out=usage.completion_tokens if usage else 0,
        )
