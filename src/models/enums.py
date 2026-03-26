from enum import StrEnum


class PayoutStatus(StrEnum):
  PENDING = "pending"
  PAID = "paid"
  CANCELLED = "cancelled"
