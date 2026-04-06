from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import db_session
from app.repositories.settings_repository import SettingsRepository
from app.schemas.app_setting import AppSettingRead, AppSettingUpsert

router = APIRouter()


@router.get('/', response_model=list[AppSettingRead])
def list_settings(db: Session = Depends(db_session)):
    return SettingsRepository(db).list()


@router.post('/upsert', response_model=AppSettingRead)
def upsert_setting(payload: AppSettingUpsert, db: Session = Depends(db_session)):
    return SettingsRepository(db).upsert(
        key=payload.setting_key,
        value=payload.setting_value,
        description=payload.description,
    )
