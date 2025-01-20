from __future__ import annotations

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class AuthConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='auth_')

    secret_key: str = 'SECRET'
    access_jwt_lifetime: int = 60 * 60
    refresh_jwt_lifetime: int = 24 * 60 * 60

    @property
    def oauth2_token_url(self) -> str:
        return 'v1/jwt/login'


class PostgreSQLConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='postgresql_')

    host: str = 'localhost'
    port: int = 5432
    database: str
    username: str
    password: str

    @property
    def engine_url(self) -> str:
        return f'postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}'


class RedisConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='redis_')

    host: str = 'localhost'
    port: int = 5432


class CacheConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='cache_')

    timeout: int = 60 * 5


class SuperUserConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='superuser_')

    login: str
    password: str


# noinspection PyArgumentList
class Settings(BaseSettings):
    auth: AuthConfig = AuthConfig()
    postgresql: PostgreSQLConfig = PostgreSQLConfig()
    redis: RedisConfig = RedisConfig()
    cache: CacheConfig = CacheConfig()
    superuser: SuperUserConfig = SuperUserConfig()


settings = Settings()
