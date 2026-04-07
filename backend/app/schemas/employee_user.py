from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr


class EmployeeUserCreate(BaseModel):
    email: EmailStr
    full_name: str | None = None
    is_active: bool = True


class EmployeeUserUpdate(BaseModel):
    full_name: str | None = None
    is_active: bool | None = None


class EmployeeUserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str | None
    is_active: bool
    created_by: EmailStr
    created_at: datetime
    updated_at: datetime


class EmployeeUserAuthorizeRequest(BaseModel):
    email: EmailStr


class EmployeeUserAuthorizeResponse(BaseModel):
    authorized: bool
    role: str
