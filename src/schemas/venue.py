from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.common import PaginationQuery


class VenueCreate(BaseModel):
    company_id: int
    name: str = Field(min_length=1, max_length=255)
    address: str = Field(min_length=1)
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    phone: str | None = Field(default=None, max_length=20)
    work_schedule: dict[str, Any] = Field(default_factory=dict)
    commission_rate: Decimal | None = None


class VenueUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    address: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    phone: str | None = Field(default=None, max_length=20)
    work_schedule: dict[str, Any] | None = None
    is_open: bool | None = None
    commission_rate: Decimal | None = None


class VenueListQuery(PaginationQuery):
    lat: Decimal | None = None
    lon: Decimal | None = None
    radius: Decimal | None = Field(default=Decimal("5"))
    name: str | None = None
    is_open: bool | None = None
    company_id: int | None = None
    include_deleted: bool = False


class VenueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int | None
    name: str
    address: str
    latitude: Decimal | None
    longitude: Decimal | None
    phone: str | None
    commission_rate: Decimal
    payout_balance: Decimal
    work_schedule: dict[str, Any]
    is_open: bool
    rating: Decimal
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
