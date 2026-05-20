from gateway.routing.strategies.balanced import choose_balanced
from gateway.routing.strategies.cost_optimized import choose_cost_optimized


def test_balanced_returns_candidate():
    candidates = ["gpt-4o-mini-2024-07-18", "claude-sonnet-4-20250514"]
    selected, reason = choose_balanced(candidates, "code")
    assert selected in candidates
    assert reason


def test_cost_strategy_prefers_efficient_candidate():
    candidates = ["gpt-4o-mini-2024-07-18", "claude-opus-4-20250514"]
    selected, _ = choose_cost_optimized(candidates, "chat", min_quality=0.70)
    assert selected == "gpt-4o-mini-2024-07-18"

