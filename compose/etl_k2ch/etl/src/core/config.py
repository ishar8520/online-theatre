from __future__ import annotations

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
)


class KafkaSettings(BaseSettings):
    hosts: str = Field(default="localhost:9092")
    topic: str = Field(default="messages")

    @property
    def kafka_hosts_as_list(self) -> list[str]:
        return self.hosts.split(",")


class Settings(BaseSettings):
    kafka: KafkaSettings = KafkaSettings()


settings = Settings()
