from __future__ import annotations

from sqlalchemy import select
from app.models.monitored_mailbox import MonitoredMailbox
from app.repositories.base import RepositoryBase
from app.schemas.monitored_mailbox import MonitoredMailboxCreate, MonitoredMailboxUpdate


class MailboxRepository(RepositoryBase):
    def list(self) -> list[MonitoredMailbox]:
        return self.db.scalars(select(MonitoredMailbox).order_by(MonitoredMailbox.id.desc())).all()

    def list_active(self) -> list[MonitoredMailbox]:
        return self.db.scalars(
            select(MonitoredMailbox).where(MonitoredMailbox.is_active.is_(True)).order_by(MonitoredMailbox.id.desc())
        ).all()

    def get(self, mailbox_id: int) -> MonitoredMailbox | None:
        return self.db.scalar(select(MonitoredMailbox).where(MonitoredMailbox.id == mailbox_id))

    def get_by_email(self, email: str) -> MonitoredMailbox | None:
        return self.db.scalar(select(MonitoredMailbox).where(MonitoredMailbox.email == email.lower()))

    def get_by_graph_user_id(self, graph_user_id: str) -> MonitoredMailbox | None:
        normalized = graph_user_id.strip()
        if not normalized:
            return None
        return self.db.scalar(select(MonitoredMailbox).where(MonitoredMailbox.graph_user_id == normalized))

    def create(self, data: MonitoredMailboxCreate) -> MonitoredMailbox:
        mailbox = MonitoredMailbox(**data.model_dump())
        self.db.add(mailbox)
        self.db.commit()
        self.db.refresh(mailbox)
        return mailbox

    def update(self, obj: MonitoredMailbox, data: MonitoredMailboxUpdate) -> MonitoredMailbox:
        for key, value in data.model_dump(exclude_none=True).items():
            setattr(obj, key, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj: MonitoredMailbox) -> None:
        self.db.delete(obj)
        self.db.commit()
