import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
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
from app.modules.documents.enums import DocumentStatus, DocumentType


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "checksum_sha256",
            name="uq_documents_company_checksum",
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

    uploaded_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    storage_key: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
        unique=True,
    )

    mime_type: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    extension: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
    )

    file_size: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    checksum_sha256: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )

    document_type: Mapped[DocumentType] = mapped_column(
    Enum(
        DocumentType,
        values_callable=lambda enum_class: [
            item.value for item in enum_class
        ],
        name="document_type",
        native_enum=False,
        create_constraint=True,
        validate_strings=True,
    ),
    nullable=False,
    default=DocumentType.UNKNOWN,
    server_default=DocumentType.UNKNOWN.value,
    )

    status: Mapped[DocumentStatus] = mapped_column(
    Enum(
        DocumentStatus,
        values_callable=lambda enum_class: [
            item.value for item in enum_class
        ],
        name="document_status",
        native_enum=False,
        create_constraint=True,
        validate_strings=True,
    ),
    nullable=False,
    default=DocumentStatus.UPLOADED,
    server_default=DocumentStatus.UPLOADED.value,
    index=True,
    )

    ai_confidence: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 4),
        nullable=True,
    )

    processing_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    company: Mapped["Company"] = relationship(
        back_populates="documents",
    )

    uploaded_by: Mapped["User"] = relationship(
        back_populates="uploaded_documents",
    )