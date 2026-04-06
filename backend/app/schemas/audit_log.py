from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    module_name: str
    action_name: str
    payload: dict
    result: str
    created_at: datetime
