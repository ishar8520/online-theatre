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


class ElasticsearchSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='elastic_')

    scheme: str = Field(default='http')
    host: str = Field(default='localhost')
    port: int = Field(default=9200)

    @property
    def url(self) -> str:
        return f'{self.scheme}://{self.host}:{self.port}'


class Settings(BaseSettings):
    elasticsearch: ElasticsearchSettings = ElasticsearchSettings()

    movies_url: str = Field(default='http://localhost:8000')

    @property
    def movies_api_url(self) -> str:
        return urljoin(self.movies_url, '/api/')


settings = Settings()
