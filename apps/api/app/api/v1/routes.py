from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.v1.auth import router as auth_router
from app.api.v1.workspace import router as workspace_router
from app.db.session import get_db

router = APIRouter()
router.include_router(auth_router)
router.include_router(workspace_router)


@router.get("/health", tags=["System"])
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "service": "contaai-api"}


@router.get("/ready", tags=["System"])
def ready():
    return {"ready": True}
