from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.audit import safe_audit_log
from app.api.deps import db_session, require_admin_user, resolve_tenant_code
from app.core.config import get_settings
from app.core.security import verify_password
from app.repositories.employee_user_repository import EmployeeUserRepository
from app.schemas.common import MessageResponse
from app.schemas.employee_user import (
    EmployeeUserCreate,
    EmployeeUserUpdate,
    EmployeeUserRead,
    EmployeeUserAuthorizeRequest,
    EmployeeUserAuthorizeResponse,
)

router = APIRouter()


@router.post('/authorize', response_model=EmployeeUserAuthorizeResponse)
def authorize_employee_login(
    payload: EmployeeUserAuthorizeRequest,
    db: Session = Depends(db_session),
    tenant_code: str = Depends(resolve_tenant_code),
):
    email = payload.email.lower()
    password = payload.password or ''
    settings = get_settings()
    if settings.is_admin_email(email):
        safe_audit_log(
            db,
            tenant_code=tenant_code,
            module_name='employee_users',
            action_name='authorize',
            payload={'email': email, 'role': 'admin'},
            result='success',
        )
        return {'authorized': True, 'role': 'admin'}

    employee = EmployeeUserRepository(db).get_by_email(email, tenant_code=tenant_code)
    if employee and employee.is_active and verify_password(password, employee.password_hash):
        safe_audit_log(
            db,
            tenant_code=tenant_code,
            module_name='employee_users',
            action_name='authorize',
            payload={'email': email, 'role': 'employee'},
            result='success',
        )
        return {'authorized': True, 'role': 'employee'}
    safe_audit_log(
        db,
        tenant_code=tenant_code,
        module_name='employee_users',
        action_name='authorize',
        payload={'email': email},
        result='denied',
    )
    return {'authorized': False, 'role': 'none'}


@router.get('/', response_model=list[EmployeeUserRead])
def list_employee_users(
    db: Session = Depends(db_session),
    _: str = Depends(require_admin_user),
    tenant_code: str = Depends(resolve_tenant_code),
):
    return EmployeeUserRepository(db).list(tenant_code=tenant_code)


@router.post('/', response_model=EmployeeUserRead, status_code=status.HTTP_201_CREATED)
def create_employee_user(
    payload: EmployeeUserCreate,
    db: Session = Depends(db_session),
    admin_email: str = Depends(require_admin_user),
    tenant_code: str = Depends(resolve_tenant_code),
):
    repo = EmployeeUserRepository(db)
    if repo.get_by_email(payload.email.lower(), tenant_code=tenant_code):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Bu e-posta zaten kayıtlı')
    created = repo.create(payload, created_by=admin_email, tenant_code=tenant_code)
    safe_audit_log(
        db,
        tenant_code=tenant_code,
        module_name='employee_users',
        action_name='create_employee_user',
        payload={'user_id': created.id, 'email': created.email, 'created_by': admin_email},
        result='success',
    )
    return created


@router.put('/{user_id}', response_model=EmployeeUserRead)
def update_employee_user(
    user_id: int,
    payload: EmployeeUserUpdate,
    db: Session = Depends(db_session),
    _: str = Depends(require_admin_user),
    tenant_code: str = Depends(resolve_tenant_code),
):
    repo = EmployeeUserRepository(db)
    obj = repo.get(user_id, tenant_code=tenant_code)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Employee user not found')
    updated = repo.update(obj, payload)
    safe_audit_log(
        db,
        tenant_code=tenant_code,
        module_name='employee_users',
        action_name='update_employee_user',
        payload={'user_id': updated.id, 'email': updated.email},
        result='success',
    )
    return updated


@router.delete('/{user_id}', response_model=MessageResponse)
def delete_employee_user(
    user_id: int,
    db: Session = Depends(db_session),
    _: str = Depends(require_admin_user),
    tenant_code: str = Depends(resolve_tenant_code),
):
    repo = EmployeeUserRepository(db)
    obj = repo.get(user_id, tenant_code=tenant_code)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Employee user not found')
    repo.delete(obj)
    safe_audit_log(
        db,
        tenant_code=tenant_code,
        module_name='employee_users',
        action_name='delete_employee_user',
        payload={'user_id': user_id, 'email': obj.email},
        result='success',
    )
    return {'message': 'Employee user deleted'}
