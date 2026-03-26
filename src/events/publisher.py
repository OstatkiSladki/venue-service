import asyncio
import json
from collections.abc import Awaitable, Callable
from datetime import timezone
from typing import Protocol
from typing import Any

from src.core_exceptions import ServiceUnavailableError
from src.events.schemas import DomainEvent
from src.events.topics import (
  PAYOUT_DLX_EXCHANGE,
  PAYOUT_DLQ,
  PAYOUT_EXCHANGE,
  VENUE_DLX_EXCHANGE,
  VENUE_DLQ,
  VENUE_EXCHANGE,
)


class EventPublisher(Protocol):
  async def publish(self, *, exchange: str, routing_key: str, event: DomainEvent) -> None: ...

  async def connect(self) -> None: ...

  async def close(self) -> None: ...


class NoopEventPublisher:
  async def connect(self) -> None:
    return

  async def publish(self, *, exchange: str, routing_key: str, event: DomainEvent) -> None:
    _ = (exchange, routing_key, event)

  async def close(self) -> None:
    return


class RabbitMQEventPublisher:
  def __init__(
    self,
    *,
    url: str,
    publish_retry_attempts: int,
    publish_retry_backoff_ms: int,
    connect_timeout_s: float,
    connect_fn: Callable[..., Awaitable[Any]] | None = None,
    sleep_fn: Callable[[float], Awaitable[None]] = asyncio.sleep,
  ) -> None:
    self.url = url
    self.publish_retry_attempts = max(1, publish_retry_attempts)
    self.publish_retry_backoff_ms = max(1, publish_retry_backoff_ms)
    self.connect_timeout_s = connect_timeout_s
    self.connect_fn = connect_fn
    self.sleep_fn = sleep_fn

    self._connection: Any | None = None
    self._channel: Any | None = None
    self._exchanges: dict[str, Any] = {}

  async def connect(self) -> None:
    if self._channel is not None:
      return
    await self._connect_with_retry()

  async def close(self) -> None:
    channel = self._channel
    connection = self._connection
    self._channel = None
    self._connection = None
    self._exchanges = {}

    if channel is not None:
      await channel.close()
    if connection is not None:
      await connection.close()

  async def publish(self, *, exchange: str, routing_key: str, event: DomainEvent) -> None:
    for attempt in range(1, self.publish_retry_attempts + 1):
      try:
        await self.connect()
        if self._channel is None:
          raise RuntimeError("RabbitMQ channel is not initialized")

        target_exchange = self._exchanges.get(exchange)
        if target_exchange is None:
          target_exchange = await self._channel.declare_exchange(exchange, "topic", durable=True)
          self._exchanges[exchange] = target_exchange

        message = await self._build_message(event)
        await target_exchange.publish(message, routing_key=routing_key)
        return
      except Exception as exc:
        await self._reset_connection()
        if attempt == self.publish_retry_attempts:
          raise ServiceUnavailableError("RabbitMQ publish failed after retries") from exc
        await self.sleep_fn(self.publish_retry_backoff_ms / 1000)

  async def _connect_with_retry(self) -> None:
    for attempt in range(1, self.publish_retry_attempts + 1):
      try:
        await self._connect_once()
        return
      except Exception as exc:
        await self._reset_connection()
        if attempt == self.publish_retry_attempts:
          raise ServiceUnavailableError("RabbitMQ connection failed after retries") from exc
        await self.sleep_fn(self.publish_retry_backoff_ms / 1000)

  async def _connect_once(self) -> None:
    connect_fn = self.connect_fn
    if connect_fn is None:
      from aio_pika import connect_robust

      connect_fn = connect_robust

    self._connection = await connect_fn(self.url, timeout=self.connect_timeout_s)
    self._channel = await self._connection.channel(publisher_confirms=True)
    await self._declare_topology()

  async def _declare_topology(self) -> None:
    if self._channel is None:
      raise RuntimeError("RabbitMQ channel is not initialized")

    venue_exchange = await self._channel.declare_exchange(VENUE_EXCHANGE, "topic", durable=True)
    payout_exchange = await self._channel.declare_exchange(PAYOUT_EXCHANGE, "topic", durable=True)
    venue_dlx = await self._channel.declare_exchange(VENUE_DLX_EXCHANGE, "topic", durable=True)
    payout_dlx = await self._channel.declare_exchange(PAYOUT_DLX_EXCHANGE, "topic", durable=True)

    venue_dlq = await self._channel.declare_queue(VENUE_DLQ, durable=True)
    payout_dlq = await self._channel.declare_queue(PAYOUT_DLQ, durable=True)
    await venue_dlq.bind(venue_dlx, routing_key="#")
    await payout_dlq.bind(payout_dlx, routing_key="#")

    self._exchanges = {
      VENUE_EXCHANGE: venue_exchange,
      PAYOUT_EXCHANGE: payout_exchange,
      VENUE_DLX_EXCHANGE: venue_dlx,
      PAYOUT_DLX_EXCHANGE: payout_dlx,
    }

  async def _build_message(self, event: DomainEvent) -> Any:
    from aio_pika import DeliveryMode, Message

    body = json.dumps(event.model_dump(mode="json"), ensure_ascii=False).encode("utf-8")
    return Message(
      body=body,
      content_type="application/json",
      delivery_mode=DeliveryMode.PERSISTENT,
      message_id=event.event_id,
      timestamp=event.timestamp.astimezone(timezone.utc),
      type=event.event_type,
    )

  async def _reset_connection(self) -> None:
    channel = self._channel
    connection = self._connection
    self._channel = None
    self._connection = None
    self._exchanges = {}

    if channel is not None:
      try:
        await channel.close()
      except Exception:
        pass

    if connection is not None:
      try:
        await connection.close()
      except Exception:
        pass
