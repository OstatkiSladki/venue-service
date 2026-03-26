from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.payout import Payout
from src.repositories.base import BaseRepository
from src.models.enums import PayoutStatus


class PayoutRepository(BaseRepository[Payout]):
  def __init__(self, session: AsyncSession) -> None:
    super().__init__(session=session, model=Payout)

  async def list_by_venue(
    self,
    *,
    venue_id: int,
    status: PayoutStatus | None,
    limit: int,
    offset: int,
  ) -> list[Payout]:
    statement = select(Payout).where(Payout.venue_id == venue_id).order_by(Payout.id.desc())
    if status is not None:
      statement = statement.where(Payout.status == status)

    statement = statement.limit(limit).offset(offset)
    result = await self.session.execute(statement)
    return list(result.scalars().all())

  async def count_by_venue(self, *, venue_id: int, status: PayoutStatus | None) -> int:
    statement = select(func.count(Payout.id)).where(Payout.venue_id == venue_id)
    if status is not None:
      statement = statement.where(Payout.status == status)

    result = await self.session.execute(statement)
    return int(result.scalar_one())

  async def get_by_id_for_venue(self, *, payout_id: int, venue_id: int) -> Payout | None:
    statement = select(Payout).where(
      Payout.id == payout_id,
      Payout.venue_id == venue_id,
    )
    result = await self.session.execute(statement)
    return result.scalar_one_or_none()
