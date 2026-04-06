from pydantic import BaseModel, ConfigDict


class AppSettingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    setting_key: str
    setting_value: str
    description: str | None = None


class AppSettingUpsert(BaseModel):
    setting_key: str
    setting_value: str
    description: str | None = None
