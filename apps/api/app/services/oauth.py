from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.user_identity import UserIdentity
from app.services.auth import AuthError, get_user_by_email


def get_identity(
    db: Session,
    provider: str,
    provider_user_id: str,
) -> UserIdentity | None:
    return db.scalar(
        select(UserIdentity).where(
            UserIdentity.provider == provider,
            UserIdentity.provider_user_id == provider_user_id,
        )
    )


def get_or_create_google_user(
    db: Session,
    user_info: dict,
) -> User:
    provider_user_id = str(user_info.get("sub", "")).strip()
    email = str(user_info.get("email", "")).strip().lower()
    email_verified = bool(user_info.get("email_verified", False))

    if not provider_user_id:
        raise AuthError("Google nu a furnizat identificatorul utilizatorului.")

    if not email:
        raise AuthError("Google nu a furnizat adresa de e-mail.")

    if not email_verified:
        raise AuthError("Adresa de e-mail Google nu este verificată.")

    identity = get_identity(
        db,
        provider="google",
        provider_user_id=provider_user_id,
    )

    if identity:
        user = identity.user

        if not user.is_active:
            raise AuthError("Contul este dezactivat.")

        return user

    user = get_user_by_email(db, email)

    if user is None:
        user = User(
            email=email,
            hashed_password=None,
            first_name=str(user_info.get("given_name", "")).strip(),
            last_name=str(user_info.get("family_name", "")).strip(),
            email_verified=True,
            avatar_url=user_info.get("picture"),
        )
        db.add(user)
        db.flush()
    else:
        if not user.is_active:
            raise AuthError("Contul este dezactivat.")

        user.email_verified = True

        if not user.first_name:
            user.first_name = str(
                user_info.get("given_name", "")
            ).strip()

        if not user.last_name:
            user.last_name = str(
                user_info.get("family_name", "")
            ).strip()

        if not user.avatar_url:
            user.avatar_url = user_info.get("picture")

    identity = UserIdentity(
        user_id=user.id,
        provider="google",
        provider_user_id=provider_user_id,
        provider_email=email,
    )

    db.add(identity)
    db.commit()
    db.refresh(user)

    return user
