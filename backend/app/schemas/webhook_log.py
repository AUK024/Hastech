from datetime import datetime
from pydantic import BaseModel


class WebhookLogRead(BaseModel):
    id: int
    event_type: str
    payload: dict
    status: str
    error_message: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True
