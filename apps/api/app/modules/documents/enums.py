from enum import StrEnum


class DocumentStatus(StrEnum):
    UPLOADED = "uploaded"
    QUEUED = "queued"
    PROCESSING = "processing"
    REVIEW_REQUIRED = "review_required"
    APPROVED = "approved"
    POSTED = "posted"
    ARCHIVED = "archived"
    FAILED = "failed"
    REJECTED = "rejected"


class DocumentType(StrEnum):
    UNKNOWN = "unknown"
    PURCHASE_INVOICE = "purchase_invoice"
    SALES_INVOICE = "sales_invoice"
    RECEIPT = "receipt"
    BANK_STATEMENT = "bank_statement"
    CREDIT_NOTE = "credit_note"
    OTHER = "other"