from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.accounting.enums import AccountingPeriodStatus
from app.modules.accounting.models import Account, AccountingPeriod
from app.modules.accounting.repository import (
    AccountingPeriodRepository,
    AccountRepository,
)
from app.modules.accounting.schemas import (
    AccountingPeriodCreate,
    AccountingPeriodUpdate,
    AccountCreate,
    AccountUpdate,
)


class AccountingServiceError(Exception):
    """Base exception for accounting service operations."""


class AccountNotFoundError(AccountingServiceError):
    """Raised when an account cannot be found."""


class AccountAlreadyExistsError(AccountingServiceError):
    """Raised when an account code already exists for the company."""


class ParentAccountNotFoundError(AccountingServiceError):
    """Raised when the requested parent account cannot be found."""


class InvalidAccountHierarchyError(AccountingServiceError):
    """Raised when an account hierarchy operation is invalid."""


class AccountHasChildrenError(AccountingServiceError):
    """Raised when deleting an account that still has children."""


class AccountPersistenceError(AccountingServiceError):
    """Raised when an account cannot be persisted."""


class AccountingPeriodNotFoundError(AccountingServiceError):
    """Raised when an accounting period cannot be found."""


class AccountingPeriodAlreadyExistsError(AccountingServiceError):
    """Raised when the same company, year, and month already exist."""


class InvalidAccountingPeriodError(AccountingServiceError):
    """Raised when accounting period dates or status are invalid."""


class AccountingPeriodLockedError(AccountingServiceError):
    """Raised when a locked accounting period is modified."""


class AccountingPeriodPersistenceError(AccountingServiceError):
    """Raised when an accounting period cannot be persisted."""


class AccountService:
    def __init__(self, *, session: Session) -> None:
        self.session = session
        self.repository = AccountRepository(session)

    def get_account(
        self,
        *,
        account_id: UUID,
        company_id: UUID,
    ) -> Account:
        account = self.repository.get_by_id(
            account_id=account_id,
            company_id=company_id,
        )

        if account is None:
            raise AccountNotFoundError("Account not found.")

        return account

    def list_accounts(
        self,
        *,
        company_id: UUID,
        offset: int = 0,
        limit: int = 100,
        is_active: bool | None = None,
        account_class: int | None = None,
        parent_id: UUID | None = None,
        root_only: bool = False,
    ) -> list[Account]:
        return self.repository.list_by_company(
            company_id=company_id,
            offset=offset,
            limit=limit,
            is_active=is_active,
            account_class=account_class,
            parent_id=parent_id,
            root_only=root_only,
        )

    def create_account(
        self,
        *,
        company_id: UUID,
        payload: AccountCreate,
    ) -> Account:
        normalized_code = payload.code.strip()
        normalized_name = payload.name.strip()

        if not normalized_code:
            raise InvalidAccountHierarchyError(
                "Account code cannot be empty."
            )

        if not normalized_name:
            raise InvalidAccountHierarchyError(
                "Account name cannot be empty."
            )

        existing_account = self.repository.get_by_code(
            company_id=company_id,
            code=normalized_code,
        )

        if existing_account is not None:
            raise AccountAlreadyExistsError(
                "An account with this code already exists."
            )

        parent = self._get_and_validate_parent(
            company_id=company_id,
            parent_id=payload.parent_id,
        )

        self._validate_posting_rules(
            is_analytic=payload.is_analytic,
            allows_posting=payload.allows_posting,
        )

        if parent is not None:
            self._validate_parent_compatibility(
                parent=parent,
                account_class=payload.account_class,
            )

        try:
            account = self.repository.create(
                company_id=company_id,
                parent_id=payload.parent_id,
                code=normalized_code,
                name=normalized_name,
                account_class=payload.account_class,
                account_type=payload.account_type,
                nature=payload.nature,
                source=payload.source,
                allows_posting=payload.allows_posting,
                is_analytic=payload.is_analytic,
                is_active=payload.is_active,
            )

            self.session.commit()
            self.session.refresh(account)

            return account

        except IntegrityError as exc:
            self.session.rollback()

            raise AccountAlreadyExistsError(
                "The account conflicts with an existing record."
            ) from exc

        except AccountingServiceError:
            self.session.rollback()
            raise

        except Exception as exc:
            self.session.rollback()

            raise AccountPersistenceError(
                "The account could not be saved."
            ) from exc

    def update_account(
        self,
        *,
        account_id: UUID,
        company_id: UUID,
        payload: AccountUpdate,
    ) -> Account:
        account = self.get_account(
            account_id=account_id,
            company_id=company_id,
        )

        values = payload.model_dump(exclude_unset=True)

        if not values:
            return account

        if "code" in values:
            normalized_code = str(values["code"]).strip()

            if not normalized_code:
                raise InvalidAccountHierarchyError(
                    "Account code cannot be empty."
                )

            existing_account = self.repository.get_by_code(
                company_id=company_id,
                code=normalized_code,
            )

            if (
                existing_account is not None
                and existing_account.id != account.id
            ):
                raise AccountAlreadyExistsError(
                    "An account with this code already exists."
                )

            values["code"] = normalized_code

        if "name" in values:
            normalized_name = str(values["name"]).strip()

            if not normalized_name:
                raise InvalidAccountHierarchyError(
                    "Account name cannot be empty."
                )

            values["name"] = normalized_name

        parent_id_supplied = "parent_id" in values

        if parent_id_supplied:
            parent_id = values["parent_id"]

            if parent_id == account.id:
                raise InvalidAccountHierarchyError(
                    "An account cannot be its own parent."
                )

            parent = self._get_and_validate_parent(
                company_id=company_id,
                parent_id=parent_id,
            )

            if parent is not None:
                self._validate_no_cycle(
                    account=account,
                    proposed_parent=parent,
                    company_id=company_id,
                )

                target_class = int(
                    values.get("account_class", account.account_class)
                )

                self._validate_parent_compatibility(
                    parent=parent,
                    account_class=target_class,
                )

        elif "account_class" in values and account.parent_id is not None:
            parent = self.repository.get_by_id(
                account_id=account.parent_id,
                company_id=company_id,
            )

            if parent is not None:
                self._validate_parent_compatibility(
                    parent=parent,
                    account_class=int(values["account_class"]),
                )

        target_is_analytic = bool(
            values.get("is_analytic", account.is_analytic)
        )
        target_allows_posting = bool(
            values.get("allows_posting", account.allows_posting)
        )

        self._validate_posting_rules(
            is_analytic=target_is_analytic,
            allows_posting=target_allows_posting,
        )

        try:
            updated_account = self.repository.update(
                account=account,
                values=values,
            )

            self.session.commit()
            self.session.refresh(updated_account)

            return updated_account

        except IntegrityError as exc:
            self.session.rollback()

            raise AccountAlreadyExistsError(
                "The account conflicts with an existing record."
            ) from exc

        except AccountingServiceError:
            self.session.rollback()
            raise

        except Exception as exc:
            self.session.rollback()

            raise AccountPersistenceError(
                "The account could not be updated."
            ) from exc

    def delete_account(
        self,
        *,
        account_id: UUID,
        company_id: UUID,
    ) -> None:
        account = self.get_account(
            account_id=account_id,
            company_id=company_id,
        )

        if self.repository.has_children(
            company_id=company_id,
            account_id=account.id,
        ):
            raise AccountHasChildrenError(
                "An account with child accounts cannot be deleted."
            )

        try:
            self.repository.delete(account=account)
            self.session.commit()

        except IntegrityError as exc:
            self.session.rollback()

            raise AccountPersistenceError(
                "The account is referenced by other records and cannot be deleted."
            ) from exc

        except Exception as exc:
            self.session.rollback()

            raise AccountPersistenceError(
                "The account could not be deleted."
            ) from exc

    def build_account_tree(
        self,
        *,
        company_id: UUID,
        is_active: bool | None = None,
    ) -> list[dict[str, object]]:
        accounts = self.repository.list_all_by_company(
            company_id=company_id,
            is_active=is_active,
        )

        nodes: dict[UUID, dict[str, object]] = {}

        for account in accounts:
            nodes[account.id] = {
                "id": account.id,
                "company_id": account.company_id,
                "parent_id": account.parent_id,
                "code": account.code,
                "name": account.name,
                "account_class": account.account_class,
                "account_type": account.account_type,
                "nature": account.nature,
                "source": account.source,
                "allows_posting": account.allows_posting,
                "is_analytic": account.is_analytic,
                "is_active": account.is_active,
                "created_at": account.created_at,
                "updated_at": account.updated_at,
                "children": [],
            }

        roots: list[dict[str, object]] = []

        for account in accounts:
            node = nodes[account.id]

            if account.parent_id is None:
                roots.append(node)
                continue

            parent_node = nodes.get(account.parent_id)

            if parent_node is None:
                roots.append(node)
                continue

            children = parent_node["children"]
            assert isinstance(children, list)
            children.append(node)

        return roots

    def _get_and_validate_parent(
        self,
        *,
        company_id: UUID,
        parent_id: object,
    ) -> Account | None:
        if parent_id is None:
            return None

        if not isinstance(parent_id, UUID):
            raise InvalidAccountHierarchyError(
                "Invalid parent account identifier."
            )

        parent = self.repository.get_by_id(
            account_id=parent_id,
            company_id=company_id,
        )

        if parent is None:
            raise ParentAccountNotFoundError(
                "Parent account not found for this company."
            )

        return parent

    def _validate_no_cycle(
        self,
        *,
        account: Account,
        proposed_parent: Account,
        company_id: UUID,
    ) -> None:
        current: Account | None = proposed_parent
        visited: set[UUID] = set()

        while current is not None:
            if current.id == account.id:
                raise InvalidAccountHierarchyError(
                    "The selected parent would create an account hierarchy cycle."
                )

            if current.id in visited:
                raise InvalidAccountHierarchyError(
                    "The existing account hierarchy already contains a cycle."
                )

            visited.add(current.id)

            if current.parent_id is None:
                break

            current = self.repository.get_by_id(
                account_id=current.parent_id,
                company_id=company_id,
            )

    @staticmethod
    def _validate_parent_compatibility(
        *,
        parent: Account,
        account_class: int,
    ) -> None:
        if parent.account_class != account_class:
            raise InvalidAccountHierarchyError(
                "A child account must belong to the same account class as its parent."
            )

    @staticmethod
    def _validate_posting_rules(
        *,
        is_analytic: bool,
        allows_posting: bool,
    ) -> None:
        if allows_posting and not is_analytic:
            raise InvalidAccountHierarchyError(
                "Only analytic accounts may allow journal posting."
            )


