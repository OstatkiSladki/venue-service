from datetime import datetime, timezone
from enum import StrEnum
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field


class UserRole(StrEnum):
  USER = "user"
  STAFF = "staff"
  ADMIN = "admin"


class IdentityContext(BaseModel):
  model_config = ConfigDict(frozen=True)

  user_id: str
  role: UserRole
  request_id: str
  venue_id: int | None = None


class ErrorResponse(BaseModel):
  code: str
  message: str
  details: list[dict[str, str]] = Field(default_factory=list)
  timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
  request_id: str | None = None
  trace_id: str | None = None


class PaginationMeta(BaseModel):
  limit: int
  offset: int
  total: int


class PaginationQuery(BaseModel):
  limit: int = Field(default=20, ge=1, le=100)
  offset: int = Field(default=0, ge=0)


DataT = TypeVar("DataT")


class PaginatedResponse(BaseModel, Generic[DataT]):
  items: list[DataT]
  meta: PaginationMeta
