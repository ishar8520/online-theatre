# mypy: disable-error-code=call-arg
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class PaymentServiceSettings(BaseSettings):
    """Конфигурация подключения к сервису оплаты."""

    model_config = SettingsConfigDict(env_prefix="payment_service_")

    host: str = "localhost"
    port: int = 8000

    @property
    def base_url(self) -> str:
        """Возвращает базовый URL для API сервиса оплаты."""
        return f"http://{self.host}:{self.port}/payment/api/v1"


class PostgresqlSettings(BaseSettings):
    """Конфигурация подключения к базе данных PostgreSQL."""

    model_config = SettingsConfigDict(env_prefix="postgresql_")

    host: str = 'localhost'
    port: int = 5432
    database: str = 'billing'
    username: str = 'admin'
    password: str = '123456'

    @property
    def engine_url(self) -> str:
        """Формирует URL подключения для SQLAlchemy с использованием asyncpg."""
        return f'postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}'


class AuthConfig(BaseSettings):
    """Конфигурация для сервиса аутентификации."""

    model_config = SettingsConfigDict(env_prefix='auth_')

    scheme: str = 'http'
    host: str = 'localhost'
    port: int = 8000

    @property
    def oauth2_token_url(self) -> str:
        """Путь для получения OAuth2 токена."""
        return '/auth/api/v1/jwt/login'

    @property
    def user_profile_url(self) -> str:
        """Полный URL для получения профиля текущего пользователя."""
        return f'{self.scheme}://{self.host}:{self.port}/auth/api/v1/users/me'


class NotificationConfig(BaseSettings):
    """Конфигурация для сервиса уведомлений"""
    
    model_config = SettingsConfigDict(env_prefix='notification_')

    scheme: str = 'http'
    host: str = 'localhost'
    port: int = 8000

class Settings(BaseSettings):
    """Основные настройки приложения."""

    test_mode: bool = False

    auth: AuthConfig = AuthConfig()
    payment_service: PaymentServiceSettings = PaymentServiceSettings()
    postgresql: PostgresqlSettings = PostgresqlSettings()
    notification: NotificationConfig = NotificationConfig()


settings = Settings()
