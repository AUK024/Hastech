from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class IncomingEmail(Base):
    __tablename__ = 'incoming_emails'
    id: Mapped[int] = mapped_column(primary_key=True)
    mailbox_id: Mapped[int] = mapped_column(ForeignKey('monitored_mailboxes.id'))
    message_id: Mapped[str] = mapped_column(String(255), unique=True)
    internet_message_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    conversation_id: Mapped[str] = mapped_column(String(255), index=True)
    sender_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sender_email: Mapped[str] = mapped_column(String(255), index=True)
    subject: Mapped[str | None] = mapped_column(String(500), nullable=True)
    body_preview: Mapped[str | None] = mapped_column(Text, nullable=True)
    detected_language: Mapped[str | None] = mapped_column(String(20), nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_internal: Mapped[bool] = mapped_column(Boolean, default=False)
    is_blocked_by_rule: Mapped[bool] = mapped_column(Boolean, default=False)
    processing_status: Mapped[str] = mapped_column(String(50), default='pending')
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
