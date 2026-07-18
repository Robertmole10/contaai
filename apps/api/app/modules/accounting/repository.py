from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.orm import Session, selectinload

from app.modules.accounting.enums import (
    AccountingPeriodStatus,
    AccountNature,
    AccountSource,
    AccountType,
)
from app.modules.accounting.models import Account, AccountingPeriod


class AccountRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(
        self,
        *,
        account_id: UUID,
        company_id: UUID,
    ) -> Account | None:
        statement = select(Account).where(
            Account.id == account_id,
            Account.company_id == company_id,
        )

        return self.session.execute(statement).scalar_one_or_none()

    def get_by_id_with_children(
        self,
        *,
        account_id: UUID,
        company_id: UUID,
    ) -> Account | None:
        statement = (
            select(Account)
            .options(selectinload(Account.children))
            .where(
                Account.id == account_id,
                Account.company_id == company_id,
            )
        )

        return self.session.execute(statement).scalar_one_or_none()

    def get_by_code(
        self,
        *,
        company_id: UUID,
        code: str,
    ) -> Account | None:
        statement = select(Account).where(
            Account.company_id == company_id,
            Account.code == code,
        )

        return self.session.execute(statement).scalar_one_or_none()

    def list_by_company(
        self,
        *,
        company_id: UUID,
        offset: int = 0,
        limit: int = 100,
        is_active: bool | None = None,
        account_class: int | None = None,
        account_type: AccountType | None = None,
        parent_id: UUID | None = None,
        root_only: bool = False,
    ) -> list[Account]:
        statement: Select[tuple[Account]] = (
            select(Account)
            .where(Account.company_id == company_id)
            .order_by(Account.code.asc())
            .offset(offset)
            .limit(limit)
        )

        if is_active is not None:
            statement = statement.where(Account.is_active == is_active)

        if account_class is not None:
            statement = statement.where(
                Account.account_class == account_class
            )

        if account_type is not None:
            statement = statement.where(
                Account.account_type == account_type
            )

        if root_only:
            statement = statement.where(Account.parent_id.is_(None))
        elif parent_id is not None:
            statement = statement.where(Account.parent_id == parent_id)

        result = self.session.execute(statement)
        return list(result.scalars().all())

    def list_all_by_company(
        self,
        *,
        company_id: UUID,
        is_active: bool | None = None,
    ) -> list[Account]:
        statement: Select[tuple[Account]] = (
            select(Account)
            .where(Account.company_id == company_id)
            .order_by(Account.code.asc())
        )

        if is_active is not None:
            statement = statement.where(Account.is_active == is_active)

        result = self.session.execute(statement)
        return list(result.scalars().all())

    def list_children(
        self,
        *,
        company_id: UUID,
        parent_id: UUID,
    ) -> list[Account]:
        statement = (
            select(Account)
            .where(
                Account.company_id == company_id,
                Account.parent_id == parent_id,
            )
            .order_by(Account.code.asc())
        )

        result = self.session.execute(statement)
        return list(result.scalars().all())

    def has_children(
        self,
        *,
        company_id: UUID,
        account_id: UUID,
    ) -> bool:
        statement = (
            select(Account.id)
            .where(
                Account.company_id == company_id,
                Account.parent_id == account_id,
            )
            .limit(1)
        )

        return self.session.execute(statement).scalar_one_or_none() is not None

    def create(
        self,
        *,
        company_id: UUID,
        code: str,
        name: str,
        account_class: int,
        account_type: AccountType,
        nature: AccountNature,
        parent_id: UUID | None = None,
        source: AccountSource = AccountSource.MANUAL,
        allows_posting: bool = True,
        is_analytic: bool = False,
        is_active: bool = True,
    ) -> Account:
        account = Account(
            company_id=company_id,
            parent_id=parent_id,
            code=code,
            name=name,
            account_class=account_class,
            account_type=account_type,
            nature=nature,
            source=source,
            allows_posting=allows_posting,
            is_analytic=is_analytic,
            is_active=is_active,
        )

        self.session.add(account)
        self.session.flush()
        self.session.refresh(account)

        return account

    def update(
        self,
        *,
        account: Account,
        values: dict[str, object],
    ) -> Account:
        for field, value in values.items():
            setattr(account, field, value)

        self.session.flush()
        self.session.refresh(account)

        return account

    def delete(self, *, account: Account) -> None:
        self.session.delete(account)
        self.session.flush()


class AccountingPeriodRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(
        self,
        *,
        period_id: UUID,
        company_id: UUID,
    ) -> AccountingPeriod | None:
        statement = select(AccountingPeriod).where(
            AccountingPeriod.id == period_id,
            AccountingPeriod.company_id == company_id,
        )

        return self.session.execute(statement).scalar_one_or_none()

    def get_by_year_month(
        self,
        *,
        company_id: UUID,
        year: int,
        month: int,
    ) -> AccountingPeriod | None:
        statement = select(AccountingPeriod).where(
            AccountingPeriod.company_id == company_id,
            AccountingPeriod.year == year,
            AccountingPeriod.month == month,
        )

        return self.session.execute(statement).scalar_one_or_none()

    def get_for_date(
        self,
        *,
        company_id: UUID,
        target_date: date,
    ) -> AccountingPeriod | None:
        statement = select(AccountingPeriod).where(
            AccountingPeriod.company_id == company_id,
            AccountingPeriod.start_date <= target_date,
            AccountingPeriod.end_date >= target_date,
        )

        return self.session.execute(statement).scalar_one_or_none()

    def list_by_company(
        self,
        *,
        company_id: UUID,
        offset: int = 0,
        limit: int = 100,
        year: int | None = None,
        status: AccountingPeriodStatus | None = None,
    ) -> list[AccountingPeriod]:
        statement: Select[tuple[AccountingPeriod]] = (
            select(AccountingPeriod)
            .where(AccountingPeriod.company_id == company_id)
            .order_by(
                AccountingPeriod.year.desc(),
                AccountingPeriod.month.desc(),
            )
            .offset(offset)
            .limit(limit)
        )

        if year is not None:
            statement = statement.where(AccountingPeriod.year == year)

        if status is not None:
            statement = statement.where(AccountingPeriod.status == status)

        result = self.session.execute(statement)
        return list(result.scalars().all())

    def create(
        self,
        *,
        company_id: UUID,
        year: int,
        month: int,
        start_date: date,
        end_date: date,
        status: AccountingPeriodStatus = AccountingPeriodStatus.OPEN,
        closed_at: datetime | None = None,
    ) -> AccountingPeriod:
        period = AccountingPeriod(
            company_id=company_id,
            year=year,
            month=month,
            start_date=start_date,
            end_date=end_date,
            status=status,
            closed_at=closed_at,
        )

        self.session.add(period)
        self.session.flush()
        self.session.refresh(period)

        return period

    def update(
        self,
        *,
        period: AccountingPeriod,
        values: dict[str, object],
    ) -> AccountingPeriod:
        for field, value in values.items():
            setattr(period, field, value)

        self.session.flush()
        self.session.refresh(period)

        return period

    def delete(self, *, period: AccountingPeriod) -> None:
        self.session.delete(period)
        self.session.flush()