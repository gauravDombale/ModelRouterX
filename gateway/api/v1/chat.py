import time
import uuid
from decimal import Decimal

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Response
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from gateway.cache.cache_manager import CacheManager
from gateway.dependencies import check_rate_limit, get_cache_manager, get_current_key, get_redis
from gateway.db.session import AsyncSessionLocal, get_session
from gateway.middleware.circuit_breaker import circuit_breaker
from gateway.models.request_log import RequestLog
from gateway.models.virtual_key import VirtualKey
from gateway.observability.langfuse import emit_chat_trace
from gateway.providers.base import ProviderError
from gateway.providers.registry import provider_registry
from gateway.routing.router import ModelRouter, RoutingDecision
from gateway.schemas import ChatCompletionRequest
from gateway.utils.pricing import calculate_cost
from gateway.utils.token_counter import count_message_tokens, count_text_tokens

router = APIRouter(prefix="/v1", tags=["chat"])


async def _log_request(record: dict) -> None:
    async with AsyncSessionLocal() as log_session:
        log_session.add(RequestLog(**record))
        await log_session.commit()


def _openai_response(request_id: str, model: str, content: str, prompt_tokens: int, completion_tokens: int) -> dict:
    return {
        "id": request_id,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [{"index": 0, "message": {"role": "assistant", "content": content}, "finish_reason": "stop"}],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        },
    }


def _headers(decision: RoutingDecision, request_id: str, cache_status: str, cost: Decimal, latency_ms: int) -> dict[str, str]:
    return {
        "X-MRX-Request-ID": request_id,
        "X-MRX-Routed-Model": decision.model,
        "X-MRX-Routing-Strategy": decision.strategy,
        "X-MRX-Task-Type": decision.task_type,
        "X-MRX-Cache-Status": cache_status,
        "X-MRX-Cost-USD": str(cost.quantize(Decimal("0.000001"))),
        "X-MRX-Latency-Ms": str(latency_ms),
    }


@router.post("/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest,
    background_tasks: BackgroundTasks,
    cache_control: str | None = Header(default=None, alias="Cache-Control"),
    key: VirtualKey = Depends(get_current_key),
    session: AsyncSession = Depends(get_session),
    redis=Depends(get_redis),
    cache: CacheManager = Depends(get_cache_manager),
):
    started = time.perf_counter()
    request_id = f"req_{uuid.uuid4().hex}"
    await check_rate_limit(key, redis, count_message_tokens(request.messages))

    try:
        decision = await ModelRouter(redis).route(request, key, session)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    if not cache.should_bypass(request, cache_control):
        cached, cache_status, similarity = await cache.read(session, key.owner_id, decision.model, request)
        if cached:
            latency_ms = int((time.perf_counter() - started) * 1000)
            headers = _headers(decision, request_id, cache_status, Decimal("0"), latency_ms)
            background_tasks.add_task(
                _log_request,
                {
                    "virtual_key_id": key.id,
                    "request_id": request_id,
                    "requested_model": request.model,
                    "routed_model": decision.model,
                    "routed_provider": decision.provider,
                    "routing_strategy": decision.strategy,
                    "task_type": decision.task_type,
                    "routing_reason": decision.reason,
                    "cache_status": cache_status,
                    "cache_similarity": similarity,
                    "total_latency_ms": latency_ms,
                    "status_code": 200,
                    "request_body": request.model_dump(),
                    "response_body": cached,
                },
            )
            background_tasks.add_task(
                emit_chat_trace,
                request_id=request_id,
                request=request,
                response_body=cached,
                model=decision.model,
                provider=decision.provider,
                strategy=decision.strategy,
                task_type=decision.task_type,
                cache_status=cache_status,
                latency_ms=latency_ms,
            )
            return JSONResponse(cached, headers=headers)
    else:
        cache_status = "skip"
        similarity = None

    provider_response = None
    errors: list[str] = []
    for model in decision.fallback_chain:
        provider = provider_registry.provider_for_model(model)
        if not circuit_breaker.allow(provider.name):
            continue
        try:
            if request.stream:
                headers = _headers(decision, request_id, "skip", Decimal("0"), int((time.perf_counter() - started) * 1000))
                return StreamingResponse(provider.stream(request, model, request_id), media_type="text/event-stream", headers=headers)
            provider_response = await provider.complete(request, model)
            circuit_breaker.record(provider.name, True)
            if model != decision.model:
                decision.model = model
                decision.provider = provider.name
            break
        except ProviderError as exc:
            circuit_breaker.record(provider.name, False)
            errors.append(f"{provider.name}: {exc}")
            if not exc.retryable:
                continue

    if not provider_response:
        raise HTTPException(502, {"message": "All providers failed", "errors": errors})

    completion_tokens = provider_response.completion_tokens or count_text_tokens(provider_response.content)
    prompt_tokens = provider_response.prompt_tokens or count_message_tokens(request.messages)
    prompt_cost, completion_cost, total_cost = calculate_cost(provider_response.model, prompt_tokens, completion_tokens)
    body = _openai_response(request_id, provider_response.model, provider_response.content, prompt_tokens, completion_tokens)
    latency_ms = int((time.perf_counter() - started) * 1000)

    if not cache.should_bypass(request, cache_control):
        await cache.write(session, key.owner_id, provider_response.model, request, body)

    background_tasks.add_task(
        _log_request,
        {
            "virtual_key_id": key.id,
            "request_id": request_id,
            "requested_model": request.model,
            "routed_model": provider_response.model,
            "routed_provider": provider_response.provider,
            "routing_strategy": decision.strategy,
            "task_type": decision.task_type,
            "routing_reason": decision.reason,
            "cache_status": cache_status,
            "cache_similarity": similarity,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "prompt_cost_usd": prompt_cost,
            "completion_cost_usd": completion_cost,
            "total_cost_usd": total_cost,
            "total_latency_ms": latency_ms,
            "provider_latency_ms": latency_ms,
            "status_code": 200,
            "fallback_used": provider_response.model != decision.fallback_chain[0],
            "fallback_chain": decision.fallback_chain,
            "request_body": request.model_dump(),
            "response_body": body,
        },
    )
    background_tasks.add_task(
        emit_chat_trace,
        request_id=request_id,
        request=request,
        response_body=body,
        model=provider_response.model,
        provider=provider_response.provider,
        strategy=decision.strategy,
        task_type=decision.task_type,
        cache_status=cache_status,
        latency_ms=latency_ms,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_cost_usd=total_cost,
    )
    return JSONResponse(body, headers=_headers(decision, request_id, cache_status, total_cost, latency_ms))
