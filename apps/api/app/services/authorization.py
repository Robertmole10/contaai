import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.membership import Membership
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user import User
from app.models.user_platform_role import UserPlatformRole


class AuthorizationService:
    def __init__(self, db: Session):
        self.db = db

    def get_membership(
        self,
        user_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Membership | None:

        return self.db.scalar(
            select(Membership).where(
                Membership.user_id == user_id,
                Membership.organization_id == organization_id,
            )
        )

    def get_platform_role_keys(
        self,
        user_id: uuid.UUID,
    ) -> set[str]:

        rows = self.db.execute(
            select(Role.key)
            .join(
                UserPlatformRole,
                UserPlatformRole.role_id == Role.id,
            )
            .where(
                UserPlatformRole.user_id == user_id,
                Role.scope == "platform",
            )
        )

        return {row[0] for row in rows}
    
    def has_platform_role(
        self,
        user_id: uuid.UUID,
        role_key: str,
    ) -> bool:

        return role_key in self.get_platform_role_keys(user_id)
    
    def has_permission(
        self,
        user_id: uuid.UUID,
        organization_id: uuid.UUID,
        permission_key: str,
    ) -> bool:

        membership = self.get_membership(
            user_id,
            organization_id,
        )

        if membership is None:
            return False

        result = self.db.execute(
            select(Permission.id)
            .join(
                RolePermission,
                RolePermission.permission_id == Permission.id,
            )
            .where(
                RolePermission.role_id == membership.role_id,
                Permission.key == permission_key,
            )
        )

        return result.first() is not None