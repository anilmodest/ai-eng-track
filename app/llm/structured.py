"""Ask for JSON, validate it against a schema, repair once, then fail loudly.

Free text from a model is not data. It becomes data only after it has passed a schema.
"""

import json

from pydantic import BaseModel, ValidationError

from app.llm.client import Message, ModelClient, ModelResponse
from app.llm.retry import with_retry


class SchemaError(Exception):
    """The model answered, twice, and neither answer fitted the schema."""

    def __init__(self, detail: str, raw: str) -> None:
        super().__init__(detail)
        self.detail = detail
        self.raw = raw


def _parse[T: BaseModel](schema: type[T], text: str) -> T:
    return schema.model_validate(json.loads(text))


async def complete_structured[T: BaseModel](
    client: ModelClient,
    messages: list[Message],
    schema: type[T],
    *,
    attempts: int,
    base_delay_s: float,
    timeout_s: float,
) -> tuple[T, list[ModelResponse]]:
    """Returns the parsed object and every response it took to get there (for cost accounting)."""
    responses: list[ModelResponse] = []

    async def call(msgs: list[Message]) -> ModelResponse:
        r = await with_retry(
            lambda: client.complete(msgs, json_mode=True),
            attempts=attempts,
            base_delay_s=base_delay_s,
            timeout_s=timeout_s,
        )
        responses.append(r)
        return r

    first = await call(messages)
    try:
        return _parse(schema, first.text), responses
    except (json.JSONDecodeError, ValidationError) as err:
        repair = [
            *messages,
            Message(role="assistant", content=first.text or "(empty)"),
            Message(
                role="user",
                content=(
                    "That was not valid. Return ONLY a JSON object matching this schema, "
                    "no prose:\n"
                    f"{json.dumps(schema.model_json_schema())}\n"
                    f"Validation error: {err}"
                ),
            ),
        ]
        second = await call(repair)
        try:
            return _parse(schema, second.text), responses
        except (json.JSONDecodeError, ValidationError) as err2:
            raise SchemaError(str(err2), second.text) from err2
