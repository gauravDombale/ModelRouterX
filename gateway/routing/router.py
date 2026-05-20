from dataclasses import dataclass

from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gateway.models.routing_rule import RoutingRule
from gateway.models.virtual_key import VirtualKey
from gateway.providers.models import MODEL_REGISTRY
from gateway.providers.registry import provider_registry
from gateway.routing.classifier import TaskClassifier
from gateway.routing.fallback import fallback_chain
from gateway.routing.strategies.balanced import choose_balanced
from gateway.routing.strategies.cost_optimized import choose_cost_optimized
from gateway.routing.strategies.latency_optimized import choose_latency_optimized
from gateway.routing.strategies.quality_optimized import choose_quality
from gateway.routing.strategies.rule_based import choose_rule_based
from gateway.schemas import ChatCompletionRequest
from gateway.utils.pricing import canonical_model


@dataclass(slots=True)
class RoutingDecision:
    requested_model: str
    model: str
    provider: str
    strategy: str
    task_type: str
    reason: str
    fallback_chain: list[str]


class ModelRouter:
    def __init__(self, redis: Redis | None = None) -> None:
        self.classifier = TaskClassifier(redis)

    async def route(self, request: ChatCompletionRequest, key: VirtualKey, session: AsyncSession) -> RoutingDecision:
        task_type, _ = await self.classifier.classify(request.messages)
        strategy = request.mrx.strategy or key.routing_strategy or "balanced"

        candidates = provider_registry.available_model_ids()
        if key.allowed_models:
            candidates = [canonical_model(m) for m in key.allowed_models if canonical_model(m) in MODEL_REGISTRY]
            candidates = [m for m in candidates if m in provider_registry.available_model_ids()]
        if not candidates:
            raise ValueError("No configured providers available. Set at least one provider API key or run Ollama locally.")
        if request.model != "auto":
            selected = canonical_model(request.model)
            if selected not in provider_registry.available_model_ids():
                info = provider_registry.model_info(selected)
                raise ValueError(f"Provider '{info.provider}' is not configured for requested model '{selected}'.")
            reason = "Client requested an explicit model"
        else:
            rules = (
                await session.execute(
                    select(RoutingRule).where((RoutingRule.virtual_key_id == key.id) | (RoutingRule.virtual_key_id.is_(None)))
                )
            ).scalars().all()
            rule_result = choose_rule_based(list(rules), request, task_type)
            if rule_result and canonical_model(rule_result[0]) in candidates:
                selected, reason = rule_result
                selected = canonical_model(selected)
                strategy = "rule_based"
            elif strategy == "cost_optimized":
                selected, reason = choose_cost_optimized(candidates, task_type)
            elif strategy == "latency_optimized":
                selected, reason = choose_latency_optimized(candidates, task_type)
            elif strategy == "quality_optimized":
                selected, reason = choose_quality(candidates, task_type)
            else:
                selected, reason = choose_balanced(candidates, task_type)

        info = provider_registry.model_info(selected)
        return RoutingDecision(
            requested_model=request.model,
            model=info.id,
            provider=info.provider,
            strategy=strategy,
            task_type=task_type,
            reason=reason,
            fallback_chain=fallback_chain(info.id, request.mrx.fallback_models),
        )
