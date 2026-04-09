from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.audit import safe_audit_log
from app.api.deps import db_session, resolve_tenant_code
from app.repositories.blocked_rule_repository import BlockedRuleRepository
from app.schemas.blocked_sender_rule import BlockedSenderRuleCreate, BlockedSenderRuleRead, BlockedSenderRuleUpdate
from app.schemas.common import MessageResponse

router = APIRouter()


@router.get('/', response_model=list[BlockedSenderRuleRead])
def list_rules(db: Session = Depends(db_session), tenant_code: str = Depends(resolve_tenant_code)):
    return BlockedRuleRepository(db).list(tenant_code=tenant_code)


@router.get('/{rule_id}', response_model=BlockedSenderRuleRead)
def get_rule(rule_id: int, db: Session = Depends(db_session), tenant_code: str = Depends(resolve_tenant_code)):
    obj = BlockedRuleRepository(db).get(rule_id, tenant_code=tenant_code)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Rule not found')
    return obj


@router.post('/', response_model=BlockedSenderRuleRead, status_code=status.HTTP_201_CREATED)
def create_rule(
    payload: BlockedSenderRuleCreate,
    db: Session = Depends(db_session),
    tenant_code: str = Depends(resolve_tenant_code),
):
    created = BlockedRuleRepository(db).create(payload, tenant_code=tenant_code)
    safe_audit_log(
        db,
        tenant_code=tenant_code,
        module_name='blocked_rules',
        action_name='create_rule',
        payload={'rule_id': created.id, 'rule_type': created.rule_type, 'rule_value': created.rule_value},
        result='success',
    )
    return created


@router.put('/{rule_id}', response_model=BlockedSenderRuleRead)
def update_rule(
    rule_id: int,
    payload: BlockedSenderRuleUpdate,
    db: Session = Depends(db_session),
    tenant_code: str = Depends(resolve_tenant_code),
):
    repo = BlockedRuleRepository(db)
    obj = repo.get(rule_id, tenant_code=tenant_code)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Rule not found')
    updated = repo.update(obj, payload)
    safe_audit_log(
        db,
        tenant_code=tenant_code,
        module_name='blocked_rules',
        action_name='update_rule',
        payload={'rule_id': updated.id, 'rule_type': updated.rule_type, 'rule_value': updated.rule_value},
        result='success',
    )
    return updated


@router.delete('/{rule_id}', response_model=MessageResponse)
def delete_rule(
    rule_id: int,
    db: Session = Depends(db_session),
    tenant_code: str = Depends(resolve_tenant_code),
):
    repo = BlockedRuleRepository(db)
    obj = repo.get(rule_id, tenant_code=tenant_code)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Rule not found')
    repo.delete(obj)
    safe_audit_log(
        db,
        tenant_code=tenant_code,
        module_name='blocked_rules',
        action_name='delete_rule',
        payload={'rule_id': rule_id, 'rule_type': obj.rule_type, 'rule_value': obj.rule_value},
        result='success',
    )
    return {'message': 'Rule deleted'}
