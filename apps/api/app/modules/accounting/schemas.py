from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.accounting.enums import (
    AccountingPeriodStatus,
    AccountNature,
    AccountSource,
    AccountType,
)


# ==========================================================
# Accounts
# ==========================================================


class AccountBase(BaseModel):
    code: str = Field(min_length=1, max_length=32)
    name: str = Field(min_length=1, max_length=255)

    account_class: int = Field(ge=1, le=9)

    account_type: AccountType
    nature: AccountNature

    allows_posting: bool = True
    is_analytic: bool = False
    is_active: bool = True


class AccountCreate(AccountBase):
    parent_id: UUID | None = None
    source: AccountSource = AccountSource.MANUAL


class AccountUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str | None = Field(
        default=None,
        min_length=1,
        max_length=32,
    )
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    parent_id: UUID | None = None

    account_class: int | None = Field(
        default=None,
        ge=1,
        le=9,
    )

    account_type: AccountType | None = None
    nature: AccountNature | None = None

    allows_posting: bool | None = None
    is_analytic: bool | None = None
    is_active: bool | None = None


class AccountRead(AccountBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    parent_id: UUID | None

    source: AccountSource

    created_at: datetime
    updated_at: datetime


class AccountTreeNode(AccountRead):
    children: list["AccountTreeNode"] = Field(default_factory=list)


class AccountListResponse(BaseModel):
    items: list[AccountRead]
    offset: int
    limit: int
    count: int


# ==========================================================
# Accounting Periods
# ==========================================================


class AccountingPeriodBase(BaseModel):
    year: int = Field(ge=2000, le=2200)
    month: int = Field(ge=1, le=12)

    start_date: date
    end_date: date


class AccountingPeriodCreate(AccountingPeriodBase):
    status: AccountingPeriodStatus = AccountingPeriodStatus.OPEN


class AccountingPeriodUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    start_date: date | None = None
    end_date: date | None = None
    status: AccountingPeriodStatus | None = None


class AccountingPeriodRead(AccountingPeriodBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID

    status: AccountingPeriodStatus
    closed_at: datetime | None

    created_at: datetime
    updated_at: datetime


class AccountingPeriodListResponse(BaseModel):
    items: list[AccountingPeriodRead]
    offset: int
    limit: int
    count: int