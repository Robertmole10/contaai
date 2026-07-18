from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.company import Company
from app.modules.documents.permissions import (
    get_company_for_user,
    require_company_roles,
)


ACCOUNTING_READ_ROLES = {
    "owner",
    "admin",
    "accountant",
    "viewer",
}

ACCOUNTING_WRITE_ROLES = {
    "owner",
    "admin",
    "accountant",
}


def require_accounting_read_access(
    *,
    db: Session,
    user_id: UUID,
    company_id: UUID,
) -> Company:
    return require_company_roles(
        db=db,
        user_id=user_id,
        company_id=company_id,
        allowed_roles=ACCOUNTING_READ_ROLES,
    )


def require_accounting_write_access(
    *,
    db: Session,
    user_id: UUID,
    company_id: UUID,
) -> Company:
    return require_company_roles(
        db=db,
        user_id=user_id,
        company_id=company_id,
        allowed_roles=ACCOUNTING_WRITE_ROLES,
    )


__all__ = [
    "ACCOUNTING_READ_ROLES",
    "ACCOUNTING_WRITE_ROLES",
    "get_company_for_user",
    "require_accounting_read_access",
    "require_accounting_write_access",
]