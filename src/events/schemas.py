from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class EventMetadata(BaseModel):
  service_origin: str = "venue-service"
  trace_id: str | None = None
  correlation_id: str
  user_id: str


class DomainEvent(BaseModel):
  event_id: str = Field(default_factory=lambda: str(uuid4()))
  event_type: str
  timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
  aggregate_id: str
  aggregate_type: str
  payload: dict[str, Any]
  metadata: EventMetadata
