from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.deps import db_session
from app.repositories.incoming_email_repository import IncomingEmailRepository
from app.schemas.incoming_email import IncomingEmailRead

router = APIRouter()


@router.get('/', response_model=list[IncomingEmailRead])
def list_incoming_mails(limit: int = Query(default=100, ge=1, le=500), db: Session = Depends(db_session)):
    return IncomingEmailRepository(db).list(limit=limit)
