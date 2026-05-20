import hashlib
import re

from redis.asyncio import Redis

from gateway.schemas import ChatMessage

TASK_TYPES = {"code", "reasoning", "creative", "factual", "chat", "long_doc"}

TASK_MODEL_HINTS = {
    "code": ["claude-sonnet-4-20250514", "gpt-4o-2024-11-20", "groq/llama-3.3-70b"],
    "reasoning": ["claude-opus-4-20250514", "gpt-4o-2024-11-20", "o3-mini-2025-01-31"],
    "creative": ["claude-sonnet-4-20250514", "gpt-4o-2024-11-20", "gemini-2.5-pro"],
    "factual": ["claude-haiku-4-5-20251001", "gpt-4o-mini-2024-07-18", "gemini-2.0-flash"],
    "chat": ["claude-haiku-4-5-20251001", "gpt-4o-mini-2024-07-18", "groq/llama-3.1-8b"],
    "long_doc": ["claude-sonnet-4-20250514", "gemini-2.5-pro"],
}


def first_user_text(messages: list[ChatMessage]) -> str:
    for message in messages:
        if message.role == "user":
            return message.content if isinstance(message.content, str) else str(message.content)
    return ""


class TaskClassifier:
    def __init__(self, redis: Redis | None = None) -> None:
        self.redis = redis

    async def classify(self, messages: list[ChatMessage]) -> tuple[str, float]:
        prompt = first_user_text(messages)
        cache_key = "classifier:" + hashlib.sha256(prompt[:4000].encode()).hexdigest()
        if self.redis:
            cached = await self.redis.get(cache_key)
            if cached:
                return cached.decode(), 0.95

        task_type = self._heuristic(prompt)
        if self.redis:
            await self.redis.set(cache_key, task_type, ex=3600)
        return task_type, 0.70

    def _heuristic(self, prompt: str) -> str:
        text = prompt.lower()
        if len(text.split()) > 50_000:
            return "long_doc"
        if re.search(r"\b(code|function|class|debug|stack trace|typescript|python|sql|api)\b", text):
            return "code"
        if re.search(r"\b(prove|derive|calculate|logic|step by step|optimize|plan)\b", text):
            return "reasoning"
        if re.search(r"\b(story|poem|copy|brainstorm|slogan|creative|rewrite)\b", text):
            return "creative"
        if re.search(r"\b(what is|define|summarize|who is|when did|where is)\b", text):
            return "factual"
        return "chat"

