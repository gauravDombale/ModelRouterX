import hashlib
import json
import re

from redis.asyncio import Redis

from gateway.schemas import ChatMessage


def normalize_prompt(messages: list[ChatMessage]) -> str:
    content = " ".join(
        str(m.content).strip().lower()
        for m in messages
        if m.role == "user"
    )
    return re.sub(r"\s+", " ", content)


def prompt_hash(messages: list[ChatMessage]) -> str:
    return hashlib.sha256(normalize_prompt(messages).encode("utf-8")).hexdigest()


class ExactCache:
    def __init__(self, redis: Redis | None) -> None:
        self.redis = redis

    def key(self, tenant_id: str, model: str, messages: list[ChatMessage]) -> str:
        return f"cache:{tenant_id}:{model}:{prompt_hash(messages)}"

    async def get(self, tenant_id: str, model: str, messages: list[ChatMessage]) -> dict | None:
        if not self.redis:
            return None
        raw = await self.redis.get(self.key(tenant_id, model, messages))
        return json.loads(raw) if raw else None

    async def set(self, tenant_id: str, model: str, messages: list[ChatMessage], response: dict, ttl: int) -> None:
        if self.redis:
            await self.redis.set(self.key(tenant_id, model, messages), json.dumps(response), ex=ttl)

