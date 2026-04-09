from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import func, literal_column, select
from sqlalchemy.orm import Session
from app.api.deps import db_session
from app.models.auto_reply_log import AutoReplyLog
from app.models.incoming_email import IncomingEmail
from app.models.monitored_mailbox import MonitoredMailbox

router = APIRouter()


@router.get('/')
def dashboard_stats(db: Session = Depends(db_session)) -> dict:
    now_utc = datetime.now(timezone.utc)
    start_of_day = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
    trend_start = start_of_day - timedelta(days=13)

    incoming_mail_count = db.scalar(select(func.count(IncomingEmail.id))) or 0
    daily_external = (
        db.scalar(
            select(func.count(IncomingEmail.id))
            .where(IncomingEmail.is_internal.is_(False))
            .where(IncomingEmail.received_at >= start_of_day)
        )
        or 0
    )
    replied_mail_count = db.scalar(select(func.count(AutoReplyLog.id)).where(AutoReplyLog.reply_sent.is_(True))) or 0
    daily_incoming = (
        db.scalar(select(func.count(IncomingEmail.id)).where(IncomingEmail.received_at >= start_of_day)) or 0
    )
    daily_auto_reply_sent = (
        db.scalar(
            select(func.count(AutoReplyLog.id))
            .where(AutoReplyLog.reply_sent.is_(True))
            .where(AutoReplyLog.sent_at.is_not(None))
            .where(AutoReplyLog.sent_at >= start_of_day)
        )
        or 0
    )
    daily_errors = (
        db.scalar(
            select(func.count(IncomingEmail.id))
            .where(IncomingEmail.processing_status == 'error')
            .where(IncomingEmail.received_at >= start_of_day)
        )
        or 0
    )

    lang_rows = db.execute(
        select(IncomingEmail.detected_language, func.count(IncomingEmail.id))
        .group_by(IncomingEmail.detected_language)
        .order_by(func.count(IncomingEmail.id).desc())
        .limit(10)
    ).all()

    incoming_lang_rows = db.execute(
        select(IncomingEmail.detected_language, func.count(IncomingEmail.id))
        .where(IncomingEmail.received_at >= start_of_day)
        .group_by(IncomingEmail.detected_language)
    ).all()
    replied_lang_rows = db.execute(
        select(AutoReplyLog.target_language, func.count(AutoReplyLog.id))
        .where(AutoReplyLog.reply_sent.is_(True))
        .where(AutoReplyLog.sent_at.is_not(None))
        .where(AutoReplyLog.sent_at >= start_of_day)
        .group_by(AutoReplyLog.target_language)
    ).all()

    incoming_by_lang = {str(row[0] or 'unknown'): int(row[1]) for row in incoming_lang_rows}
    replied_by_lang = {str(row[0] or 'unknown'): int(row[1]) for row in replied_lang_rows}
    all_langs = sorted(set(incoming_by_lang.keys()) | set(replied_by_lang.keys()))
    language_performance = [
        {
            'lang': lang,
            'incoming_count': incoming_by_lang.get(lang, 0),
            'replied_count': replied_by_lang.get(lang, 0),
        }
        for lang in all_langs
    ]

    incoming_day_expr = func.date_trunc('day', IncomingEmail.received_at).label('incoming_day')
    incoming_daily_rows = db.execute(
        select(incoming_day_expr, func.count(IncomingEmail.id))
        .where(IncomingEmail.received_at >= trend_start)
        .group_by(incoming_day_expr)
        .order_by(incoming_day_expr.asc())
    ).all()
    replied_day_expr = func.date_trunc('day', AutoReplyLog.sent_at).label('replied_day')
    replied_daily_rows = db.execute(
        select(replied_day_expr, func.count(AutoReplyLog.id))
        .where(AutoReplyLog.reply_sent.is_(True))
        .where(AutoReplyLog.sent_at.is_not(None))
        .where(AutoReplyLog.sent_at >= trend_start)
        .group_by(replied_day_expr)
        .order_by(replied_day_expr.asc())
    ).all()

    incoming_daily_map = {
        row[0].date().isoformat(): int(row[1]) for row in incoming_daily_rows if row[0] is not None
    }
    replied_daily_map = {
        row[0].date().isoformat(): int(row[1]) for row in replied_daily_rows if row[0] is not None
    }
    daily_trend = []
    for day_offset in range(14):
        day = trend_start + timedelta(days=day_offset)
        key = day.date().isoformat()
        daily_trend.append(
            {
                'date': key,
                'incoming_count': incoming_daily_map.get(key, 0),
                'replied_count': replied_daily_map.get(key, 0),
            }
        )

    domain_expr = func.split_part(
        IncomingEmail.sender_email, literal_column("'@'"), literal_column('2')
    ).label('sender_domain')
    domain_count_expr = func.count(IncomingEmail.id).label('domain_count')
    top_domain_rows = db.execute(
        select(domain_expr, domain_count_expr)
        .where(IncomingEmail.sender_email.contains('@'))
        .group_by(domain_expr)
        .order_by(domain_count_expr.desc())
        .limit(10)
    ).all()

    top_mailbox_rows = db.execute(
        select(MonitoredMailbox.email, func.count(IncomingEmail.id))
        .join(MonitoredMailbox, MonitoredMailbox.id == IncomingEmail.mailbox_id)
        .group_by(MonitoredMailbox.email)
        .order_by(func.count(IncomingEmail.id).desc())
        .limit(10)
    ).all()

    return {
        'incoming_mail_count': incoming_mail_count,
        'replied_mail_count': replied_mail_count,
        'daily_incoming': daily_incoming,
        'daily_external': daily_external,
        'daily_auto_reply_sent': daily_auto_reply_sent,
        'daily_errors': daily_errors,
        'language_distribution': [{'lang': row[0] or 'unknown', 'count': row[1]} for row in lang_rows],
        'language_performance': language_performance,
        'daily_trend': daily_trend,
        'top_domains': [{'domain': row[0] or 'unknown', 'count': row[1]} for row in top_domain_rows],
        'top_mailboxes': [{'mailbox': row[0], 'count': row[1]} for row in top_mailbox_rows],
    }
