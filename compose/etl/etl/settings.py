from __future__ import annotations

from dotenv import load_dotenv
from pydantic import (
    Field,
)
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

load_dotenv()


class PostgreSQLSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='postgresql_')

    host: str | None = Field(default=None)
    port: int | None = Field(default=None)
    database: str = Field()
    username: str | None = Field(default=None)
    password: str | None = Field(default=None)

    def get_connection_params(self) -> dict:
        return {
            'host': self.host,
            'port': self.port,
            'dbname': self.database,
            'user': self.username,
            'password': self.password,
        }


class ElasticsearchSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='elastic_')

    host: str | None = Field(default=None)
    port: int | None = Field(default=None)
    # url: str = Field(default='http://localhost:9200')


class Settings(BaseSettings):
    postgresql: PostgreSQLSettings = PostgreSQLSettings()
    elasticsearch: ElasticsearchSettings = ElasticsearchSettings()


settings = Settings()
