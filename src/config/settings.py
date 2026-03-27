from functools import lru_cache
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

  app_name: str = "venue-service"
  app_version: str = "1.0.0"
  app_env: str = "development"
  debug: bool = False
  app_root_path: str = ""

  host: str = "0.0.0.0"
  port: int = 8002
  workers: int = 1
  reload: bool = False

  database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/db_venue"
  database_pool_size: int = 10
  database_max_overflow: int = 20
  database_pool_timeout: int = 30

  log_level: str = "INFO"
  log_format: str = "json"
  rabbitmq_enabled: bool = False
  rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
  rabbitmq_publish_retry_attempts: int = 3
  rabbitmq_publish_retry_backoff_ms: int = 200
  rabbitmq_connect_timeout_s: float = 5.0

  @field_validator("debug", mode="before")
  @classmethod
  def normalize_debug_value(cls, value: Any) -> bool:
    if isinstance(value, bool):
      return value
    if isinstance(value, str):
      normalized = value.strip().lower()
      if normalized in {"1", "true", "yes", "on", "debug", "development"}:
        return True
      if normalized in {"0", "false", "no", "off", "release", "production"}:
        return False
    return bool(value)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
  return Settings()
