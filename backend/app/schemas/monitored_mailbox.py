from pydantic import BaseModel, ConfigDict, EmailStr


class MonitoredMailboxBase(BaseModel):
    email: EmailStr
    display_name: str
    mailbox_type: str
    is_active: bool = True
    auto_reply_enabled: bool = True
    description: str | None = None


class MonitoredMailboxCreate(MonitoredMailboxBase):
    pass


class MonitoredMailboxUpdate(BaseModel):
    display_name: str | None = None
    mailbox_type: str | None = None
    is_active: bool | None = None
    auto_reply_enabled: bool | None = None
    description: str | None = None


class MonitoredMailboxRead(MonitoredMailboxBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
