from pydantic import BaseModel


class AppSettingRead(BaseModel):
    id: int
    setting_key: str
    setting_value: str
    description: str | None = None

    class Config:
        from_attributes = True


class AppSettingUpsert(BaseModel):
    setting_key: str
    setting_value: str
    description: str | None = None
