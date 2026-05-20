from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, Numeric, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from gateway.models.base import Base


class ProviderHealth(Base):
    __tablename__ = "provider_health"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    provider: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[str] = mapped_column(Text, nullable=False)
    is_healthy: Mapped[bool] = mapped_column(Boolean, nullable=False)
    p50_latency_ms: Mapped[int | None] = mapped_column(Integer)
    p95_latency_ms: Mapped[int | None] = mapped_column(Integer)
    error_rate_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    circuit_state: Mapped[str] = mapped_column(Text, default="closed")
    sampled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

