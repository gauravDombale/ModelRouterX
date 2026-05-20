from gateway.providers.anthropic import AnthropicProvider
from gateway.providers.base import BaseProvider
from gateway.providers.google import GoogleProvider
from gateway.providers.groq import GroqProvider
from gateway.providers.models import MODEL_REGISTRY, ModelInfo
from gateway.providers.ollama import OllamaProvider
from gateway.providers.openai import OpenAIProvider
from gateway.config import get_settings
from gateway.utils.pricing import MODEL_PRICING, canonical_model


class ProviderRegistry:
    def __init__(self) -> None:
        self.providers: dict[str, BaseProvider] = {
            "anthropic": AnthropicProvider(),
            "openai": OpenAIProvider(),
            "google": GoogleProvider(),
            "groq": GroqProvider(),
            "ollama": OllamaProvider(),
        }

    def provider_available(self, provider: str) -> bool:
        settings = get_settings()
        return {
            "anthropic": bool(settings.anthropic_api_key),
            "openai": bool(settings.openai_api_key),
            "google": bool(settings.google_api_key),
            "groq": bool(settings.groq_api_key),
            "ollama": bool(settings.ollama_base_url),
        }.get(provider, False)

    def available_model_ids(self) -> list[str]:
        return [model for model, info in MODEL_REGISTRY.items() if self.provider_available(info.provider)]

    def model_info(self, model: str) -> ModelInfo:
        resolved = canonical_model(model)
        if resolved not in MODEL_REGISTRY:
            raise KeyError(f"Unknown model: {model}")
        return MODEL_REGISTRY[resolved]

    def provider_for_model(self, model: str) -> BaseProvider:
        info = self.model_info(model)
        return self.providers[info.provider]

    def list_models(self) -> list[dict]:
        return [
            {
                "id": info.id,
                "provider": info.provider,
                "context_window": info.context_window,
                "pricing_per_1m": MODEL_PRICING.get(info.id, (0, 0)),
                "supports_streaming": info.supports_streaming,
                "available": self.provider_available(info.provider),
            }
            for info in MODEL_REGISTRY.values()
        ]


provider_registry = ProviderRegistry()
