import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_token, decode_token, digest_jti, hash_password, verify_password
from app.models.refresh_token import RefreshToken
from app.models.user import User


class AuthError(Exception):
    pass


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.lower()))


def register_user(db: Session, email: str, password: str, first_name: str, last_name: str) -> User:
    if get_user_by_email(db, email):
        raise AuthError("Un cont cu această adresă de e-mail există deja.")
    user = User(
        email=email.lower(),
        hashed_password=hash_password(password),
        first_name=first_name.strip(),
        last_name=last_name.strip(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise AuthError("E-mail sau parolă incorectă.")
    if not user.is_active:
        raise AuthError("Contul este dezactivat.")
    return user


def issue_tokens(db: Session, user: User) -> tuple[str, str]:
    access_token, _, _ = create_token(
        str(user.id), "access", timedelta(minutes=settings.access_token_expire_minutes)
    )
    refresh_token, jti, expires_at = create_token(
        str(user.id), "refresh", timedelta(days=settings.refresh_token_expire_days)
    )
    db.add(RefreshToken(user_id=user.id, jti_hash=digest_jti(jti), expires_at=expires_at))
    db.commit()
    return access_token, refresh_token


def rotate_refresh_token(db: Session, raw_token: str) -> tuple[User, str, str]:
    try:
        payload = decode_token(raw_token, "refresh")
        user_id = uuid.UUID(payload["sub"])
    except (ValueError, TypeError) as exc:
        raise AuthError("Sesiunea nu mai este validă.") from exc

    stored = db.scalar(select(RefreshToken).where(RefreshToken.jti_hash == digest_jti(payload["jti"])))
    now = datetime.now(timezone.utc)
    if not stored or stored.revoked_at or stored.expires_at <= now:
        raise AuthError("Sesiunea nu mai este validă.")

    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise AuthError("Utilizatorul nu mai este activ.")

    stored.revoked_at = now
    access_token, refresh_token = issue_tokens(db, user)
    return user, access_token, refresh_token


def revoke_refresh_token(db: Session, raw_token: str | None) -> None:
    if not raw_token:
        return
    try:
        payload = decode_token(raw_token, "refresh")
    except ValueError:
        return
    stored = db.scalar(select(RefreshToken).where(RefreshToken.jti_hash == digest_jti(payload["jti"])))
    if stored and stored.revoked_at is None:
        stored.revoked_at = datetime.now(timezone.utc)
        db.commit()
