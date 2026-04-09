from __future__ import annotations

from sqlalchemy import select
from app.models.auto_reply_log import AutoReplyLog
from app.repositories.base import RepositoryBase


class AutoReplyLogRepository(RepositoryBase):
    def list(self, limit: int = 100, tenant_code: str = 'default') -> list[AutoReplyLog]:
        normalized_tenant = tenant_code.strip().lower() or 'default'
        stmt = (
            select(AutoReplyLog)
            .where(AutoReplyLog.tenant_code == normalized_tenant)
            .order_by(AutoReplyLog.created_at.desc())
            .limit(limit)
        )
        return self.db.scalars(stmt).all()

    def has_successful_reply_for_incoming(self, incoming_email_id: int) -> bool:
        stmt = select(AutoReplyLog).where(
            AutoReplyLog.incoming_email_id == incoming_email_id,
            AutoReplyLog.reply_sent.is_(True),
        )
        return self.db.scalar(stmt) is not None

    def has_successful_reply_for_conversation(self, incoming_email_ids: list[int]) -> bool:
        if not incoming_email_ids:
            return False
        stmt = select(AutoReplyLog).where(
            AutoReplyLog.incoming_email_id.in_(incoming_email_ids),
            AutoReplyLog.reply_sent.is_(True),
        )
        return self.db.scalar(stmt) is not None

    def create(self, **kwargs) -> AutoReplyLog:
        tenant_code = str(kwargs.get('tenant_code', 'default')).strip().lower() or 'default'
        kwargs['tenant_code'] = tenant_code
        obj = AutoReplyLog(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj
