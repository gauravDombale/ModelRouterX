from gateway.middleware.circuit_breaker import CircuitBreaker


def test_circuit_opens_after_failures():
    breaker = CircuitBreaker(threshold_pct=20, window_seconds=60, open_seconds=30)
    for _ in range(6):
        breaker.record("openai", False)
    assert breaker.state("openai") == "open"
    assert not breaker.allow("openai")

