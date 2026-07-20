from __future__ import annotations

from uuid import UUID

from sqlalchemy import Select, or_, select
from sqlalchemy.orm import Session

from app.modules.invoicing.business_partner import BusinessPartner
from app.modules.invoicing.invoice import Invoice
from app.modules.invoicing.invoice_line import InvoiceLine


class BusinessPartnerRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(
        self,
        *,
        partner_id: UUID,
        company_id: UUID,
    ) -> BusinessPartner | None:
        statement = select(BusinessPartner).where(
            BusinessPartner.id == partner_id,
            BusinessPartner.company_id == company_id,
        )

        return self.session.execute(statement).scalar_one_or_none()

    def get_by_tax_id(
        self,
        *,
        company_id: UUID,
        tax_id: str,
    ) -> BusinessPartner | None:
        statement = select(BusinessPartner).where(
            BusinessPartner.company_id == company_id,
            BusinessPartner.tax_id == tax_id,
        )

        return self.session.execute(statement).scalar_one_or_none()

    def list_by_company(
        self,
        *,
        company_id: UUID,
        offset: int = 0,
        limit: int = 50,
        active_only: bool = True,
    ) -> list[BusinessPartner]:
        statement: Select[tuple[BusinessPartner]] = (
            select(BusinessPartner)
            .where(BusinessPartner.company_id == company_id)
            .order_by(BusinessPartner.name.asc())
            .offset(offset)
            .limit(limit)
        )

        if active_only:
            statement = statement.where(
                BusinessPartner.is_active.is_(True)
            )

        return list(self.session.execute(statement).scalars().all())

    def search(
        self,
        *,
        company_id: UUID,
        query: str,
        limit: int = 20,
    ) -> list[BusinessPartner]:
        pattern = f"%{query}%"

        statement: Select[tuple[BusinessPartner]] = (
            select(BusinessPartner)
            .where(BusinessPartner.company_id == company_id)
            .where(
                or_(
                    BusinessPartner.name.ilike(pattern),
                    BusinessPartner.tax_id.ilike(pattern),
                )
            )
            .order_by(BusinessPartner.name.asc())
            .limit(limit)
        )

        return list(self.session.execute(statement).scalars().all())


class InvoiceRepository:
    def __init__(self, session: Session) -> None:
        self.session = session


class InvoiceLineRepository:
    def __init__(self, session: Session) -> None:
        self.session = session