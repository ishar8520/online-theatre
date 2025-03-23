from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class ProjectConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='project_')

    name: str = 'admin_panel'


class OpenTelemetryConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='otel_')

    enabled: bool = False
    request_id_required: bool = False
    exporter_otlp_http_endpoint: str | None = None
    service_name: str = 'admin_panel'


class AdminNotificationConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='admin_panel_')

    scheme: str = 'http'
    host: str = 'localhost'
    port: int = 8000


class SentryConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='sentry_')

    dsn: str = ''
    enable_sdk: bool = False
    enable_tracing: bool = False
    traces_sample_rate: float = 1.0
    profiles_sample_rate: float = 1.0


class PostgreSQLConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='postgresql_')

    host: str = 'localhost'
    port: int = 5432
    database: str = 'admin_panel'
    username: str = 'admin_panel'
    password: str = '123qwe'

    @property
    def engine_url(self) -> str:
        return f'postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}'


class RedisConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='redis_')
    
    host: str
    port: int
    
class Settings(BaseSettings):
    project: ProjectConfig = ProjectConfig()
    admin_notification: AdminNotificationConfig = AdminNotificationConfig()
    otel: OpenTelemetryConfig = OpenTelemetryConfig()
    sentry: SentryConfig = SentryConfig()
    postgresql: PostgreSQLConfig = PostgreSQLConfig()  # type: ignore[call-arg]
    redis: RedisConfig = RedisConfig()


settings = Settings()
