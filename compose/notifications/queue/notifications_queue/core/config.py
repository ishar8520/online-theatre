from __future__ import annotations

import uuid
from urllib.parse import urljoin

from pydantic_settings import BaseSettings, SettingsConfigDict


class NotificationsQueueConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='notifications_queue_')


class NotificationsAdminPanelConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='notifications_admin_panel_')

    scheme: str = 'http'
    host: str = 'localhost'
    port: int = 8000

    @property
    def service_url(self) -> str:
        return f'{self.scheme}://{self.host}:{self.port}'

    @property
    def api_url(self) -> str:
        return urljoin(self.service_url, '/admin_panel/api/')

    @property
    def api_v1_url(self) -> str:
        return urljoin(self.api_url, 'v1/')

    def get_template_by_id_url(self, *, template_id: uuid.UUID) -> str:
        return f'template/{template_id}'

    def get_template_by_code_url(self, *, template_code: str) -> str:
        return f'template/by-code/{template_code}'


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

    def get_login_url(self) -> str:
        return 'jwt/login'

    def get_refresh_url(self) -> str:
        return 'jwt/refresh'

    def get_user_url(self, *, user_id: uuid.UUID) -> str:
        return f'users/{user_id}/profile'

    def get_users_list_url(self) -> str:
        return f'users/list'


class RabbitMQConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='rabbitmq_')

    host: str = 'localhost'
    port: int = 5672
    username: str
    password: str

    @property
    def url(self) -> str:
        return f'amqp://{self.username}:{self.password}@{self.host}:{self.port}'


class RedisConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='redis_')

    host: str = 'localhost'
    port: int = 6379

    @property
    def url(self) -> str:
        return f'redis://{self.host}:{self.port}'


class SmtpConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='smtp_')

    host: str = 'localhost'
    port: int = 1025
    username: str = 'username'
    password: str = 'password'


class EmailConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='email_')
    
    from_email: str = 'email_service@example.com'
    
class DQLRabbitMQConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='dlq_rabbitmq_')
    
    queue_name: str = 'undelivered_messages'
    
    @property
    def url(self) -> str:
        return f'amqp://{self.username}:{self.password}@{self.host}:{self.port}'

class Settings(BaseSettings):
    notifications_queue: NotificationsQueueConfig = NotificationsQueueConfig()
    notifications_admin_panel: NotificationsAdminPanelConfig = NotificationsAdminPanelConfig()
    auth: AuthConfig = AuthConfig()  # type: ignore[call-arg]
    rabbitmq: RabbitMQConfig = RabbitMQConfig()  # type: ignore[call-arg]
    redis: RedisConfig = RedisConfig()
    smtp: SmtpConfig = SmtpConfig()
    email: EmailConfig = EmailConfig()
    dlq: DQLRabbitMQConfig = DQLRabbitMQConfig()

settings = Settings()