class AccountingPeriodService:
    def __init__(self, *, session: Session) -> None:
        self.session = session
        self.repository = AccountingPeriodRepository(session)

    def get_period(
        self,
        *,
        period_id: UUID,
        company_id: UUID,
    ) -> AccountingPeriod:
        period = self.repository.get_by_id(
            period_id=period_id,
            company_id=company_id,
        )

        if period is None:
            raise AccountingPeriodNotFoundError(
                "Accounting period not found."
            )

        return period

    def list_periods(
        self,
        *,
        company_id: UUID,
        offset: int = 0,
        limit: int = 100,
        year: int | None = None,
        status: AccountingPeriodStatus | None = None,
    ) -> list[AccountingPeriod]:
        return self.repository.list_by_company(
            company_id=company_id,
            offset=offset,
            limit=limit,
            year=year,
            status=status,
        )

    def create_period(
        self,
        *,
        company_id: UUID,
        payload: AccountingPeriodCreate,
    ) -> AccountingPeriod:
        self._validate_date_range(
            start_date=payload.start_date,
            end_date=payload.end_date,
        )

        existing_period = self.repository.get_by_year_month(
            company_id=company_id,
            year=payload.year,
            month=payload.month,
        )

        if existing_period is not None:
            raise AccountingPeriodAlreadyExistsError(
                "An accounting period already exists for this year and month."
            )

        closed_at = self._resolve_closed_at(
            status=payload.status,
            current_closed_at=None,
        )

        try:
            period = self.repository.create(
                company_id=company_id,
                year=payload.year,
                month=payload.month,
                start_date=payload.start_date,
                end_date=payload.end_date,
                status=payload.status,
                closed_at=closed_at,
            )

            self.session.commit()
            self.session.refresh(period)

            return period

        except IntegrityError as exc:
            self.session.rollback()

            raise AccountingPeriodAlreadyExistsError(
                "The accounting period conflicts with an existing record."
            ) from exc

        except AccountingServiceError:
            self.session.rollback()
            raise

        except Exception as exc:
            self.session.rollback()

            raise AccountingPeriodPersistenceError(
                "The accounting period could not be saved."
            ) from exc

    def update_period(
        self,
        *,
        period_id: UUID,
        company_id: UUID,
        payload: AccountingPeriodUpdate,
    ) -> AccountingPeriod:
        period = self.get_period(
            period_id=period_id,
            company_id=company_id,
        )

        if period.status == AccountingPeriodStatus.LOCKED:
            raise AccountingPeriodLockedError(
                "A locked accounting period cannot be modified."
            )

        values = payload.model_dump(exclude_unset=True)

        if not values:
            return period

        target_start_date = values.get(
            "start_date",
            period.start_date,
        )
        target_end_date = values.get(
            "end_date",
            period.end_date,
        )

        self._validate_date_range(
            start_date=target_start_date,
            end_date=target_end_date,
        )

        if "status" in values:
            target_status = values["status"]

            if not isinstance(target_status, AccountingPeriodStatus):
                raise InvalidAccountingPeriodError(
                    "Invalid accounting period status."
                )

            self._validate_status_transition(
                current_status=period.status,
                target_status=target_status,
            )

            values["closed_at"] = self._resolve_closed_at(
                status=target_status,
                current_closed_at=period.closed_at,
            )

        try:
            updated_period = self.repository.update(
                period=period,
                values=values,
            )

            self.session.commit()
            self.session.refresh(updated_period)

            return updated_period

        except IntegrityError as exc:
            self.session.rollback()

            raise AccountingPeriodPersistenceError(
                "The accounting period conflicts with an existing record."
            ) from exc

        except AccountingServiceError:
            self.session.rollback()
            raise

        except Exception as exc:
            self.session.rollback()

            raise AccountingPeriodPersistenceError(
                "The accounting period could not be updated."
            ) from exc

    @staticmethod
    def _validate_date_range(
        *,
        start_date: object,
        end_date: object,
    ) -> None:
        if start_date > end_date:
            raise InvalidAccountingPeriodError(
                "The accounting period start date must be before or equal to the end date."
            )

    @staticmethod
    def _validate_status_transition(
        *,
        current_status: AccountingPeriodStatus,
        target_status: AccountingPeriodStatus,
    ) -> None:
        allowed_transitions = {
            AccountingPeriodStatus.OPEN: {
                AccountingPeriodStatus.OPEN,
                AccountingPeriodStatus.CLOSED,
                AccountingPeriodStatus.LOCKED,
            },
            AccountingPeriodStatus.CLOSED: {
                AccountingPeriodStatus.OPEN,
                AccountingPeriodStatus.CLOSED,
                AccountingPeriodStatus.LOCKED,
            },
            AccountingPeriodStatus.LOCKED: {
                AccountingPeriodStatus.LOCKED,
            },
        }

        if target_status not in allowed_transitions[current_status]:
            raise InvalidAccountingPeriodError(
                f"Invalid accounting period transition from "
                f"{current_status.value} to {target_status.value}."
            )

    @staticmethod
    def _resolve_closed_at(
        *,
        status: AccountingPeriodStatus,
        current_closed_at: datetime | None,
    ) -> datetime | None:
        if status in {
            AccountingPeriodStatus.CLOSED,
            AccountingPeriodStatus.LOCKED,
        }:
            return current_closed_at or datetime.now(timezone.utc)

        return None