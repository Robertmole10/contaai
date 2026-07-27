from datetime import timedelta

from fastapi.testclient import TestClient

from app.core.security import create_token
from app.models.user import User


def access_token_for_user(user: User) -> str:
    token, _, _ = create_token(
        subject=str(user.id),
        token_type="access",
        expires_delta=timedelta(minutes=15),
    )
    return token


def authenticate_client(
    client: TestClient,
    user: User,
) -> TestClient:
    client.cookies.set(
        "access_token",
        access_token_for_user(user),
    )
    return client
