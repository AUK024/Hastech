from sqlalchemy import select
from app.models.app_setting import AppSetting
from app.repositories.base import RepositoryBase


class SettingsRepository(RepositoryBase):
    def list(self) -> list[AppSetting]:
        return self.db.scalars(select(AppSetting).order_by(AppSetting.setting_key.asc())).all()

    def get(self, key: str) -> AppSetting | None:
        return self.db.scalar(select(AppSetting).where(AppSetting.setting_key == key))

    def upsert(self, key: str, value: str, description: str | None = None) -> AppSetting:
        obj = self.get(key)
        if obj:
            obj.setting_value = value
            if description is not None:
                obj.description = description
        else:
            obj = AppSetting(setting_key=key, setting_value=value, description=description)
            self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj
