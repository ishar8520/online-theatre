from __future__ import annotations

import uuid
from urllib.parse import urljoin

from pydantic_settings import BaseSettings, SettingsConfigDict


class NotificationsQueueConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='notifications_queue_')


class AuthConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='auth_')

    scheme: str = 'http'
    host: str = 'localhost'
    port: int = 8000
    superuser_login: str
    superuser_password: str

    @property
    def service_url(self) -> str:
        return f'{self.scheme}://{self.host}:{self.port}'

    @property
    def api_url(self) -> str:
        return urljoin(self.service_url, '/auth/api/')

    @property
    def api_v1_url(self) -> str:
        return urljoin(self.api_url, 'v1/')

    def get_user_url(self, *, user_id: uuid.UUID) -> str:
        return urljoin(self.api_v1_url, f'users/{user_id}')

    def get_login_url(self) -> str:
        return urljoin(self.api_v1_url, f'jwt/login')

    def get_refresh_url(self) -> str:
        return urljoin(self.api_v1_url, f'jwt/refresh')


class Settings(BaseSettings):
    notifications_queue: NotificationsQueueConfig = NotificationsQueueConfig()
    auth: AuthConfig = AuthConfig()  # type: ignore[call-arg]


settings = Settings()
