from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.api.deps import db_session
from app.models.incoming_email import IncomingEmail

router = APIRouter()


@router.get('/domains')
def report_domains(db: Session = Depends(db_session)) -> dict:
    rows = db.execute(
        select(func.split_part(IncomingEmail.sender_email, '@', 2).label('domain'), func.count(IncomingEmail.id))
        .group_by('domain')
        .order_by(func.count(IncomingEmail.id).desc())
        .limit(25)
    ).all()
    return {'top_domains': [{'domain': domain or 'unknown', 'count': count} for domain, count in rows]}


@router.get('/personnel')
def report_personnel(db: Session = Depends(db_session)) -> dict:
    rows = db.execute(
        select(IncomingEmail.mailbox_id, func.count(IncomingEmail.id))
        .group_by(IncomingEmail.mailbox_id)
        .order_by(func.count(IncomingEmail.id).desc())
        .limit(25)
    ).all()
    return {'top_personnel': [{'mailbox_id': mailbox_id, 'count': count} for mailbox_id, count in rows]}
