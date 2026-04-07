from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class EmployeeUserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = None
    is_active: bool = True


class EmployeeUserUpdate(BaseModel):
    password: str | None = Field(default=None, min_length=8, max_length=128)
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
    password: str | None = Field(default=None, min_length=1, max_length=128)


class EmployeeUserAuthorizeResponse(BaseModel):
    authorized: bool
    role: str
