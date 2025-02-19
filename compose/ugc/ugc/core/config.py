from __future__ import annotations

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
)


class KafkaSettings(BaseSettings):
    kafka_hosts: str = Field(validation_alias='KAFKA_HOSTS', default='localhost:9092')

    @property
    def kafka_hosts_as_list(self) -> list[str]:
        return self.kafka_hosts.split(',')


settings = KafkaSettings()

