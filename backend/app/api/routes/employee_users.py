from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import db_session, require_admin_user
from app.core.config import get_settings
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
def authorize_employee_login(payload: EmployeeUserAuthorizeRequest, db: Session = Depends(db_session)):
    email = payload.email.lower()
    settings = get_settings()
    if settings.is_admin_email(email):
        return {'authorized': True, 'role': 'admin'}

    employee = EmployeeUserRepository(db).get_by_email(email)
    if employee and employee.is_active:
        return {'authorized': True, 'role': 'employee'}
    return {'authorized': False, 'role': 'none'}


@router.get('/', response_model=list[EmployeeUserRead])
def list_employee_users(
    db: Session = Depends(db_session),
    _: str = Depends(require_admin_user),
):
    return EmployeeUserRepository(db).list()


@router.post('/', response_model=EmployeeUserRead, status_code=status.HTTP_201_CREATED)
def create_employee_user(
    payload: EmployeeUserCreate,
    db: Session = Depends(db_session),
    admin_email: str = Depends(require_admin_user),
):
    repo = EmployeeUserRepository(db)
    if repo.get_by_email(payload.email.lower()):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Bu e-posta zaten kayıtlı')
    return repo.create(payload, created_by=admin_email)


@router.put('/{user_id}', response_model=EmployeeUserRead)
def update_employee_user(
    user_id: int,
    payload: EmployeeUserUpdate,
    db: Session = Depends(db_session),
    _: str = Depends(require_admin_user),
):
    repo = EmployeeUserRepository(db)
    obj = repo.get(user_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Employee user not found')
    return repo.update(obj, payload)


@router.delete('/{user_id}', response_model=MessageResponse)
def delete_employee_user(
    user_id: int,
    db: Session = Depends(db_session),
    _: str = Depends(require_admin_user),
):
    repo = EmployeeUserRepository(db)
    obj = repo.get(user_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Employee user not found')
    repo.delete(obj)
    return {'message': 'Employee user deleted'}
