import uuid

from fastapi import status
from sqlalchemy import select

from app.main import app
from app.models.company import Company
from tests.helpers.auth import authenticate_client
from tests.helpers.factories import (
    create_membership,
    create_organization,
    create_user,
)


def company_url(organization_id: uuid.UUID) -> str:
    return str(
        app.url_path_for(
            "create_company",
            organization_id=str(organization_id),
        )
    )


def company_payload() -> dict[str, str]:
    unique = uuid.uuid4().hex[:10].upper()
    return {
        "name": f"Test Company {unique}",
        "tax_id": f"RO{unique}",
        "legal_form": "SRL",
        "country_code": "RO",
    }


def test_create_company_requires_authentication(client, db_session):
    organization = create_organization(db_session)

    response = client.post(
        company_url(organization.id),
        json=company_payload(),
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Autentificare necesară."


def test_create_company_rejects_invalid_token(client, db_session):
    organization = create_organization(db_session)
    client.cookies.set("access_token", "invalid-token")

    response = client.post(
        company_url(organization.id),
        json=company_payload(),
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Sesiune invalidă."


def test_create_company_hides_organization_from_non_member(
    client,
    db_session,
):
    user = create_user(db_session)
    organization = create_organization(db_session)
    authenticate_client(client, user)

    response = client.post(
        company_url(organization.id),
        json=company_payload(),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Organizația nu a fost găsită."


def test_accountant_cannot_create_company(client, db_session):
    user = create_user(db_session)
    organization = create_organization(db_session)
    create_membership(
        db_session,
        user=user,
        organization=organization,
        role_key="accountant",
    )
    authenticate_client(client, user)

    response = client.post(
        company_url(organization.id),
        json=company_payload(),
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == (
        "Nu ai permisiunea necesară pentru această acțiune."
    )


def test_owner_can_create_company(client, db_session):
    user = create_user(db_session)
    organization = create_organization(db_session)
    create_membership(
        db_session,
        user=user,
        organization=organization,
        role_key="owner",
    )
    authenticate_client(client, user)
    payload = company_payload()

    response = client.post(
        company_url(organization.id),
        json=payload,
    )

    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["name"] == payload["name"]
    assert body["tax_id"] == payload["tax_id"]
    assert body["legal_form"] == payload["legal_form"]
    assert body["country_code"] == payload["country_code"]

    company = db_session.scalar(
        select(Company).where(
            Company.organization_id == organization.id,
            Company.tax_id == payload["tax_id"],
        )
    )
    assert company is not None
    assert company.name == payload["name"]
    assert company.name_key


def test_admin_can_create_company(client, db_session):
    user = create_user(db_session)
    organization = create_organization(db_session)
    create_membership(
        db_session,
        user=user,
        organization=organization,
        role_key="admin",
    )
    authenticate_client(client, user)

    response = client.post(
        company_url(organization.id),
        json=company_payload(),
    )

    assert response.status_code == status.HTTP_201_CREATED


def test_member_of_another_organization_gets_not_found(
    client,
    db_session,
):
    user = create_user(db_session)
    accessible_organization = create_organization(db_session)
    inaccessible_organization = create_organization(db_session)
    create_membership(
        db_session,
        user=user,
        organization=accessible_organization,
        role_key="owner",
    )
    authenticate_client(client, user)

    response = client.post(
        company_url(inaccessible_organization.id),
        json=company_payload(),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Organizația nu a fost găsită."
