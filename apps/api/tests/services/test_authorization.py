import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.membership import Membership
from app.models.organization import Organization
from app.models.role import Role
from app.models.user import User
from app.models.user_platform_role import UserPlatformRole
from app.services.authorization import AuthorizationService


def create_user(db: Session) -> User:
    user = User(
        email=f"rbac-{uuid.uuid4()}@example.com",
        first_name="RBAC",
        last_name="Test",
        is_active=True,
    )
    db.add(user)
    db.flush()
    return user


def get_role(db: Session, role_key: str) -> Role:
    role = db.scalar(
        select(Role).where(Role.key == role_key)
    )

    assert role is not None, (
        f"Rolul seed-uit {role_key!r} nu există."
    )

    return role


def create_membership(
    db: Session,
    user: User,
    role_key: str,
) -> tuple[Organization, Membership]:
    organization = Organization(
        name=f"RBAC Organization {uuid.uuid4()}"
    )
    db.add(organization)
    db.flush()

    role = get_role(db, role_key)

    membership = Membership(
        user_id=user.id,
        organization_id=organization.id,
        role_id=role.id,
    )
    db.add(membership)
    db.flush()

    return organization, membership


@pytest.mark.parametrize(
    ("role_key", "expected"),
    [
        ("owner", True),
        ("admin", True),
        ("accountant", False),
        ("auditor", False),
        ("employee", False),
    ],
)
def test_company_manage_permission_by_organization_role(
    db_session: Session,
    role_key: str,
    expected: bool,
):
    user = create_user(db_session)
    organization, _ = create_membership(
        db_session,
        user,
        role_key,
    )

    authorization = AuthorizationService(db_session)

    assert authorization.has_permission(
        user_id=user.id,
        organization_id=organization.id,
        permission_key="company.manage",
    ) is expected


def test_non_member_has_no_organization_permission(
    db_session: Session,
):
    user = create_user(db_session)

    organization = Organization(
        name=f"RBAC Organization {uuid.uuid4()}"
    )
    db_session.add(organization)
    db_session.flush()

    authorization = AuthorizationService(db_session)

    assert authorization.has_permission(
        user_id=user.id,
        organization_id=organization.id,
        permission_key="company.manage",
    ) is False


def test_unknown_permission_returns_false(
    db_session: Session,
):
    user = create_user(db_session)
    organization, _ = create_membership(
        db_session,
        user,
        "owner",
    )

    authorization = AuthorizationService(db_session)

    assert authorization.has_permission(
        user_id=user.id,
        organization_id=organization.id,
        permission_key="permission.does.not.exist",
    ) is False


def test_get_membership_returns_membership(
    db_session: Session,
):
    user = create_user(db_session)
    organization, membership = create_membership(
        db_session,
        user,
        "accountant",
    )

    authorization = AuthorizationService(db_session)

    result = authorization.get_membership(
        user_id=user.id,
        organization_id=organization.id,
    )

    assert result is not None
    assert result.id == membership.id
    assert result.user_id == user.id
    assert result.organization_id == organization.id


def test_get_membership_returns_none_for_unknown_membership(
    db_session: Session,
):
    authorization = AuthorizationService(db_session)

    result = authorization.get_membership(
        user_id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
    )

    assert result is None


def test_platform_role_lookup(
    db_session: Session,
):
    user = create_user(db_session)

    platform_role = get_role(
        db_session,
        "platform_admin",
    )

    assignment = UserPlatformRole(
        user_id=user.id,
        role_id=platform_role.id,
    )
    db_session.add(assignment)
    db_session.flush()

    authorization = AuthorizationService(db_session)

    assert authorization.get_platform_role_keys(
        user.id
    ) == {"platform_admin"}

    assert authorization.has_platform_role(
        user.id,
        "platform_admin",
    ) is True

    assert authorization.has_platform_role(
        user.id,
        "platform_super_admin",
    ) is False


def test_user_without_platform_roles_returns_empty_set(
    db_session: Session,
):
    user = create_user(db_session)

    authorization = AuthorizationService(db_session)

    assert authorization.get_platform_role_keys(
        user.id
    ) == set()
