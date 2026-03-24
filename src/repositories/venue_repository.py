from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from src.models.venue import Venue
from src.repositories.base import BaseRepository


class VenueRepository(BaseRepository[Venue]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session, model=Venue)

    async def list_filtered(
        self,
        *,
        limit: int,
        offset: int,
        include_deleted: bool = False,
        name: str | None = None,
        is_open: bool | None = None,
        company_id: int | None = None,
        lat: Decimal | None = None,
        lon: Decimal | None = None,
        radius_km: Decimal | None = None,
    ) -> list[Venue]:
        statement = select(Venue)
        statement = self._apply_filters(
            statement,
            include_deleted=include_deleted,
            name=name,
            is_open=is_open,
            company_id=company_id,
            lat=lat,
            lon=lon,
            radius_km=radius_km,
        )
        statement = statement.order_by(Venue.id).limit(limit).offset(offset)

        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def count_filtered(
        self,
        *,
        include_deleted: bool = False,
        name: str | None = None,
        is_open: bool | None = None,
        company_id: int | None = None,
        lat: Decimal | None = None,
        lon: Decimal | None = None,
        radius_km: Decimal | None = None,
    ) -> int:
        statement = select(func.count(Venue.id))
        statement = self._apply_filters(
            statement,
            include_deleted=include_deleted,
            name=name,
            is_open=is_open,
            company_id=company_id,
            lat=lat,
            lon=lon,
            radius_km=radius_km,
        )

        result = await self.session.execute(statement)
        return int(result.scalar_one())

    @staticmethod
    def _apply_filters(
        statement: Select[Any],
        *,
        include_deleted: bool,
        name: str | None,
        is_open: bool | None,
        company_id: int | None,
        lat: Decimal | None,
        lon: Decimal | None,
        radius_km: Decimal | None,
    ) -> Select[Any]:
        if not include_deleted:
            statement = statement.where(Venue.deleted_at.is_(None))

        if name is not None:
            statement = statement.where(Venue.name.ilike(f"%{name}%"))

        if is_open is not None:
            statement = statement.where(Venue.is_open.is_(is_open))

        if company_id is not None:
            statement = statement.where(Venue.company_id == company_id)

        if lat is not None and lon is not None:
            earth_radius_km = 6371.0
            distance_expr = earth_radius_km * func.acos(
                func.cos(func.radians(lat))
                * func.cos(func.radians(Venue.latitude))
                * func.cos(func.radians(Venue.longitude) - func.radians(lon))
                + func.sin(func.radians(lat)) * func.sin(func.radians(Venue.latitude))
            )
            effective_radius = float(radius_km) if radius_km is not None else 5.0
            statement = statement.where(distance_expr <= effective_radius)

        return statement
