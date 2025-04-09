from __future__ import annotations

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)


class PaymentServiceSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='payment_service_')

    host: str = 'localhost'
    port: int = 8000

    @property
    def created_url(self) -> str:
        return f'http://{self.host}:{self.port}/api/v1/payment/create'


class Settings(BaseSettings):
    payment_service: PaymentServiceSettings = PaymentServiceSettings()


settings = Settings()
