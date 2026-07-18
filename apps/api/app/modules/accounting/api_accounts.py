from __future__ import annotations

from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.modules.accounting.permissions import (
    require_accounting_read_access,
    require_accounting_write_access,
)
from app.modules.accounting.schemas import (
    AccountCreate,
    AccountListResponse,
    AccountRead,
    AccountTreeNode,
    AccountUpdate,
)
from app.modules.accounting.service import (
    AccountAlreadyExistsError,
    AccountHasChildrenError,
    AccountNotFoundError,
    AccountPersistenceError,
    AccountService,
    InvalidAccountHierarchyError,
    ParentAccountNotFoundError,
)


router = APIRouter(
    prefix="/companies/{company_id}/accounts",
    tags=["Accounting - Accounts"],
)


@router.get(
    "",
    response_model=AccountListResponse,
)
def list_accounts(
    company_id: UUID,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    is_active: bool | None = Query(default=None),
    account_class: int | None = Query(
        default=None,
        ge=1,
        le=9,
    ),
    parent_id: UUID | None = Query(default=None),
    root_only: bool = Query(default=False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AccountListResponse:
    require_accounting_read_access(
        db=db,
        user_id=current_user.id,
        company_id=company_id,
    )

    service = AccountService(session=db)

    accounts = service.list_accounts(
        company_id=company_id,
        offset=offset,
        limit=limit,
        is_active=is_active,
        account_class=account_class,
        parent_id=parent_id,
        root_only=root_only,
    )

    return AccountListResponse(
        items=[
            AccountRead.model_validate(account)
            for account in accounts
        ],
        offset=offset,
        limit=limit,
        count=len(accounts),
    )


@router.get(
    "/tree",
    response_model=list[AccountTreeNode],
)
def get_account_tree(
    company_id: UUID,
    is_active: bool | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AccountTreeNode]:
    require_accounting_read_access(
        db=db,
        user_id=current_user.id,
        company_id=company_id,
    )

    service = AccountService(session=db)

    tree = service.build_account_tree(
        company_id=company_id,
        is_active=is_active,
    )

    return [
        AccountTreeNode.model_validate(node)
        for node in tree
    ]


@router.get(
    "/{account_id}",
    response_model=AccountRead,
)
def get_account(
    company_id: UUID,
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AccountRead:
    require_accounting_read_access(
        db=db,
        user_id=current_user.id,
        company_id=company_id,
    )

    service = AccountService(session=db)

    try:
        account = service.get_account(
            account_id=account_id,
            company_id=company_id,
        )

        return AccountRead.model_validate(account)

    except AccountNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contul contabil nu a fost găsit.",
        ) from exc


@router.post(
    "",
    response_model=AccountRead,
    status_code=status.HTTP_201_CREATED,
)
def create_account(
    company_id: UUID,
    payload: AccountCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AccountRead:
    require_accounting_write_access(
        db=db,
        user_id=current_user.id,
        company_id=company_id,
    )

    service = AccountService(session=db)

    try:
        account = service.create_account(
            company_id=company_id,
            payload=payload,
        )

        return AccountRead.model_validate(account)

    except AccountAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Există deja un cont cu acest cod.",
        ) from exc

    except ParentAccountNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Contul părinte nu există sau nu aparține companiei.",
        ) from exc

    except InvalidAccountHierarchyError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except AccountPersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Contul contabil nu a putut fi salvat.",
        ) from exc


@router.patch(
    "/{account_id}",
    response_model=AccountRead,
)
def update_account(
    company_id: UUID,
    account_id: UUID,
    payload: AccountUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AccountRead:
    require_accounting_write_access(
        db=db,
        user_id=current_user.id,
        company_id=company_id,
    )

    service = AccountService(session=db)

    try:
        account = service.update_account(
            account_id=account_id,
            company_id=company_id,
            payload=payload,
        )

        return AccountRead.model_validate(account)

    except AccountNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contul contabil nu a fost găsit.",
        ) from exc

    except AccountAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Există deja un cont cu acest cod.",
        ) from exc

    except ParentAccountNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Contul părinte nu există sau nu aparține companiei.",
        ) from exc

    except InvalidAccountHierarchyError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except AccountPersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Contul contabil nu a putut fi actualizat.",
        ) from exc


@router.delete(
    "/{account_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_account(
    company_id: UUID,
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    require_accounting_write_access(
        db=db,
        user_id=current_user.id,
        company_id=company_id,
    )

    service = AccountService(session=db)

    try:
        service.delete_account(
            account_id=account_id,
            company_id=company_id,
        )

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except AccountNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contul contabil nu a fost găsit.",
        ) from exc

    except AccountHasChildrenError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Contul nu poate fi șters deoarece are "
                "conturi subordonate."
            ),
        ) from exc

    except AccountPersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Contul este utilizat de alte înregistrări "
                "și nu poate fi șters."
            ),
        ) from exc