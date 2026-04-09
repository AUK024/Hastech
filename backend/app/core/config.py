from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = 'Hascelik Mail Automation Platform'
    env: str = 'dev'
    debug: bool = True
    api_prefix: str = '/api/v1'

    postgres_host: str = 'localhost'
    postgres_port: int = 5432
    postgres_db: str = 'hascelik_mail'
    postgres_user: str = 'hascelik'
    postgres_password: str = 'hascelik'

    redis_url: str = 'redis://localhost:6379/0'
    celery_broker_url: str = 'redis://localhost:6379/1'
    celery_result_backend: str = 'redis://localhost:6379/2'

    graph_tenant_id: str = ''
    graph_client_id: str = ''
    graph_client_secret: str = ''
    graph_scope: str = 'https://graph.microsoft.com/.default'
    graph_base_url: str = 'https://graph.microsoft.com/v1.0'
    graph_webhook_client_state: str = ''
    graph_webhook_notification_url: str = ''
    graph_webhook_lifecycle_url: str = ''
    graph_subscription_expiry_minutes: int = 120
    graph_subscription_renew_threshold_minutes: int = 30
    azure_translator_endpoint: str = 'https://api.cognitive.microsofttranslator.com'
    azure_translator_key: str = ''
    azure_translator_region: str = ''

    admin_user_emails: str = 'admin@hascelik.com'
    admin_user_domains: str = ''

    default_fallback_language: str = 'en'
    default_confidence_threshold: float = 0.70
    default_tenant_code: str = 'default'

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    @property
    def database_url(self) -> str:
        return f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @staticmethod
    def _parse_csv(value: str) -> set[str]:
        return {item.strip().lower() for item in value.split(',') if item.strip()}

    @property
    def admin_email_set(self) -> set[str]:
        return self._parse_csv(self.admin_user_emails)

    @property
    def admin_domain_set(self) -> set[str]:
        return self._parse_csv(self.admin_user_domains)

    def is_admin_email(self, email: str) -> bool:
        normalized = email.strip().lower()
        if not normalized or '@' not in normalized:
            return False
        domain = normalized.split('@', 1)[1]
        return normalized in self.admin_email_set or domain in self.admin_domain_set


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
