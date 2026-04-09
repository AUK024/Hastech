from app.db.session import SessionLocal
from app.integrations.microsoft_graph.client import GraphClient
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.settings_repository import SettingsRepository
from app.services.mail_processing_service import MailProcessingService
from app.services.provider_factory import ProviderFactory
from app.services.settings_service import SettingsService
from app.workers.celery_app import celery_app


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={'max_retries': 3})
def process_graph_mail_event(
    self,
    mailbox_id: int,
    mailbox_email: str,
    message_id: str,
    tenant_code: str = 'default',
) -> dict:
    db = SessionLocal()
    try:
        settings_service = SettingsService(SettingsRepository(db))
        provider_factory = ProviderFactory(settings_service)
        service = MailProcessingService(
            db=db,
            graph_client=GraphClient(),
            lang_provider=provider_factory.build_language_detection_provider(),
            translation_provider=provider_factory.build_translation_provider(),
        )
        result = service.process_graph_event(
            mailbox_id=mailbox_id,
            mailbox_email=mailbox_email,
            message_id=message_id,
            tenant_code=tenant_code,
        )
        AuditLogRepository(db).create(
            tenant_code=tenant_code,
            module_name='worker',
            action_name='process_graph_mail_event',
            payload={
                'mailbox_id': mailbox_id,
                'mailbox_email': mailbox_email,
                'message_id': message_id,
                'tenant_code': tenant_code,
            },
            result=result.get('status', 'unknown'),
        )
        return result
    finally:
        db.close()
