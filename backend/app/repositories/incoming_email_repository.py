from __future__ import annotations

from sqlalchemy import select
from app.models.incoming_email import IncomingEmail
from app.repositories.base import RepositoryBase


class IncomingEmailRepository(RepositoryBase):
    def list(self, limit: int = 100, tenant_code: str = 'default') -> list[IncomingEmail]:
        normalized_tenant = tenant_code.strip().lower() or 'default'
        stmt = (
            select(IncomingEmail)
            .where(IncomingEmail.tenant_code == normalized_tenant)
            .order_by(IncomingEmail.created_at.desc())
            .limit(limit)
        )
        return self.db.scalars(stmt).all()

    def get_by_message_id(self, message_id: str) -> IncomingEmail | None:
        return self.db.scalar(select(IncomingEmail).where(IncomingEmail.message_id == message_id))

    def get_by_conversation(self, conversation_id: str, tenant_code: str = 'default') -> list[IncomingEmail]:
        normalized_tenant = tenant_code.strip().lower() or 'default'
        stmt = select(IncomingEmail).where(
            IncomingEmail.conversation_id == conversation_id,
            IncomingEmail.tenant_code == normalized_tenant,
        )
        return self.db.scalars(stmt).all()

    def create(self, **kwargs) -> IncomingEmail:
        tenant_code = str(kwargs.get('tenant_code', 'default')).strip().lower() or 'default'
        kwargs['tenant_code'] = tenant_code
        obj = IncomingEmail(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, obj: IncomingEmail, **kwargs) -> IncomingEmail:
        for key, value in kwargs.items():
            setattr(obj, key, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj
