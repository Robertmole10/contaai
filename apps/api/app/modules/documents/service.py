from __future__ import annotations

import hashlib
from pathlib import Path
from typing import BinaryIO
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.documents.enums import DocumentStatus, DocumentType
from app.modules.documents.models import Document
from app.modules.documents.repository import DocumentRepository
from app.modules.documents.storage import (
    DocumentStorage,
    DocumentStorageError,
)


class DocumentServiceError(Exception):
    """Base exception for document service operations."""


class InvalidDocumentError(DocumentServiceError):
    """Raised when an uploaded document is invalid."""


class DuplicateDocumentError(DocumentServiceError):
    """Raised when the same document already exists for the company."""


class DocumentPersistenceError(DocumentServiceError):
    """Raised when document metadata cannot be saved."""


class DocumentService:
    ALLOWED_EXTENSIONS = {
        ".pdf",
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
        ".tif",
        ".tiff",
    }

    ALLOWED_MIME_TYPES = {
        "application/pdf",
        "image/png",
        "image/jpeg",
        "image/webp",
        "image/tiff",
    }

    MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB

    def __init__(
        self,
        *,
        session: Session,
        storage: DocumentStorage,
    ) -> None:
        self.session = session
        self.storage = storage
        self.repository = DocumentRepository(session)

    def upload_document(
        self,
        *,
        company_id: UUID,
        uploaded_by_id: UUID,
        original_filename: str,
        mime_type: str,
        file_data: bytes | BinaryIO,
        document_type: DocumentType = DocumentType.UNKNOWN,
    ) -> Document:
        extension = self._validate_filename(original_filename)
        normalized_mime_type = self._validate_mime_type(mime_type)

        file_bytes = self._read_file(file_data)
        file_size = len(file_bytes)

        self._validate_file_size(file_size)

        checksum_sha256 = hashlib.sha256(file_bytes).hexdigest()

        existing_document = self.repository.get_by_checksum(
            company_id=company_id,
            checksum_sha256=checksum_sha256,
        )

        if existing_document is not None:
            raise DuplicateDocumentError(
                "This document has already been uploaded for this company."
            )

        storage_key = self.storage.generate_storage_key(
            company_id=company_id,
            original_filename=original_filename,
        )

        uploaded_to_storage = False

        try:
            self.storage.upload_file(
                storage_key=storage_key,
                file_data=file_bytes,
                file_size=file_size,
                content_type=normalized_mime_type,
            )
            uploaded_to_storage = True

            document = self.repository.create(
                company_id=company_id,
                uploaded_by_id=uploaded_by_id,
                original_filename=Path(original_filename).name,
                storage_key=storage_key,
                mime_type=normalized_mime_type,
                extension=extension,
                file_size=file_size,
                checksum_sha256=checksum_sha256,
                document_type=document_type,
                status=DocumentStatus.UPLOADED,
            )

            self.session.commit()
            self.session.refresh(document)

            return document

        except IntegrityError as exc:
            self.session.rollback()

            if uploaded_to_storage:
                self._safe_delete_from_storage(storage_key)

            raise DuplicateDocumentError(
                "This document already exists or conflicts with an existing record."
            ) from exc

        except DocumentStorageError:
            self.session.rollback()
            raise

        except Exception as exc:
            self.session.rollback()

            if uploaded_to_storage:
                self._safe_delete_from_storage(storage_key)

            raise DocumentPersistenceError(
                "The document could not be saved."
            ) from exc

    @classmethod
    def _validate_filename(cls, original_filename: str) -> str:
        safe_filename = Path(original_filename).name

        if not safe_filename:
            raise InvalidDocumentError("The file name is missing.")

        extension = Path(safe_filename).suffix.lower()

        if extension not in cls.ALLOWED_EXTENSIONS:
            raise InvalidDocumentError(
                f"Unsupported file extension: {extension or 'none'}."
            )

        return extension

    @classmethod
    def _validate_mime_type(cls, mime_type: str) -> str:
        normalized_mime_type = mime_type.lower().strip()

        if normalized_mime_type not in cls.ALLOWED_MIME_TYPES:
            raise InvalidDocumentError(
                f"Unsupported MIME type: {normalized_mime_type or 'unknown'}."
            )

        return normalized_mime_type

    @classmethod
    def _validate_file_size(cls, file_size: int) -> None:
        if file_size <= 0:
            raise InvalidDocumentError("The uploaded file is empty.")

        if file_size > cls.MAX_FILE_SIZE:
            raise InvalidDocumentError(
                "The uploaded file exceeds the maximum size of 20 MB."
            )

    @staticmethod
    def _read_file(file_data: bytes | BinaryIO) -> bytes:
        if isinstance(file_data, bytes):
            return file_data

        file_data.seek(0)
        content = file_data.read()

        if not isinstance(content, bytes):
            raise InvalidDocumentError(
                "The uploaded file could not be read as binary data."
            )

        return content

    def _safe_delete_from_storage(self, storage_key: str) -> None:
        try:
            self.storage.delete_file(storage_key)
        except DocumentStorageError:
            # Cleanup failure should not hide the original database error.
            pass