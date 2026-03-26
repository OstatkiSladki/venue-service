from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from src.api.deps import get_company_service, get_identity_context, get_optional_identity_context
from src.schemas.common import IdentityContext, PaginatedResponse, PaginationMeta
from src.schemas.company import CompanyCreate, CompanyListQuery, CompanyResponse, CompanyUpdate
from src.services.company_service import CompanyService

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.get("", response_model=PaginatedResponse[CompanyResponse])
async def list_companies(
  service: Annotated[CompanyService, Depends(get_company_service)],
  identity: Annotated[IdentityContext | None, Depends(get_optional_identity_context)],
  query: Annotated[CompanyListQuery, Query()],
) -> PaginatedResponse[CompanyResponse]:
  items, total = await service.list_companies(
    identity=identity,
    query=query,
  )
  return PaginatedResponse[CompanyResponse](
    items=[CompanyResponse.model_validate(item) for item in items],
    meta=PaginationMeta(limit=query.limit, offset=query.offset, total=total),
  )


@router.post("", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
  payload: CompanyCreate,
  service: Annotated[CompanyService, Depends(get_company_service)],
  identity: Annotated[IdentityContext, Depends(get_identity_context)],
) -> CompanyResponse:
  company = await service.create_company(payload=payload, identity=identity)
  return CompanyResponse.model_validate(company)


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
  company_id: int,
  service: Annotated[CompanyService, Depends(get_company_service)],
  identity: Annotated[IdentityContext | None, Depends(get_optional_identity_context)],
) -> CompanyResponse:
  company = await service.get_company(company_id=company_id, identity=identity)
  return CompanyResponse.model_validate(company)


@router.patch("/{company_id}", response_model=CompanyResponse)
async def patch_company(
  company_id: int,
  payload: CompanyUpdate,
  service: Annotated[CompanyService, Depends(get_company_service)],
  identity: Annotated[IdentityContext, Depends(get_identity_context)],
) -> CompanyResponse:
  company = await service.update_company(company_id=company_id, payload=payload, identity=identity)
  return CompanyResponse.model_validate(company)


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
  company_id: int,
  service: Annotated[CompanyService, Depends(get_company_service)],
  identity: Annotated[IdentityContext, Depends(get_identity_context)],
) -> None:
  await service.soft_delete_company(company_id=company_id, identity=identity)
