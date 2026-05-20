from collections.abc import AsyncIterator

import httpx

from gateway.config import get_settings
from gateway.providers.base import BaseProvider, ProviderResponse
from gateway.schemas import ChatCompletionRequest
from gateway.utils.streaming import openai_sse_from_text
from gateway.utils.token_counter import count_message_tokens, count_text_tokens


class OllamaProvider(BaseProvider):
    name = "ollama"
    supported_models = {"ollama/llama3.1"}

    def __init__(self) -> None:
        self.settings = get_settings()

    async def complete(self, request: ChatCompletionRequest, model: str) -> ProviderResponse:
        from gateway.providers.base import ProviderError

        ollama_model = model.removeprefix("ollama/")
        payload = {
            "model": ollama_model,
            "messages": [m.model_dump() for m in request.messages],
            "stream": False,
            "options": {"temperature": request.temperature},
        }
        async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
            resp = await client.post(f"{self.settings.ollama_base_url}/api/chat", json=payload)
        if resp.status_code >= 400:
            raise ProviderError(self.name, resp.text, retryable=resp.status_code in {429, 500, 502, 503, 504})
        raw = resp.json()
        content = raw.get("message", {}).get("content", "")
        return ProviderResponse(model, self.name, content, raw, count_message_tokens(request.messages), count_text_tokens(content))

    async def stream(self, request: ChatCompletionRequest, model: str, request_id: str) -> AsyncIterator[str]:
        response = await self.complete(request, model)
        async for chunk in openai_sse_from_text(response.content, model, request_id):
            yield chunk

    async def health(self) -> bool:
        if not self.settings.ollama_base_url:
            return False
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(f"{self.settings.ollama_base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False
