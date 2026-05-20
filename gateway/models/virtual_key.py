import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gateway.models.base import Base


class VirtualKey(Base):
    __tablename__ = "virtual_keys"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key_hash: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    key_prefix: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    owner_id: Mapped[str] = mapped_column(Text, nullable=False, default="default")
    budget_limit_usd: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    budget_used_usd: Mapped[Decimal] = mapped_column(Numeric(10, 4), default=0)
    rpm_limit: Mapped[int | None] = mapped_column(Integer)
    tpm_limit: Mapped[int | None] = mapped_column(Integer)
    routing_strategy: Mapped[str] = mapped_column(String(64), default="balanced")
    allowed_models: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    key_metadata: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    request_logs = relationship("RequestLog", back_populates="virtual_key")

