from collections.abc import AsyncIterator

from gateway.providers.openai import OpenAIProvider


class GroqProvider(OpenAIProvider):
    name = "groq"
    supported_models = {"groq/llama-3.3-70b", "groq/llama-3.1-8b"}
    base_url = "https://api.groq.com/openai/v1"

    def _headers(self) -> dict[str, str]:
        if not self.settings.groq_api_key:
            from gateway.providers.base import ProviderError

            raise ProviderError(self.name, "GROQ_API_KEY is not configured", retryable=False)
        return {"Authorization": f"Bearer {self.settings.groq_api_key}", "Content-Type": "application/json"}

    async def complete(self, request, model: str):
        response = await super().complete(request, model.removeprefix("groq/"))
        response.model = model
        return response

    async def stream(self, request, model: str, request_id: str) -> AsyncIterator[str]:
        async for chunk in super().stream(request, model.removeprefix("groq/"), request_id):
            yield chunk
