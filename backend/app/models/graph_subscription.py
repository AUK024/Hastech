from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.models.common import TimestampMixin


class GraphSubscription(Base, TimestampMixin):
    __tablename__ = 'graph_subscriptions'

    id: Mapped[int] = mapped_column(primary_key=True)
    mailbox_id: Mapped[int] = mapped_column(ForeignKey('monitored_mailboxes.id'), unique=True, index=True)
    graph_subscription_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True, index=True)
    resource: Mapped[str] = mapped_column(String(500))
    change_type: Mapped[str] = mapped_column(String(50), default='created')
    notification_url: Mapped[str] = mapped_column(String(500))
    lifecycle_notification_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    client_state: Mapped[str | None] = mapped_column(String(255), nullable=True)
    expiration_datetime: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_renewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
