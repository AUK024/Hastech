from sqlalchemy import select
from app.models.audit_log import AuditLog
from app.repositories.base import RepositoryBase


class AuditLogRepository(RepositoryBase):
    def list(self, limit: int = 100, tenant_code: str = 'default') -> list[AuditLog]:
        normalized_tenant = tenant_code.strip().lower() or 'default'
        stmt = (
            select(AuditLog)
            .where(AuditLog.tenant_code == normalized_tenant)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        return self.db.scalars(stmt).all()

    def create(
        self,
        module_name: str,
        action_name: str,
        payload: dict,
        result: str,
        tenant_code: str = 'default',
    ) -> AuditLog:
        normalized_tenant = tenant_code.strip().lower() or 'default'
        obj = AuditLog(
            tenant_code=normalized_tenant,
            module_name=module_name,
            action_name=action_name,
            payload=payload,
            result=result,
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj
