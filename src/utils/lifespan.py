from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.config import get_settings
from src.db.session import close_engine
from src.events.publisher import EventPublisher, NoopEventPublisher, RabbitMQEventPublisher
from src.grpc import start_grpc_server, stop_grpc_server


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
  settings = get_settings()
  publisher: EventPublisher
  if settings.rabbitmq_enabled:
    publisher = RabbitMQEventPublisher(
      url=settings.rabbitmq_url,
      publish_retry_attempts=settings.rabbitmq_publish_retry_attempts,
      publish_retry_backoff_ms=settings.rabbitmq_publish_retry_backoff_ms,
      connect_timeout_s=settings.rabbitmq_connect_timeout_s,
    )
    await publisher.connect()
  else:
    publisher = NoopEventPublisher()

  app.state.event_publisher = publisher
  grpc_server, grpc_health = await start_grpc_server()
  app.state.grpc_server = grpc_server
  app.state.grpc_health = grpc_health
  try:
    yield
  finally:
    await stop_grpc_server(grpc_server, grpc_health)
    await publisher.close()
    await close_engine()
