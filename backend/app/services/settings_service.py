from app.repositories.settings_repository import SettingsRepository


class SettingsService:
    def __init__(self, settings_repo: SettingsRepository) -> None:
        self.settings_repo = settings_repo

    def get_value(self, key: str, default: str) -> str:
        item = self.settings_repo.get(key)
        return item.setting_value if item else default

    def get_bool(self, key: str, default: bool) -> bool:
        value = self.get_value(key, str(default).lower())
        return value.lower() in {'1', 'true', 'yes', 'on'}

    def get_float(self, key: str, default: float) -> float:
        value = self.get_value(key, str(default))
        try:
            return float(value)
        except ValueError:
            return default

    def seed_defaults(self) -> None:
        defaults = [
            ('internal_domain', 'hascelik.com', 'Kurumiçi domain'),
            ('fallback_language', 'en', 'Düşük confidence için fallback dil'),
            ('confidence_threshold', '0.70', 'Minimum language confidence threshold'),
            ('prevent_duplicate_thread_reply', 'true', 'Aynı thread için tekrar yanıt engeli'),
            ('translation_enabled', 'true', 'Çeviri aktif/pasif'),
            ('only_first_mail_reply', 'true', 'Sadece ilk maile otomatik cevap ver'),
            ('mail_loop_guard_enabled', 'true', 'Tanımlı mailbox kaynaklı mail loop engeli'),
            ('skip_if_thread_has_sent_reply', 'true', 'Thread içinde sent item varsa otomatik cevap verme'),
        ]
        for key, value, desc in defaults:
            if not self.settings_repo.get(key):
                self.settings_repo.upsert(key=key, value=value, description=desc)
