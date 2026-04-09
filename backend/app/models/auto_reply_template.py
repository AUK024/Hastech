from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.models.common import TimestampMixin


class AutoReplyTemplate(Base, TimestampMixin):
    __tablename__ = 'auto_reply_templates'
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_code: Mapped[str] = mapped_column(String(120), default='default', index=True)
    name: Mapped[str] = mapped_column(String(120))
    source_language: Mapped[str] = mapped_column(String(10))
    subject_template: Mapped[str] = mapped_column(Text)
    body_template: Mapped[str] = mapped_column(Text)
    signature_template: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
