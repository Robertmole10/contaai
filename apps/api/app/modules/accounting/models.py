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
from decimal import Decimal
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.modules.accounting.enums import (
    AccountingPeriodStatus,
    AccountNature,
    AccountSource,
    AccountType,
    JournalEntrySource,
    JournalEntryStatus,
    JournalOriginType,
)
from app.db.types import ExchangeRate, ForeignAmount, Money


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
    journal_lines: Mapped[list["JournalEntryLine"]] = relationship(
        back_populates="account",
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

    journal_entries: Mapped[list["JournalEntry"]] = relationship(
      back_populates="accounting_period",
      
    )

class JournalEntry(Base):
    __tablename__ = "journal_entries"

    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "fiscal_year",
            "sequence",
            name="uq_journal_entries_company_year_sequence",
        ),
        UniqueConstraint(
            "company_id",
            "display_number",
            name="uq_journal_entries_company_display_number",
        ),
        CheckConstraint(
            "fiscal_year >= 2000 AND fiscal_year <= 2200",
            name="ck_journal_entries_fiscal_year_range",
        ),
        CheckConstraint(
            "sequence >= 1",
            name="ck_journal_entries_sequence_positive",
        ),
        CheckConstraint(
            "char_length(display_number) >= 1",
            name="ck_journal_entries_display_number_not_empty",
        ),
        CheckConstraint(
            "char_length(currency_code) = 3",
            name="ck_journal_entries_currency_code_length",
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

    accounting_period_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounting_periods.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    fiscal_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    sequence: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    display_number: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    entry_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    document_number: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        index=True,
    )

    reference: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    currency_code: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="RON",
        server_default="RON",
    )

    status: Mapped[JournalEntryStatus] = mapped_column(
        Enum(
            JournalEntryStatus,
            values_callable=lambda enum_class: [
                item.value for item in enum_class
            ],
            name="journal_entry_status",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        nullable=False,
        default=JournalEntryStatus.DRAFT,
        server_default=JournalEntryStatus.DRAFT.value,
        index=True,
    )

    source: Mapped[JournalEntrySource] = mapped_column(
        Enum(
            JournalEntrySource,
            values_callable=lambda enum_class: [
                item.value for item in enum_class
            ],
            name="journal_entry_source",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        nullable=False,
        default=JournalEntrySource.MANUAL,
        server_default=JournalEntrySource.MANUAL.value,
        index=True,
    )

    origin_type: Mapped[JournalOriginType] = mapped_column(
        Enum(
            JournalOriginType,
            values_callable=lambda enum_class: [
                item.value for item in enum_class
            ],
            name="journal_origin_type",
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        nullable=False,
        default=JournalOriginType.MANUAL,
        server_default=JournalOriginType.MANUAL.value,
        index=True,
    )

    origin_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
    )

    is_system_generated: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    created_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    updated_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
    )

    posted_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
    )

    posted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    reversed_entry_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("journal_entries.id", ondelete="RESTRICT"),
        nullable=True,
        unique=True,
    )

    deleted_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
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
        back_populates="journal_entries",
    )

    accounting_period: Mapped["AccountingPeriod"] = relationship(
        back_populates="journal_entries",
    )

    lines: Mapped[list["JournalEntryLine"]] = relationship(
        back_populates="journal_entry",
        cascade="all, delete-orphan",
        order_by="JournalEntryLine.line_number",
    )

    reversed_entry: Mapped["JournalEntry | None"] = relationship(
        remote_side="JournalEntry.id",
        foreign_keys=[reversed_entry_id],
        back_populates="reversal_entry",
    )

    reversal_entry: Mapped["JournalEntry | None"] = relationship(
        foreign_keys="JournalEntry.reversed_entry_id",
        back_populates="reversed_entry",
        uselist=False,
    )


class JournalEntryLine(Base):
    __tablename__ = "journal_entry_lines"

    __table_args__ = (
        UniqueConstraint(
            "journal_entry_id",
            "line_number",
            name="uq_journal_entry_lines_entry_line_number",
        ),
        CheckConstraint(
            "line_number >= 1",
            name="ck_journal_entry_lines_line_number_positive",
        ),
        CheckConstraint(
            "debit >= 0",
            name="ck_journal_entry_lines_debit_non_negative",
        ),
        CheckConstraint(
            "credit >= 0",
            name="ck_journal_entry_lines_credit_non_negative",
        ),
        CheckConstraint(
            "NOT (debit > 0 AND credit > 0)",
            name="ck_journal_entry_lines_not_both_debit_credit",
        ),
        CheckConstraint(
            "char_length(currency_code) = 3",
            name="ck_journal_entry_lines_currency_code_length",
        ),
        CheckConstraint(
            "exchange_rate > 0",
            name="ck_journal_entry_lines_exchange_rate_positive",
        ),
        CheckConstraint(
            "foreign_amount >= 0",
            name="ck_journal_entry_lines_foreign_amount_non_negative",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    journal_entry_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("journal_entries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    line_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    currency_code: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="RON",
        server_default="RON",
    )

    foreign_amount: Mapped[Decimal] = mapped_column(
        ForeignAmount,
        nullable=False,
        default=Decimal("0"),
        server_default="0",
    )

    exchange_rate: Mapped[Decimal] = mapped_column(
        ExchangeRate,
        nullable=False,
        default=Decimal("1"),
        server_default="1",
    )

    debit: Mapped[Decimal] = mapped_column(
        Money,
        nullable=False,
        default=Decimal("0"),
        server_default="0",
    )

    credit: Mapped[Decimal] = mapped_column(
        Money,
        nullable=False,
        default=Decimal("0"),
        server_default="0",
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

    journal_entry: Mapped["JournalEntry"] = relationship(
        back_populates="lines",
    )

    account: Mapped["Account"] = relationship(
        back_populates="journal_lines",
    )

from app.models.company import Company  # noqa: E402