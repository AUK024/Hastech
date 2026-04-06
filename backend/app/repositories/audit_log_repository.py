from sqlalchemy import select
from app.models.audit_log import AuditLog
from app.repositories.base import RepositoryBase


class AuditLogRepository(RepositoryBase):
    def list(self, limit: int = 100) -> list[AuditLog]:
        stmt = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
        return self.db.scalars(stmt).all()

    def create(self, module_name: str, action_name: str, payload: dict, result: str) -> AuditLog:
        obj = AuditLog(module_name=module_name, action_name=action_name, payload=payload, result=result)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj
