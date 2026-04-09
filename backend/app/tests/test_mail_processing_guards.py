from types import SimpleNamespace
from app.services.mail_processing_service import MailProcessingService


class FakeSettings:
    def __init__(self, values: dict[str, str]):
        self.values = values

    def get_value(self, key: str, default: str) -> str:
        return self.values.get(key, default)

    def get_bool(self, key: str, default: bool) -> bool:
        value = self.values.get(key, str(default).lower())
        return value.lower() in {'1', 'true', 'yes', 'on'}

    def get_float(self, key: str, default: float) -> float:
        value = self.values.get(key, str(default))
        try:
            return float(value)
        except ValueError:
            return default


class FakeIncomingRepo:
    def __init__(self, conversation_rows: list[SimpleNamespace] | None = None):
        self.conversation_rows = conversation_rows or []

    def get_by_message_id(self, message_id: str):
        return None

    def create(self, **kwargs):
        return SimpleNamespace(id=101)

    def get_by_conversation(self, conversation_id: str):
        return self.conversation_rows


class FakeReplyRepo:
    def has_successful_reply_for_conversation(self, incoming_email_ids: list[int]) -> bool:
        return False

    def create(self, **kwargs):
        return SimpleNamespace(id=201)


class FakeLangProvider:
    def detect_language(self, text: str) -> dict:
        return {'language': 'en', 'confidence': 0.99}


class FakeTranslationProvider:
    def translate(self, text: str, source_language: str, target_language: str) -> str:
        return text


class FakeGraphClient:
    def __init__(self, sender_email: str, sent_reply_exists: bool):
        self.sender_email = sender_email
        self.sent_reply_exists = sent_reply_exists
        self.send_reply_called = False

    def get_message(self, mailbox_email: str, message_id: str) -> dict:
        return {
            'id': message_id,
            'internet_message_id': f'<{message_id}@example.com>',
            'conversation_id': 'conv-1',
            'sender_name': 'Sender',
            'sender_email': self.sender_email,
            'subject': 'Test',
            'body_preview': 'Body',
        }

    def has_sent_reply_in_conversation(self, mailbox_email: str, conversation_id: str) -> bool:
        return self.sent_reply_exists

    def send_reply(self, mailbox_email: str, message_id: str, comment: str) -> None:
        self.send_reply_called = True


def build_service(graph_client: FakeGraphClient) -> MailProcessingService:
    service = MailProcessingService(
        db=None,
        graph_client=graph_client,
        lang_provider=FakeLangProvider(),
        translation_provider=FakeTranslationProvider(),
    )
    service.settings = FakeSettings(
        {
            'internal_domain': 'hascelik.com',
            'fallback_language': 'en',
            'confidence_threshold': '0.70',
            'mail_loop_guard_enabled': 'true',
            'skip_if_thread_has_sent_reply': 'true',
            'prevent_duplicate_thread_reply': 'true',
            'only_first_mail_reply': 'false',
            'translation_enabled': 'true',
        }
    )
    service.incoming_repo = FakeIncomingRepo([SimpleNamespace(id=101)])
    service.reply_repo = FakeReplyRepo()
    service.blocked_repo = SimpleNamespace(list=lambda: [])
    service.mailbox_repo = SimpleNamespace(list=lambda: [])
    service.template_repo = SimpleNamespace(list=lambda: [])
    return service


def test_mail_loop_guard_skips_when_sender_is_managed_mailbox() -> None:
    graph_client = FakeGraphClient(sender_email='sales@hascelik.com', sent_reply_exists=False)
    service = build_service(graph_client)
    service.mailbox_repo = SimpleNamespace(list=lambda: [SimpleNamespace(email='sales@hascelik.com', is_active=True)])

    result = service.process_graph_event(mailbox_id=1, mailbox_email='sales@hascelik.com', message_id='m-1')

    assert result['status'] == 'skipped'
    assert result['reason'] == 'mail_loop_guard'
    assert graph_client.send_reply_called is False


def test_thread_has_sent_reply_guard_skips_auto_reply() -> None:
    graph_client = FakeGraphClient(sender_email='external@example.com', sent_reply_exists=True)
    service = build_service(graph_client)

    result = service.process_graph_event(mailbox_id=1, mailbox_email='sales@hascelik.com', message_id='m-2')

    assert result['status'] == 'skipped'
    assert result['reason'] == 'thread_has_sent_reply'
    assert graph_client.send_reply_called is False
