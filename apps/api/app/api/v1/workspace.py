import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.company import Company
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.role import Role
from app.models.user import User
from app.schemas.workspace import (
    CompanyCreate,
    CompanyResponse,
    CompanyVatStatusUpdate,
    OrganizationCreate,
    OrganizationResponse,
    RoleResponse,
    WorkspaceResponse,
)
from app.api.utils.company_identity import (
    InvalidCompanyNameError,
    InvalidTaxIdError,
    input_contains_vat_prefix,
    normalize_company_name,
    normalize_tax_id,
)

router = APIRouter(tags=["Workspace"])


def membership_for(
    db: Session,
    user_id: uuid.UUID,
    organization_id: uuid.UUID,
) -> Membership:
    membership = db.scalar(
        select(Membership)
        .options(joinedload(Membership.role))
        .where(
            Membership.user_id == user_id,
            Membership.organization_id == organization_id,
        )
    )

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organizația nu a fost găsită.",
        )

    return membership


def require_manage_company(membership: Membership) -> None:
    if membership.role.key not in {"owner", "admin"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nu ai dreptul să administrezi companii.",
        )


def serialize_organization(
    membership: Membership,
) -> OrganizationResponse:
    organization = membership.organization

    return OrganizationResponse(
        id=organization.id,
        name=organization.name,
        role=RoleResponse.model_validate(membership.role),
        companies=[
            CompanyResponse.model_validate(company)
            for company in organization.companies
        ],
        created_at=organization.created_at,
    )


def prepare_company_identity(
    payload: CompanyCreate,
) -> tuple[str, str, str | None, bool]:
    name = payload.name.strip()

    try:
        name_key = normalize_company_name(name)
        tax_id = normalize_tax_id(payload.tax_id)
    except (InvalidCompanyNameError, InvalidTaxIdError) as exception:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exception),
        ) from exception

    is_vat_payer = payload.is_vat_payer

    # Compatibilitate cu introducerea directă a prefixului RO.
    if input_contains_vat_prefix(payload.tax_id):
        is_vat_payer = True

    if not tax_id:
        is_vat_payer = False

    return name, name_key, tax_id, is_vat_payer


def ensure_company_is_unique(
    db: Session,
    organization_id: uuid.UUID,
    name_key: str,
    tax_id: str | None,
) -> None:
    company_with_same_name = db.scalar(
        select(Company).where(
            Company.organization_id == organization_id,
            Company.name_key == name_key,
        )
    )

    if company_with_same_name:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Există deja o companie cu această denumire "
                "în organizație."
            ),
        )

    if tax_id:
        company_with_same_tax_id = db.scalar(
            select(Company).where(
                Company.organization_id == organization_id,
                Company.tax_id == tax_id,
            )
        )

        if company_with_same_tax_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Există deja o companie înregistrată cu acest CUI "
                    "în organizație."
                ),
            )


def handle_company_integrity_error(exception: IntegrityError) -> None:
    constraint_name = getattr(
        getattr(exception.orig, "diag", None),
        "constraint_name",
        None,
    )

    if constraint_name == "uq_companies_organization_name_key":
        detail = (
            "Există deja o companie cu această denumire "
            "în organizație."
        )
    elif constraint_name == "uq_companies_organization_tax_id":
        detail = (
            "Există deja o companie înregistrată cu acest CUI "
            "în organizație."
        )
    else:
        detail = "Compania nu a putut fi salvată din cauza unui conflict."

    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=detail,
    ) from exception


