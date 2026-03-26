from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
  AsyncEngine,
  AsyncSession,
  async_sessionmaker,
  create_async_engine,
)

from src.config.settings import get_settings

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
  global _engine
  if _engine is None:
    settings = get_settings()
    _engine = create_async_engine(
      settings.database_url,
      pool_size=settings.database_pool_size,
      max_overflow=settings.database_max_overflow,
      pool_timeout=settings.database_pool_timeout,
      future=True,
    )
  return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
  global _session_factory
  if _session_factory is None:
    _session_factory = async_sessionmaker(
      get_engine(),
      autoflush=False,
      autocommit=False,
      expire_on_commit=False,
    )
  return _session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
  session_factory = get_session_factory()
  async with session_factory() as session:
    yield session


async def close_engine() -> None:
  global _engine
  if _engine is not None:
    await _engine.dispose()
    _engine = None
