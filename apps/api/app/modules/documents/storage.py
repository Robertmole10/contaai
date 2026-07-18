from __future__ import annotations

from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path
from typing import BinaryIO
from uuid import UUID, uuid4

from minio import Minio
from minio.error import S3Error
from functools import lru_cache

from app.core.config import settings


@lru_cache
def get_document_storage() -> DocumentStorage:
    return DocumentStorage(
        endpoint=settings.minio_endpoint,
        access_key=settings.minio_root_user,
        secret_key=settings.minio_root_password,
        bucket_name=settings.minio_bucket,
        secure=settings.minio_secure,
    )

class DocumentStorageError(Exception):
    """Base exception for document storage operations."""


class DocumentUploadError(DocumentStorageError):
    """Raised when a document cannot be uploaded."""


class DocumentDownloadError(DocumentStorageError):
    """Raised when a document cannot be downloaded."""


class DocumentDeleteError(DocumentStorageError):
    """Raised when a document cannot be deleted."""


class DocumentStorage:
    def __init__(
        self,
        *,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        secure: bool = False,
    ) -> None:
        self.bucket_name = bucket_name

        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )

    def ensure_bucket_exists(self) -> None:
        """Create the configured bucket when it does not already exist."""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
        except S3Error as exc:
            raise DocumentStorageError(
                f"Could not verify or create MinIO bucket: {self.bucket_name}"
            ) from exc

    def generate_storage_key(
        self,
        *,
        company_id: UUID,
        original_filename: str,
        created_at: datetime | None = None,
    ) -> str:
        """
        Generate a storage key such as:

        documents/{company_uuid}/{year}/{month}/{uuid}.pdf
        """
        timestamp = created_at or datetime.now(UTC)

        extension = Path(original_filename).suffix.lower()
        object_id = uuid4()

        return (
            f"documents/{company_id}/"
            f"{timestamp.year:04d}/"
            f"{timestamp.month:02d}/"
            f"{object_id}{extension}"
        )

    def upload_file(
        self,
        *,
        storage_key: str,
        file_data: bytes | BinaryIO,
        file_size: int,
        content_type: str,
    ) -> str:
        """Upload a document to MinIO and return its storage key."""
        try:
            stream = self._to_stream(file_data)

            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=storage_key,
                data=stream,
                length=file_size,
                content_type=content_type,
            )

            return storage_key
        except S3Error as exc:
            raise DocumentUploadError(
                f"Could not upload document to storage: {storage_key}"
            ) from exc

    def download_file(self, storage_key: str):
        """
        Return the MinIO response stream.

        The caller must close the response and release the connection.
        """
        try:
            return self.client.get_object(
                bucket_name=self.bucket_name,
                object_name=storage_key,
            )
        except S3Error as exc:
            raise DocumentDownloadError(
                f"Could not download document from storage: {storage_key}"
            ) from exc

    def delete_file(self, storage_key: str) -> None:
        """Delete an object from MinIO."""
        try:
            self.client.remove_object(
                bucket_name=self.bucket_name,
                object_name=storage_key,
            )
        except S3Error as exc:
            raise DocumentDeleteError(
                f"Could not delete document from storage: {storage_key}"
            ) from exc

    def exists(self, storage_key: str) -> bool:
        """Return True when an object exists in MinIO."""
        try:
            self.client.stat_object(
                bucket_name=self.bucket_name,
                object_name=storage_key,
            )
            return True
        except S3Error as exc:
            if exc.code in {"NoSuchKey", "NoSuchObject", "NoSuchBucket"}:
                return False

            raise DocumentStorageError(
                f"Could not verify document existence: {storage_key}"
            ) from exc

    @staticmethod
    def _to_stream(file_data: bytes | BinaryIO) -> BinaryIO:
        if isinstance(file_data, bytes):
            return BytesIO(file_data)

        file_data.seek(0)
        return file_data