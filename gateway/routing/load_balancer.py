from collections import defaultdict


class RoundRobinLoadBalancer:
    def __init__(self) -> None:
        self._positions: dict[str, int] = defaultdict(int)

    def choose(self, key: str, models: list[str]) -> str:
        if not models:
            raise ValueError("No models to load balance")
        index = self._positions[key] % len(models)
        self._positions[key] += 1
        return models[index]

