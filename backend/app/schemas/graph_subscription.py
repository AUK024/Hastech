from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr


class GraphSubscriptionBase(BaseModel):
    mailbox_id: int
    graph_subscription_id: str | None = None
    resource: str
    change_type: str = 'created'
    notification_url: str
    lifecycle_notification_url: str | None = None
    client_state: str | None = None
    expiration_datetime: datetime | None = None
    is_active: bool = True
    last_renewed_at: datetime | None = None
    error_message: str | None = None


class GraphSubscriptionCreate(GraphSubscriptionBase):
    pass


class GraphSubscriptionUpdate(BaseModel):
    graph_subscription_id: str | None = None
    resource: str | None = None
    change_type: str | None = None
    notification_url: str | None = None
    lifecycle_notification_url: str | None = None
    client_state: str | None = None
    expiration_datetime: datetime | None = None
    is_active: bool | None = None
    last_renewed_at: datetime | None = None
    error_message: str | None = None


class GraphSubscriptionRead(GraphSubscriptionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class GraphSubscriptionActionResult(BaseModel):
    mailbox_id: int
    mailbox_email: EmailStr | str
    status: str
    error: str | None = None
    subscription_id: str | None = None
    expiration_datetime: datetime | None = None


class GraphSubscriptionBatchResponse(BaseModel):
    total: int
    success: int
    failed: int
    results: list[GraphSubscriptionActionResult]
