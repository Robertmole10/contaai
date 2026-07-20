from __future__ import annotations

from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.modules.documents.enums import DocumentStatus, DocumentType
from app.modules.documents.models import Document


class DocumentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(
        self,
        *,
        document_id: UUID,
        company_id: UUID,
    ) -> Document | None:
        statement = select(Document).where(
            Document.id == document_id,
            Document.company_id == company_id,
        )

        return self.session.execute(statement).scalar_one_or_none()

    def get_by_checksum(
        self,
        *,
        company_id: UUID,
        checksum_sha256: str,
    ) -> Document | None:
        statement = select(Document).where(
            Document.company_id == company_id,
            Document.checksum_sha256 == checksum_sha256,
        )

        return self.session.execute(statement).scalar_one_or_none()

    def create(
        self,
        *,
        company_id: UUID,
        uploaded_by_id: UUID,
        original_filename: str,
        storage_key: str,
        mime_type: str,
        extension: str,
        file_size: int,
        checksum_sha256: str,
        document_type: DocumentType = DocumentType.UNKNOWN,
        status: DocumentStatus = DocumentStatus.UPLOADED,
    ) -> Document:
        document = Document(
            company_id=company_id,
            uploaded_by_id=uploaded_by_id,
            original_filename=original_filename,
            storage_key=storage_key,
            mime_type=mime_type,
            extension=extension,
            file_size=file_size,
            checksum_sha256=checksum_sha256,
            document_type=document_type,
            status=status,
        )

        self.session.add(document)
        self.session.flush()
        self.session.refresh(document)

        return document

    def list_by_company(
        self,
        *,
        company_id: UUID,
        offset: int = 0,
        limit: int = 50,
        status: DocumentStatus | None = None,
        document_type: DocumentType | None = None,
    ) -> list[Document]:
        statement: Select[tuple[Document]] = (
            select(Document)
            .where(Document.company_id == company_id)
            .order_by(Document.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        if status is not None:
            statement = statement.where(Document.status == status)

        if document_type is not None:
            statement = statement.where(
                Document.document_type == document_type
            )

        result = self.session.execute(statement)
        return list(result.scalars().all())