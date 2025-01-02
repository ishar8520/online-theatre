from __future__ import annotations

from logging import config as logging_config

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .logger import LOGGING

logging_config.dictConfig(LOGGING)


class ProjectConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='project_')

    name: str | None = Field(default=None)


class RedisConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='redis_')

    host: str = Field(default='localhost')
    port: int = Field(default=5432)
    cache_expire_in_seconds: int = 60 * 5


class ElasticConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='elastic_')

    scheme: str = Field(default='http')
    host: str = Field(default='localhost')
    port: int = Field(default=9200)

    index_name_films: str = Field(default='films')
    index_name_genres: str = Field(default='genres')
    index_name_persons: str = Field(default='persons')

    @property
    def url(self) -> str:
        return f'{self.scheme}://{self.host}:{self.port}'


class Settings(BaseSettings):
    project: ProjectConfig = ProjectConfig()
    redis: RedisConfig = RedisConfig()
    elasticsearch: ElasticConfig = ElasticConfig()


settings = Settings()
