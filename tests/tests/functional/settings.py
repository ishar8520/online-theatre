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


class Settings(BaseSettings):
    redis: RedisSettings = RedisSettings()
    elasticsearch: ElasticsearchSettings = ElasticsearchSettings()

    movies_url: str = Field(default='http://localhost:8000')

    @property
    def movies_api_url(self) -> str:
        return urljoin(self.movies_url, '/api/')

    @property
    def movies_api_v1_url(self) -> str:
        return urljoin(self.movies_url, '/api/v1/')
    
    @property
    def auth_api_url(self) -> str:
        return urljoin(self.movies_url, '/auth/')


settings = Settings()
