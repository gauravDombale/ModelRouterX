from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any

from gateway.schemas import ChatCompletionRequest


@dataclass(slots=True)
class ProviderResponse:
    model: str
    provider: str
    content: str
    raw: dict[str, Any]
    prompt_tokens: int
    completion_tokens: int


class ProviderError(RuntimeError):
    def __init__(self, provider: str, message: str, retryable: bool = True) -> None:
        super().__init__(message)
        self.provider = provider
        self.retryable = retryable


class BaseProvider(ABC):
    name: str
    supported_models: set[str]

    @abstractmethod
    async def complete(self, request: ChatCompletionRequest, model: str) -> ProviderResponse:
        raise NotImplementedError

    @abstractmethod
    async def stream(self, request: ChatCompletionRequest, model: str, request_id: str) -> AsyncIterator[str]:
        raise NotImplementedError

    async def health(self) -> bool:
        return True

