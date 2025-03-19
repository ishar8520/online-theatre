from __future__ import annotations

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)


class AdminSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='notifications_admin_')

    login: str
    password: str


class QueueSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='queue_')

    host: str
    port: int


class Settings(BaseSettings):
    admin: AdminSettings = AdminSettings()
    queue: QueueSettings = QueueSettings()
