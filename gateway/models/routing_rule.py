import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from gateway.models.base import Base


class RoutingRule(Base):
    __tablename__ = "routing_rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    virtual_key_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("virtual_keys.id"))
    name: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    conditions: Mapped[dict] = mapped_column(JSONB, nullable=False)
    target_model: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

