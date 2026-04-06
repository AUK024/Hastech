from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class AutoReplyLog(Base):
    __tablename__ = 'auto_reply_logs'
    id: Mapped[int] = mapped_column(primary_key=True)
    incoming_email_id: Mapped[int] = mapped_column(ForeignKey('incoming_emails.id'))
    template_id: Mapped[int] = mapped_column(ForeignKey('auto_reply_templates.id'))
    translated_subject: Mapped[str | None] = mapped_column(Text, nullable=True)
    translated_body: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_language: Mapped[str | None] = mapped_column(String(20), nullable=True)
    reply_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    provider_message_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
