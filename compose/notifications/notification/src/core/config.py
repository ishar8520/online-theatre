from __future__ import annotations

import uuid

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)


class AdminSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='auth_superuser_')

    login: str
    password: str


class QueueSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='queue_')

    host: str = 'localhost'
    port: int = 8000

    @property
    def notification_url_template(self) -> str:
        return f'http://{self.host}:{self.port}/api/v1/notifications/send/template'


class TemplateList(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='template_message_')

    registration: uuid.UUID
    new_movie: uuid.UUID


class Settings(BaseSettings):
    admin: AdminSettings = AdminSettings() # type: ignore[call-arg]
    queue: QueueSettings = QueueSettings()

    templates: TemplateList = TemplateList() # type: ignore[call-arg]


settings = Settings()