@router.get(
    "/workspace",
    response_model=WorkspaceResponse,
)
def workspace(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    memberships = (
        db.scalars(
            select(Membership)
            .options(
                joinedload(Membership.role),
                joinedload(Membership.organization).joinedload(
                    Organization.companies
                ),
            )
            .where(Membership.user_id == current_user.id)
            .order_by(Membership.created_at)
        )
        .unique()
        .all()
    )

    return WorkspaceResponse(
        organizations=[
            serialize_organization(membership)
            for membership in memberships
        ]
    )


@router.post(
    "/organizations",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_organization(
    payload: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    owner_role = db.scalar(
        select(Role).where(Role.key == "owner")
    )

    if not owner_role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Rolurile implicite nu sunt configurate.",
        )

    organization = Organization(name=payload.name.strip())
    db.add(organization)
    db.flush()

    membership = Membership(
        user_id=current_user.id,
        organization_id=organization.id,
        role_id=owner_role.id,
    )
    db.add(membership)

    if payload.company:
        name, name_key, tax_id, is_vat_payer = (
            prepare_company_identity(payload.company)
        )

        company = Company(
            organization_id=organization.id,
            name=name,
            name_key=name_key,
            tax_id=tax_id,
            is_vat_payer=is_vat_payer,
            legal_form=payload.company.legal_form,
            country_code=payload.company.country_code,
        )
        db.add(company)

    try:
        db.commit()
    except IntegrityError as exception:
        db.rollback()
        handle_company_integrity_error(exception)

    membership = db.scalar(
        select(Membership)
        .options(
            joinedload(Membership.role),
            joinedload(Membership.organization).joinedload(
                Organization.companies
            ),
        )
        .where(Membership.id == membership.id)
    )

    return serialize_organization(membership)


@router.get(
    "/organizations",
    response_model=list[OrganizationResponse],
)
def list_organizations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    memberships = (
        db.scalars(
            select(Membership)
            .options(
                joinedload(Membership.role),
                joinedload(Membership.organization).joinedload(
                    Organization.companies
                ),
            )
            .where(Membership.user_id == current_user.id)
        )
        .unique()
        .all()
    )

    return [
        serialize_organization(membership)
        for membership in memberships
    ]


@router.post(
    "/organizations/{organization_id}/companies",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_company(
    organization_id: uuid.UUID,
    payload: CompanyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    membership = membership_for(
        db,
        current_user.id,
        organization_id,
    )
    require_manage_company(membership)

    name, name_key, tax_id, is_vat_payer = (
        prepare_company_identity(payload)
    )

    ensure_company_is_unique(
        db=db,
        organization_id=organization_id,
        name_key=name_key,
        tax_id=tax_id,
    )

    company = Company(
        organization_id=organization_id,
        name=name,
        name_key=name_key,
        tax_id=tax_id,
        is_vat_payer=is_vat_payer,
        legal_form=payload.legal_form,
        country_code=payload.country_code,
    )

    db.add(company)

    try:
        db.commit()
    except IntegrityError as exception:
        db.rollback()
        handle_company_integrity_error(exception)

    db.refresh(company)
    return company


@router.patch(
    "/organizations/{organization_id}/companies/{company_id}/vat-status",
    response_model=CompanyResponse,
)
def update_company_vat_status(
    organization_id: uuid.UUID,
    company_id: uuid.UUID,
    payload: CompanyVatStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    membership = membership_for(
        db,
        current_user.id,
        organization_id,
    )
    require_manage_company(membership)

    company = db.scalar(
        select(Company).where(
            Company.id == company_id,
            Company.organization_id == organization_id,
        )
    )

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compania nu a fost găsită.",
        )

    if not company.tax_id and payload.is_vat_payer:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Compania nu poate fi marcată drept plătitoare de TVA "
                "fără un CUI."
            ),
        )

    company.is_vat_payer = payload.is_vat_payer
    db.commit()
    db.refresh(company)

    return company


@router.get(
    "/organizations/{organization_id}/companies",
    response_model=list[CompanyResponse],
)
def list_companies(
    organization_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    membership_for(
        db,
        current_user.id,
        organization_id,
    )

    return db.scalars(
        select(Company)
        .where(Company.organization_id == organization_id)
        .order_by(Company.name)
    ).all()