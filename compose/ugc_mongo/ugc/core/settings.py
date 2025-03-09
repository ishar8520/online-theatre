from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MongoSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='mongo_')

    db: str = ''

    host: str | None = Field(default='localhost')
    port: int | None = Field(default=27017)


class Settings(BaseSettings):
    mongo: MongoSettings = MongoSettings()


settings = Settings()
