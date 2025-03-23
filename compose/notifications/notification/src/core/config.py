from __future__ import annotations

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)


class QueueSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='queue_')

    host: str = 'localhost'
    port: int = 8000

    @property
    def notification_url_template(self) -> str:
        return f'http://{self.host}:{self.port}/api/v1/notifications/send/template'


class Settings(BaseSettings):
    queue: QueueSettings = QueueSettings()


settings = Settings()
