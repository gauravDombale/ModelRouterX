DEFAULT_P50_MS = {
    "groq/llama-3.1-8b": 120,
    "groq/llama-3.3-70b": 180,
    "gemini-2.0-flash": 450,
    "gpt-4o-mini-2024-07-18": 650,
    "claude-haiku-4-5-20251001": 700,
    "gpt-4o-2024-11-20": 1100,
    "claude-sonnet-4-20250514": 1300,
    "o3-mini-2025-01-31": 1400,
    "gemini-2.5-pro": 1600,
    "claude-opus-4-20250514": 2200,
    "ollama/llama3.1": 350,
}


def latency_ms(model: str) -> int:
    return DEFAULT_P50_MS.get(model, 1000)


def choose_latency_optimized(candidates: list[str], task_type: str) -> tuple[str, str]:
    selected = min(candidates, key=latency_ms)
    return selected, f"Lowest recent p50 latency for {task_type}"

