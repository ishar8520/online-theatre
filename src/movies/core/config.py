from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class ProjectConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='project_')

    name: str = 'movies'


class OpenTelemetryConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='otel_')

    enabled: bool = False
    request_id_required: bool = False
    exporter_otlp_http_endpoint: str | None = None
    service_name: str = 'movies'


class RedisConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='redis_')

    host: str = 'localhost'
    port: int = 5432
    cache_expire_in_seconds: int = 60 * 5


class ElasticConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='elastic_')

    scheme: str = 'http'
    host: str = 'localhost'
    port: int = 9200

    index_name_films: str = 'films'
    index_name_genres: str = 'genres'
    index_name_persons: str = 'persons'

    @property
    def url(self) -> str:
        return f'{self.scheme}://{self.host}:{self.port}'


class AuthConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='auth_')

    scheme: str = 'http'
    host: str = 'localhost'
    port: int = 8000

    @property
    def url_token(self) -> str:
        return f'{self.scheme}://{self.host}:{self.port}/auth/api/v1/jwt/login'

    @property
    def url_me(self) -> str:
        return f'{self.scheme}://{self.host}:{self.port}/auth/api/v1/users/me'


class Settings(BaseSettings):
    project: ProjectConfig = ProjectConfig()
    redis: RedisConfig = RedisConfig()
    elasticsearch: ElasticConfig = ElasticConfig()
    auth: AuthConfig = AuthConfig()
    otel: OpenTelemetryConfig = OpenTelemetryConfig()


settings = Settings()
