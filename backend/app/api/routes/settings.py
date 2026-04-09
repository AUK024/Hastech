from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.audit import safe_audit_log
from app.api.deps import db_session, resolve_tenant_code
from app.repositories.settings_repository import SettingsRepository
from app.schemas.app_setting import AppSettingRead, AppSettingUpsert

router = APIRouter()


@router.get('/', response_model=list[AppSettingRead])
def list_settings(db: Session = Depends(db_session)):
    return SettingsRepository(db).list()


@router.post('/upsert', response_model=AppSettingRead)
def upsert_setting(
    payload: AppSettingUpsert,
    db: Session = Depends(db_session),
    tenant_code: str = Depends(resolve_tenant_code),
):
    updated = SettingsRepository(db).upsert(
        key=payload.setting_key,
        value=payload.setting_value,
        description=payload.description,
    )
    safe_audit_log(
        db,
        tenant_code=tenant_code,
        module_name='settings',
        action_name='upsert_setting',
        payload={'setting_key': payload.setting_key},
        result='success',
    )
    return updated
