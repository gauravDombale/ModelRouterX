from fastapi import APIRouter, Depends
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from gateway.db.session import get_session
from gateway.models.provider_health import ProviderHealth
from gateway.middleware.circuit_breaker import circuit_breaker
from gateway.providers.models import MODEL_REGISTRY

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/health/providers")
@router.get("/api/v1/providers/health")
async def provider_health(session: AsyncSession = Depends(get_session)):
    providers_list = []
    for info in MODEL_REGISTRY.values():
        stmt = (
            select(ProviderHealth)
            .where(ProviderHealth.model == info.id)
            .order_by(desc(ProviderHealth.sampled_at))
            .limit(1)
        )
        res = (await session.execute(stmt)).scalar_one_or_none()
        if res:
            providers_list.append({
                "provider": res.provider,
                "model": res.model,
                "is_healthy": res.is_healthy,
                "circuit_state": res.circuit_state,
                "p50_latency_ms": res.p50_latency_ms or 0,
                "p95_latency_ms": res.p95_latency_ms or 0,
            })
        else:
            providers_list.append({
                "provider": info.provider,
                "model": info.id,
                "is_healthy": circuit_breaker.allow(info.provider),
                "circuit_state": circuit_breaker.state(info.provider),
                "p50_latency_ms": 0,
                "p95_latency_ms": 0,
            })
    return {"providers": providers_list}
