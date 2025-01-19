from __future__ import annotations

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class AuthConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='auth_')

    secret_key: str = 'SECRET'
    jwt_lifetime: int = 3600


class PostgreSQLConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='postgresql_')

    host: str = 'localhost'
    port: int = 5432
    database: str = Field()
    username: str = Field()
    password: str = Field()

    @property
    def engine_url(self) -> str:
        return f'postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}'


class RedisConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='redis_')

    host: str = 'localhost'
    port: int = 5432
    cache_expire_in_seconds: int = 60 * 5


class SuperUserConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='superuser_')

    login: str
    password: str


class Settings(BaseSettings):
    auth: AuthConfig = AuthConfig()
    postgresql: PostgreSQLConfig = PostgreSQLConfig()
    redis: RedisConfig = RedisConfig()
    superuser: SuperUserConfig = SuperUserConfig()


settings = Settings()
