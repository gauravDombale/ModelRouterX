import time
from sqlalchemy.ext.asyncio import AsyncSession

from gateway.middleware.circuit_breaker import circuit_breaker
from gateway.models.provider_health import ProviderHealth
from gateway.providers.models import MODEL_REGISTRY
from gateway.providers.registry import provider_registry


async def write_health_snapshot(session: AsyncSession) -> None:
    for info in MODEL_REGISTRY.values():
        provider = provider_registry.providers.get(info.provider)
        is_healthy = False
        latency_ms = None
        
        # Only ping if the provider adapter is available, has keys configured, and circuit breaker allows
        if provider and provider_registry.provider_available(info.provider) and circuit_breaker.allow(info.provider):
            try:
                start = time.perf_counter()
                is_healthy = await provider.health()
                if is_healthy:
                    latency_ms = int((time.perf_counter() - start) * 1000)
            except Exception:
                is_healthy = False

        session.add(
            ProviderHealth(
                provider=info.provider,
                model=info.id,
                is_healthy=is_healthy,
                p50_latency_ms=latency_ms if is_healthy else 0,
                p95_latency_ms=int(latency_ms * 1.5) if is_healthy else 0,
                error_rate_pct=0.0 if is_healthy else 100.0,
                circuit_state=circuit_breaker.state(info.provider),
            )
        )
    await session.commit()
