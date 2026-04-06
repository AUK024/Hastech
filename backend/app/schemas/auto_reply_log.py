from datetime import datetime
from pydantic import BaseModel


class AutoReplyLogRead(BaseModel):
    id: int
    incoming_email_id: int
    template_id: int
    translated_subject: str | None = None
    translated_body: str | None = None
    target_language: str | None = None
    reply_sent: bool
    sent_at: datetime | None = None
    provider_message_id: str | None = None
    error_message: str | None = None

    class Config:
        from_attributes = True
