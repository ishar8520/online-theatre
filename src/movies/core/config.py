from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class ProjectConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='project_')

    name: str | None = None


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


class Settings(BaseSettings):
    project: ProjectConfig = ProjectConfig()
    redis: RedisConfig = RedisConfig()
    elasticsearch: ElasticConfig = ElasticConfig()


settings = Settings()
