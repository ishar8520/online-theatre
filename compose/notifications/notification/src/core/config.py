from __future__ import annotations

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
    def queue_url(self) -> str:
        return f'http://{self.host}:{self.port}/api/v1/notifications/send/'


class Settings(BaseSettings):
    admin: AdminSettings = AdminSettings() # type: ignore[call-arg]
    queue: QueueSettings = QueueSettings()


settings = Settings()
