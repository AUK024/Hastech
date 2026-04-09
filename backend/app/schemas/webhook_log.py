from datetime import datetime
from pydantic import BaseModel, ConfigDict


class WebhookLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_code: str
    event_type: str
    payload: dict
    status: str
    error_message: str | None = None
    created_at: datetime
