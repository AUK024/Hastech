from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.audit import safe_audit_log
from app.api.deps import db_session, require_admin_user
from app.repositories.tenant_repository import TenantRepository
from app.schemas.common import MessageResponse
from app.schemas.tenant import TenantCreate, TenantRead, TenantUpdate

router = APIRouter()


@router.get('/', response_model=list[TenantRead])
def list_tenants(
    db: Session = Depends(db_session),
    _: str = Depends(require_admin_user),
):
    return TenantRepository(db).list()


@router.post('/', response_model=TenantRead, status_code=status.HTTP_201_CREATED)
def create_tenant(
    payload: TenantCreate,
    db: Session = Depends(db_session),
    admin_email: str = Depends(require_admin_user),
):
    repo = TenantRepository(db)
    if repo.get_by_code(payload.tenant_code):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Tenant code already exists')
    created = repo.create(payload)
    safe_audit_log(
        db,
        tenant_code=created.tenant_code,
        module_name='tenants',
        action_name='create_tenant',
        payload={'tenant_id': created.id, 'tenant_code': created.tenant_code, 'admin_email': admin_email},
        result='success',
    )
    return created


@router.put('/{tenant_id}', response_model=TenantRead)
def update_tenant(
    tenant_id: int,
    payload: TenantUpdate,
    db: Session = Depends(db_session),
    admin_email: str = Depends(require_admin_user),
):
    repo = TenantRepository(db)
    obj = repo.get(tenant_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Tenant not found')
    updated = repo.update(obj, payload)
    safe_audit_log(
        db,
        tenant_code=updated.tenant_code,
        module_name='tenants',
        action_name='update_tenant',
        payload={'tenant_id': updated.id, 'tenant_code': updated.tenant_code, 'admin_email': admin_email},
        result='success',
    )
    return updated


@router.delete('/{tenant_id}', response_model=MessageResponse)
def delete_tenant(
    tenant_id: int,
    db: Session = Depends(db_session),
    admin_email: str = Depends(require_admin_user),
):
    repo = TenantRepository(db)
    obj = repo.get(tenant_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Tenant not found')
    repo.delete(obj)
    safe_audit_log(
        db,
        tenant_code=obj.tenant_code,
        module_name='tenants',
        action_name='delete_tenant',
        payload={'tenant_id': tenant_id, 'tenant_code': obj.tenant_code, 'admin_email': admin_email},
        result='success',
    )
    return {'message': 'Tenant deleted'}
