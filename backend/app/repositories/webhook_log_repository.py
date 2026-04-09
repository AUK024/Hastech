from sqlalchemy import select
from app.models.webhook_log import WebhookLog
from app.repositories.base import RepositoryBase


class WebhookLogRepository(RepositoryBase):
    def list(self, limit: int = 100, tenant_code: str = 'default') -> list[WebhookLog]:
        normalized_tenant = tenant_code.strip().lower() or 'default'
        stmt = (
            select(WebhookLog)
            .where(WebhookLog.tenant_code == normalized_tenant)
            .order_by(WebhookLog.created_at.desc())
            .limit(limit)
        )
        return self.db.scalars(stmt).all()

    def create(self, **kwargs) -> WebhookLog:
        tenant_code = str(kwargs.get('tenant_code', 'default')).strip().lower() or 'default'
        kwargs['tenant_code'] = tenant_code
        obj = WebhookLog(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj
