from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PayoutStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"


class PayoutCreate(BaseModel):
    amount: Decimal = Field(gt=Decimal("0"))
    period_start: date
    period_end: date
    payment_details: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_period(self) -> "PayoutCreate":
        if self.period_start > self.period_end:
            raise ValueError("period_start must be less than or equal to period_end")
        return self


class PayoutResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    venue_id: int
    amount: Decimal
    period_start: date
    period_end: date
    status: PayoutStatus
    payment_details: dict[str, Any]
    created_at: datetime
    paid_at: datetime | None
