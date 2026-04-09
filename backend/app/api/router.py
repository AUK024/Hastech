from fastapi import APIRouter
from app.api.routes import (
    auth,
    mailboxes,
    templates,
    blocked_rules,
    settings,
    incoming_mails,
    auto_reply_logs,
    reports,
    dashboard,
    workers,
    translations,
    language_detection,
    webhooks,
    logs,
    employee_users,
    graph_subscriptions,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix='/auth', tags=['auth'])
api_router.include_router(webhooks.router, prefix='/webhooks', tags=['webhooks'])
api_router.include_router(mailboxes.router, prefix='/mailboxes', tags=['mailboxes'])
api_router.include_router(templates.router, prefix='/templates', tags=['templates'])
api_router.include_router(blocked_rules.router, prefix='/blocked-rules', tags=['blocked-rules'])
api_router.include_router(settings.router, prefix='/settings', tags=['settings'])
api_router.include_router(incoming_mails.router, prefix='/incoming-mails', tags=['incoming-mails'])
api_router.include_router(auto_reply_logs.router, prefix='/auto-reply-logs', tags=['auto-reply-logs'])
api_router.include_router(reports.router, prefix='/reports', tags=['reports'])
api_router.include_router(dashboard.router, prefix='/dashboard', tags=['dashboard'])
api_router.include_router(workers.router, prefix='/workers', tags=['workers'])
api_router.include_router(translations.router, prefix='/translations', tags=['translations'])
api_router.include_router(language_detection.router, prefix='/language-detection', tags=['language-detection'])
api_router.include_router(logs.router, prefix='/logs', tags=['logs'])
api_router.include_router(employee_users.router, prefix='/employee-users', tags=['employee-users'])
api_router.include_router(graph_subscriptions.router, prefix='/graph-subscriptions', tags=['graph-subscriptions'])
