import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.modules.invoicing.enums import BusinessPartnerType


class BusinessPartner(Base):
    __tablename__ = "business_partners"

    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "name_key",
            "tax_id",
            name="uq_business_partners_company_name_tax_id",
        ),
        CheckConstraint(
            "char_length(name) >= 1",
            name="ck_business_partners_name_not_empty",
        ),
        CheckConstraint(
            "char_length(country_code) = 2",
            name="ck_business_partners_country_code_length",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    partner_type: Mapped[BusinessPartnerType] = mapped_column(
        Enum(
            BusinessPartnerType,
            values_callable=lambda enum_class: [
                item.value for item in enum_class
            ],
            name="business_partner_type",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        nullable=False,
        default=BusinessPartnerType.CUSTOMER,
        server_default=BusinessPartnerType.CUSTOMER.value,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    name_key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    tax_id: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
        index=True,
    )

    registration_number: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    country_code: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        default="RO",
        server_default="RO",
    )

    address: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    city: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    county: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    postal_code: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    iban: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    payment_term_days: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    company: Mapped["Company"] = relationship(
        back_populates="business_partners",
    )


from app.models.company import Company  # noqa: E402