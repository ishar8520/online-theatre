from __future__ import annotations

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)


class KafkaSettings(BaseSettings):
    kafka_hosts: str = Field(validation_alias="KAFKA_HOSTS", default="kafka-0:9092")
    kafka_topic: str = Field(default="messages")

    @property
    def kafka_hosts_as_list(self) -> list[str]:
        return self.kafka_hosts.split(",")


class SentrySettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='sentry_')

    dsn: str = ''
    enable_sdk: bool = False
    enable_tracing: bool = False
    traces_sample_rate: float = 1.0
    profiles_sample_rate: float = 1.0


settings = KafkaSettings()
sentry_settings = SentrySettings()
