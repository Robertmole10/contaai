import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.modules.invoicing.enums import InvoiceStatus, InvoiceType


class Invoice(Base):
    __tablename__ = "invoices"

    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "invoice_type",
            "series",
            "number",
            name="uq_invoices_company_type_series_number",
        ),
        CheckConstraint(
            "char_length(series) >= 1",
            name="ck_invoices_series_not_empty",
        ),
        CheckConstraint(
            "char_length(number) >= 1",
            name="ck_invoices_number_not_empty",
        ),
        CheckConstraint(
            "due_date >= issue_date",
            name="ck_invoices_due_date_after_issue_date",
        ),
        CheckConstraint(
            "exchange_rate > 0",
            name="ck_invoices_exchange_rate_positive",
        ),
        CheckConstraint(
            "subtotal >= 0",
            name="ck_invoices_subtotal_non_negative",
        ),
        CheckConstraint(
            "vat_total >= 0",
            name="ck_invoices_vat_total_non_negative",
        ),
        CheckConstraint(
            "total >= 0",
            name="ck_invoices_total_non_negative",
        ),
        CheckConstraint(
            "paid_amount >= 0",
            name="ck_invoices_paid_amount_non_negative",
        ),
        CheckConstraint(
            "paid_amount <= total",
            name="ck_invoices_paid_amount_not_over_total",
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

    business_partner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("business_partners.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    invoice_type: Mapped[InvoiceType] = mapped_column(
        Enum(
            InvoiceType,
            values_callable=lambda enum_class: [
                item.value for item in enum_class
            ],
            name="invoice_type",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        nullable=False,
        default=InvoiceType.SALES,
        server_default=InvoiceType.SALES.value,
        index=True,
    )

    status: Mapped[InvoiceStatus] = mapped_column(
        Enum(
            InvoiceStatus,
            values_callable=lambda enum_class: [
                item.value for item in enum_class
            ],
            name="invoice_status",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        nullable=False,
        default=InvoiceStatus.DRAFT,
        server_default=InvoiceStatus.DRAFT.value,
        index=True,
    )

    series: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="INV",
        server_default="INV",
    )

    number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    issue_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        default=date.today,
        index=True,
    )

    due_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="RON",
        server_default="RON",
    )

    exchange_rate: Mapped[Decimal] = mapped_column(
        Numeric(18, 6),
        nullable=False,
        default=Decimal("1.000000"),
        server_default="1.000000",
    )

    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
        server_default="0.00",
    )

    vat_total: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
        server_default="0.00",
    )

    total: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
        server_default="0.00",
    )

    paid_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
        server_default="0.00",
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
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
        back_populates="invoices",
    )

    business_partner: Mapped["BusinessPartner"] = relationship(
        back_populates="invoices",
    )

    lines: Mapped[list["InvoiceLine"]] = relationship(
        back_populates="invoice",
        cascade="all, delete-orphan",
        order_by="InvoiceLine.position",
    )


from app.models.company import Company  # noqa: E402
from app.modules.invoicing.business_partner import BusinessPartner  # noqa: E402
from app.modules.invoicing.invoice_line import InvoiceLine  # noqa: E402
