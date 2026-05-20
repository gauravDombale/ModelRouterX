QUALITY_MATRIX: dict[str, dict[str, float]] = {
    "claude-opus-4-20250514": {"code": 0.98, "reasoning": 0.99, "creative": 0.97, "factual": 0.96, "chat": 0.90, "long_doc": 0.97},
    "claude-sonnet-4-20250514": {"code": 0.95, "reasoning": 0.93, "creative": 0.94, "factual": 0.93, "chat": 0.88, "long_doc": 0.95},
    "claude-haiku-4-5-20251001": {"code": 0.80, "reasoning": 0.75, "creative": 0.78, "factual": 0.82, "chat": 0.85, "long_doc": 0.75},
    "gpt-4o-2024-11-20": {"code": 0.94, "reasoning": 0.94, "creative": 0.91, "factual": 0.93, "chat": 0.87, "long_doc": 0.88},
    "gpt-4o-mini-2024-07-18": {"code": 0.78, "reasoning": 0.74, "creative": 0.76, "factual": 0.80, "chat": 0.84, "long_doc": 0.72},
    "o3-mini-2025-01-31": {"code": 0.88, "reasoning": 0.97, "creative": 0.72, "factual": 0.88, "chat": 0.75, "long_doc": 0.80},
    "gemini-2.5-pro": {"code": 0.91, "reasoning": 0.90, "creative": 0.88, "factual": 0.90, "chat": 0.85, "long_doc": 0.98},
    "gemini-2.0-flash": {"code": 0.75, "reasoning": 0.72, "creative": 0.74, "factual": 0.78, "chat": 0.82, "long_doc": 0.80},
    "groq/llama-3.3-70b-versatile": {"code": 0.82, "reasoning": 0.80, "creative": 0.79, "factual": 0.80, "chat": 0.83, "long_doc": 0.70},
    "groq/llama-3.1-8b-instant": {"code": 0.65, "reasoning": 0.62, "creative": 0.64, "factual": 0.66, "chat": 0.75, "long_doc": 0.55},
    "ollama/llama3.1": {"code": 0.70, "reasoning": 0.68, "creative": 0.68, "factual": 0.70, "chat": 0.78, "long_doc": 0.50},
}


def quality_score(model: str, task_type: str) -> float:
    return QUALITY_MATRIX.get(model, {}).get(task_type, 0.50)


def choose_quality(candidates: list[str], task_type: str) -> tuple[str, str]:
    selected = max(candidates, key=lambda model: quality_score(model, task_type))
    return selected, f"Highest quality score for {task_type}"

