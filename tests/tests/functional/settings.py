from __future__ import annotations

from urllib.parse import urljoin

from dotenv import load_dotenv
from pydantic import (
    Field,
)
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

load_dotenv()


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='redis_')

    host: str = Field(default='localhost')
    port: int = Field(default=6379)


class ElasticsearchSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='elastic_')

    scheme: str = Field(default='http')
    host: str = Field(default='localhost')
    port: int = Field(default=9200)

    @property
    def url(self) -> str:
        return f'{self.scheme}://{self.host}:{self.port}'


class AuthPostgresqlSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='auth_postgresql_')

    database: str = Field(default='auth')
    username: str = Field(default='auth')
    password: str = Field()
    host: str = Field(default='localhost')
    port: int = Field(default=5432)


class SuperUserSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='auth_superuser_')

    login: str = Field()
    password: str = Field()


class RateLimiterConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='ratelimiter_')

    times: int = 5
    seconds: int = 60


class AutRedisConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='auth_redis_')

    host: str = Field(default='localhost')
    port: int = Field(default=6379)


class MongoSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='mongo_')

    db: str = ''

    host: str | None = Field(default='localhost')
    port: int | None = Field(default=27017)



class Settings(BaseSettings):
    redis: RedisSettings = RedisSettings()
    elasticsearch: ElasticsearchSettings = ElasticsearchSettings()
    auth_postgresql: AuthPostgresqlSettings = AuthPostgresqlSettings()  # type: ignore[call-arg]
    superuser: SuperUserSettings = SuperUserSettings()  # type: ignore[call-arg]
    ratelimiter: RateLimiterConfig = RateLimiterConfig()
    auth_redis: AutRedisConfig = AutRedisConfig()
    mongo: MongoSettings = MongoSettings()

    movies_url: str = Field(default='http://localhost:8000')
    auth_url: str = Field(default='http://localhost:8000')
    ugc_url: str = Field(default='http://localhost:8000/ugc-mongo')

    @property
    def movies_api_url(self) -> str:
        return urljoin(self.movies_url, '/api/')

    @property
    def movies_api_v1_url(self) -> str:
        return urljoin(self.movies_url, '/api/v1/')

    @property
    def auth_api_url(self) -> str:
        return urljoin(self.auth_url, '/auth/api/')

    @property
    def auth_api_v1_url(self) -> str:
        return urljoin(self.auth_url, '/auth/api/v1/')

    @property
    def ugc_api_v1_url(self) -> str:
        return urljoin(self.ugc_url, '/v1/')


settings = Settings()
