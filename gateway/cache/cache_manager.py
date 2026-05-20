from sqlalchemy.ext.asyncio import AsyncSession

from gateway.cache.exact_cache import ExactCache
from gateway.cache.semantic_cache import SemanticCache
from gateway.schemas import ChatCompletionRequest


class CacheManager:
    def __init__(self, exact: ExactCache, semantic: SemanticCache, default_ttl: int = 3600) -> None:
        self.exact = exact
        self.semantic = semantic
        self.default_ttl = default_ttl

    def should_bypass(self, request: ChatCompletionRequest, cache_control: str | None = None) -> bool:
        user_turns = sum(1 for m in request.messages if m.role == "user")
        return (
            request.mrx.cache is False
            or cache_control == "no-store"
            or user_turns > 3
            or (request.temperature is not None and request.temperature > 0.7)
        )

    async def read(self, session: AsyncSession, tenant_id: str, model: str, request: ChatCompletionRequest) -> tuple[dict | None, str, float | None]:
        exact = await self.exact.get(tenant_id, model, request.messages)
        if exact:
            return exact, "hit_exact", None
        semantic, similarity = await self.semantic.get(session, tenant_id, model, request.messages)
        if semantic:
            await self.exact.set(tenant_id, model, request.messages, semantic, request.mrx.cache_ttl or self.default_ttl)
            return semantic, "hit_semantic", similarity
        return None, "miss", None

    async def write(self, session: AsyncSession, tenant_id: str, model: str, request: ChatCompletionRequest, response: dict) -> None:
        ttl = request.mrx.cache_ttl or self.default_ttl
        await self.exact.set(tenant_id, model, request.messages, response, ttl)
        if not request.stream:
            await self.semantic.set(session, tenant_id, model, request.messages, response, ttl)

