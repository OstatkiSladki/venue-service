from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.common import PaginationQuery


class CompanyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    inn: str | None = Field(default=None, max_length=20)


class CompanyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    inn: str | None = Field(default=None, max_length=20)
    is_active: bool | None = None


class CompanyListQuery(PaginationQuery):
    include_deleted: bool = False


class CompanyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    inn: str | None
    is_active: bool
    created_at: datetime
    deleted_at: datetime | None
