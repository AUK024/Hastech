from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.deps import db_session
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.webhook_log_repository import WebhookLogRepository
from app.schemas.audit_log import AuditLogRead
from app.schemas.webhook_log import WebhookLogRead

router = APIRouter()


@router.get('/webhook', response_model=list[WebhookLogRead])
def list_webhook_logs(limit: int = Query(default=100, ge=1, le=500), db: Session = Depends(db_session)):
    return WebhookLogRepository(db).list(limit=limit)


@router.get('/audit', response_model=list[AuditLogRead])
def list_audit_logs(limit: int = Query(default=100, ge=1, le=500), db: Session = Depends(db_session)):
    return AuditLogRepository(db).list(limit=limit)
