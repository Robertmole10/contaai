from __future__ import annotations

from sqlalchemy.orm import Session

from app.modules.invoicing.repository import BusinessPartnerRepository


class BusinessPartnerService:
    def __init__(
        self,
        *,
        session: Session,
    ) -> None:
        self.session = session
        self.repository = BusinessPartnerRepository(session)