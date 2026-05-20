from collections.abc import AsyncIterator

import httpx

from gateway.config import get_settings
from gateway.providers.base import BaseProvider, ProviderError, ProviderResponse
from gateway.schemas import ChatCompletionRequest
from gateway.utils.streaming import openai_sse_from_text
from gateway.utils.token_counter import count_message_tokens, count_text_tokens


class AnthropicProvider(BaseProvider):
    name = "anthropic"
    supported_models = {"claude-opus-4-20250514", "claude-sonnet-4-20250514", "claude-haiku-4-5-20251001"}

    def __init__(self) -> None:
        self.settings = get_settings()

    def _headers(self) -> dict[str, str]:
        if not self.settings.anthropic_api_key:
            raise ProviderError(self.name, "ANTHROPIC_API_KEY is not configured", retryable=False)
        return {
            "x-api-key": self.settings.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

    def _payload(self, request: ChatCompletionRequest, model: str, stream: bool) -> dict:
        system = "\n".join(m.content for m in request.messages if m.role == "system" and isinstance(m.content, str))
        messages = [m.model_dump() for m in request.messages if m.role != "system"]
        return {
            "model": model,
            "messages": messages,
            "system": system or None,
            "max_tokens": request.max_tokens or 1024,
            "temperature": request.temperature,
            "stream": stream,
        }

    async def complete(self, request: ChatCompletionRequest, model: str) -> ProviderResponse:
        async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
            resp = await client.post("https://api.anthropic.com/v1/messages", headers=self._headers(), json=self._payload(request, model, False))
        if resp.status_code >= 400:
            raise ProviderError(self.name, resp.text, retryable=resp.status_code in {429, 500, 502, 503, 504})
        raw = resp.json()
        content = "".join(part.get("text", "") for part in raw.get("content", []) if part.get("type") == "text")
        usage = raw.get("usage") or {}
        return ProviderResponse(
            model=model,
            provider=self.name,
            content=content,
            raw=raw,
            prompt_tokens=usage.get("input_tokens", count_message_tokens(request.messages)),
            completion_tokens=usage.get("output_tokens", count_text_tokens(content)),
        )

    async def stream(self, request: ChatCompletionRequest, model: str, request_id: str) -> AsyncIterator[str]:
        # Anthropic SSE uses a different shape; this MVP returns an OpenAI-compatible stream after one call.
        response = await self.complete(request, model)
        async for chunk in openai_sse_from_text(response.content, model, request_id):
            yield chunk

    async def health(self) -> bool:
        if not self.settings.anthropic_api_key:
            return False
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get("https://api.anthropic.com/v1/models", headers=self._headers())
                return resp.status_code == 200
        except Exception:
            return False

