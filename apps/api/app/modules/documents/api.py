from __future__ import annotations

from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.modules.documents.enums import DocumentStatus, DocumentType
from app.modules.documents.permissions import get_company_for_user
from app.modules.documents.repository import DocumentRepository
from app.modules.documents.schemas import (
    DocumentListResponse,
    DocumentResponse,
)
from app.modules.documents.service import (
    DocumentPersistenceError,
    DocumentService,
    DuplicateDocumentError,
    InvalidDocumentError,
)
from app.modules.documents.storage import (
    DocumentStorage,
    DocumentStorageError,
    get_document_storage,
)


router = APIRouter(
    prefix="/companies/{company_id}/documents",
    tags=["Documents"],
)


@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_document(
    company_id: UUID,
    file: UploadFile = File(...),
    document_type: DocumentType = Form(
        default=DocumentType.UNKNOWN,
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    storage: DocumentStorage = Depends(get_document_storage),
) -> DocumentResponse:
    get_company_for_user(
        db=db,
        user_id=current_user.id,
        company_id=company_id,
    )

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Numele fișierului lipsește.",
        )

    service = DocumentService(
        session=db,
        storage=storage,
    )

    try:
        document = service.upload_document(
            company_id=company_id,
            uploaded_by_id=current_user.id,
            original_filename=file.filename,
            mime_type=file.content_type or "",
            file_data=file.file,
            document_type=document_type,
        )

        return DocumentResponse.model_validate(document)

    except InvalidDocumentError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except DuplicateDocumentError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except DocumentStorageError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviciul de stocare nu este disponibil.",
        ) from exc

    except DocumentPersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Documentul nu a putut fi salvat.",
        ) from exc


@router.get(
    "",
    response_model=DocumentListResponse,
)
def list_documents(
    company_id: UUID,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    document_status: DocumentStatus | None = Query(
        default=None,
        alias="status",
    ),
    document_type: DocumentType | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentListResponse:
    get_company_for_user(
        db=db,
        user_id=current_user.id,
        company_id=company_id,
    )

    repository = DocumentRepository(db)

    documents = repository.list_by_company(
        company_id=company_id,
        offset=offset,
        limit=limit,
        status=document_status,
        document_type=document_type,
    )

    return DocumentListResponse(
        items=[
            DocumentResponse.model_validate(document)
            for document in documents
        ],
        offset=offset,
        limit=limit,
        count=len(documents),
    )


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
def get_document(
    company_id: UUID,
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    get_company_for_user(
        db=db,
        user_id=current_user.id,
        company_id=company_id,
    )

    repository = DocumentRepository(db)

    document = repository.get_by_id(
        document_id=document_id,
        company_id=company_id,
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documentul nu a fost găsit.",
        )

    return DocumentResponse.model_validate(document)