import time

from fastapi import Depends, Header, HTTPException, Request, status
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gateway.cache.cache_manager import CacheManager
from gateway.cache.exact_cache import ExactCache
from gateway.cache.semantic_cache import SemanticCache
from gateway.config import get_settings
from gateway.db.session import get_session
from gateway.models.virtual_key import VirtualKey
from gateway.utils.security import hash_api_key


async def get_redis(request: Request) -> Redis | None:
    return getattr(request.app.state, "redis", None)


async def get_cache_manager(redis: Redis | None = Depends(get_redis)) -> CacheManager:
    settings = get_settings()
    return CacheManager(ExactCache(redis), SemanticCache(threshold=settings.semantic_cache_threshold), settings.cache_ttl_seconds)


async def get_current_key(
    authorization: str | None = Header(default=None),
    session: AsyncSession = Depends(get_session),
) -> VirtualKey:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing bearer token")
    token = authorization.removeprefix("Bearer ").strip()
    key_hash = hash_api_key(token)
    key = (await session.execute(select(VirtualKey).where(VirtualKey.key_hash == key_hash))).scalar_one_or_none()
    if not key or not key.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid API key")
    return key


async def check_rate_limit(key: VirtualKey, redis: Redis | None, estimated_tokens: int) -> None:
    if not redis:
        return
    minute = int(time.time() // 60)
    rpm_key = f"rpm:{key.id}:{minute}"
    tpm_key = f"tpm:{key.id}:{minute}"
    pipe = redis.pipeline()
    pipe.incr(rpm_key)
    pipe.expire(rpm_key, 60)
    pipe.incrby(tpm_key, estimated_tokens)
    pipe.expire(tpm_key, 60)
    rpm, _, tpm, _ = await pipe.execute()
    if key.rpm_limit and rpm > key.rpm_limit:
        raise HTTPException(429, "RPM limit exceeded")
    if key.tpm_limit and tpm > key.tpm_limit:
        raise HTTPException(429, "TPM limit exceeded")
