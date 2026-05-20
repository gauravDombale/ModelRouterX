import json
from collections.abc import AsyncIterator


def sse(data: dict | str) -> str:
    payload = data if isinstance(data, str) else json.dumps(data)
    return f"data: {payload}\n\n"


async def openai_sse_from_text(text: str, model: str, request_id: str) -> AsyncIterator[str]:
    yield sse({"id": request_id, "object": "chat.completion.chunk", "model": model, "choices": [{"index": 0, "delta": {"role": "assistant"}, "finish_reason": None}]})
    yield sse({"id": request_id, "object": "chat.completion.chunk", "model": model, "choices": [{"index": 0, "delta": {"content": text}, "finish_reason": None}]})
    yield sse({"id": request_id, "object": "chat.completion.chunk", "model": model, "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]})
    yield "data: [DONE]\n\n"

