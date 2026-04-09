from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.integrations.language_detection.base import LanguageDetectionProvider
from app.integrations.translation.base import TranslationProvider
from app.integrations.microsoft_graph.client import GraphClient
from app.models.auto_reply_template import AutoReplyTemplate
from app.repositories.auto_reply_log_repository import AutoReplyLogRepository
from app.repositories.blocked_rule_repository import BlockedRuleRepository
from app.repositories.incoming_email_repository import IncomingEmailRepository
from app.repositories.mailbox_repository import MailboxRepository
from app.repositories.settings_repository import SettingsRepository
from app.repositories.template_repository import TemplateRepository
from app.services.rule_engine import RuleEngineService
from app.services.settings_service import SettingsService
from app.utils.email_parser import extract_domain


class MailProcessingService:
    def __init__(
        self,
        db: Session,
        graph_client: GraphClient,
        lang_provider: LanguageDetectionProvider,
        translation_provider: TranslationProvider,
    ) -> None:
        self.db = db
        self.graph_client = graph_client
        self.lang_provider = lang_provider
        self.translation_provider = translation_provider
        self.rule_engine = RuleEngineService()
        self.settings = SettingsService(SettingsRepository(db))
        self.incoming_repo = IncomingEmailRepository(db)
        self.reply_repo = AutoReplyLogRepository(db)
        self.blocked_repo = BlockedRuleRepository(db)
        self.mailbox_repo = MailboxRepository(db)
        self.template_repo = TemplateRepository(db)

    def _pick_active_template(self) -> AutoReplyTemplate | None:
        templates = self.template_repo.list()
        for tpl in templates:
            if tpl.is_active:
                return tpl
        return None

    def process_graph_event(self, mailbox_id: int, mailbox_email: str, message_id: str) -> dict:
        mailbox = self.mailbox_repo.get(mailbox_id)
        if not mailbox or not mailbox.is_active:
            return {'status': 'skipped', 'reason': 'mailbox_inactive_or_missing', 'message_id': message_id}

        existing = self.incoming_repo.get_by_message_id(message_id)
        if existing:
            return {'status': 'duplicate_message', 'message_id': message_id, 'incoming_email_id': existing.id}

        resolved_mailbox_email = mailbox.email
        message = self.graph_client.get_message(mailbox_email=resolved_mailbox_email, message_id=message_id)
        sender_email = message.get('sender_email', '').lower()
        conversation_id = message.get('conversation_id', message_id)
        body_preview = message.get('body_preview', '')
        normalized_mailbox_email = resolved_mailbox_email.lower()
        managed_mailbox_emails = {
            mailbox.email.lower()
            for mailbox in self.mailbox_repo.list()
            if mailbox.is_active
        }
        mail_loop_guard_enabled = self.settings.get_bool('mail_loop_guard_enabled', True)
        is_managed_mail_loop = mail_loop_guard_enabled and (
            sender_email == normalized_mailbox_email or sender_email in managed_mailbox_emails
        )

        blocked_rules = self.blocked_repo.list()
        is_blocked = self.rule_engine.is_sender_blocked(sender_email=sender_email, rules=blocked_rules)

        internal_domain = self.settings.get_value('internal_domain', 'hascelik.com')
        is_internal = extract_domain(sender_email) == internal_domain.lower().lstrip('@')

        detected = self.lang_provider.detect_language(text=body_preview)
        confidence_threshold = self.settings.get_float('confidence_threshold', 0.70)
        fallback_language = self.settings.get_value('fallback_language', 'en')

        detected_lang = str(detected.get('language', fallback_language))
        confidence = float(detected.get('confidence', 0.0))
        if confidence < confidence_threshold:
            detected_lang = fallback_language

        incoming = self.incoming_repo.create(
            mailbox_id=mailbox_id,
            message_id=message_id,
            internet_message_id=message.get('internet_message_id'),
            conversation_id=conversation_id,
            sender_name=message.get('sender_name'),
            sender_email=sender_email,
            subject=message.get('subject'),
            body_preview=body_preview,
            detected_language=detected_lang,
            confidence_score=confidence,
            received_at=datetime.now(timezone.utc),
            is_internal=is_internal,
            is_blocked_by_rule=is_blocked,
            processing_status='processed',
            error_message=None,
        )

        if is_managed_mail_loop:
            return {
                'status': 'skipped',
                'reason': 'mail_loop_guard',
                'incoming_email_id': incoming.id,
            }

        if not mailbox.auto_reply_enabled:
            return {
                'status': 'skipped',
                'reason': 'mailbox_auto_reply_disabled',
                'incoming_email_id': incoming.id,
            }

        if is_internal or is_blocked:
            return {
                'status': 'skipped',
                'reason': 'internal_or_blocked',
                'incoming_email_id': incoming.id,
            }

        prevent_duplicate_thread_reply = self.settings.get_bool('prevent_duplicate_thread_reply', True)
        only_first_mail_reply = self.settings.get_bool('only_first_mail_reply', True)
        skip_if_thread_has_sent_reply = self.settings.get_bool('skip_if_thread_has_sent_reply', True)
        conversation_emails = self.incoming_repo.get_by_conversation(conversation_id)
        conversation_ids = [row.id for row in conversation_emails]

        if skip_if_thread_has_sent_reply and self.graph_client.has_sent_reply_in_conversation(
            mailbox_email=resolved_mailbox_email,
            conversation_id=conversation_id,
        ):
            return {'status': 'skipped', 'reason': 'thread_has_sent_reply', 'incoming_email_id': incoming.id}

        if prevent_duplicate_thread_reply and self.reply_repo.has_successful_reply_for_conversation(conversation_ids):
            return {'status': 'skipped', 'reason': 'already_replied_thread', 'incoming_email_id': incoming.id}

        if only_first_mail_reply and len(conversation_ids) > 1:
            return {'status': 'skipped', 'reason': 'not_first_mail_in_thread', 'incoming_email_id': incoming.id}

        template = self._pick_active_template()
        if not template:
            return {'status': 'skipped', 'reason': 'no_active_template', 'incoming_email_id': incoming.id}

        translation_enabled = self.settings.get_bool('translation_enabled', True)
        subject = template.subject_template
        body = (template.body_template + "\n\n" + (template.signature_template or "")).strip()

        if translation_enabled:
            subject = self.translation_provider.translate(
                text=subject,
                source_language=template.source_language,
                target_language=detected_lang,
            )
            body = self.translation_provider.translate(
                text=body,
                source_language=template.source_language,
                target_language=detected_lang,
            )

        self.graph_client.send_reply(mailbox_email=resolved_mailbox_email, message_id=message_id, comment=body)
        log = self.reply_repo.create(
            incoming_email_id=incoming.id,
            template_id=template.id,
            translated_subject=subject,
            translated_body=body,
            target_language=detected_lang,
            reply_sent=True,
            sent_at=datetime.now(timezone.utc),
            provider_message_id=f'graph-reply-{message_id}',
            error_message=None,
        )
        return {
            'status': 'replied',
            'incoming_email_id': incoming.id,
            'auto_reply_log_id': log.id,
            'target_language': detected_lang,
        }
