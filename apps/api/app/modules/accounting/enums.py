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

class JournalEntryStatus(str, Enum):
    DRAFT = "draft"
    POSTED = "posted"
    REVERSED = "reversed"


class JournalEntrySource(str, Enum):
    MANUAL = "manual"
    DOCUMENT = "document"
    IMPORT = "import"
    AI = "ai"
    REVERSAL = "reversal"

class JournalOriginType(str, Enum):
    MANUAL = "manual"
    DOCUMENT = "document"
    BANK_STATEMENT = "bank_statement"
    PAYROLL = "payroll"
    INVENTORY = "inventory"
    FIXED_ASSET = "fixed_asset"
    VAT_ADJUSTMENT = "vat_adjustment"
    OPENING_BALANCE = "opening_balance"
    CLOSING_ENTRY = "closing_entry"
    AI = "ai"
    OTHER = "other"