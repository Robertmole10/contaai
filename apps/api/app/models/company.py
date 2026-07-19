import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    name_key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Se salvează întotdeauna fără prefixul RO.
    tax_id: Mapped[str | None] = mapped_column(

        String(20),
        nullable=True,
        index=True,
    )

    is_vat_payer: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    legal_form: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    country_code: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        default="RO",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    @property
    def display_tax_id(self) -> str | None:
        if not self.tax_id:
            return None

        if self.is_vat_payer:
            return f"RO{self.tax_id}"

        return self.tax_id

    organization: Mapped["Organization"] = relationship(
        back_populates="companies"
    )

    
    accounts: Mapped[list["Account"]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
    )

    accounting_periods: Mapped[list["AccountingPeriod"]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
    )
    journal_entries: Mapped[list["JournalEntry"]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
    )
    business_partners: Mapped[list["BusinessPartner"]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
    )

from app.modules.accounting.models import (  # noqa: E402
    Account,
    AccountingPeriod,
    JournalEntry,
)
from app.modules.invoicing.models import BusinessPartner  # noqa: E402
