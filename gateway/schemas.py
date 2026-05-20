from typing import Any, Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str | list[dict[str, Any]]


class MRXOptions(BaseModel):
    strategy: str | None = None
    cache: bool = True
    cache_ttl: int | None = None
    fallback_models: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class ChatCompletionRequest(BaseModel):
    model: str = "auto"
    messages: list[ChatMessage]
    stream: bool = False
    max_tokens: int | None = None
    temperature: float | None = None
    mrx: MRXOptions = Field(default_factory=MRXOptions)


class KeyCreate(BaseModel):
    name: str
    owner_id: str = "default"
    budget_limit_usd: float | None = None
    rpm_limit: int | None = 60
    tpm_limit: int | None = 60_000
    routing_strategy: str = "balanced"
    allowed_models: list[str] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class RoutingRuleCreate(BaseModel):
    name: str
    priority: int = 0
    conditions: dict[str, Any]
    target_model: str
    is_active: bool = True

