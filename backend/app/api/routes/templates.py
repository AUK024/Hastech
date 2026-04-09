from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.audit import safe_audit_log
from app.api.deps import db_session, resolve_tenant_code
from app.repositories.template_repository import TemplateRepository
from app.schemas.auto_reply_template import AutoReplyTemplateCreate, AutoReplyTemplateRead, AutoReplyTemplateUpdate
from app.schemas.common import MessageResponse

router = APIRouter()


@router.get('/', response_model=list[AutoReplyTemplateRead])
def list_templates(db: Session = Depends(db_session), tenant_code: str = Depends(resolve_tenant_code)):
    return TemplateRepository(db).list(tenant_code=tenant_code)


@router.get('/{template_id}', response_model=AutoReplyTemplateRead)
def get_template(template_id: int, db: Session = Depends(db_session), tenant_code: str = Depends(resolve_tenant_code)):
    obj = TemplateRepository(db).get(template_id, tenant_code=tenant_code)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Template not found')
    return obj


@router.post('/', response_model=AutoReplyTemplateRead, status_code=status.HTTP_201_CREATED)
def create_template(
    payload: AutoReplyTemplateCreate,
    db: Session = Depends(db_session),
    tenant_code: str = Depends(resolve_tenant_code),
):
    created = TemplateRepository(db).create(payload, tenant_code=tenant_code)
    safe_audit_log(
        db,
        tenant_code=tenant_code,
        module_name='templates',
        action_name='create_template',
        payload={'template_id': created.id, 'name': created.name},
        result='success',
    )
    return created


@router.put('/{template_id}', response_model=AutoReplyTemplateRead)
def update_template(
    template_id: int,
    payload: AutoReplyTemplateUpdate,
    db: Session = Depends(db_session),
    tenant_code: str = Depends(resolve_tenant_code),
):
    repo = TemplateRepository(db)
    obj = repo.get(template_id, tenant_code=tenant_code)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Template not found')
    updated = repo.update(obj, payload)
    safe_audit_log(
        db,
        tenant_code=tenant_code,
        module_name='templates',
        action_name='update_template',
        payload={'template_id': updated.id, 'name': updated.name},
        result='success',
    )
    return updated


@router.delete('/{template_id}', response_model=MessageResponse)
def delete_template(
    template_id: int,
    db: Session = Depends(db_session),
    tenant_code: str = Depends(resolve_tenant_code),
):
    repo = TemplateRepository(db)
    obj = repo.get(template_id, tenant_code=tenant_code)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Template not found')
    repo.delete(obj)
    safe_audit_log(
        db,
        tenant_code=tenant_code,
        module_name='templates',
        action_name='delete_template',
        payload={'template_id': template_id, 'name': obj.name},
        result='success',
    )
    return {'message': 'Template deleted'}
