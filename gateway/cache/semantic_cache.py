from datetime import datetime, timedelta, timezone
import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from gateway.cache.exact_cache import normalize_prompt, prompt_hash
from gateway.cache.embedder import Embedder
from gateway.schemas import ChatMessage


class SemanticCache:
    def __init__(self, embedder: Embedder | None = None, threshold: float = 0.92) -> None:
        self.embedder = embedder or Embedder()
        self.threshold = threshold

    async def get(self, session: AsyncSession, tenant_id: str, model: str, messages: list[ChatMessage]) -> tuple[dict[str, Any] | None, float | None]:
        embedding = await self.embedder.embed(normalize_prompt(messages))
        result = await session.execute(
            text(
                """
                SELECT id, response_body, 1 - (prompt_embedding <=> :embedding) AS similarity
                FROM semantic_cache
                WHERE tenant_id = :tenant_id
                  AND model = :model
                  AND (expires_at IS NULL OR expires_at > now())
                ORDER BY prompt_embedding <=> :embedding
                LIMIT 1
                """
            ),
            {"tenant_id": tenant_id, "model": model, "embedding": str(embedding)},
        )
        row = result.mappings().first()
        if not row or float(row["similarity"]) < self.threshold:
            return None, None
        await session.execute(text("UPDATE semantic_cache SET hit_count = hit_count + 1, last_hit_at = now() WHERE id = :id"), {"id": row["id"]})
        await session.commit()
        return dict(row["response_body"]), float(row["similarity"])

    async def set(self, session: AsyncSession, tenant_id: str, model: str, messages: list[ChatMessage], response: dict, ttl: int) -> None:
        embedding = await self.embedder.embed(normalize_prompt(messages))
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl)
        await session.execute(
            text(
                """
                INSERT INTO semantic_cache
                    (tenant_id, prompt_hash, prompt_embedding, model, response_body, prompt_tokens, completion_tokens, expires_at)
                VALUES
                    (:tenant_id, :prompt_hash, :embedding, :model, :response_body, :prompt_tokens, :completion_tokens, :expires_at)
                """
            ),
            {
                "tenant_id": tenant_id,
                "prompt_hash": prompt_hash(messages),
                "embedding": str(embedding),
                "model": model,
                "response_body": json.dumps(response),
                "prompt_tokens": response.get("usage", {}).get("prompt_tokens"),
                "completion_tokens": response.get("usage", {}).get("completion_tokens"),
                "expires_at": expires_at,
            },
        )
        await session.commit()
