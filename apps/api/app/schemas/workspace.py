import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CompanyCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    tax_id: str | None = Field(default=None, max_length=64)
    is_vat_payer: bool = False
    legal_form: str | None = Field(default=None, max_length=64)
    country_code: str = Field(default="RO", min_length=2, max_length=2)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        normalized = value.strip()

        if len(normalized) < 2:
            raise ValueError("Denumirea companiei este obligatorie.")

        return normalized

    @field_validator("tax_id")
    @classmethod
    def clean_tax_id(cls, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = value.strip()
        return normalized or None

    @field_validator("country_code")
    @classmethod
    def normalize_country_code(cls, value: str) -> str:
        return value.strip().upper()


class CompanyVatStatusUpdate(BaseModel):
    is_vat_payer: bool


class CompanyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    tax_id: str | None
    is_vat_payer: bool
    display_tax_id: str | None
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