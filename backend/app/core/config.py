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

    default_fallback_language: str = 'en'
    default_confidence_threshold: float = 0.70

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    @property
    def database_url(self) -> str:
        return f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
