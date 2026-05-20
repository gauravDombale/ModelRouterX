import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gateway.models.base import Base


class RequestLog(Base):
    __tablename__ = "request_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    virtual_key_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("virtual_keys.id"))
    request_id: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    requested_model: Mapped[str] = mapped_column(Text, nullable=False)
    routed_model: Mapped[str] = mapped_column(Text, nullable=False)
    routed_provider: Mapped[str] = mapped_column(Text, nullable=False)
    routing_strategy: Mapped[str] = mapped_column(Text, nullable=False)
    task_type: Mapped[str | None] = mapped_column(Text)
    routing_reason: Mapped[str | None] = mapped_column(Text)
    cache_status: Mapped[str] = mapped_column(Text, default="miss")
    cache_similarity: Mapped[Decimal | None] = mapped_column(Numeric(4, 3))
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    prompt_cost_usd: Mapped[Decimal] = mapped_column(Numeric(10, 6), default=0)
    completion_cost_usd: Mapped[Decimal] = mapped_column(Numeric(10, 6), default=0)
    total_cost_usd: Mapped[Decimal] = mapped_column(Numeric(10, 6), default=0)
    ttfb_ms: Mapped[int | None] = mapped_column(Integer)
    total_latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    provider_latency_ms: Mapped[int | None] = mapped_column(Integer)
    status_code: Mapped[int] = mapped_column(Integer, default=200)
    error_type: Mapped[str | None] = mapped_column(Text)
    fallback_used: Mapped[bool] = mapped_column(Boolean, default=False)
    fallback_chain: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    request_body: Mapped[dict | None] = mapped_column(JSONB)
    response_body: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    virtual_key = relationship("VirtualKey", back_populates="request_logs")

