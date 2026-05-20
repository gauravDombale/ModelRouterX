from collections.abc import AsyncIterator

import httpx

from gateway.config import get_settings
from gateway.providers.base import BaseProvider, ProviderResponse
from gateway.schemas import ChatCompletionRequest
from gateway.utils.streaming import openai_sse_from_text
from gateway.utils.token_counter import count_message_tokens, count_text_tokens


class GoogleProvider(BaseProvider):
    name = "google"
    supported_models = {"gemini-2.5-pro", "gemini-2.0-flash"}

    def __init__(self) -> None:
        self.settings = get_settings()

    def _payload(self, request: ChatCompletionRequest) -> dict:
        contents = []
        system_parts = []
        for message in request.messages:
            text = message.content if isinstance(message.content, str) else str(message.content)
            if message.role == "system":
                system_parts.append({"text": text})
                continue
            contents.append({"role": "model" if message.role == "assistant" else "user", "parts": [{"text": text}]})
        payload = {"contents": contents, "generationConfig": {"temperature": request.temperature, "maxOutputTokens": request.max_tokens}}
        if system_parts:
            payload["systemInstruction"] = {"parts": system_parts}
        return payload

    async def complete(self, request: ChatCompletionRequest, model: str) -> ProviderResponse:
        from gateway.providers.base import ProviderError

        if not self.settings.google_api_key:
            raise ProviderError(self.name, "GOOGLE_API_KEY is not configured", retryable=False)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
            resp = await client.post(url, params={"key": self.settings.google_api_key}, json=self._payload(request))
        if resp.status_code >= 400:
            raise ProviderError(self.name, resp.text, retryable=resp.status_code in {429, 500, 502, 503, 504})
        raw = resp.json()
        content = "".join(
            part.get("text", "")
            for candidate in raw.get("candidates", [])
            for part in candidate.get("content", {}).get("parts", [])
        )
        usage = raw.get("usageMetadata") or {}
        return ProviderResponse(
            model,
            self.name,
            content,
            raw,
            usage.get("promptTokenCount", count_message_tokens(request.messages)),
            usage.get("candidatesTokenCount", count_text_tokens(content)),
        )

    async def stream(self, request: ChatCompletionRequest, model: str, request_id: str) -> AsyncIterator[str]:
        response = await self.complete(request, model)
        async for chunk in openai_sse_from_text(response.content, model, request_id):
            yield chunk

    async def health(self) -> bool:
        if not self.settings.google_api_key:
            return False
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                url = "https://generativelanguage.googleapis.com/v1beta/models"
                resp = await client.get(url, params={"key": self.settings.google_api_key})
                return resp.status_code == 200
        except Exception:
            return False
