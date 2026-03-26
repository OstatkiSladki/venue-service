from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, SoftDeleteMixin, TimestampMixin


class Company(TimestampMixin, SoftDeleteMixin, Base):
  __tablename__ = "companies"

  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
  name: Mapped[str] = mapped_column(String(255), nullable=False)
  inn: Mapped[str | None] = mapped_column(String(20), nullable=True)
  is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")

  venues = relationship("Venue", back_populates="company")
