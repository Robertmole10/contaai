import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.company import Company
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.role import Role
from app.models.user import User
from app.schemas.workspace import CompanyCreate, CompanyResponse, OrganizationCreate, OrganizationResponse, RoleResponse, WorkspaceResponse

router = APIRouter(tags=["Workspace"])


def membership_for(db: Session, user_id: uuid.UUID, organization_id: uuid.UUID) -> Membership:
    membership = db.scalar(
        select(Membership).options(joinedload(Membership.role)).where(
            Membership.user_id == user_id,
            Membership.organization_id == organization_id,
        )
    )
    if not membership:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organizația nu a fost găsită.")
    return membership


def require_manage_company(membership: Membership) -> None:
    if membership.role.key not in {"owner", "admin"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Nu ai dreptul să administrezi companii.")


def serialize_organization(membership: Membership) -> OrganizationResponse:
    org = membership.organization
    return OrganizationResponse(
        id=org.id,
        name=org.name,
        role=RoleResponse.model_validate(membership.role),
        companies=[CompanyResponse.model_validate(company) for company in org.companies],
        created_at=org.created_at,
    )


@router.get("/workspace", response_model=WorkspaceResponse)
def workspace(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    memberships = db.scalars(
        select(Membership)
        .options(joinedload(Membership.role), joinedload(Membership.organization).joinedload(Organization.companies))
        .where(Membership.user_id == current_user.id)
        .order_by(Membership.created_at)
    ).unique().all()
    return WorkspaceResponse(organizations=[serialize_organization(m) for m in memberships])


@router.post("/organizations", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_organization(payload: OrganizationCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    owner_role = db.scalar(select(Role).where(Role.key == "owner"))
    if not owner_role:
        raise HTTPException(status_code=500, detail="Rolurile implicite nu sunt configurate.")

    organization = Organization(name=payload.name.strip())
    db.add(organization)
    db.flush()
    membership = Membership(user_id=current_user.id, organization_id=organization.id, role_id=owner_role.id)
    db.add(membership)
    if payload.company:
        company = Company(
            organization_id=organization.id,
            name=payload.company.name.strip(),
            tax_id=payload.company.tax_id,
            legal_form=payload.company.legal_form,
            country_code=payload.company.country_code.upper(),
        )
        db.add(company)
    db.commit()

    membership = db.scalar(
        select(Membership).options(joinedload(Membership.role), joinedload(Membership.organization).joinedload(Organization.companies)).where(Membership.id == membership.id)
    )
    return serialize_organization(membership)


@router.get("/organizations", response_model=list[OrganizationResponse])
def list_organizations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    memberships = db.scalars(
        select(Membership)
        .options(joinedload(Membership.role), joinedload(Membership.organization).joinedload(Organization.companies))
        .where(Membership.user_id == current_user.id)
    ).unique().all()
    return [serialize_organization(m) for m in memberships]


@router.post("/organizations/{organization_id}/companies", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_company(organization_id: uuid.UUID, payload: CompanyCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    membership = membership_for(db, current_user.id, organization_id)
    require_manage_company(membership)
    company = Company(
        organization_id=organization_id,
        name=payload.name.strip(),
        tax_id=payload.tax_id,
        legal_form=payload.legal_form,
        country_code=payload.country_code.upper(),
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.get("/organizations/{organization_id}/companies", response_model=list[CompanyResponse])
def list_companies(organization_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    membership_for(db, current_user.id, organization_id)
    return db.scalars(select(Company).where(Company.organization_id == organization_id).order_by(Company.name)).all()
