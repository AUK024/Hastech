from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import db_session
from app.repositories.template_repository import TemplateRepository
from app.schemas.auto_reply_template import AutoReplyTemplateCreate, AutoReplyTemplateRead, AutoReplyTemplateUpdate
from app.schemas.common import MessageResponse

router = APIRouter()


@router.get('/', response_model=list[AutoReplyTemplateRead])
def list_templates(db: Session = Depends(db_session)):
    return TemplateRepository(db).list()


@router.get('/{template_id}', response_model=AutoReplyTemplateRead)
def get_template(template_id: int, db: Session = Depends(db_session)):
    obj = TemplateRepository(db).get(template_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Template not found')
    return obj


@router.post('/', response_model=AutoReplyTemplateRead, status_code=status.HTTP_201_CREATED)
def create_template(payload: AutoReplyTemplateCreate, db: Session = Depends(db_session)):
    return TemplateRepository(db).create(payload)


@router.put('/{template_id}', response_model=AutoReplyTemplateRead)
def update_template(template_id: int, payload: AutoReplyTemplateUpdate, db: Session = Depends(db_session)):
    repo = TemplateRepository(db)
    obj = repo.get(template_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Template not found')
    return repo.update(obj, payload)


@router.delete('/{template_id}', response_model=MessageResponse)
def delete_template(template_id: int, db: Session = Depends(db_session)):
    repo = TemplateRepository(db)
    obj = repo.get(template_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Template not found')
    repo.delete(obj)
    return {'message': 'Template deleted'}
