from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ModelInfo:
    id: str
    provider: str
    context_window: int
    supports_streaming: bool = True


MODEL_REGISTRY: dict[str, ModelInfo] = {
    "claude-opus-4-20250514": ModelInfo("claude-opus-4-20250514", "anthropic", 200_000),
    "claude-sonnet-4-20250514": ModelInfo("claude-sonnet-4-20250514", "anthropic", 200_000),
    "claude-haiku-4-5-20251001": ModelInfo("claude-haiku-4-5-20251001", "anthropic", 200_000),
    "gpt-4o-2024-11-20": ModelInfo("gpt-4o-2024-11-20", "openai", 128_000),
    "gpt-4o-mini-2024-07-18": ModelInfo("gpt-4o-mini-2024-07-18", "openai", 128_000),
    "o3-mini-2025-01-31": ModelInfo("o3-mini-2025-01-31", "openai", 128_000),
    "gemini-2.5-pro": ModelInfo("gemini-2.5-pro", "google", 1_000_000),
    "gemini-2.0-flash": ModelInfo("gemini-2.0-flash", "google", 1_000_000),
    "groq/llama-3.3-70b-versatile": ModelInfo("groq/llama-3.3-70b-versatile", "groq", 128_000),
    "groq/llama-3.1-8b-instant": ModelInfo("groq/llama-3.1-8b-instant", "groq", 128_000),
    "ollama/llama3.1": ModelInfo("ollama/llama3.1", "ollama", 128_000),
}

