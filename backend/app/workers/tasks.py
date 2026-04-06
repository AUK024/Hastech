from app.db.session import SessionLocal
from app.integrations.language_detection.mock_provider import MockLanguageDetectionProvider
from app.integrations.microsoft_graph.client import GraphClient
from app.integrations.translation.mock_provider import MockTranslationProvider
from app.repositories.audit_log_repository import AuditLogRepository
from app.services.mail_processing_service import MailProcessingService
from app.workers.celery_app import celery_app


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={'max_retries': 3})
def process_graph_mail_event(self, mailbox_id: int, mailbox_email: str, message_id: str) -> dict:
    db = SessionLocal()
    try:
        service = MailProcessingService(
            db=db,
            graph_client=GraphClient(),
            lang_provider=MockLanguageDetectionProvider(),
            translation_provider=MockTranslationProvider(),
        )
        result = service.process_graph_event(mailbox_id=mailbox_id, mailbox_email=mailbox_email, message_id=message_id)
        AuditLogRepository(db).create(
            module_name='worker',
            action_name='process_graph_mail_event',
            payload={'mailbox_id': mailbox_id, 'mailbox_email': mailbox_email, 'message_id': message_id},
            result=result.get('status', 'unknown'),
        )
        return result
    finally:
        db.close()
