import uuid

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User
from collections.abc import Callable

from app.models.membership import Membership
from app.services.authorization import AuthorizationService

def get_current_user(
    db: Session = Depends(get_db),
    access_token: str | None = Cookie(default=None),
) -> User:
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Autentificare necesară.")
    try:
        payload = decode_token(access_token, "access")
        user_id = uuid.UUID(payload["sub"])
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesiune invalidă.")
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Utilizator inactiv.")
    return user

def require_platform_role(
    *role_keys: str,
) -> Callable[..., User]:
    allowed_roles = set(role_keys)

    if not allowed_roles:
        raise ValueError(
            "Trebuie specificat cel puțin un rol de platformă."
        )

    def dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        authorization = AuthorizationService(db)

        user_roles = authorization.get_platform_role_keys(
            current_user.id
        )

        if user_roles.isdisjoint(allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Nu ai rolul de platformă necesar "
                    "pentru această acțiune."
                ),
            )

        return current_user

    return dependency


def require_permission(
    permission_key: str,
) -> Callable[..., Membership]:
    if not permission_key.strip():
        raise ValueError(
            "Cheia permisiunii nu poate fi goală."
        )

    def dependency(
        organization_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> Membership:
        authorization = AuthorizationService(db)

        membership = authorization.get_membership(
            current_user.id,
            organization_id,
        )

        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organizația nu a fost găsită.",
            )

        if not authorization.has_permission(
            current_user.id,
            organization_id,
            permission_key,
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Nu ai permisiunea necesară "
                    "pentru această acțiune."
                ),
            )

        return membership

    return dependency
