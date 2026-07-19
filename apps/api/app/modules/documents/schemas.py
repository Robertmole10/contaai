from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.documents.enums import DocumentStatus, DocumentType


class DocumentResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "19d48f4f-0d61-4058-87f4-dc1bab0b9fe4",
                "company_id": "0a06922a-9e9b-4984-8385-a844efd0501a",
                "uploaded_by_id": "b81ee6c2-707f-4bdc-a56e-28722405e094",
                "original_filename": "Invoice-IN-71861736.pdf",
                "mime_type": "application/pdf",
                "extension": ".pdf",
                "file_size": 35092,
                "checksum_sha256": (
                    "d4f04bc38f069019a233e812fae9029d2ab65a6e5e6c5c0c7ba8f6a2ec0bd98d"
                ),
                "document_type": "purchase_invoice",
                "status": "uploaded",
                "ai_confidence": None,
                "processing_error": None,
                "created_at": "2026-07-17T20:06:39.324429Z",
                "updated_at": "2026-07-17T20:06:39.324429Z",
            }
        },
    )

    id: UUID
    company_id: UUID
    uploaded_by_id: UUID

    original_filename: str
    mime_type: str
    extension: str
    file_size: int = Field(ge=1)
    checksum_sha256: str = Field(min_length=64, max_length=64)

    document_type: DocumentType
    status: DocumentStatus

    ai_confidence: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
        le=Decimal("1"),
        decimal_places=4,
    )

    processing_error: str | None = None

    created_at: datetime
    updated_at: datetime


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    offset: int = Field(ge=0)
    limit: int = Field(ge=1)
    count: int = Field(ge=0)


class DocumentErrorResponse(BaseModel):
    detail: str