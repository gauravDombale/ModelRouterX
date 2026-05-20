import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from gateway.models.base import Base


class CostRollup(Base):
    __tablename__ = "cost_rollups"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    virtual_key_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("virtual_keys.id"))
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_type: Mapped[str] = mapped_column(Text, default="hour")
    provider: Mapped[str | None] = mapped_column(Text)
    model: Mapped[str | None] = mapped_column(Text)
    request_count: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(BigInteger, default=0)
    total_cost_usd: Mapped[Decimal] = mapped_column(Numeric(10, 4), default=0)
    cache_hits: Mapped[int] = mapped_column(Integer, default=0)

