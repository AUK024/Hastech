from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import db_session
from app.repositories.blocked_rule_repository import BlockedRuleRepository
from app.schemas.blocked_sender_rule import BlockedSenderRuleCreate, BlockedSenderRuleRead, BlockedSenderRuleUpdate
from app.schemas.common import MessageResponse

router = APIRouter()


@router.get('/', response_model=list[BlockedSenderRuleRead])
def list_rules(db: Session = Depends(db_session)):
    return BlockedRuleRepository(db).list()


@router.get('/{rule_id}', response_model=BlockedSenderRuleRead)
def get_rule(rule_id: int, db: Session = Depends(db_session)):
    obj = BlockedRuleRepository(db).get(rule_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Rule not found')
    return obj


@router.post('/', response_model=BlockedSenderRuleRead, status_code=status.HTTP_201_CREATED)
def create_rule(payload: BlockedSenderRuleCreate, db: Session = Depends(db_session)):
    return BlockedRuleRepository(db).create(payload)


@router.put('/{rule_id}', response_model=BlockedSenderRuleRead)
def update_rule(rule_id: int, payload: BlockedSenderRuleUpdate, db: Session = Depends(db_session)):
    repo = BlockedRuleRepository(db)
    obj = repo.get(rule_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Rule not found')
    return repo.update(obj, payload)


@router.delete('/{rule_id}', response_model=MessageResponse)
def delete_rule(rule_id: int, db: Session = Depends(db_session)):
    repo = BlockedRuleRepository(db)
    obj = repo.get(rule_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Rule not found')
    repo.delete(obj)
    return {'message': 'Rule deleted'}
