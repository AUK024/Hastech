from __future__ import annotations

from sqlalchemy import select
from app.models.auto_reply_log import AutoReplyLog
from app.repositories.base import RepositoryBase


class AutoReplyLogRepository(RepositoryBase):
    def list(self, limit: int = 100) -> list[AutoReplyLog]:
        stmt = select(AutoReplyLog).order_by(AutoReplyLog.created_at.desc()).limit(limit)
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
        obj = AutoReplyLog(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj
