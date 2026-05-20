from decimal import Decimal

from gateway.routing.strategies.latency_optimized import latency_ms
from gateway.routing.strategies.quality_optimized import quality_score
from gateway.utils.pricing import MODEL_PRICING


def _norm(value: float, low: float, high: float) -> float:
    if high == low:
        return 1.0
    return (value - low) / (high - low)


def choose_balanced(candidates: list[str], task_type: str) -> tuple[str, str]:
    qualities = {m: quality_score(m, task_type) for m in candidates}
    costs = {m: float(sum(MODEL_PRICING.get(m, (Decimal("0"), Decimal("0"))))) for m in candidates}
    latencies = {m: float(latency_ms(m)) for m in candidates}

    q_low, q_high = min(qualities.values()), max(qualities.values())
    c_low, c_high = min(costs.values()), max(costs.values())
    l_low, l_high = min(latencies.values()), max(latencies.values())

    def score(model: str) -> float:
        return (
            0.35 * _norm(qualities[model], q_low, q_high)
            + 0.35 * (1 - _norm(costs[model], c_low, c_high))
            + 0.30 * (1 - _norm(latencies[model], l_low, l_high))
        )

    selected = max(candidates, key=score)
    return selected, "Weighted balanced score across quality, cost, and latency"

