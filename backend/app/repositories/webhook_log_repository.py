from sqlalchemy import select
from app.models.webhook_log import WebhookLog
from app.repositories.base import RepositoryBase


class WebhookLogRepository(RepositoryBase):
    def list(self, limit: int = 100) -> list[WebhookLog]:
        stmt = select(WebhookLog).order_by(WebhookLog.created_at.desc()).limit(limit)
        return self.db.scalars(stmt).all()

    def create(self, **kwargs) -> WebhookLog:
        obj = WebhookLog(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj
