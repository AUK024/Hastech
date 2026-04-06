from sqlalchemy import select
from app.models.incoming_email import IncomingEmail
from app.repositories.base import RepositoryBase


class IncomingEmailRepository(RepositoryBase):
    def list(self, limit: int = 100) -> list[IncomingEmail]:
        stmt = select(IncomingEmail).order_by(IncomingEmail.created_at.desc()).limit(limit)
        return self.db.scalars(stmt).all()

    def get_by_message_id(self, message_id: str) -> IncomingEmail | None:
        return self.db.scalar(select(IncomingEmail).where(IncomingEmail.message_id == message_id))

    def get_by_conversation(self, conversation_id: str) -> list[IncomingEmail]:
        stmt = select(IncomingEmail).where(IncomingEmail.conversation_id == conversation_id)
        return self.db.scalars(stmt).all()

    def create(self, **kwargs) -> IncomingEmail:
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
