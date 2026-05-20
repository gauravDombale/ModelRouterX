import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from gateway.config import get_settings
from gateway.schemas import ChatCompletionRequest

logger = logging.getLogger(__name__)


def _decimal_to_float(value: Decimal) -> float:
    return float(value.quantize(Decimal("0.000001")))


async def emit_chat_trace(
    *,
    request_id: str,
    request: ChatCompletionRequest,
    response_body: dict[str, Any],
    model: str,
    provider: str,
    strategy: str,
    task_type: str | None,
    cache_status: str,
    latency_ms: int,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    total_cost_usd: Decimal = Decimal("0"),
) -> None:
    settings = get_settings()
    if not settings.langfuse_public_key or not settings.langfuse_secret_key:
        return

    try:
        from langfuse import Langfuse

        client = Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            host=settings.langfuse_host,
            flush_at=1,
            timeout=5,
            environment=settings.environment,
        )
        client.trace(
            id=request_id,
            name="chat.completion",
            user_id="modelrouterx",
            input=request.model_dump(),
            output=response_body,
            tags=request.mrx.tags,
            metadata={
                "provider": provider,
                "routing_strategy": strategy,
                "task_type": task_type,
                "cache_status": cache_status,
                "latency_ms": latency_ms,
            },
        )
        client.generation(
            trace_id=request_id,
            name="provider_call",
            start_time=datetime.now(timezone.utc),
            end_time=datetime.now(timezone.utc),
            model=model,
            input=request.model_dump(),
            output=response_body,
            usage_details={
                "input": prompt_tokens,
                "output": completion_tokens,
                "total": prompt_tokens + completion_tokens,
            },
            cost_details={"total": _decimal_to_float(total_cost_usd)},
            metadata={"provider": provider},
        )
        client.flush()
        client.shutdown()
    except Exception as exc:
        logger.warning("Langfuse trace emission failed: %s", exc)
