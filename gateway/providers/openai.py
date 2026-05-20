import json
from collections.abc import AsyncIterator

import httpx

from gateway.config import get_settings
from gateway.providers.base import BaseProvider, ProviderError, ProviderResponse
from gateway.schemas import ChatCompletionRequest
from gateway.utils.token_counter import count_message_tokens, count_text_tokens


class OpenAIProvider(BaseProvider):
    name = "openai"
    supported_models = {"gpt-4o-2024-11-20", "gpt-4o-mini-2024-07-18", "o3-mini-2025-01-31"}
    base_url = "https://api.openai.com/v1"

    def __init__(self) -> None:
        self.settings = get_settings()

    def _headers(self) -> dict[str, str]:
        if not self.settings.openai_api_key:
            raise ProviderError(self.name, "OPENAI_API_KEY is not configured", retryable=False)
        return {"Authorization": f"Bearer {self.settings.openai_api_key}", "Content-Type": "application/json"}

    async def complete(self, request: ChatCompletionRequest, model: str) -> ProviderResponse:
        payload = request.model_dump(exclude={"mrx"})
        payload["model"] = model
        payload["stream"] = False
        async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
            resp = await client.post(f"{self.base_url}/chat/completions", headers=self._headers(), json=payload)
        if resp.status_code >= 400:
            raise ProviderError(self.name, resp.text, retryable=resp.status_code in {429, 500, 502, 503, 504})
        raw = resp.json()
        content = raw["choices"][0]["message"].get("content", "")
        usage = raw.get("usage") or {}
        return ProviderResponse(
            model=model,
            provider=self.name,
            content=content,
            raw=raw,
            prompt_tokens=usage.get("prompt_tokens", count_message_tokens(request.messages)),
            completion_tokens=usage.get("completion_tokens", count_text_tokens(content)),
        )

    async def stream(self, request: ChatCompletionRequest, model: str, request_id: str) -> AsyncIterator[str]:
        payload = request.model_dump(exclude={"mrx"})
        payload["model"] = model
        payload["stream"] = True
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("POST", f"{self.base_url}/chat/completions", headers=self._headers(), json=payload) as resp:
                if resp.status_code >= 400:
                    body = await resp.aread()
                    raise ProviderError(self.name, body.decode(), retryable=resp.status_code in {429, 500, 502, 503, 504})
                async for line in resp.aiter_lines():
                    if line.startswith("data:"):
                        yield line + "\n\n"
        _ = json, request_id

    async def health(self) -> bool:
        if not self.settings.openai_api_key:
            return False
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/models", headers=self._headers())
                return resp.status_code == 200
        except Exception:
            return False
