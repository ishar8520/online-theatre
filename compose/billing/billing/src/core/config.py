from __future__ import annotations

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)


class PaymentServiceSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="payment_service_")

    host: str = "localhost"
    port: int = 8000

    @property
    def created_url(self) -> str:
        return f"http://{self.host}:{self.port}/api/v1/payment/create"


class PostgresqlSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="postgresql_")

    host: str = 'localhost'
    port: int = 5432
    database: str = 'billing'
    username: str = 'movies'
    password: str = '123456'

    @property
    def engine_url(self):
        return f'postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}'


class Settings(BaseSettings):
    payment_service: PaymentServiceSettings = PaymentServiceSettings()
    postgresql: PostgresqlSettings = PostgresqlSettings()


settings = Settings()
