from sqlalchemy.ext.asyncio import AsyncSession

from src.core_exceptions import ConflictError, ForbiddenError, NotFoundError
from src.models.company import Company
from src.repositories.company_repository import CompanyRepository
from src.schemas.common import IdentityContext, UserRole
from src.schemas.company import CompanyCreate, CompanyListQuery, CompanyUpdate


class CompanyService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = CompanyRepository(session)

    @staticmethod
    def _require_admin(identity: IdentityContext) -> None:
        if identity.role != UserRole.ADMIN:
            raise ForbiddenError()

    async def list_companies(
        self,
        *,
        identity: IdentityContext,
        query: CompanyListQuery,
    ) -> tuple[list[Company], int]:
        self._require_admin(identity)

        if query.include_deleted and identity.role != UserRole.ADMIN:
            raise ForbiddenError()

        items = await self.repository.list(
            limit=query.limit,
            offset=query.offset,
            include_deleted=query.include_deleted,
        )
        total = await self.repository.count(include_deleted=query.include_deleted)
        return items, total

    async def get_company(self, *, company_id: int, identity: IdentityContext) -> Company:
        self._require_admin(identity)
        company = await self.repository.get_by_id(company_id)
        if company is None:
            raise NotFoundError("Company not found")
        return company

    async def create_company(
        self, *, payload: CompanyCreate, identity: IdentityContext
    ) -> Company:
        self._require_admin(identity)

        if payload.inn:
            existing = await self.repository.find_by_inn(payload.inn)
            if existing is not None:
                raise ConflictError("Company with this INN already exists")

        company = await self.repository.create(payload.model_dump(exclude_none=True))
        await self.session.commit()
        return company

    async def update_company(
        self, *, company_id: int, payload: CompanyUpdate, identity: IdentityContext
    ) -> Company:
        self._require_admin(identity)

        company = await self.repository.get_by_id(company_id)
        if company is None:
            raise NotFoundError("Company not found")

        data = payload.model_dump(exclude_unset=True)
        if "inn" in data and data["inn"]:
            existing = await self.repository.find_by_inn(data["inn"])
            if existing is not None and existing.id != company_id:
                raise ConflictError("Company with this INN already exists")

        updated = await self.repository.update(company, data)
        await self.session.commit()
        return updated

    async def soft_delete_company(self, *, company_id: int, identity: IdentityContext) -> None:
        self._require_admin(identity)

        company = await self.repository.get_by_id(company_id)
        if company is None:
            raise NotFoundError("Company not found")

        await self.repository.soft_delete(company)
        await self.session.commit()
