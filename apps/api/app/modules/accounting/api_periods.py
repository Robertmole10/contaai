from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.modules.accounting.permissions import (
    require_accounting_read_access,
    require_accounting_write_access,
)
from app.modules.accounting.schemas import (
    AccountingPeriodCreate,
    AccountingPeriodListResponse,
    AccountingPeriodRead,
    AccountingPeriodUpdate,
)
from app.modules.accounting.service import (
    AccountingPeriodAlreadyExistsError,
    AccountingPeriodLockedError,
    AccountingPeriodNotFoundError,
    AccountingPeriodPersistenceError,
    AccountingPeriodService,
    InvalidAccountingPeriodError,
)


router = APIRouter(
    prefix="/companies/{company_id}/accounting-periods",
    tags=["Accounting - Periods"],
)


@router.get(
    "",
    response_model=AccountingPeriodListResponse,
)
def list_accounting_periods(
    company_id: UUID,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    year: int | None = Query(default=None, ge=2000, le=2200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AccountingPeriodListResponse:
    require_accounting_read_access(
        db=db,
        user_id=current_user.id,
        company_id=company_id,
    )

    service = AccountingPeriodService(session=db)

    periods = service.list_periods(
        company_id=company_id,
        offset=offset,
        limit=limit,
        year=year,
    )

    return AccountingPeriodListResponse(
        items=[
            AccountingPeriodRead.model_validate(period)
            for period in periods
        ],
        offset=offset,
        limit=limit,
        count=len(periods),
    )


@router.get(
    "/{period_id}",
    response_model=AccountingPeriodRead,
)
def get_accounting_period(
    company_id: UUID,
    period_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AccountingPeriodRead:
    require_accounting_read_access(
        db=db,
        user_id=current_user.id,
        company_id=company_id,
    )

    service = AccountingPeriodService(session=db)

    try:
        period = service.get_period(
            period_id=period_id,
            company_id=company_id,
        )
        return AccountingPeriodRead.model_validate(period)

    except AccountingPeriodNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perioada contabilă nu a fost găsită.",
        ) from exc


@router.post(
    "",
    response_model=AccountingPeriodRead,
    status_code=status.HTTP_201_CREATED,
)
def create_accounting_period(
    company_id: UUID,
    payload: AccountingPeriodCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AccountingPeriodRead:
    require_accounting_write_access(
        db=db,
        user_id=current_user.id,
        company_id=company_id,
    )

    service = AccountingPeriodService(session=db)

    try:
        period = service.create_period(
            company_id=company_id,
            payload=payload,
        )
        return AccountingPeriodRead.model_validate(period)

    except AccountingPeriodAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Există deja o perioadă contabilă pentru "
                "anul și luna selectate."
            ),
        ) from exc

    except InvalidAccountingPeriodError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except AccountingPeriodPersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Perioada contabilă nu a putut fi salvată.",
        ) from exc


@router.patch(
    "/{period_id}",
    response_model=AccountingPeriodRead,
)
def update_accounting_period(
    company_id: UUID,
    period_id: UUID,
    payload: AccountingPeriodUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AccountingPeriodRead:
    require_accounting_write_access(
        db=db,
        user_id=current_user.id,
        company_id=company_id,
    )

    service = AccountingPeriodService(session=db)

    try:
        period = service.update_period(
            period_id=period_id,
            company_id=company_id,
            payload=payload,
        )
        return AccountingPeriodRead.model_validate(period)

    except AccountingPeriodNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perioada contabilă nu a fost găsită.",
        ) from exc

    except InvalidAccountingPeriodError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except AccountingPeriodLockedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except AccountingPeriodAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Există deja o perioadă contabilă pentru "
                "anul și luna selectate."
            ),
        ) from exc

    except AccountingPeriodPersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Perioada contabilă nu a putut fi actualizată.",
        ) from exc