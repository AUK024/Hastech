from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
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
    _: str = Depends(require_admin_user),
):
    repo = TenantRepository(db)
    if repo.get_by_code(payload.tenant_code):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Tenant code already exists')
    return repo.create(payload)


@router.put('/{tenant_id}', response_model=TenantRead)
def update_tenant(
    tenant_id: int,
    payload: TenantUpdate,
    db: Session = Depends(db_session),
    _: str = Depends(require_admin_user),
):
    repo = TenantRepository(db)
    obj = repo.get(tenant_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Tenant not found')
    return repo.update(obj, payload)


@router.delete('/{tenant_id}', response_model=MessageResponse)
def delete_tenant(
    tenant_id: int,
    db: Session = Depends(db_session),
    _: str = Depends(require_admin_user),
):
    repo = TenantRepository(db)
    obj = repo.get(tenant_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Tenant not found')
    repo.delete(obj)
    return {'message': 'Tenant deleted'}
