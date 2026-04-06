from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.api.deps import db_session
from app.models.auto_reply_log import AutoReplyLog
from app.models.incoming_email import IncomingEmail

router = APIRouter()


@router.get('/')
def dashboard_stats(db: Session = Depends(db_session)) -> dict:
    incoming_mail_count = db.scalar(select(func.count(IncomingEmail.id))) or 0
    daily_external = db.scalar(select(func.count(IncomingEmail.id)).where(IncomingEmail.is_internal.is_(False))) or 0
    replied_mail_count = db.scalar(select(func.count(AutoReplyLog.id)).where(AutoReplyLog.reply_sent.is_(True))) or 0
    daily_errors = db.scalar(select(func.count(IncomingEmail.id)).where(IncomingEmail.processing_status == 'error')) or 0

    lang_rows = db.execute(
        select(IncomingEmail.detected_language, func.count(IncomingEmail.id))
        .group_by(IncomingEmail.detected_language)
        .order_by(func.count(IncomingEmail.id).desc())
        .limit(10)
    ).all()

    return {
        'incoming_mail_count': incoming_mail_count,
        'replied_mail_count': replied_mail_count,
        'daily_incoming': incoming_mail_count,
        'daily_external': daily_external,
        'daily_auto_reply_sent': replied_mail_count,
        'daily_errors': daily_errors,
        'language_distribution': [{'lang': row[0] or 'unknown', 'count': row[1]} for row in lang_rows],
        'top_domains': [],
        'top_mailboxes': [],
    }
