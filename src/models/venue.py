from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import Boolean, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.models.base import Base, SoftDeleteMixin, TimestampMixin


class Venue(TimestampMixin, SoftDeleteMixin, Base):
  __tablename__ = "venues"

  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
  company_id: Mapped[int | None] = mapped_column(
    ForeignKey("companies.id", ondelete="SET NULL"), nullable=True
  )
  name: Mapped[str] = mapped_column(String(255), nullable=False)
  address: Mapped[str] = mapped_column(Text, nullable=False)
  latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
  longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
  phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
  commission_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), server_default="10.00")
  payout_balance: Mapped[Decimal] = mapped_column(Numeric(10, 2), server_default="0.00")
  work_schedule: Mapped[dict[str, Any]] = mapped_column(JSONB, server_default="{}")
  is_open: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
  rating: Mapped[Decimal] = mapped_column(Numeric(3, 2), server_default="0.00")
  updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

  company = relationship("Company", back_populates="venues")
  payouts = relationship("Payout", back_populates="venue")
