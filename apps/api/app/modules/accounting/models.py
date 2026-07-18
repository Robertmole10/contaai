import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.modules.accounting.enums import (
    AccountingPeriodStatus,
    AccountNature,
    AccountSource,
    AccountType,
)


class Account(Base):
    __tablename__ = "accounts"

    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "code",
            name="uq_accounts_company_code",
        ),
        CheckConstraint(
            "char_length(code) >= 1",
            name="ck_accounts_code_not_empty",
        ),
        CheckConstraint(
            "account_class >= 1 AND account_class <= 9",
            name="ck_accounts_class_range",
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

    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    code: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    account_class: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    account_type: Mapped[AccountType] = mapped_column(
        Enum(
            AccountType,
            values_callable=lambda enum_class: [
                item.value for item in enum_class
            ],
            name="account_type",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        nullable=False,
        index=True,
    )

    nature: Mapped[AccountNature] = mapped_column(
        Enum(
            AccountNature,
            values_callable=lambda enum_class: [
                item.value for item in enum_class
            ],
            name="account_nature",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        nullable=False,
    )

    source: Mapped[AccountSource] = mapped_column(
        Enum(
            AccountSource,
            values_callable=lambda enum_class: [
                item.value for item in enum_class
            ],
            name="account_source",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        nullable=False,
        default=AccountSource.MANUAL,
        server_default=AccountSource.MANUAL.value,
    )

    allows_posting: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    is_analytic: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
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
        back_populates="accounts",
    )

    parent: Mapped["Account | None"] = relationship(
        remote_side="Account.id",
        back_populates="children",
    )

    children: Mapped[list["Account"]] = relationship(
        back_populates="parent",
    )


class AccountingPeriod(Base):
    __tablename__ = "accounting_periods"

    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "year",
            "month",
            name="uq_accounting_periods_company_year_month",
        ),
        CheckConstraint(
            "month >= 1 AND month <= 12",
            name="ck_accounting_periods_month_range",
        ),
        CheckConstraint(
            "year >= 2000 AND year <= 2200",
            name="ck_accounting_periods_year_range",
        ),
        CheckConstraint(
            "start_date <= end_date",
            name="ck_accounting_periods_date_range",
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

    year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    month: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    end_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    status: Mapped[AccountingPeriodStatus] = mapped_column(
        Enum(
            AccountingPeriodStatus,
            values_callable=lambda enum_class: [
                item.value for item in enum_class
            ],
            name="accounting_period_status",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        nullable=False,
        default=AccountingPeriodStatus.OPEN,
        server_default=AccountingPeriodStatus.OPEN.value,
        index=True,
    )

    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
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
        back_populates="accounting_periods",
    )


from app.models.company import Company  # noqa: E402