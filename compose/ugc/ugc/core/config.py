from __future__ import annotations

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
)


class KafkaSettings(BaseSettings):
    kafka_hosts: str = Field(validation_alias="KAFKA_HOSTS", default="kafka-0:9092")
    kafka_topic: str = Field(default="messages")

    @property
    def kafka_hosts_as_list(self) -> list[str]:
        return self.kafka_hosts.split(",")


settings = KafkaSettings()
