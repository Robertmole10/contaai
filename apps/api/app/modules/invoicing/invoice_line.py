import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class InvoiceLine(Base):
    __tablename__ = "invoice_lines"

    __table_args__ = (
        UniqueConstraint(
            "invoice_id",
            "position",
            name="uq_invoice_lines_invoice_position",
        ),
        CheckConstraint(
            "position >= 1",
            name="ck_invoice_lines_position_positive",
        ),
        CheckConstraint(
            "quantity > 0",
            name="ck_invoice_lines_quantity_positive",
        ),
        CheckConstraint(
            "unit_price >= 0",
            name="ck_invoice_lines_unit_price_non_negative",
        ),
        CheckConstraint(
            "vat_rate >= 0 AND vat_rate <= 100",
            name="ck_invoice_lines_vat_rate_range",
        ),
        CheckConstraint(
            "discount_percent >= 0 AND discount_percent <= 100",
            name="ck_invoice_lines_discount_percent_range",
        ),
        CheckConstraint(
            "net_amount >= 0",
            name="ck_invoice_lines_net_amount_non_negative",
        ),
        CheckConstraint(
            "vat_amount >= 0",
            name="ck_invoice_lines_vat_amount_non_negative",
        ),
        CheckConstraint(
            "gross_amount >= 0",
            name="ck_invoice_lines_gross_amount_non_negative",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    invoice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("invoices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    product_code: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )

    unit_of_measure: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="buc",
        server_default="buc",
    )

    quantity: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
        default=Decimal("1.0000"),
        server_default="1.0000",
    )

    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
        default=Decimal("0.0000"),
        server_default="0.0000",
    )

    vat_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("19.00"),
        server_default="19.00",
    )

    discount_percent: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("0.00"),
        server_default="0.00",
    )

    net_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
        server_default="0.00",
    )

    vat_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
        server_default="0.00",
    )

    gross_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
        server_default="0.00",
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

    invoice: Mapped["Invoice"] = relationship(
        back_populates="lines",
    )


from app.modules.invoicing.invoice import Invoice  # noqa: E402
