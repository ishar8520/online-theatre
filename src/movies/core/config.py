import os
from logging import config as logging_config
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

from .logger import LOGGING

logging_config.dictConfig(LOGGING)


class ProjectConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='project_')
    
    name: str | None = Field(default=None)


class RedisConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='redis_')
    
    host: str | None = Field(default='localhost')
    port: int | None = Field(default=5432)
    cache_expire_in_seconds: int = 60 * 5


class ElasticConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='elastic_')
    
    host: str | None = Field(default='localhost')
    port: int | None = Field(default=9200)
    index_name_films: str = Field(default='films')
    index_name_genres: str = Field(default='genres')
    index_name_persons: str = Field(default='persons')  

    
class Settings(BaseSettings):
    project: ProjectConfig=ProjectConfig()
    redis: RedisConfig=RedisConfig()
    elasticsearch: ElasticConfig=ElasticConfig()


settings = Settings()
