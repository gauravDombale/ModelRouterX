from decimal import Decimal

MODEL_PRICING: dict[str, tuple[Decimal, Decimal]] = {
    "claude-opus-4-20250514": (Decimal("15.00"), Decimal("75.00")),
    "claude-sonnet-4-20250514": (Decimal("3.00"), Decimal("15.00")),
    "claude-haiku-4-5-20251001": (Decimal("0.80"), Decimal("4.00")),
    "gpt-4o-2024-11-20": (Decimal("2.50"), Decimal("10.00")),
    "gpt-4o-mini-2024-07-18": (Decimal("0.15"), Decimal("0.60")),
    "o3-mini-2025-01-31": (Decimal("1.10"), Decimal("4.40")),
    "gemini-2.5-pro": (Decimal("1.25"), Decimal("10.00")),
    "gemini-2.0-flash": (Decimal("0.10"), Decimal("0.40")),
    "groq/llama-3.3-70b-versatile": (Decimal("0.59"), Decimal("0.79")),
    "groq/llama-3.1-8b-instant": (Decimal("0.05"), Decimal("0.08")),
    "ollama/llama3.1": (Decimal("0.00"), Decimal("0.00")),
}


def canonical_model(model: str) -> str:
    aliases = {
        "claude-sonnet-4": "claude-sonnet-4-20250514",
        "claude-haiku-4": "claude-haiku-4-5-20251001",
        "claude-haiku-4-5": "claude-haiku-4-5-20251001",
        "gpt-4o": "gpt-4o-2024-11-20",
        "gpt-4o-mini": "gpt-4o-mini-2024-07-18",
        "o3-mini": "o3-mini-2025-01-31",
    }
    return aliases.get(model, model)


def calculate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> tuple[Decimal, Decimal, Decimal]:
    input_per_m, output_per_m = MODEL_PRICING.get(canonical_model(model), (Decimal("0"), Decimal("0")))
    prompt_cost = (Decimal(prompt_tokens) / Decimal(1_000_000)) * input_per_m
    completion_cost = (Decimal(completion_tokens) / Decimal(1_000_000)) * output_per_m
    return prompt_cost, completion_cost, prompt_cost + completion_cost

