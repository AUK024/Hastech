from sqlalchemy.orm import Session
from app.repositories.audit_log_repository import AuditLogRepository


def safe_audit_log(
    db: Session,
    *,
    tenant_code: str,
    module_name: str,
    action_name: str,
    payload: dict,
    result: str,
) -> None:
    try:
        AuditLogRepository(db).create(
            tenant_code=tenant_code,
            module_name=module_name,
            action_name=action_name,
            payload=payload,
            result=result,
        )
    except Exception:
        # Never break primary API flow due to audit persistence failures.
        return
