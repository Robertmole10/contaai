import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.membership import Membership
from app.models.organization import Organization
from app.models.role import Role
from app.models.user import User


def create_user(
    db: Session,
    *,
    email: str | None = None,
    is_active: bool = True,
) -> User:
    unique = uuid.uuid4().hex
    user = User(
        email=email or f"test-{unique}@example.com",
        first_name="Test",
        last_name="User",
        email_verified=True,
        is_active=is_active,
    )
    db.add(user)
    db.flush()
    return user


def create_organization(
    db: Session,
    *,
    name: str | None = None,
) -> Organization:
    organization = Organization(
        name=name or f"Test Organization {uuid.uuid4().hex[:8]}",
    )
    db.add(organization)
    db.flush()
    return organization


def get_role(
    db: Session,
    role_key: str,
) -> Role:
    role = db.scalar(
        select(Role).where(
            Role.key == role_key,
            Role.scope == "organization",
        )
    )
    if role is None:
        raise AssertionError(
            f"Rolul de organizație {role_key!r} nu există în baza de test."
        )
    return role


def create_membership(
    db: Session,
    *,
    user: User,
    organization: Organization,
    role_key: str,
) -> Membership:
    role = get_role(db, role_key)
    membership = Membership(
        user_id=user.id,
        organization_id=organization.id,
        role_id=role.id,
    )
    db.add(membership)
    db.flush()
    return membership
