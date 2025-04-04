from __future__ import annotations

from pydantic_settings import (
    BaseSettings, SettingsConfigDict,
)


class KafkaSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="kafka_")

    host: str = "localhost:9092"

    @property
    def kafka_hosts_as_list(self) -> list[str]:
        return self.hosts.split(",")


class ClickhouseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="clickhouse_")

    host: str = "localhost"
    batch_size: int = 1000
    flush_interval: int = 5


class Settings(BaseSettings):
    kafka: KafkaSettings = KafkaSettings()
    clickhouse: ClickhouseSettings = ClickhouseSettings()


settings = Settings()
