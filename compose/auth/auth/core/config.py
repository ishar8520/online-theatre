from __future__ import annotations

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class PostgreSQLConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='postgresql_')

    host: str | None = 'localhost'
    port: int | None = 5432
    database: str = Field()
    username: str | None = None
    password: str | None = None


class RedisConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='redis_')

    host: str = 'localhost'
    port: int = 5432
    cache_expire_in_seconds: int = 60 * 5


class Settings(BaseSettings):
    postgresql: PostgreSQLConfig = PostgreSQLConfig()
    redis: RedisConfig = RedisConfig()


settings = Settings()
