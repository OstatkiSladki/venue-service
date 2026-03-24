from datetime import datetime, timezone
from typing import Any, Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    def __init__(self, session: AsyncSession, model: type[ModelT]) -> None:
        self.session = session
        self.model = model

    async def get_by_id(self, entity_id: int, include_deleted: bool = False) -> ModelT | None:
        id_column = getattr(self.model, "id")
        statement = select(self.model).where(id_column == entity_id)
        deleted_at_column = getattr(self.model, "deleted_at", None)
        if deleted_at_column is not None and not include_deleted:
            statement = statement.where(deleted_at_column.is_(None))
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        limit: int,
        offset: int,
        include_deleted: bool = False,
    ) -> list[ModelT]:
        id_column = getattr(self.model, "id")
        statement = select(self.model).limit(limit).offset(offset).order_by(id_column)
        deleted_at_column = getattr(self.model, "deleted_at", None)
        if deleted_at_column is not None and not include_deleted:
            statement = statement.where(deleted_at_column.is_(None))
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def count(self, include_deleted: bool = False) -> int:
        id_column = getattr(self.model, "id")
        statement = select(func.count(id_column))
        deleted_at_column = getattr(self.model, "deleted_at", None)
        if deleted_at_column is not None and not include_deleted:
            statement = statement.where(deleted_at_column.is_(None))
        result = await self.session.execute(statement)
        return int(result.scalar_one())

    async def create(self, data: dict[str, Any]) -> ModelT:
        entity = self.model(**data)
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def update(self, entity: ModelT, data: dict[str, Any]) -> ModelT:
        for key, value in data.items():
            setattr(entity, key, value)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def soft_delete(self, entity: ModelT) -> None:
        if not hasattr(entity, "deleted_at"):
            raise ValueError(f"Model {self.model.__name__} does not support soft delete")
        entity.deleted_at = datetime.now(timezone.utc)
        await self.session.flush()
