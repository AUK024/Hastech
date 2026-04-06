from datetime import datetime
from pydantic import BaseModel


class IncomingEmailRead(BaseModel):
    id: int
    mailbox_id: int
    message_id: str
    internet_message_id: str | None = None
    conversation_id: str
    sender_name: str | None = None
    sender_email: str
    subject: str | None = None
    body_preview: str | None = None
    detected_language: str | None = None
    confidence_score: float | None = None
    received_at: datetime
    is_internal: bool
    is_blocked_by_rule: bool
    processing_status: str
    error_message: str | None = None

    class Config:
        from_attributes = True
