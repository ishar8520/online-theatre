from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class NotificationsQueueConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='notifications_queue_')


class Settings(BaseSettings):
    notifications_queue: NotificationsQueueConfig = NotificationsQueueConfig()


settings = Settings()
