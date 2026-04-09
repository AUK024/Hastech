from __future__ import annotations

from sqlalchemy import select
from app.models.monitored_mailbox import MonitoredMailbox
from app.repositories.base import RepositoryBase
from app.schemas.monitored_mailbox import MonitoredMailboxCreate, MonitoredMailboxUpdate


class MailboxRepository(RepositoryBase):
    def list_all(self) -> list[MonitoredMailbox]:
        return self.db.scalars(select(MonitoredMailbox).order_by(MonitoredMailbox.id.desc())).all()

    def list_active_all(self) -> list[MonitoredMailbox]:
        return self.db.scalars(
            select(MonitoredMailbox)
            .where(MonitoredMailbox.is_active.is_(True))
            .order_by(MonitoredMailbox.id.desc())
        ).all()

    def list(self, tenant_code: str = 'default') -> list[MonitoredMailbox]:
        normalized_tenant = tenant_code.strip().lower() or 'default'
        return self.db.scalars(
            select(MonitoredMailbox)
            .where(MonitoredMailbox.tenant_code == normalized_tenant)
            .order_by(MonitoredMailbox.id.desc())
        ).all()

    def list_active(self, tenant_code: str = 'default') -> list[MonitoredMailbox]:
        normalized_tenant = tenant_code.strip().lower() or 'default'
        return self.db.scalars(
            select(MonitoredMailbox)
            .where(MonitoredMailbox.tenant_code == normalized_tenant)
            .where(MonitoredMailbox.is_active.is_(True))
            .order_by(MonitoredMailbox.id.desc())
        ).all()

    def get(self, mailbox_id: int, tenant_code: str = 'default') -> MonitoredMailbox | None:
        normalized_tenant = tenant_code.strip().lower() or 'default'
        return self.db.scalar(
            select(MonitoredMailbox).where(
                MonitoredMailbox.id == mailbox_id,
                MonitoredMailbox.tenant_code == normalized_tenant,
            )
        )

    def get_by_email(self, email: str, tenant_code: str = 'default') -> MonitoredMailbox | None:
        normalized_tenant = tenant_code.strip().lower() or 'default'
        return self.db.scalar(
            select(MonitoredMailbox).where(
                MonitoredMailbox.email == email.lower(),
                MonitoredMailbox.tenant_code == normalized_tenant,
            )
        )

    def get_by_graph_user_id(self, graph_user_id: str, tenant_code: str = 'default') -> MonitoredMailbox | None:
        normalized = graph_user_id.strip()
        if not normalized:
            return None
        normalized_tenant = tenant_code.strip().lower() or 'default'
        return self.db.scalar(
            select(MonitoredMailbox).where(
                MonitoredMailbox.graph_user_id == normalized,
                MonitoredMailbox.tenant_code == normalized_tenant,
            )
        )

    def create(self, data: MonitoredMailboxCreate, tenant_code: str = 'default') -> MonitoredMailbox:
        normalized_tenant = tenant_code.strip().lower() or 'default'
        mailbox = MonitoredMailbox(tenant_code=normalized_tenant, **data.model_dump())
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
