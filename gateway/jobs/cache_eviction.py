from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def evict_expired_cache(session: AsyncSession) -> int:
    result = await session.execute(text("DELETE FROM semantic_cache WHERE expires_at IS NOT NULL AND expires_at < now()"))
    await session.commit()
    return result.rowcount or 0

