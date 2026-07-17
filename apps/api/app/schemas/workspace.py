import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CompanyCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    tax_id: str | None = Field(default=None, max_length=64)
    legal_form: str | None = Field(default=None, max_length=64)
    country_code: str = Field(default="RO", min_length=2, max_length=2)


class CompanyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    tax_id: str | None
    legal_form: str | None
    country_code: str
    created_at: datetime


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    company: CompanyCreate | None = None


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    key: str
    name: str


class OrganizationResponse(BaseModel):
    id: uuid.UUID
    name: str
    role: RoleResponse
    companies: list[CompanyResponse]
    created_at: datetime


class WorkspaceResponse(BaseModel):
    organizations: list[OrganizationResponse]
