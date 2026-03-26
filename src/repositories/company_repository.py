from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.company import Company
from src.repositories.base import BaseRepository


class CompanyRepository(BaseRepository[Company]):
  def __init__(self, session: AsyncSession) -> None:
    super().__init__(session=session, model=Company)

  async def find_by_inn(self, inn: str, include_deleted: bool = False) -> Company | None:
    statement = select(Company).where(Company.inn == inn)
    if not include_deleted:
      statement = statement.where(Company.deleted_at.is_(None))
    result = await self.session.execute(statement)
    return result.scalar_one_or_none()
