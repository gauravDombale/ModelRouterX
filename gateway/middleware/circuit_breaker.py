import time
from collections import defaultdict, deque


class CircuitBreaker:
    def __init__(self, threshold_pct: float = 20.0, window_seconds: int = 60, open_seconds: int = 30) -> None:
        self.threshold_pct = threshold_pct
        self.window_seconds = window_seconds
        self.open_seconds = open_seconds
        self.events: dict[str, deque[tuple[float, bool]]] = defaultdict(deque)
        self.open_until: dict[str, float] = {}

    def state(self, provider: str) -> str:
        until = self.open_until.get(provider, 0)
        if until > time.time():
            return "open"
        if until:
            return "half_open"
        return "closed"

    def allow(self, provider: str) -> bool:
        return self.state(provider) != "open"

    def record(self, provider: str, success: bool) -> None:
        now = time.time()
        q = self.events[provider]
        q.append((now, success))
        while q and now - q[0][0] > self.window_seconds:
            q.popleft()
        if len(q) < 5:
            return
        failures = sum(1 for _, ok in q if not ok)
        if failures / len(q) * 100 > self.threshold_pct:
            self.open_until[provider] = now + self.open_seconds
        elif success and self.state(provider) == "half_open":
            self.open_until.pop(provider, None)


circuit_breaker = CircuitBreaker()

