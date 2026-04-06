from datetime import datetime
from pydantic import BaseModel


class AuditLogRead(BaseModel):
    id: int
    module_name: str
    action_name: str
    payload: dict
    result: str
    created_at: datetime

    class Config:
        from_attributes = True
