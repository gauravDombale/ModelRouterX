from decimal import Decimal

from gateway.routing.strategies.quality_optimized import quality_score
from gateway.utils.pricing import MODEL_PRICING


def choose_cost_optimized(candidates: list[str], task_type: str, min_quality: float = 0.72) -> tuple[str, str]:
    eligible = [m for m in candidates if quality_score(m, task_type) >= min_quality] or candidates

    def score(model: str) -> Decimal:
        input_cost, output_cost = MODEL_PRICING.get(model, (Decimal("0.01"), Decimal("0.01")))
        blended = max(input_cost + output_cost, Decimal("0.01"))
        return Decimal(str(quality_score(model, task_type))) / blended

    selected = max(eligible, key=score)
    return selected, f"Best quality-per-dollar above {min_quality:.2f} quality bar"

