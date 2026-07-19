from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.company import Company
from app.models.membership import Membership


COMPANY_NOT_FOUND_DETAIL = "Compania nu a fost găsită."


def get_company_for_user(
    *,
    db: Session,
    user_id: UUID,
    company_id: UUID,
) -> Company:
    """
    Returnează compania numai dacă utilizatorul este membru
    al organizației căreia îi aparține compania.

    Răspunde cu 404 atât pentru o companie inexistentă,
    cât și pentru una la care utilizatorul nu are acces.
    """

    company = db.scalar(
        select(Company)
        .join(
            Membership,
            Membership.organization_id == Company.organization_id,
        )
        .where(
            Company.id == company_id,
            Membership.user_id == user_id,
        )
    )

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=COMPANY_NOT_FOUND_DETAIL,
        )

    return company


def require_company_roles(
    *,
    db: Session,
    user_id: UUID,
    company_id: UUID,
    allowed_roles: set[str],
) -> Company:
    """
    Verifică accesul la companie și restricționează operația
    la rolurile indicate.
    """

    result = db.execute(
        select(Company, Membership)
        .join(
            Membership,
            Membership.organization_id == Company.organization_id,
        )
        .options(joinedload(Membership.role))
        .where(
            Company.id == company_id,
            Membership.user_id == user_id,
      )
    ).one_or_none()

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=COMPANY_NOT_FOUND_DETAIL,
        )

    company, membership = result

    role_key = getattr(membership.role, "key", None)

    if role_key not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nu ai permisiunea necesară pentru această operație.",
        )

    return company