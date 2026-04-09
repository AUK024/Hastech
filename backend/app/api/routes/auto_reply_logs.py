from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.deps import db_session, resolve_tenant_code
from app.repositories.auto_reply_log_repository import AutoReplyLogRepository
from app.schemas.auto_reply_log import AutoReplyLogRead

router = APIRouter()


@router.get('/', response_model=list[AutoReplyLogRead])
def list_auto_reply_logs(
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(db_session),
    tenant_code: str = Depends(resolve_tenant_code),
):
    return AutoReplyLogRepository(db).list(limit=limit, tenant_code=tenant_code)
