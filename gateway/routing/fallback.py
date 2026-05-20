from gateway.providers.models import MODEL_REGISTRY

FALLBACKS = {
    "claude-opus-4-20250514": ["gpt-4o-2024-11-20", "gemini-2.5-pro", "gpt-4o-mini-2024-07-18"],
    "claude-sonnet-4-20250514": ["gpt-4o-2024-11-20", "gemini-2.5-pro", "gpt-4o-mini-2024-07-18"],
    "claude-haiku-4-5-20251001": ["gpt-4o-mini-2024-07-18", "gemini-2.0-flash", "groq/llama-3.1-8b"],
    "gpt-4o-2024-11-20": ["claude-sonnet-4-20250514", "gemini-2.5-pro", "gpt-4o-mini-2024-07-18"],
    "gpt-4o-mini-2024-07-18": ["claude-haiku-4-5-20251001", "gemini-2.0-flash", "groq/llama-3.1-8b"],
    "o3-mini-2025-01-31": ["gpt-4o-2024-11-20", "claude-sonnet-4-20250514", "gpt-4o-mini-2024-07-18"],
}


def fallback_chain(primary: str, user_fallbacks: list[str] | None = None) -> list[str]:
    chain = [primary, *(user_fallbacks or []), *FALLBACKS.get(primary, [])]
    deduped: list[str] = []
    for model in chain:
        if model in MODEL_REGISTRY and model not in deduped:
            deduped.append(model)
    return deduped
