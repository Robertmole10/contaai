from enum import Enum


class AccountType(str, Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    INCOME = "income"
    EXPENSE = "expense"
    OFF_BALANCE = "off_balance"


class AccountNature(str, Enum):
    DEBIT = "debit"
    CREDIT = "credit"
    BIFUNCTIONAL = "bifunctional"


class AccountSource(str, Enum):
    TEMPLATE = "template"
    MANUAL = "manual"
    IMPORTED = "imported"


class AccountingPeriodStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    LOCKED = "locked"