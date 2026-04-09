from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TenantBase(BaseModel):
    tenant_code: str
    display_name: str
    is_active: bool = True
    description: str | None = None


class TenantCreate(TenantBase):
    pass


class TenantUpdate(BaseModel):
    display_name: str | None = None
    is_active: bool | None = None
    description: str | None = None


class TenantRead(TenantBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
